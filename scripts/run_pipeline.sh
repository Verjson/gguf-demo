#!/usr/bin/env bash
# Full evaluation pipeline: one step at a time.
#
# Shared setup runs once. Each metric-producing step runs on CPU first,
# then again on GPU when CUDA is available — before moving to the next step.
#
#   Step 1 / 1b / 3  → once
#   Step 2, 4, 5, 6  → CPU, then GPU (if available)
#   Step 7 / 8       → export CPU run, CUDA run, combined summary
set -euo pipefail

cd "$(dirname "$0")/.."

TIMESTAMP="$(date -u +%Y-%m-%d_%H%M%S)"
CPU_RUN_ID="${TIMESTAMP}_cpu"
CUDA_RUN_ID="${TIMESTAMP}_cuda"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Run a script inside the app container on a given device.
# Usage: run_app cpu|cuda scripts/foo.py [args...]
run_app() {
  local device="$1"
  shift
  if [[ "$device" == "cpu" ]]; then
    docker compose exec -T \
      -e CUDA_VISIBLE_DEVICES= \
      -e SKIP_AUTO_EXPORT=1 \
      app python "$@"
  else
    docker compose exec -T \
      -e SKIP_AUTO_EXPORT=1 \
      app python "$@"
  fi
}

# Same as run_app but allows extra -e KEY=VAL pairs before the script path.
# Usage: run_app_env cpu|cuda "FINE_TUNED_PATH=/app/..." scripts/06_....py
run_app_env() {
  local device="$1"
  local extra_env="$2"
  shift 2
  local -a env_flags=(-e SKIP_AUTO_EXPORT=1)
  if [[ -n "$extra_env" ]]; then
    env_flags+=(-e "$extra_env")
  fi
  if [[ "$device" == "cpu" ]]; then
    env_flags+=(-e CUDA_VISIBLE_DEVICES=)
  fi
  docker compose exec -T "${env_flags[@]}" app python "$@"
}

snapshot() {
  # snapshot <src_basename> <device>  e.g. snapshot baseline_results cpu
  local name="$1"
  local device="$2"
  docker compose exec -T app bash -c \
    "test -f data/processed/${name}.json && cp data/processed/${name}.json data/processed/${name}_${device}.json || true"
}

stage_for_export() {
  # Copy device-tagged artifacts back to canonical names before export
  local device="$1"
  docker compose exec -T app bash -c "
    for f in baseline_results rag_results comparison_report; do
      if [ -f data/processed/\${f}_${device}.json ]; then
        cp data/processed/\${f}_${device}.json data/processed/\${f}.json
      fi
    done
  "
}

export_results() {
  local run_id="$1"
  docker compose exec -T app python scripts/07_export_results.py --run-id "$run_id"
}

echo "========================================================================"
echo "gguf-demo pipeline — one step at a time"
echo "  Each eval step: CPU first, then GPU (if available)"
echo "  Run stamp: ${TIMESTAMP}"
echo "========================================================================"

# ---------------------------------------------------------------------------
# Detect CUDA once (GPU visible)
# ---------------------------------------------------------------------------

echo ""
echo "==> Detect CUDA"
if docker compose exec -T app python -c "import torch; raise SystemExit(0 if torch.cuda.is_available() else 1)"; then
  HAS_CUDA=1
  echo "    CUDA available — eval steps will run twice (CPU → GPU)."
  docker compose exec app python scripts/check_cuda.py || true
else
  HAS_CUDA=0
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
# Step 2: Baseline — CPU, then GPU
# ---------------------------------------------------------------------------

echo ""
echo "==> Step 2: Baseline evaluation [CPU]"
run_app cpu scripts/02_baseline_evaluation.py
snapshot baseline_results cpu

if [[ "$HAS_CUDA" -eq 1 ]]; then
  echo ""
  echo "==> Step 2: Baseline evaluation [GPU]"
  run_app cuda scripts/02_baseline_evaluation.py
  snapshot baseline_results cuda
fi

# ---------------------------------------------------------------------------
# Step 3: RAG index (once)
# ---------------------------------------------------------------------------

echo ""
echo "==> Step 3: Create RAG database (once)"
run_app cuda scripts/03_create_rag_db.py

# ---------------------------------------------------------------------------
# Step 4: RAG eval — CPU, then GPU
# ---------------------------------------------------------------------------

echo ""
echo "==> Step 4: RAG evaluation [CPU]"
run_app cpu scripts/04_rag_evaluation.py
snapshot rag_results cpu

if [[ "$HAS_CUDA" -eq 1 ]]; then
  echo ""
  echo "==> Step 4: RAG evaluation [GPU]"
  run_app cuda scripts/04_rag_evaluation.py
  snapshot rag_results cuda
fi

# ---------------------------------------------------------------------------
# Step 5: Fine-tune — GPU preferred; CPU optional (SKIP_CPU_FINETUNE=1 by default)
# Phi-3 LoRA on CPU often OOMs or takes many hours; skip unless explicitly requested.
# ---------------------------------------------------------------------------

