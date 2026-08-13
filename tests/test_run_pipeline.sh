#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEST_TMP="$(mktemp -d)"
trap 'rm -rf "$TEST_TMP"' EXIT

mkdir -p "$TEST_TMP/bin"
FAKE_DOCKER="$TEST_TMP/bin/docker"

cat > "$FAKE_DOCKER" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

printf '%s|%s\n' "${TORCH_INDEX_URL:-}" "$*" >> "$DOCKER_CALLS"

if [[ "${1:-}" == "info" ]]; then
  if [[ "${FAKE_NVIDIA_RUNTIME:-0}" == "1" ]]; then
    printf '%s\n' '{"io.containerd.runc.v2":{},"nvidia":{}}'
  else
    printf '%s\n' '{"io.containerd.runc.v2":{}}'
  fi
  exit 0
fi

if [[ "${FAKE_GPU_START_FAIL:-0}" == "1" && "$*" == *"docker-compose.gpu.yml"* && "$*" == *" up "* ]]; then
  exit 1
fi

if [[ "$*" == *"torch.cuda.is_available"* ]]; then
  [[ "${FAKE_CUDA_AVAILABLE:-$FAKE_NVIDIA_RUNTIME}" == "1" ]]
fi
EOF
chmod +x "$FAKE_DOCKER"

cat > "$TEST_TMP/bin/nvidia-smi" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

if [[ "${FAKE_NVIDIA_RUNTIME:-0}" == "1" && "${1:-}" == "-L" ]]; then
  echo 'GPU 0: Fake NVIDIA GPU'
  exit 0
fi
exit 1
EOF
chmod +x "$TEST_TMP/bin/nvidia-smi"

run_pipeline() {
  local runtime="$1"
  local log_file="$2"
  local output_file="$3"
  local cuda_available="${4:-$runtime}"
  local gpu_start_fail="${5:-0}"

  PATH="$TEST_TMP/bin:$PATH" \
    DOCKER_CALLS="$log_file" \
    FAKE_NVIDIA_RUNTIME="$runtime" \
    FAKE_CUDA_AVAILABLE="$cuda_available" \
    FAKE_GPU_START_FAIL="$gpu_start_fail" \
    "$ROOT_DIR/scripts/run_pipeline.sh" > "$output_file"
}

CPU_LOG="$TEST_TMP/cpu.log"
CPU_OUTPUT="$TEST_TMP/cpu.out"
run_pipeline 0 "$CPU_LOG" "$CPU_OUTPUT"

grep -q '^https://download.pytorch.org/whl/cpu|compose -f docker-compose.yml up -d --build$' "$CPU_LOG"
if grep -q 'docker-compose.gpu.yml' "$CPU_LOG"; then
  echo "CPU run unexpectedly used the GPU Compose overlay" >&2
  exit 1
fi
grep -q 'CUDA not available — eval steps will run on CPU only.' "$CPU_OUTPUT"
if grep -q 'scripts/05_fine_tune.py' "$CPU_LOG"; then
  echo "CPU run ignored SKIP_CPU_FINETUNE=1" >&2
  exit 1
fi

GPU_LOG="$TEST_TMP/gpu.log"
GPU_OUTPUT="$TEST_TMP/gpu.out"
run_pipeline 1 "$GPU_LOG" "$GPU_OUTPUT"

head -n 1 "$GPU_LOG" | grep -q '^|info --format {{json .Runtimes}}$'
grep -q '^https://download.pytorch.org/whl/cu130|compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build$' "$GPU_LOG"
grep -q 'CUDA available — eval steps will run twice (CPU → GPU).' "$GPU_OUTPUT"

FALLBACK_LOG="$TEST_TMP/fallback.log"
FALLBACK_OUTPUT="$TEST_TMP/fallback.out"
run_pipeline 1 "$FALLBACK_LOG" "$FALLBACK_OUTPUT" 0 1

grep -q '^https://download.pytorch.org/whl/cu130|compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build$' "$FALLBACK_LOG"
grep -q '^https://download.pytorch.org/whl/cpu|compose -f docker-compose.yml up -d --build$' "$FALLBACK_LOG"
grep -q 'GPU-enabled startup failed — retrying with the CPU stack.' "$FALLBACK_OUTPUT"
grep -q 'CUDA not available — eval steps will run on CPU only.' "$FALLBACK_OUTPUT"

echo "pipeline device selection tests passed"
