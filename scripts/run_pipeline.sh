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

: "${GRAFANA_ADMIN_PASSWORD:?Set GRAFANA_ADMIN_PASSWORD to a strong local secret before running}"

cd "$(dirname "$0")/.."

# Host/port/budget helpers, also driven directly by the tests.
# shellcheck source=scripts/lib/host.sh
source "$(dirname "$0")/lib/host.sh"

TIMESTAMP="$(date -u +%Y-%m-%d_%H%M%S)"
CPU_RUN_ID="${TIMESTAMP}_cpu"
CUDA_RUN_ID="${TIMESTAMP}_cuda"
SKIP_CPU_FINETUNE="${SKIP_CPU_FINETUNE:-1}"
SKIP_CPU_EVAL="${SKIP_CPU_EVAL:-0}"
SKIP_GGUF="${SKIP_GGUF:-0}"
COMPUTE_DEVICE="${COMPUTE_DEVICE:-auto}"
SOURCE_GIT_SHA="${SOURCE_GIT_SHA:-$(git rev-parse --verify HEAD 2>/dev/null || printf unknown)}"
if [[ -z "${SOURCE_GIT_DIRTY+x}" ]]; then
  if [[ -n "$(git status --porcelain --untracked-files=normal 2>/dev/null | head -n 1)" ]]; then
    SOURCE_GIT_DIRTY=true
  else
    SOURCE_GIT_DIRTY=false
  fi
fi
export SOURCE_GIT_SHA SOURCE_GIT_DIRTY
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
#
# `shared` is for the setup steps that run once and belong to neither device. They
# used to be invoked as `run_app cuda`, and this function's catch-all branch stamped
# them CUDA_RUN_ID — so on a machine with no GPU at all, downloading papers and
# building the index reported RUN_ID=<stamp>_cuda. The dashboards group on the stamp,
# so a device-free id groups correctly and claims nothing untrue.
run_id_for_device() {
  case "$1" in
    cpu)    echo "$CPU_RUN_ID" ;;
    shared) echo "$TIMESTAMP" ;;
    *)      echo "$CUDA_RUN_ID" ;;
  esac
}

# Run a script inside the app container on a given device.
# Usage: run_app cpu|cuda|shared scripts/foo.py [args...]
#   shared — a setup step belonging to neither device; uses the GPU when one is
#            present (indexing embeds faster there) but is stamped device-free.
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
# Before any step writes a row. An existing volume can be several columns behind —
# the app used to be the only thing that migrated it, which left the migration path
# behind whatever was wrong with the app. This needs only the postgres service.
scripts/migrate_db.sh
reclaim_outputs

echo "========================================================================"
echo "gguf-demo pipeline — one step at a time"
echo "  App budget: ${APP_MEM_LIMIT} RAM, ${APP_CPUS:-auto-detected} CPUs, uid ${APP_UID}"
echo "  UIs: MLflow http://localhost:${MLFLOW_PORT}  Grafana http://localhost:${GRAFANA_PORT} (admin)"
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
run_app shared scripts/01_download_papers.py

echo ""
echo "==> Step 1b: Generate QA pairs (once)"
run_app shared scripts/01b_generate_qa_pairs.py

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
run_app shared scripts/03_create_rag_db.py

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
