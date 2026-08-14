#!/usr/bin/env bash
# Full evaluation pipeline: one step at a time.
#
# Shared setup runs once. Each metric-producing step runs on CPU first,
# then again on GPU when CUDA is available — before moving to the next step.
#
#   Step 1 / 1b / 3  → once
#   Step 2, 4, 5, 6  → CPU, then GPU (if available)
#   Step 7 / 8       → export CPU run, CUDA run, combined summary
#
# Env knobs:
#   COMPUTE_DEVICE=auto  (default) — use NVIDIA GPU when Docker supports it, else CPU
#   COMPUTE_DEVICE=cpu|cuda       — force a device mode (cuda fails instead of falling back)
#   SKIP_CPU_FINETUNE=1  (default) — skip CPU LoRA train (RAM-heavy)
#   SKIP_GGUF=0          (default) — also eval baseline/RAG with llama.cpp GGUF
#   SKIP_GGUF=1          — Transformers-only (skip GGUF download + llama.cpp)
set -euo pipefail

cd "$(dirname "$0")/.."

TIMESTAMP="$(date -u +%Y-%m-%d_%H%M%S)"
CPU_RUN_ID="${TIMESTAMP}_cpu"
CUDA_RUN_ID="${TIMESTAMP}_cuda"
SKIP_CPU_FINETUNE="${SKIP_CPU_FINETUNE:-1}"
SKIP_CPU_EVAL="${SKIP_CPU_EVAL:-0}"
SKIP_GGUF="${SKIP_GGUF:-0}"
COMPUTE_DEVICE="${COMPUTE_DEVICE:-auto}"
CPU_TORCH_INDEX_URL="https://download.pytorch.org/whl/cpu"
CUDA_TORCH_INDEX_URL="https://download.pytorch.org/whl/cu130"
COMPOSE=(docker compose -f docker-compose.yml)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

start_stack() {
  case "$COMPUTE_DEVICE" in
    auto|cpu|cuda) ;;
    *)
      echo "ERROR: COMPUTE_DEVICE must be one of: auto, cpu, cuda" >&2
      return 2
      ;;
  esac

  if [[ "$COMPUTE_DEVICE" == "cpu" ]]; then
    echo "==> Starting services in CPU mode"
    TORCH_INDEX_URL="${TORCH_INDEX_URL:-$CPU_TORCH_INDEX_URL}" \
      "${COMPOSE[@]}" up -d --build
    return
  fi

  if [[ "$COMPUTE_DEVICE" == "cuda" ]] || gpu_is_available; then
    COMPOSE+=(-f docker-compose.gpu.yml)
    echo "==> Starting services with NVIDIA GPU support"
    if TORCH_INDEX_URL="${TORCH_INDEX_URL:-$CUDA_TORCH_INDEX_URL}" \
      "${COMPOSE[@]}" up -d --build; then
      return
    fi

    if [[ "$COMPUTE_DEVICE" == "cuda" ]]; then
      echo "ERROR: CUDA mode was requested, but the GPU-enabled stack failed to start." >&2
      return 1
    fi

    echo "    GPU-enabled startup failed — retrying with the CPU stack."
    COMPOSE=(docker compose -f docker-compose.yml)
  fi

  echo "==> Starting services in CPU mode"
  TORCH_INDEX_URL="${TORCH_INDEX_URL:-$CPU_TORCH_INDEX_URL}" \
    "${COMPOSE[@]}" up -d --build
}

gpu_is_available() {
  command -v nvidia-smi >/dev/null 2>&1 &&
    nvidia-smi -L >/dev/null 2>&1 &&
    docker info --format '{{json .Runtimes}}' 2>/dev/null | grep -q '"nvidia"'
}

