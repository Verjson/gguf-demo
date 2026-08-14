#!/usr/bin/env bash
# Host safety watchdog for a long pipeline run.
#
# The app container is bounded by mem_limit/memswap_limit, so it can only kill
# itself. What that does not bound is the *aggregate*: the app plus Postgres,
# MLflow, Prometheus, Grafana, a docker build, and whatever else the machine is
# doing. Under WSL2 that aggregate is what drives the VM into swap and makes the
# whole desktop unresponsive — the failure this watches for.
#
# Thresholds are percentages of whatever memory is actually available to the
# containers, so the same numbers hold on a laptop, a CI runner, or a slice of a
# shared box. On Linux that comes from /proc/meminfo, with a cgroup limit
# preferred when the watchdog itself runs inside a container. On macOS and
# Windows there is no /proc, and the host's RAM would be the wrong number anyway:
# containers live in a fixed-size Docker Desktop VM, so it falls back to Docker's
# own accounting, which measures the budget they are actually killed for
# exceeding.
#
# stdout is an event stream — one line per state change plus a heartbeat — so it
# can be tailed or piped into a monitor. Every sample goes to --log regardless.
#
#   scripts/host_guard.sh --interval 15 --action stop
#
set -uo pipefail

INTERVAL=15
WARN_PCT=20          # MemAvailable below this share of MemTotal: warn
CRITICAL_PCT=8       # ...and below this: act
SWAP_WARN_PCT=50     # Swap this full means reclaim is already failing
SWAP_CRITICAL_PCT=80
HEARTBEAT_EVERY=20   # Samples between "still healthy" lines
ACTION=stop          # stop | report
GUARD_TARGET="${GUARD_TARGET:-rag-app}"   # container stopped first when critical
LOG="${GUARD_LOG:-}"

usage() {
  sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

# Every threshold below reaches an awk program body. Rejecting anything that is not
# a plain integer at parse time — before it can be interpolated — is what keeps
# `--warn-pct '1); system("rm -rf /"); ('` an argument error rather than an awk
# program. The values are passed with `awk -v` further down for the same reason.
require_integer() {
  local flag="$1" value="$2"
  if [[ ! "$value" =~ ^[0-9]+$ ]]; then
    echo "ERROR: ${flag} must be a non-negative integer, got: ${value}" >&2
    exit 2
  fi
}

while (( $# )); do
  case "$1" in
    --interval) require_integer "$1" "${2:-}"; INTERVAL="$2"; shift 2 ;;
    --warn-pct) require_integer "$1" "${2:-}"; WARN_PCT="$2"; shift 2 ;;
    --critical-pct) require_integer "$1" "${2:-}"; CRITICAL_PCT="$2"; shift 2 ;;
    --swap-warn-pct) require_integer "$1" "${2:-}"; SWAP_WARN_PCT="$2"; shift 2 ;;
    --swap-critical-pct) require_integer "$1" "${2:-}"; SWAP_CRITICAL_PCT="$2"; shift 2 ;;
    --heartbeat-every) require_integer "$1" "${2:-}"; HEARTBEAT_EVERY="$2"; shift 2 ;;
    --action) ACTION="${2:-}"; shift 2 ;;
    --target) GUARD_TARGET="${2:-}"; shift 2 ;;
    --log) LOG="${2:-}"; shift 2 ;;
    -h|--help) usage 0 ;;
    *) echo "unknown option: $1" >&2; usage 2 ;;
  esac
done

case "$ACTION" in
  stop|report) ;;
  *) echo "ERROR: --action must be stop or report" >&2; exit 2 ;;
esac

# Defaults are integers too, so an env-set default cannot smuggle a value past the
# per-flag checks above.
require_integer --interval "$INTERVAL"
require_integer --warn-pct "$WARN_PCT"
require_integer --critical-pct "$CRITICAL_PCT"
require_integer --swap-warn-pct "$SWAP_WARN_PCT"
require_integer --swap-critical-pct "$SWAP_CRITICAL_PCT"
require_integer --heartbeat-every "$HEARTBEAT_EVERY"

# `samples % HEARTBEAT_EVERY` divides by this, and `sleep 0` would spin the sampler.
if (( HEARTBEAT_EVERY < 1 )); then
  echo "ERROR: --heartbeat-every must be at least 1" >&2
  exit 2
fi
if (( INTERVAL < 1 )); then
  echo "ERROR: --interval must be at least 1 second" >&2
  exit 2
fi

