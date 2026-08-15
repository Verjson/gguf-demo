#!/usr/bin/env bash
# Verifies the demo sizes its thread pool from the CPU budget it is granted,
# not from the core count it can see. Needs the app image built.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE="${APP_IMAGE:-gguf-demo-app:latest}"

# A missing image is a reasonable skip on a laptop and an unacceptable one in CI.
# This suite is the only test that runs anything inside the app image, so while it
# skipped itself the image sat unbuildable for weeks with the suite reporting green.
# Under CI the absence of the image is the failure.
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  if [[ "${CI:-}" == "true" ]]; then
    echo "FAIL: $IMAGE is not built — CI must build it before running this suite" >&2
    exit 1
  fi
  echo "SKIP: $IMAGE not built (set CI=true to make this a failure)" >&2
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
#
# Only when there is a probe to pay for. cpu_budget() calibrates when the ceiling
# reaches MIN_CORES_TO_CALIBRATE (8) and takes the heuristic below that, and only
# calibration writes the cache — so on a smaller machine "no cache file" is the
# documented behaviour, not a failure. This assertion sat outside the `visible >= 8`
# guard that the measurement assertions above already use, so it passed on a
# 32-thread laptop and failed on a 4-core CI runner: a test that only held on the
# machine it was written on.
cache_dir="$(mktemp -d)"
trap 'rm -rf "$cache_dir"' EXIT
first="$(budget -v "$cache_dir:/cache" -e CPU_BUDGET_CACHE=/cache/cpu_budget.json)"
start=$SECONDS
second="$(budget -v "$cache_dir:/cache" -e CPU_BUDGET_CACHE=/cache/cpu_budget.json)"
elapsed=$((SECONDS - start))
expect "budget is stable across runs" "$first" "$second"

if (( visible >= 8 )); then
  if [[ ! -s "$cache_dir/cpu_budget.json" ]]; then
    echo "FAIL: no cache file written on a machine large enough to calibrate" >&2
    exit 1
  fi
  echo "ok: budget cached and reused in ${elapsed}s"
else
  # Assert the other half of the contract rather than skipping silently: below the
  # threshold nothing is measured, so nothing should be cached either.
  if [[ -s "$cache_dir/cpu_budget.json" ]]; then
    echo "FAIL: cache written on a ${visible}-CPU machine, which should not calibrate" >&2
    exit 1
  fi
  echo "ok: ${visible} CPUs is below the calibration threshold — heuristic used, nothing cached"
fi

echo "cpu budget tests passed"