# Memory this script may account for, in bytes.
#
# The number that matters is what Docker can actually give a container, not what
# the machine running this script has. On Linux those are the same. On macOS and
# Windows they are not: Docker Desktop runs a fixed-size VM, often 8GB, on a Mac
# with far more RAM — and /proc/meminfo does not exist there at all, so the old
# reading fell through to a 10g default that the VM could not honor and the app
# container was killed on load. `docker info` reports the VM, so it is right on
# every platform; the host reading is only a fallback for when Docker cannot be
# queried, and a cgroup limit still wins when the pipeline itself runs in a
# container.
available_memory_bytes() {
  local docker_total="" physical="" limit="" kb
  docker_total="$(docker info --format '{{.MemTotal}}' 2>/dev/null || true)"
  [[ "$docker_total" =~ ^[0-9]+$ ]] && (( docker_total > 0 )) || docker_total=""

  if [[ -r /proc/meminfo ]]; then
    kb="$(awk '/^MemTotal:/ {print $2; exit}' /proc/meminfo)"
    [[ "$kb" =~ ^[0-9]+$ ]] && physical=$(( kb * 1024 ))
  elif [[ "$(uname -s)" == "Darwin" ]]; then
    physical="$(sysctl -n hw.memsize 2>/dev/null || true)"
    [[ "$physical" =~ ^[0-9]+$ ]] || physical=""
  fi

  # Prefer Docker's view; fall back to the host's only when it is unavailable.
  local budget="${docker_total:-$physical}"

  for f in /sys/fs/cgroup/memory.max /sys/fs/cgroup/memory/memory.limit_in_bytes; do
    [[ -r "$f" ]] || continue
    local value
    value="$(cat "$f")"
    # cgroup v2 reports "max"; v1 reports a sentinel larger than real RAM.
    if [[ "$value" =~ ^[0-9]+$ ]] && { [[ -z "$budget" ]] || (( value < budget )); }; then
      limit="$value"
      break
    fi
  done
  echo "${limit:-${budget:-0}}"
}

# First free TCP port at or after $1, so a published port that the host already
# uses does not fail the whole stack. macOS runs an AirPlay Receiver on 5000,
# which is what stopped MLflow from starting there.
first_free_port() {
  local port="$1" limit=$(( $1 + 20 ))
  while (( port < limit )); do
    if ! port_in_use "$port"; then
      echo "$port"
      return 0
    fi
    port=$(( port + 1 ))
  done
  echo "$1"  # Nothing free nearby; let Docker report the conflict itself.
}

# A port this stack already publishes is not a conflict. Without this, re-running
# the pipeline against a live stack sees its own MLflow on 5000, moves to 5001,
# recreates the container, and walks one port further on every subsequent run.
#
# Decision: matching any `rag-*` container name is deliberately loose. A container
# outside this stack that is both named rag-* and holding one of these ports would
# be misread as ours, and Docker would then refuse the bind — a loud, immediate
# failure at `up`, not a silent one. Tightening this to the exact container names
# would buy a better error message for a case that has not occurred; the ports these
# services want are the real constraint.
port_held_by_this_stack() {
  local port="$1" names
  names="$(docker ps --filter "publish=${port}" --format '{{.Names}}' 2>/dev/null || true)"
  [[ -n "$names" ]] && grep -q '^rag-' <<<"$names"
}

port_in_use() {
  local port="$1"
  port_held_by_this_stack "$port" && return 1
  # Try the tools most likely to exist, newest first.
  #
  # Decision: fail open — a host with none of lsof/ss/netstat reports every port
  # free. This is the right default *here*, and deliberately unlike the results
  # budget guard, which fails closed. The two differ in what a wrong answer costs:
  # an unnoticed port conflict surfaces immediately as a Docker bind error at `up`
  # and nothing is lost, whereas an unmeasured results/ lets a runaway copy keep
  # writing to the host disk. Blocking the whole pipeline because a probe binary is
  # missing would trade a guaranteed stop for a recoverable, self-announcing error.
  if command -v lsof >/dev/null 2>&1; then
    lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1 && return 0
    return 1
  fi
  if command -v ss >/dev/null 2>&1; then
    ss -lntH "sport = :$port" 2>/dev/null | grep -q . && return 0
    return 1
  fi
  if command -v netstat >/dev/null 2>&1; then
    netstat -an 2>/dev/null | grep -qE "[.:]${port}[[:space:]]+.*LISTEN" && return 0
    return 1
  fi
  return 1
}