# The watchdog appends to --log for the life of a run, so a path outside the repo or
# the temp dir is either a mistake or an attempt to make this script the writer.
if [[ -n "$LOG" ]]; then
  GUARD_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
  log_parent="$(cd "$(dirname "$LOG")" 2>/dev/null && pwd -P)" || {
    echo "ERROR: --log directory does not exist: $(dirname "$LOG")" >&2
    exit 2
  }
  log_ok=0
  for allowed in "$GUARD_REPO_ROOT" "${TMPDIR:-/tmp}" /tmp /var/tmp; do
    allowed="$(cd "$allowed" 2>/dev/null && pwd -P)" || continue
    [[ "$log_parent" == "$allowed" || "$log_parent" == "$allowed"/* ]] && { log_ok=1; break; }
  done
  if (( ! log_ok )); then
    echo "ERROR: --log must resolve under ${GUARD_REPO_ROOT} or a temp dir, got: ${log_parent}" >&2
    exit 2
  fi
fi

stamp() { date -u +%H:%M:%SZ; }

emit() { printf '%s %s\n' "$(stamp)" "$*"; }

record() { [[ -n "$LOG" ]] && printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >>"$LOG"; }

# Where the memory numbers come from. On Linux /proc/meminfo describes the machine
# the containers actually run on. On macOS and Windows it does not exist, and the
# host's RAM is the wrong number anyway: containers live in a fixed-size Docker
# Desktop VM, so that VM is what fills up and kills them. Falling back to Docker's
# own accounting measures the thing that fails on those platforms.
# GUARD_MEM_SOURCE forces one path, which is how the docker path gets exercised
# on a Linux box that has /proc.
SOURCE="${GUARD_MEM_SOURCE:-}"
if [[ -z "$SOURCE" ]]; then
  SOURCE=proc
  [[ -r /proc/meminfo ]] || SOURCE=docker
fi

# Memory this machine (or this cgroup, or the Docker VM) actually has, in KiB. A
# cgroup limit wins when it is smaller, so the watchdog measures its own budget
# when containerized — the same rule available_memory_bytes() uses.
mem_total_kb() {
  local physical="" cg value
  if [[ "$SOURCE" == proc ]]; then
    physical="$(awk '/^MemTotal:/ {print $2; exit}' /proc/meminfo)"
  else
    value="$(docker info --format '{{.MemTotal}}' 2>/dev/null || true)"
    [[ "$value" =~ ^[0-9]+$ ]] && physical=$(( value / 1024 ))
  fi
  [[ "$physical" =~ ^[0-9]+$ ]] || return 1
  for cg in /sys/fs/cgroup/memory.max /sys/fs/cgroup/memory/memory.limit_in_bytes; do
    [[ -r "$cg" ]] || continue
    value="$(cat "$cg" 2>/dev/null)"
    [[ "$value" =~ ^[0-9]+$ ]] || continue
    value=$(( value / 1024 ))
    (( value > 0 && value < physical )) && physical="$value"
    break
  done
  echo "$physical"
}

TOTAL_KB="$(mem_total_kb || true)"
[[ "$TOTAL_KB" =~ ^[0-9]+$ ]] && (( TOTAL_KB > 0 )) || {
  echo "ERROR: could not determine total memory from /proc/meminfo or docker info" >&2
  exit 1
}

# Without /proc, the containers' own usage against the Docker VM's size is the
# closest honest answer: it is the budget they are killed for exceeding. Swap
# inside the VM is not observable from here, so it is reported as zero rather
# than guessed at.
sample_docker() {
  local used_kb
  used_kb="$(timeout 20 docker stats --no-stream --format '{{.MemUsage}}' 2>/dev/null |
    awk -F' / ' '{
      v = $1
      unit = v; sub(/^[0-9.]+/, "", unit)
      sub(/[A-Za-z]+$/, "", v)
      f = (unit ~ /^GiB/) ? 1048576 : (unit ~ /^MiB/) ? 1024 : (unit ~ /^KiB/) ? 1 : \
          (unit ~ /^GB/)  ? 1000000 : (unit ~ /^MB/)  ? 1000 : (unit ~ /^kB/) ? 1 : 0
      total += v * f
    } END { printf "%d", total }')"
  [[ "$used_kb" =~ ^[0-9]+$ ]] || used_kb=0
  local avail_kb=$(( TOTAL_KB - used_kb ))
  (( avail_kb < 0 )) && avail_kb=0
  awk -v avail="$avail_kb" -v total="$TOTAL_KB" \
    'BEGIN { printf "%d %d %.1f %.1f %.1f\n", avail, 0, avail * 100 / total, 0, (total - avail) / 1048576 }'
}

# MemAvailable is the kernel's own estimate of what a new allocation can get
# without swapping, so reclaimable page cache is already discounted. Older
# kernels omit it; MemFree alone is the pessimistic fallback.
sample_proc() {
  awk -v total="$TOTAL_KB" '
    /^MemAvailable:/ { avail = $2 }
    /^MemFree:/      { free  = $2 }
    /^SwapTotal:/    { st    = $2 }
    /^SwapFree:/     { sf    = $2 }
    END {
      if (avail == "") avail = free
      if (avail > total) avail = total
      swap_used_pct = (st > 0) ? (st - sf) * 100 / st : 0
      printf "%d %d %.1f %.1f %.1f\n", \
        avail, st - sf, avail * 100 / total, swap_used_pct, (total - avail) / 1048576
    }
  ' /proc/meminfo
}

sample() {
  if [[ "$SOURCE" == proc ]]; then sample_proc; else sample_docker; fi
}

container_line() {
  command -v docker >/dev/null 2>&1 || return 0
  timeout 20 docker stats --no-stream --format '{{.Name}}:{{.CPUPerc}}/{{.MemUsage}}' 2>/dev/null |
    tr '\n' ' '
}

# A container the kernel OOM-killed is the signal that a limit was hit. Reporting
# it is the point: without it, a killed eval step looks like an ordinary failure.
oom_report() {
  command -v docker >/dev/null 2>&1 || return 0
  local name killed
  for name in $(docker ps -a --filter "label=com.docker.compose.project" --format '{{.Names}}' 2>/dev/null); do
    killed="$(docker inspect -f '{{.State.OOMKilled}}' "$name" 2>/dev/null)"
    [[ "$killed" == "true" ]] && echo "$name"
  done
}

state=ok
samples=0
reported_ooms=""
emit "GUARD start total=$(( TOTAL_KB / 1024 ))MiB source=${SOURCE} warn<${WARN_PCT}% critical<${CRITICAL_PCT}% action=${ACTION} target=${GUARD_TARGET}"

while true; do
  read -r avail_kb swap_used_kb avail_pct swap_pct used_gib < <(sample)
  samples=$(( samples + 1 ))
  record "avail_pct=${avail_pct} avail_mib=$(( avail_kb / 1024 )) swap_used_mib=$(( swap_used_kb / 1024 )) swap_pct=${swap_pct} used_gib=${used_gib} $(container_line)"

  for name in $(oom_report); do
    case " $reported_ooms " in
      *" $name "*) ;;
      *) reported_ooms="$reported_ooms $name"
         emit "OOM-KILLED ${name} — it exceeded its container memory limit (the limit did its job; the run step failed)" ;;
    esac
  done

  # Values arrive as awk variables, never as program text: the comparison is fixed
  # code, so no argument can extend it.
  critical=0
  awk -v avail="$avail_pct" -v swap="$swap_pct" -v acrit="$CRITICAL_PCT" -v scrit="$SWAP_CRITICAL_PCT" \
    'BEGIN { exit !(avail < acrit || swap > scrit) }' && critical=1
  warn=0
  awk -v avail="$avail_pct" -v swap="$swap_pct" -v awarn="$WARN_PCT" -v swarn="$SWAP_WARN_PCT" \
    'BEGIN { exit !(avail < awarn || swap > swarn) }' && warn=1

  if (( critical )); then
    if [[ "$state" != critical ]]; then
      state=critical
      emit "CRITICAL avail=${avail_pct}% swap=${swap_pct}% — the machine is about to thrash"
      if [[ "$ACTION" == stop ]] && command -v docker >/dev/null 2>&1; then
        emit "CRITICAL stopping ${GUARD_TARGET} to release memory before the OOM killer picks a victim"
        timeout 60 docker stop "$GUARD_TARGET" >/dev/null 2>&1 &&
          emit "CRITICAL stopped ${GUARD_TARGET}; the pipeline will fail its current step" ||
          emit "CRITICAL could not stop ${GUARD_TARGET} — intervene by hand"
      fi
    fi
  elif (( warn )); then
    [[ "$state" != warn ]] && { state=warn; emit "WARN avail=${avail_pct}% swap=${swap_pct}% used=${used_gib}GiB — headroom shrinking"; }
  else
    [[ "$state" != ok ]] && { state=ok; emit "RECOVERED avail=${avail_pct}% swap=${swap_pct}%"; }
  fi

  if (( samples % HEARTBEAT_EVERY == 0 )); then
    emit "HEARTBEAT avail=${avail_pct}% swap=${swap_pct}% used=${used_gib}GiB ${state}"
  fi

  sleep "$INTERVAL"
done
