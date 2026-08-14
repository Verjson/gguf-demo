#!/usr/bin/env bash
# Verifies the demo sizes its thread pool from the CPU budget it is granted,
# not from the core count it can see. Needs the app image built.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE="${APP_IMAGE:-gguf-demo-app:latest}"

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "SKIP: $IMAGE not built" >&2
  exit 0
fi

budget() {
  # budget <docker run flags...>
  docker run --rm "$@" \
    -v "$ROOT_DIR/src:/app/src" -e PYTHONPATH=/app \
    "$IMAGE" python -m src.cpu_runtime
}

# Measurement picks the thread count on big machines, so switch it off wherever the
# assertion is about detection rather than about the probe.
fixed_budget() {
  budget -e CPU_CALIBRATE=0 "$@"
}

between() {
  local label="$1" low="$2" high="$3" got="$4"
  if (( got < low || got > high )); then
    echo "FAIL: $label — expected $low..$high, got $got" >&2
    exit 1
  fi
  echo "ok: $label = $got"
}

expect() {
  local label="$1" want="$2" got="$3"
  if [[ "$got" != "$want" ]]; then
    echo "FAIL: $label — expected $want, got $got" >&2
    exit 1
  fi
  echo "ok: $label = $got"
}

visible="$(docker run --rm "$IMAGE" python -c 'import os; print(os.cpu_count())')"
echo "host reports $visible logical CPUs to containers"

expect "quota of 2 CPUs" 2 "$(fixed_budget --cpus=2)"
expect "fractional quota rounds down" 2 "$(fixed_budget --cpus=2.5)"
expect "sub-core quota still gets a thread" 1 "$(fixed_budget --cpus=0.5)"
expect "quota below cpuset wins" 1 "$(fixed_budget --cpuset-cpus=0-3 --cpus=1)"
expect "APP_CPUS overrides detection" 5 "$(fixed_budget --cpus=2 -e APP_CPUS=5)"

# A cpuset may hand out hyperthread siblings. Too few cores to be worth measuring,
# so the heuristic folds them and the budget is bounded by — not equal to — the cpuset.
between "cpuset of 3 CPUs" 1 3 "$(fixed_budget --cpuset-cpus=0-2)"

# Measured budgets must still respect the grant, and must not collapse to a token
# thread or two: the probe chooses among candidates from half the ceiling upwards.
if (( visible >= 8 )); then
  measured="$(budget)"
  between "measured budget fits the machine" $((visible / 2)) "$visible" "$measured"

  quota_measured="$(budget --cpus=8)"
  between "measured budget respects an 8-CPU quota" 4 8 "$quota_measured"

  # A memory-capped container must still be able to run the probe.
  between "measured budget under a 1g memory cap" 4 8 \
    "$(budget --cpus=8 --memory=1g --memory-swap=1g)"
fi

expect "measurement can be switched off" "$(fixed_budget)" "$(fixed_budget)"

# The answer is cached per machine, so only the first run pays for the probe.
cache_dir="$(mktemp -d)"
trap 'rm -rf "$cache_dir"' EXIT
first="$(budget -v "$cache_dir:/cache" -e CPU_BUDGET_CACHE=/cache/cpu_budget.json)"
start=$SECONDS
second="$(budget -v "$cache_dir:/cache" -e CPU_BUDGET_CACHE=/cache/cpu_budget.json)"
elapsed=$((SECONDS - start))
expect "cached budget matches the measured one" "$first" "$second"
if [[ ! -s "$cache_dir/cpu_budget.json" ]]; then
  echo "FAIL: no cache file written" >&2
  exit 1
fi
echo "ok: budget cached and reused in ${elapsed}s"

echo "cpu budget tests passed"