# Publish each service on a port the host actually has free, and say so when the
# preferred one was taken — otherwise the UI URLs printed later are wrong.
resolve_published_ports() {
  local name preferred chosen
  for spec in "MLFLOW_PORT 5000" "GRAFANA_PORT 3000" "PROMETHEUS_PORT 9090" \
              "POSTGRES_PORT 5432" "APP_PORT 8000"; do
    name="${spec%% *}"
    preferred="${spec##* }"
    if [[ -n "${!name:-}" ]]; then
      continue  # Explicitly set by the caller; respect it even if it is busy.
    fi
    chosen="$(first_free_port "$preferred")"
    export "$name=$chosen"
    if [[ "$chosen" != "$preferred" ]]; then
      echo "    Port ${preferred} is in use; publishing ${name%_PORT} on ${chosen}." >&2
    fi
  done
}

# Leave roughly a third of memory to the rest of the machine: the app container
# is the only large consumer, but Docker, Postgres, MLflow and the host still
# need room. Phi-3 in bfloat16 plus BERTScore needs about 9GB.
default_mem_limit_gb() {
  local total gb
  total="$(available_memory_bytes)"
  (( total == 0 )) && { echo 10; return; }
  gb=$(( total * 2 / 3 / 1024 / 1024 / 1024 ))
  (( gb < 4 )) && gb=4
  (( gb > 14 )) && gb=14
  echo "$gb"
}

# The run id a step's rows are stamped with. It must follow the device, not the
# pipeline: a CPU step and a GPU step of the same invocation write different ids
# (${TIMESTAMP}_cpu, ${TIMESTAMP}_cuda) sharing the TIMESTAMP prefix, which is what
# lets the dashboards group them into one run while keeping the two legs separable.
# Stamping both with TIMESTAMP would make CPU and GPU rows indistinguishable.
run_id_for_device() {
  case "$1" in
    cpu) echo "$CPU_RUN_ID" ;;
    *)   echo "$CUDA_RUN_ID" ;;
  esac
}

# Run a script inside the app container on a given device.
# Usage: run_app cpu|cuda scripts/foo.py [args...]
run_app() {
  local device="$1"
  shift
  if [[ "$device" == "cpu" ]]; then
    "${COMPOSE[@]}" exec -T \
      -e CUDA_VISIBLE_DEVICES=-1 \
      -e COMPUTE_DEVICE=cpu \
      -e SKIP_AUTO_EXPORT=1 \
      -e "RUN_ID=$(run_id_for_device cpu)" \
      app python "$@"
  else
    "${COMPOSE[@]}" exec -T \
      -e SKIP_AUTO_EXPORT=1 \
      -e "RUN_ID=$(run_id_for_device "$device")" \
      app python "$@"
  fi
}

# Same as run_app but allows extra -e KEY=VAL pairs before the script path.
# Usage: run_app_env cpu|cuda "FINE_TUNED_PATH=/app/..." scripts/06_....py
run_app_env() {
  local device="$1"
  local extra_env="$2"
  shift 2
  local -a env_flags=(-e SKIP_AUTO_EXPORT=1 -e "RUN_ID=$(run_id_for_device "$device")")
  if [[ -n "$extra_env" ]]; then
    env_flags+=(-e "$extra_env")
  fi
  if [[ "$device" == "cpu" ]]; then
    env_flags+=(-e CUDA_VISIBLE_DEVICES=-1 -e COMPUTE_DEVICE=cpu)
  fi
  "${COMPOSE[@]}" exec -T "${env_flags[@]}" app python "$@"
}

snapshot() {
  # snapshot <src_basename> <device>  e.g. snapshot baseline_results cpu
  local name="$1"
  local device="$2"
  "${COMPOSE[@]}" exec -T app bash -c \
    "test -f data/processed/${name}.json && cp data/processed/${name}.json data/processed/${name}_${device}.json || true"
}

