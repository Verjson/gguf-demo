#!/usr/bin/env bash
# Host-facing helpers for the pipeline: what memory this machine can actually give a
# container, which ports it has free, and whether results/ has outgrown its budget.
#
# Sourced by scripts/run_pipeline.sh, and directly by tests/test_host_portability.sh and
# tests/test_run_pipeline.sh — which is the point of the split. Reaching these through a
# full pipeline invocation meant standing up a fake docker just to test arithmetic.
#
#   source "$(dirname "$0")/lib/host.sh"
#
# Callers provide: COMPOSE (array), and cwd at the repo root for assert_results_budget.

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
