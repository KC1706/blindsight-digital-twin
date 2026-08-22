#!/usr/bin/env bash
# Centralized progress dashboard: done vs remaining, per person/role.
# Usage: bash scripts/progress.sh
set -euo pipefail
REPO="${REPO:-KC1706/blindsight-digital-twin}"

count() { gh issue list --repo "$REPO" -L 300 --state "$1" ${2:+--label "$2"} --json number --jq 'length'; }
bar() { # done total
  local d=$1 t=$2 w=24 f; [ "$t" -eq 0 ] && { printf "[%*s] 0%%" "$w" ""; return; }
  f=$(( d * w / t )); printf "["; printf "%0.s#" $(seq 1 $f 2>/dev/null); printf "%0.s-" $(seq 1 $((w-f)) 2>/dev/null); printf "] %d%%" $(( d*100/t )); }

row() { # label name
  local all open done; all=$(count all "$1"); open=$(count open "$1"); done=$((all-open))
  printf "%-16s done %2d / %-2d  remaining %-2d  " "$2" "$done" "$all" "$open"; bar "$done" "$all"; echo
}

echo "=== Blindsight — progress ($(date '+%Y-%m-%d %H:%M')) ==="
row "role:dev"  "Kunal · Dev"
row "role:ba"   "Rahul · BA"
row "role:deck" "Deep · Deck"
echo "-------------------------------------------------------------------"
row ""          "TOTAL"
echo
echo "Critical path (p0) still open:"
gh issue list --repo "$REPO" -L 50 --state open --label "priority:p0-critical" \
  --json number,title,labels \
  --jq '.[] | "  #\(.number) [\(.labels[].name | select(startswith("role:")))]  \(.title)"' 2>/dev/null || true