stage_for_export() {
  # Copy device-tagged artifacts back to canonical names before export
  local device="$1"
  "${COMPOSE[@]}" exec -T app bash -c "
    for f in baseline_results baseline_gguf_results rag_results rag_gguf_results comparison_report; do
      if [ -f data/processed/\${f}_${device}.json ]; then
        cp data/processed/\${f}_${device}.json data/processed/\${f}.json
      fi
    done
  "
}

export_results() {
  # export_results <run_id> <cpu|cuda>. The device matters: the export records the
  # hardware it detects, so exporting a CPU run from a GPU-visible process is how
  # a CPU run came to report an RTX 4080 as its device.
  local run_id="$1"
  local device="${2:-cuda}"
  run_app "$device" scripts/07_export_results.py --run-id "$run_id"
  assert_results_budget "after exporting ${run_id}"
}

compare_runtimes() {
  "${COMPOSE[@]}" exec -T app python scripts/09_compare_runtimes.py "$@"
  assert_results_budget "after 09_compare_runtimes"
}

# results/ is bind-mounted onto the host disk, so a snapshot that copies a parent of
# results/latest/ writes the duplicated tree to the host for real — that filled a
# 200GB volume and deadlocked WSL before any step failed. Fail loudly on both the
# shape (results/ nested inside itself) and the size, rather than silently doubling.
RESULTS_MAX_MB="${RESULTS_MAX_MB:-5000}"

assert_results_budget() {
  local when="${1:-at startup}" used_mb nested
  # Any results/<anything>/results, not just results/latest/results: a wrong snapshot
  # destination nests under whatever folder it was pointed at.
  nested="$(compgen -G 'results/*/results' || true)"
  if [[ -n "$nested" ]]; then
    echo "ERROR: results/ is nested inside itself (${when}): ${nested//$'\n'/ }" >&2
    echo "       A snapshot copied results/ into itself. Deleting it by hand is the" >&2
    echo "       only way out: an export never removes a directory from results/latest/," >&2
    echo "       so rerunning the pipeline stops here again. Check the folder, then:" >&2
    echo "         rm -rf ${nested//$'\n'/ }" >&2
    echo "       results/runs/ holds the real exports and is not affected." >&2
    return 1
  fi
  # Nothing exported yet is fine; a results/ that exists but cannot be measured is not.
  # Failing open here would let the runaway growth this guard exists to catch through
  # exactly when the tree is too broken to walk.
  [[ -d results ]] || return 0
  if ! used_mb="$(du -sm results 2>/dev/null | cut -f1)" || [[ ! "$used_mb" =~ ^[0-9]+$ ]]; then
    echo "ERROR: could not measure results/ (${when})." >&2
    echo "       du failed or returned no total — check permissions and ownership" >&2
    echo "       (scripts/run_pipeline.sh reclaim_outputs chowns container-written files)." >&2
    return 1
  fi
  if (( used_mb > RESULTS_MAX_MB )); then
    echo "ERROR: results/ is ${used_mb}MB, over the ${RESULTS_MAX_MB}MB budget (${when})." >&2
    echo "       Exports are text artifacts and should be a few MB per run. Check for" >&2
    echo "       a model, cache, or nested copy under results/ before rerunning." >&2
    echo "       Raise RESULTS_MAX_MB only once you know why it grew." >&2
    return 1
  fi
}

# Files the container writes land as root on a bind mount unless the app runs as
# the host user. Compose sets user: $APP_UID:$APP_GID; this chown covers the
# Hugging Face cache volume (created as root on first pull) and anything that
# still slipped through.
reclaim_outputs() {
  local uid gid
  uid="${APP_UID:-$(id -u)}"
  gid="${APP_GID:-$(id -g)}"
  "${COMPOSE[@]}" exec -T -u 0 app chown -R "${uid}:${gid}" \
    /app/results /app/data /app/models /app/.cache /tmp/prometheus_multiproc \
    /mlflow-artifacts \
    2>/dev/null || true
}