SKIP_CPU_FINETUNE="${SKIP_CPU_FINETUNE:-1}"

if [[ "$SKIP_CPU_FINETUNE" != "1" ]]; then
  echo ""
  echo "==> Step 5: Fine-tune LoRA [CPU]"
  echo "    Warning: CPU fine-tuning of Phi-3 can take a long time / use lots of RAM."
  run_app cpu scripts/05_fine_tune.py
  docker compose exec -T app bash -c '
    if [ -d models/fine_tuned/adapter ]; then
      mkdir -p models/fine_tuned/adapter_cpu
      cp -a models/fine_tuned/adapter/. models/fine_tuned/adapter_cpu/
    fi
  '
else
  echo ""
  echo "==> Step 5: Skipping CPU fine-tune (SKIP_CPU_FINETUNE=1)."
  echo "    Set SKIP_CPU_FINETUNE=0 to train LoRA on CPU as well."
fi

if [[ "$HAS_CUDA" -eq 1 ]]; then
  echo ""
  echo "==> Step 5: Fine-tune LoRA [GPU]"
  run_app cuda scripts/05_fine_tune.py
  docker compose exec -T app bash -c '
    if [ -d models/fine_tuned/adapter ]; then
      mkdir -p models/fine_tuned/adapter_cuda
      cp -a models/fine_tuned/adapter/. models/fine_tuned/adapter_cuda/
    fi
  '
elif [[ "$SKIP_CPU_FINETUNE" == "1" ]]; then
  echo ""
  echo "==> Step 5: Fine-tune LoRA [CPU fallback — no CUDA]"
  run_app cpu scripts/05_fine_tune.py
  docker compose exec -T app bash -c '
    if [ -d models/fine_tuned/adapter ]; then
      mkdir -p models/fine_tuned/adapter_cpu
      cp -a models/fine_tuned/adapter/. models/fine_tuned/adapter_cpu/
    fi
  '
fi

# ---------------------------------------------------------------------------
# Step 6: Comparison — CPU, then GPU
# ---------------------------------------------------------------------------

echo ""
echo "==> Step 6: Fine-tuned comparison [CPU]"
CPU_ADAPTER="/app/models/fine_tuned/adapter_cpu"
# Prefer CPU adapter; else reuse default adapter trained on GPU-only path
if docker compose exec -T app test -d "$CPU_ADAPTER"; then
  run_app_env cpu "FINE_TUNED_PATH=${CPU_ADAPTER}" scripts/06_fine_tuned_evaluation.py
elif docker compose exec -T app test -d /app/models/fine_tuned/adapter; then
  echo "    No adapter_cpu — evaluating default adapter under CUDA_VISIBLE_DEVICES= (CPU inference)."
  run_app cpu scripts/06_fine_tuned_evaluation.py
else
  echo "    ERROR: No fine-tuned adapter found. Skipping Step 6 CPU."
fi
snapshot comparison_report cpu

# Only export CPU results if we have baseline/rag snapshots at least
echo ""
echo "==> Step 7a: Export CPU results → results/runs/${CPU_RUN_ID}"
stage_for_export cpu
export_results "$CPU_RUN_ID"

if [[ "$HAS_CUDA" -eq 1 ]]; then
  echo ""
  echo "==> Step 6: Fine-tuned comparison [GPU]"
  CUDA_ADAPTER="/app/models/fine_tuned/adapter_cuda"
  if docker compose exec -T app test -d "$CUDA_ADAPTER"; then
    run_app_env cuda "FINE_TUNED_PATH=${CUDA_ADAPTER}" scripts/06_fine_tuned_evaluation.py
  elif docker compose exec -T app test -d /app/models/fine_tuned/adapter; then
    run_app cuda scripts/06_fine_tuned_evaluation.py
  else
    echo "    ERROR: No fine-tuned adapter found. Skipping Step 6 GPU."
  fi
  snapshot comparison_report cuda

  echo ""
  echo "==> Step 7b: Export CUDA results → results/runs/${CUDA_RUN_ID}"
  stage_for_export cuda
  export_results "$CUDA_RUN_ID"

  echo ""
  echo "==> Step 8: CPU vs CUDA summary"
  docker compose exec -T app python scripts/08_compare_devices.py \
    --cpu-run-id "$CPU_RUN_ID" \
    --cuda-run-id "$CUDA_RUN_ID" \
    --out "results/runs/${TIMESTAMP}_cpu_vs_cuda"
fi

echo ""
echo "========================================================================"
echo "DONE"
echo "========================================================================"
echo "  CPU results : results/runs/${CPU_RUN_ID}/"
if [[ "$HAS_CUDA" -eq 1 ]]; then
  echo "  CUDA results: results/runs/${CUDA_RUN_ID}/"
  echo "  Combined    : results/runs/${TIMESTAMP}_cpu_vs_cuda/"
  echo "  ★ Open first: results/latest/by_question.md"
fi
echo ""
echo "Review then commit:"
echo "  git add results/"
echo "  git commit -m \"results: CPU vs CUDA full pipeline ${TIMESTAMP}\""
echo "========================================================================"
