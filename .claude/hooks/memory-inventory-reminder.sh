#!/bin/bash
# SessionStart (startup): remind to run the memory-inventory skill when this
# project's auto memory needs it. Prints nothing otherwise.
#
# Fires when either:
#   - MEMORY.md is 15KB or larger (60% of the 25KB load limit), or
#   - 30+ days have passed since the last inventory AND 15+ topic files were
#     added or updated since then. The last inventory is the mtime of
#     memory/.inventory-state.md, which memory-inventory writes in Phase 6.
# Requiring both conditions in the second rule keeps projects with little
# memory quiet.
set -u

input=$(cat 2>/dev/null) || exit 0
command -v jq >/dev/null 2>&1 || exit 0
transcript=$(printf '%s' "$input" | jq -r '.transcript_path // empty' 2>/dev/null) || exit 0
[ -n "$transcript" ] || exit 0

mem_dir="$(dirname "$transcript")/memory"
index="$mem_dir/MEMORY.md"
[ -f "$index" ] || exit 0

size_limit=15000
days_limit=30
changes_limit=15

size=$(wc -c < "$index" | tr -d ' ')
reason=""
if [ "$size" -ge "$size_limit" ]; then
  reason="MEMORY.md が ${size} bytes で、目安の ${size_limit} bytes を超えています"
else
  state="$mem_dir/.inventory-state.md"
  if [ -f "$state" ]; then
    age_days=$(( ( $(date +%s) - $(stat -f %m "$state") ) / 86400 ))
    changed=$(find "$mem_dir" -maxdepth 1 -name '*.md' ! -name MEMORY.md -newer "$state" | wc -l | tr -d ' ')
    if [ "$age_days" -ge "$days_limit" ] && [ "$changed" -ge "$changes_limit" ]; then
      reason="前回の棚卸しから ${age_days} 日たち、その後に ${changed} 件が新規・更新されています"
    fi
  else
    changed=$(find "$mem_dir" -maxdepth 1 -name '*.md' ! -name MEMORY.md | wc -l | tr -d ' ')
    if [ "$changed" -ge "$changes_limit" ]; then
      reason="棚卸しの記録（.inventory-state.md）が無く、トピックファイルが ${changed} 件あります"
    fi
  fi
fi

[ -n "$reason" ] || exit 0
echo "auto memory の棚卸しの時期です（${reason}）。ユーザーへの最初の応答で一度だけ、memory-inventory スキルの実行を提案してください。"