APP_MEM_LIMIT="${APP_MEM_LIMIT:-$(default_mem_limit_gb)g}"
export APP_MEM_LIMIT
export APP_UID="${APP_UID:-$(id -u)}"
export APP_GID="${APP_GID:-$(id -g)}"
if [[ "$APP_MEM_LIMIT" =~ ^([0-9]+)g$ ]] && (( BASH_REMATCH[1] < 9 )); then
  echo "WARNING: app container capped at ${APP_MEM_LIMIT}; Phi-3 needs ~9GB." >&2
  echo "         Expect the container to be killed, or set a smaller LLM_MODEL." >&2
  if [[ "$(uname -s)" != "Linux" ]]; then
    echo "         On Docker Desktop this cap comes from the VM's memory, not the" >&2
    echo "         machine's: raise it in Settings > Resources > Memory." >&2
  fi
fi

assert_results_budget "at startup"
resolve_published_ports
start_stack
reclaim_outputs

echo "========================================================================"
echo "gguf-demo pipeline — one step at a time"
echo "  App budget: ${APP_MEM_LIMIT} RAM, ${APP_CPUS:-auto-detected} CPUs, uid ${APP_UID}"
echo "  UIs: MLflow http://localhost:${MLFLOW_PORT}  Grafana http://localhost:${GRAFANA_PORT}"
if [[ "$SKIP_CPU_EVAL" == "1" ]]; then
  echo "  Mode: GPU-only evals (SKIP_CPU_EVAL=1)"
else
  echo "  Each eval step: CPU first, then GPU (if available)"
fi
echo "  Run stamp: ${TIMESTAMP}"
echo "========================================================================"

# ---------------------------------------------------------------------------
# Detect CUDA once (GPU visible)
# ---------------------------------------------------------------------------

echo ""
echo "==> Detect CUDA"
if "${COMPOSE[@]}" exec -T app python -c "import torch; raise SystemExit(0 if torch.cuda.is_available() else 1)"; then
  HAS_CUDA=1
  if [[ "$SKIP_CPU_EVAL" == "1" ]]; then
    echo "    CUDA available — running GPU evals only (SKIP_CPU_EVAL=1)."
  else
    echo "    CUDA available — eval steps will run twice (CPU → GPU)."
  fi
  "${COMPOSE[@]}" exec app python scripts/check_cuda.py || true
else
  HAS_CUDA=0
  SKIP_CPU_EVAL=0
  echo "    CUDA not available — eval steps will run on CPU only."
fi

# ---------------------------------------------------------------------------
# Shared setup (once)
# ---------------------------------------------------------------------------

echo ""
echo "==> Step 1: Download papers (once)"
run_app cuda scripts/01_download_papers.py

echo ""
echo "==> Step 1b: Generate QA pairs (once)"
run_app cuda scripts/01b_generate_qa_pairs.py

# ---------------------------------------------------------------------------
# Step 2: Baseline — CPU (optional), then GPU
# ---------------------------------------------------------------------------

if [[ "$SKIP_CPU_EVAL" != "1" ]]; then
  echo ""
  echo "==> Step 2: Baseline evaluation [CPU / Transformers]"
  run_app cpu scripts/02_baseline_evaluation.py
  snapshot baseline_results cpu
  if [[ "$SKIP_GGUF" != "1" ]]; then
    echo ""
    echo "==> Step 2b: Baseline evaluation [CPU / GGUF llama.cpp]"
    run_app_env cpu "LLM_RUNTIME=gguf" scripts/02_baseline_evaluation.py
    snapshot baseline_gguf_results cpu
  fi
fi

if [[ "$HAS_CUDA" -eq 1 ]]; then
  echo ""
  echo "==> Step 2: Baseline evaluation [GPU / Transformers]"
  run_app cuda scripts/02_baseline_evaluation.py
  snapshot baseline_results cuda
  if [[ "$SKIP_GGUF" != "1" ]]; then
    echo ""
    echo "==> Step 2b: Baseline evaluation [GPU / GGUF llama.cpp]"
    run_app_env cuda "LLM_RUNTIME=gguf" scripts/02_baseline_evaluation.py
    snapshot baseline_gguf_results cuda
  fi
