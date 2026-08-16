#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEST_TMP="$(mktemp -d)"
trap 'rm -rf "$TEST_TMP"' EXIT

mkdir -p "$TEST_TMP/bin"
cat > "$TEST_TMP/bin/docker" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

printf '%s\n' "$*" >> "$DOCKER_CALLS"
case "$*" in
  *"SELECT 1"*) printf '1\n' ;;
  *"pg_database_collation_actual_version"*) printf '%s\n' "${FAKE_COLLATION_MISMATCH:-f}" ;;
  *"quote_ident(current_database())"*) printf 'rag_eval\n' ;;
  *"to_regclass"*) printf '\n' ;;
esac
EOF
chmod +x "$TEST_TMP/bin/docker"

run_migration() {
  local mismatch="$1" log_file="$2" output_file="$3"
  PATH="$TEST_TMP/bin:$PATH" DOCKER_CALLS="$log_file" \
    FAKE_COLLATION_MISMATCH="$mismatch" \
    "$ROOT_DIR/scripts/migrate_db.sh" >"$output_file"
}

MISMATCH_LOG="$TEST_TMP/mismatch.log"
MISMATCH_OUTPUT="$TEST_TMP/mismatch.out"
run_migration t "$MISMATCH_LOG" "$MISMATCH_OUTPUT"
grep -q 'REINDEX DATABASE rag_eval' "$MISMATCH_LOG"
grep -q 'ALTER DATABASE rag_eval REFRESH COLLATION VERSION' "$MISMATCH_LOG"
grep -q 'collation version refreshed' "$MISMATCH_OUTPUT"

CURRENT_LOG="$TEST_TMP/current.log"
run_migration f "$CURRENT_LOG" "$TEST_TMP/current.out"
if grep -qE 'REINDEX DATABASE|REFRESH COLLATION VERSION' "$CURRENT_LOG"; then
  echo "current collation was rebuilt unnecessarily" >&2
  exit 1
fi

CHECK_LOG="$TEST_TMP/check.log"
status=0
PATH="$TEST_TMP/bin:$PATH" DOCKER_CALLS="$CHECK_LOG" FAKE_COLLATION_MISMATCH=t \
  "$ROOT_DIR/scripts/migrate_db.sh" --check >"$TEST_TMP/check.out" \
  2>"$TEST_TMP/check.err" || status=$?
if (( status == 0 )); then
  echo "collation check accepted stale metadata" >&2
  exit 1
fi
grep -q 'database collation version is stale' "$TEST_TMP/check.err"
if grep -qE 'REINDEX DATABASE|REFRESH COLLATION VERSION' "$CHECK_LOG"; then
  echo "collation check mutated the database" >&2
  exit 1
fi
