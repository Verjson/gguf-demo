#!/usr/bin/env bash
# Argument handling for the host watchdog.
#
# The thresholds reach an awk program, so anything that is not a plain integer has to
# be rejected at parse time rather than interpolated. These cases are the reason the
# script validates before it samples.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
GUARD="$ROOT_DIR/scripts/host_guard.sh"
TEST_TMP="$(mktemp -d)"
trap 'rm -rf "$TEST_TMP"' EXIT

# Usage: expect_rejected <label> <stderr-pattern> [args...]
expect_rejected() {
  local label="$1" pattern="$2"; shift 2
  local status=0
  "$GUARD" "$@" >"$TEST_TMP/out" 2>"$TEST_TMP/err" || status=$?
  if (( status != 2 )); then
    echo "FAIL: ${label} exited ${status}, expected 2" >&2
    cat "$TEST_TMP/err" >&2
    exit 1
  fi
  if ! grep -q "$pattern" "$TEST_TMP/err"; then
    echo "FAIL: ${label} did not report '${pattern}'" >&2
    cat "$TEST_TMP/err" >&2
    exit 1
  fi
}

# Balanced on purpose: this payload is valid awk in the threshold's position, so
# before validation it ran `touch` on the first sample. An unbalanced payload would
# only crash awk and would not prove anything.
for flag in --warn-pct --critical-pct --swap-warn-pct --swap-critical-pct; do
  CANARY="$TEST_TMP/canary${flag}"
  expect_rejected "awk injection via ${flag}" "must be a non-negative integer" \
    "$flag" "0 || system(\"touch ${CANARY}\") || 0" --action report
  if [[ -e "$CANARY" ]]; then
    echo "FAIL: injected awk statement executed via ${flag}" >&2
    exit 1
  fi
done
expect_rejected "non-numeric --interval" "must be a non-negative integer" --interval abc
expect_rejected "negative --swap-warn-pct" "must be a non-negative integer" --swap-warn-pct -5
expect_rejected "float --heartbeat-every" "must be a non-negative integer" --heartbeat-every 1.5
# samples % HEARTBEAT_EVERY would divide by zero, and sleep 0 would spin the sampler.
expect_rejected "zero --heartbeat-every" "at least 1" --heartbeat-every 0
expect_rejected "zero --interval" "at least 1 second" --interval 0
expect_rejected "--log outside the repo or a temp dir" "must resolve under" --log /etc/host_guard.log
expect_rejected "invalid --action" "must be stop or report" --action delete

# A valid invocation still samples, emits, and writes its log.
LOG="$TEST_TMP/guard.log"
GUARD_MEM_SOURCE=proc timeout 3 "$GUARD" \
  --interval 1 --heartbeat-every 1 --action report --log "$LOG" >"$TEST_TMP/valid.out" 2>&1 || true
grep -q '^[0-9:]*Z GUARD start ' "$TEST_TMP/valid.out"
grep -q 'HEARTBEAT avail=' "$TEST_TMP/valid.out"
[[ -s "$LOG" ]]

echo "host guard argument tests passed"