fi

# ---------------------------------------------------------------------------
# Step 3: RAG index (once)
# ---------------------------------------------------------------------------

echo ""
echo "==> Step 3: Create RAG database (once)"
run_app cuda scripts/03_create_rag_db.py

# ---------------------------------------------------------------------------
# Step 4: RAG eval — CPU (optional), then GPU
# ---------------------------------------------------------------------------

if [[ "$SKIP_CPU_EVAL" != "1" ]]; then
  echo ""
  echo "==> Step 4: RAG evaluation [CPU / Transformers]"
  run_app cpu scripts/04_rag_evaluation.py
  snapshot rag_results cpu
  if [[ "$SKIP_GGUF" != "1" ]]; then
    echo ""
    echo "==> Step 4b: RAG evaluation [CPU / GGUF llama.cpp]"
    run_app_env cpu "LLM_RUNTIME=gguf" scripts/04_rag_evaluation.py
    snapshot rag_gguf_results cpu
  fi
fi

if [[ "$HAS_CUDA" -eq 1 ]]; then
  echo ""
  echo "==> Step 4: RAG evaluation [GPU / Transformers]"
  run_app cuda scripts/04_rag_evaluation.py
  snapshot rag_results cuda
  if [[ "$SKIP_GGUF" != "1" ]]; then
    echo ""
    echo "==> Step 4b: RAG evaluation [GPU / GGUF llama.cpp]"
    run_app_env cuda "LLM_RUNTIME=gguf" scripts/04_rag_evaluation.py
    snapshot rag_gguf_results cuda
  fi
fi

# ---------------------------------------------------------------------------
# Step 5: Fine-tune — GPU preferred; CPU optional (SKIP_CPU_FINETUNE=1 by default)
# ---------------------------------------------------------------------------

if [[ "$SKIP_CPU_EVAL" != "1" && "$SKIP_CPU_FINETUNE" != "1" ]]; then
  echo ""
  echo "==> Step 5: Fine-tune LoRA [CPU]"
  echo "    Warning: CPU fine-tuning of Phi-3 can take a long time / use lots of RAM."
  run_app cpu scripts/05_fine_tune.py
  "${COMPOSE[@]}" exec -T app bash -c '
    if [ -d models/fine_tuned/adapter ]; then
      mkdir -p models/fine_tuned/adapter_cpu
      cp -a models/fine_tuned/adapter/. models/fine_tuned/adapter_cpu/
    fi
  '
elif [[ "$SKIP_CPU_FINETUNE" == "1" ]]; then
  echo ""
  echo "==> Step 5: Skipping CPU fine-tune (SKIP_CPU_FINETUNE=1)."
  echo "    Set SKIP_CPU_FINETUNE=0 to train LoRA on CPU as well."
fi

if [[ "$HAS_CUDA" -eq 1 ]]; then
  echo ""
  echo "==> Step 5: Fine-tune LoRA [GPU]"
  run_app cuda scripts/05_fine_tune.py
  "${COMPOSE[@]}" exec -T app bash -c '
    if [ -d models/fine_tuned/adapter ]; then
      mkdir -p models/fine_tuned/adapter_cuda
      cp -a models/fine_tuned/adapter/. models/fine_tuned/adapter_cuda/
    fi
  '
fi

# ---------------------------------------------------------------------------
# Step 6 / 7: Comparison + export
# ---------------------------------------------------------------------------

