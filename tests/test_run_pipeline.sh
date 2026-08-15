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

  # Pin the published ports so this test describes device selection only, and
  # does not change behavior depending on what else the machine is listening on.
  PATH="$TEST_TMP/bin:$PATH" \
    DOCKER_CALLS="$log_file" \
    FAKE_NVIDIA_RUNTIME="$runtime" \
    FAKE_CUDA_AVAILABLE="$cuda_available" \
    FAKE_GPU_START_FAIL="$gpu_start_fail" \
    MLFLOW_PORT=5000 GRAFANA_PORT=3000 PROMETHEUS_PORT=9090 \
    POSTGRES_PORT=5432 APP_PORT=8000 \
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

# The runtimes probe must happen; it is no longer the first docker call, because
# memory sizing now asks docker how much it can actually give a container.
grep -q '^|info --format {{json .Runtimes}}$' "$GPU_LOG"
grep -q '^https://download.pytorch.org/whl/cu130|compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build$' "$GPU_LOG"
grep -q 'CUDA available — eval steps will run twice (CPU → GPU).' "$GPU_OUTPUT"

FALLBACK_LOG="$TEST_TMP/fallback.log"
FALLBACK_OUTPUT="$TEST_TMP/fallback.out"
run_pipeline 1 "$FALLBACK_LOG" "$FALLBACK_OUTPUT" 0 1

grep -q '^https://download.pytorch.org/whl/cu130|compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build$' "$FALLBACK_LOG"
grep -q '^https://download.pytorch.org/whl/cpu|compose -f docker-compose.yml up -d --build$' "$FALLBACK_LOG"
grep -q 'GPU-enabled startup failed — retrying with the CPU stack.' "$FALLBACK_OUTPUT"
grep -q 'CUDA not available — eval steps will run on CPU only.' "$FALLBACK_OUTPUT"

# The budget guard is called directly rather than through a whole pipeline run: it is
# arithmetic over a directory, and reaching it via `docker compose up` meant standing up
# a fake docker to test it. This is what extracting scripts/lib/host.sh bought.
budget_direct() {
  local when="$1" max="$2"
  ( cd "$ROOT_DIR" \
    && RESULTS_MAX_MB="$max" \
    && source scripts/lib/host.sh \
    && assert_results_budget "$when" ) 2>"$TEST_TMP/budget.err"
}

if budget_direct "unit" 0; then
  echo "assert_results_budget accepted results/ over the size budget" >&2
  exit 1
fi
grep -q 'over the 0MB budget' "$TEST_TMP/budget.err"

if ! budget_direct "unit" 100000; then
  echo "assert_results_budget rejected a results/ that is well inside its budget" >&2
  cat "$TEST_TMP/budget.err" >&2
  exit 1
fi

# Run the pipeline expecting it to abort, and to say why on stderr.
# Usage: expect_abort <label> <stderr-pattern>
expect_abort() {
  local label="$1" pattern="$2" status=0
  run_pipeline 0 "$TEST_TMP/${label}.log" "$TEST_TMP/${label}.out" \
    2>"$TEST_TMP/${label}.err" || status=$?
  if (( status == 0 )); then
    echo "Pipeline started despite: ${label}" >&2
    exit 1
  fi
  if ! grep -q "$pattern" "$TEST_TMP/${label}.err"; then
    echo "Pipeline aborted on ${label} without reporting '${pattern}':" >&2
    cat "$TEST_TMP/${label}.err" >&2
    exit 1
  fi
}

# The nesting check covers results/*/results, not just the results/latest/ case: a
# mistargeted snapshot nests under whichever folder it was pointed at.
for nested_rel in results/latest/results results/runs/results; do
  NESTED_DIR="$ROOT_DIR/$nested_rel"
  if [[ -e "$NESTED_DIR" ]]; then
    echo "${nested_rel} already exists — refusing to run the nesting test" >&2
    exit 1
  fi
  mkdir -p "$NESTED_DIR"
  trap 'rm -rf "$TEST_TMP"; rmdir "$NESTED_DIR" 2>/dev/null; rmdir "$ROOT_DIR/results/latest" 2>/dev/null; true' EXIT
  expect_abort "nested-${nested_rel//\//-}" 'results/ is nested inside itself'
  rmdir "$NESTED_DIR"
  rmdir "$ROOT_DIR/results/latest" 2>/dev/null || true
done
trap 'rm -rf "$TEST_TMP"' EXIT

# A results/ that cannot be measured must abort rather than fall through as "fine":
# failing open here would wave through exactly the runaway growth the guard exists to
# catch. Root ignores the permission bits, so the case is only meaningful unprivileged.
if (( EUID != 0 )); then
  UNREADABLE="$ROOT_DIR/results/.unreadable_probe"
  mkdir -p "$UNREADABLE"
  chmod 000 "$UNREADABLE"
  trap 'chmod 755 "$UNREADABLE" 2>/dev/null; rm -rf "$UNREADABLE"; rm -rf "$TEST_TMP"' EXIT
  expect_abort unreadable 'could not measure results/'
  chmod 755 "$UNREADABLE"
  rm -rf "$UNREADABLE"
  trap 'rm -rf "$TEST_TMP"' EXIT
else
  echo "  (skipping unreadable-results/ case: running as root)" >&2
fi

echo "pipeline device selection tests passed"
