#!/usr/bin/env bash
# Assemble the unreleased changelog from NEXT/ fragments, newest first.
#
# NEXT/ is the sole unreleased store: one file per entry, so concurrent pull
# requests never conflict on a shared log. Nothing here is authored by hand —
# this only reads. Add an entry by writing a new NEXT/<date>-<slug>.md.
#
#   scripts/render-next.sh              # to stdout
#   scripts/render-next.sh --check      # validate metadata, write nothing
#
set -euo pipefail

cd "$(dirname "$0")/.."
NEXT_DIR="${NEXT_DIR:-NEXT}"
CHECK=0
[[ "${1:-}" == "--check" ]] && CHECK=1

if [[ ! -d "$NEXT_DIR" ]]; then
  echo "No $NEXT_DIR/ directory." >&2
  exit 1
fi

shopt -s nullglob
fragments=("$NEXT_DIR"/*.md)
shopt -u nullglob

if (( ${#fragments[@]} == 0 )); then
  (( CHECK )) && { echo "No fragments in $NEXT_DIR/ (nothing unreleased)."; exit 0; }
  echo "# Next"
  echo
  echo "_No unreleased entries._"
  exit 0
fi

# Front matter is delimited by the first two '---' lines. Read one field out of it
# without depending on a YAML parser being installed.
field() {
  awk -v key="$2" '
    NR == 1 && $0 == "---" { inside = 1; next }
    inside && $0 == "---"  { exit }
    inside {
      split($0, kv, ":")
      k = kv[1]
      gsub(/^[ \t]+|[ \t]+$/, "", k)
      if (k == key) {
        sub(/^[^:]*:[ \t]*/, "")
        gsub(/^[ \t]+|[ \t]+$/, "")
        print
        exit
      }
    }
  ' "$1"
}

body() {
  awk 'NR == 1 && $0 == "---" { inside = 1; next }
       inside && $0 == "---"  { inside = 0; started = 1; next }
       started { print }' "$1"
}

status=0
if (( CHECK )); then
  for f in "${fragments[@]}"; do
    date="$(field "$f" date)"
    title="$(field "$f" title)"
    [[ "$date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] || { echo "$f: missing or malformed 'date'" >&2; status=1; }
    [[ -n "$title" ]] || { echo "$f: missing 'title'" >&2; status=1; }
    [[ -n "$(body "$f" | tr -d '[:space:]')" ]] || { echo "$f: empty body" >&2; status=1; }
  done
  (( status == 0 )) && echo "${#fragments[@]} fragment(s) OK."
  exit "$status"
fi

echo "# Next"
echo
# Sort by the date field, newest first, falling back to the filename so the order
# is stable when several entries share a date.
for f in "${fragments[@]}"; do
  printf '%s\t%s\t%s\n' "$(field "$f" date)" "$f" "$(field "$f" title)"
done | sort -r | while IFS=$'\t' read -r date path title; do
  issue="$(field "$path" issue)"
  printf '## %s\n\n' "${title:-$(basename "$path" .md)}"
  printf '_%s' "$date"
  [[ -n "$issue" ]] && printf ' · #%s' "$issue"
  printf '_\n\n'
  body "$path"
  echo
done