if [[ "$SKIP_CPU_EVAL" != "1" ]]; then
  echo ""
  echo "==> Step 6: Fine-tuned comparison [CPU]"
  CPU_ADAPTER="/app/models/fine_tuned/adapter_cpu"
  if "${COMPOSE[@]}" exec -T app test -d "$CPU_ADAPTER"; then
    run_app_env cpu "FINE_TUNED_PATH=${CPU_ADAPTER}" scripts/06_fine_tuned_evaluation.py
  elif "${COMPOSE[@]}" exec -T app test -d /app/models/fine_tuned/adapter; then
    echo "    No adapter_cpu — evaluating default adapter under CUDA_VISIBLE_DEVICES=-1 (CPU inference)."
    run_app cpu scripts/06_fine_tuned_evaluation.py
  else
    echo "    ERROR: No fine-tuned adapter found. Skipping Step 6 CPU."
  fi
  snapshot comparison_report cpu

  echo ""
  echo "==> Step 7a: Export CPU results → results/runs/${CPU_RUN_ID}"
  stage_for_export cpu
  export_results "$CPU_RUN_ID" cpu
  if [[ "$SKIP_GGUF" != "1" && "$HAS_CUDA" -eq 0 ]]; then
    echo ""
    echo "==> Step 9: Transformers vs GGUF [CPU run]"
    compare_runtimes \
      --cpu-run-id "$CPU_RUN_ID" \
      --out "results/runs/${TIMESTAMP}_transformers_vs_gguf"
  fi
fi

if [[ "$HAS_CUDA" -eq 1 ]]; then
  echo ""
  echo "==> Step 6: Fine-tuned comparison [GPU]"
  CUDA_ADAPTER="/app/models/fine_tuned/adapter_cuda"
  if "${COMPOSE[@]}" exec -T app test -d "$CUDA_ADAPTER"; then
    run_app_env cuda "FINE_TUNED_PATH=${CUDA_ADAPTER}" scripts/06_fine_tuned_evaluation.py
  elif "${COMPOSE[@]}" exec -T app test -d /app/models/fine_tuned/adapter; then
    run_app cuda scripts/06_fine_tuned_evaluation.py
  else
    echo "    ERROR: No fine-tuned adapter found. Skipping Step 6 GPU."
  fi
  snapshot comparison_report cuda

  echo ""
  echo "==> Step 7b: Export CUDA results → results/runs/${CUDA_RUN_ID}"
  stage_for_export cuda
  export_results "$CUDA_RUN_ID" cuda

  if [[ "$SKIP_CPU_EVAL" != "1" ]]; then
    echo ""
    echo "==> Step 8: CPU vs CUDA summary"
    "${COMPOSE[@]}" exec -T app python scripts/08_compare_devices.py \
      --cpu-run-id "$CPU_RUN_ID" \
      --cuda-run-id "$CUDA_RUN_ID" \
      --out "results/runs/${TIMESTAMP}_cpu_vs_cuda"
    assert_results_budget "after 08_compare_devices"
    if [[ "$SKIP_GGUF" != "1" ]]; then
      echo ""
      echo "==> Step 9: Transformers vs GGUF (same device pairs)"
      compare_runtimes \
        --cpu-run-id "$CPU_RUN_ID" \
        --cuda-run-id "$CUDA_RUN_ID" \
        --out "results/runs/${TIMESTAMP}_transformers_vs_gguf"
    fi
  elif [[ "$SKIP_GGUF" != "1" ]]; then
    echo ""
    echo "==> Step 9: Transformers vs GGUF [GPU run]"
    compare_runtimes \
      --cuda-run-id "$CUDA_RUN_ID" \
      --out "results/runs/${TIMESTAMP}_transformers_vs_gguf"
  fi
fi

reclaim_outputs

echo ""
echo "========================================================================"
echo "DONE"
echo "========================================================================"
if [[ "$SKIP_CPU_EVAL" != "1" ]]; then
  echo "  CPU results : results/runs/${CPU_RUN_ID}/"
fi
if [[ "$HAS_CUDA" -eq 1 ]]; then
  echo "  CUDA results: results/runs/${CUDA_RUN_ID}/"
  if [[ "$SKIP_CPU_EVAL" != "1" ]]; then
    echo "  Combined    : results/runs/${TIMESTAMP}_cpu_vs_cuda/"
  fi
fi
echo "  ★ Open first: results/latest/README.md"
echo ""
echo "Review then commit:"
echo "  git add results/"
echo "  git commit -m \"results: pipeline ${TIMESTAMP}\""
echo "========================================================================"
