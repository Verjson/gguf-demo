#!/usr/bin/env bash
# Verifies the pipeline sizes memory and picks ports from what the *container
# runtime* offers, not from whatever the machine running the script happens to
# have. Both of these were reported from a Mac, where the two differ.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEST_TMP="$(mktemp -d)"
trap 'rm -rf "$TEST_TMP"; [[ -n "${LISTENER_PID:-}" ]] && kill "$LISTENER_PID" 2>/dev/null' EXIT

PASS=0
check() { # check <label> <expected> <actual>
  if [[ "$2" == "$3" ]]; then
    echo "ok: $1 = $3"
    PASS=$(( PASS + 1 ))
  else
    echo "FAIL: $1 — expected '$2', got '$3'" >&2
    exit 1
  fi
}

# Load the helpers under test.
#
# This used to sed the function bodies out of run_pipeline.sh, because sourcing
# that script would have started a stack. Extracting them into lib/host.sh —
# which has no side effects at all — is what made that hack unnecessary, and the
# hack outlived the refactor: the sed kept matching nothing, `eval ""` defined
# nothing, and every assertion below failed with "command not found" for weeks.
# A silent no-op is the worst thing a test helper can be, so this sources the
# file and then proves the functions are actually there.
helpers() {
  cat "$ROOT_DIR/scripts/lib/host.sh"
}

require_defined() {
  local missing=0 fn
  for fn in "$@"; do
    if ! declare -F "$fn" >/dev/null; then
      echo "FAIL: $fn is not defined after sourcing scripts/lib/host.sh" >&2
      missing=1
    fi
  done
  (( missing )) && exit 1
  return 0
}

mkdir -p "$TEST_TMP/bin"
make_fake_docker() { # make_fake_docker <memtotal-bytes> <names-publishing-any-port>
  cat > "$TEST_TMP/bin/docker" <<EOF
#!/usr/bin/env bash
if [[ "\$1" == "info" ]]; then printf '%s\n' "$1"; exit 0; fi
if [[ "\$1" == "ps" ]]; then printf '%s\n' "$2"; exit 0; fi
exit 0
EOF
  chmod +x "$TEST_TMP/bin/docker"
}

# --- memory is read from Docker, which is the VM's size on macOS/Windows -------
make_fake_docker 8589934592 ""   # 8GiB Docker Desktop VM
export PATH="$TEST_TMP/bin:$PATH"
eval "$(helpers)"
require_defined available_memory_bytes first_free_port port_held_by_this_stack \
                port_in_use resolve_published_ports assert_results_budget
check "docker VM memory wins over the host's" 8589934592 "$(available_memory_bytes)"

# A Docker that cannot answer must not zero the budget: the host reading is the
# fallback, and returning 0 would make default_mem_limit_gb pick its 10g default.
cat > "$TEST_TMP/bin/docker" <<'EOF'
#!/usr/bin/env bash
exit 1
EOF
chmod +x "$TEST_TMP/bin/docker"
fallback="$(available_memory_bytes)"
if [[ -r /proc/meminfo ]]; then
  expected=$(( $(awk '/^MemTotal:/ {print $2; exit}' /proc/meminfo) * 1024 ))
  check "falls back to the host when docker is unavailable" "$expected" "$fallback"
else
  [[ "$fallback" -gt 0 ]] && { echo "ok: fallback returned $fallback"; PASS=$(( PASS + 1 )); }
fi

# --- ports --------------------------------------------------------------------
make_fake_docker 8589934592 ""   # nothing published by this stack
eval "$(helpers)"

# Pick a base port that is genuinely free right now, so the assertions below
# describe the helper rather than whatever else this machine happens to run.
BASE=""
for candidate in $(seq 5300 5380); do
  if ! port_in_use "$candidate" && ! port_in_use $(( candidate + 1 )); then
    BASE="$candidate"
    break
  fi
done
[[ -n "$BASE" ]] || { echo "FAIL: no free port pair in 5300-5380 to test with" >&2; exit 1; }

# A port nothing is listening on is used as-is.
check "a free port is kept" "$BASE" "$(first_free_port "$BASE")"

# A foreign listener pushes the choice to the next port. This is the macOS
# AirPlay-on-5000 case that stopped MLflow from starting.
python3 -m http.server "$BASE" --bind 127.0.0.1 >/dev/null 2>&1 &
LISTENER_PID=$!
for _ in $(seq 1 30); do
  port_in_use "$BASE" && break
  sleep 0.2
done
check "a foreign listener is stepped over" "$(( BASE + 1 ))" "$(first_free_port "$BASE")"

# ...but a port published by this stack's own container is not a conflict.
# Without this, each re-run walks one port further and recreates the container.
make_fake_docker 8589934592 "rag-mlflow"
eval "$(helpers)"
check "this stack's own port is reused" "$BASE" "$(first_free_port "$BASE")"

# A container that is not ours on the same port still counts as a conflict.
make_fake_docker 8589934592 "someone-elses-app"
eval "$(helpers)"
check "another project's container is stepped over" "$(( BASE + 1 ))" "$(first_free_port "$BASE")"

echo "host portability tests passed ($PASS assertions)"
