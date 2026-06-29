#!/bin/bash
# PreToolUse(Bash) hook: enforce `mise exec --` for mise-managed runtimes.
#
# Blocks bare `bundle|rails|rspec|ruby|pnpm|node|npm` invocations so they
# always run under mise's environment. Compound commands are split on
# `;`, `&&`, `||`, `|` and inspected per-segment. Leading `FOO=bar`
# env-var assignments are skipped before reading the first token.
#
# Exit 0 + JSON `permissionDecision: deny` blocks the call and feeds the
# reason back to Claude so it can retry with the correct prefix.

set -euo pipefail

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty')

[ -z "$cmd" ] && exit 0

PATTERN='^(bundle|rails|rspec|ruby|pnpm|node|npm)$'

segments=$(printf '%s' "$cmd" | sed -E 's/(\|\||&&|;|\|)/\n/g')

violation=""
viol_seg=""

while IFS= read -r seg; do
  seg_trim=$(printf '%s' "$seg" | sed -E 's/^[[:space:]]+//;s/[[:space:]]+$//')
  [ -z "$seg_trim" ] && continue

  while printf '%s' "$seg_trim" | grep -qE '^[A-Za-z_][A-Za-z0-9_]*='; do
    seg_trim=$(printf '%s' "$seg_trim" | sed -E 's/^[A-Za-z_][A-Za-z0-9_]*=[^[:space:]]*[[:space:]]+//')
  done

  first=$(printf '%s' "$seg_trim" | awk '{print $1}')

  if [ "$first" = "mise" ]; then
    second=$(printf '%s' "$seg_trim" | awk '{print $2}')
    case "$second" in
      exec|x) continue ;;
    esac
  fi

  if printf '%s' "$first" | grep -qE "$PATTERN"; then
    violation="$first"
    viol_seg="$seg_trim"
    break
  fi
done <<EOF
$segments
EOF

if [ -n "$violation" ]; then
  reason="\`$violation\` must run via \`mise exec --\` (segment: \"$viol_seg\"). Replace with: \`mise exec -- $viol_seg\`. Chain each subcommand separately when using && / ||. See ~/.claude/CLAUDE.md §Shell Commands."
  reason_json=$(printf '%s' "$reason" | jq -Rs .)
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":%s}}\n' "$reason_json"
  exit 0
fi

exit 0
