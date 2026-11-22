#!/bin/bash
# Build generated agent instruction files from single-source-of-truth files:
#   - .codex/AGENTS.md         (AGENTS.md + emma.md body)
#   - .gemini/config/GEMINI.md (emma.md body for Antigravity)
#
# Usage:
#   .codex/build-agents.sh          # (re)generate; no-op when already current
#   .codex/build-agents.sh --check  # exit 1 if any generated file has drifted
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "$0")/.." && pwd)"
shared="$DOTFILES_DIR/AGENTS.md"
persona="$DOTFILES_DIR/.claude/output-styles/emma.md"
codex_target="$DOTFILES_DIR/.codex/AGENTS.md"
gemini_target="$DOTFILES_DIR/.gemini/config/GEMINI.md"

strip_frontmatter() {
  awk '
    NR == 1 && $0 == "---" { in_fm = 1; next }
    in_fm && $0 == "---"   { in_fm = 0; skip_blank = 1; next }
    in_fm                  { next }
    skip_blank && $0 == "" { skip_blank = 0; next }
    { skip_blank = 0; print }
  ' "$1"
}

render_codex() {
  cat <<'EOF'
<!--
  GENERATED FILE — DO NOT EDIT.
  Built by .codex/build-agents.sh from:
    - AGENTS.md                      (shared rules for all agents)
    - .claude/output-styles/emma.md  (persona SSOT, body only)
  Edit those sources, then run .codex/build-agents.sh and commit the result.
-->

EOF
  cat "$shared"
  printf '\n---\n\n## Persona\n\n'
  strip_frontmatter "$persona"
}

render_gemini() {
  cat <<'EOF'
<!--
  GENERATED FILE — DO NOT EDIT.
  Built by .codex/build-agents.sh from:
    - .claude/output-styles/emma.md  (persona SSOT, body only)
  Edit that source, then run .codex/build-agents.sh and commit the result.
-->

# Persona

EOF
  strip_frontmatter "$persona"
}

sync_file() {
  local label="$1"
  local target="$2"
  local expected="$3"
  local mode="$4"

  if [[ "$mode" == "--check" ]]; then
    if [[ -f "$target" && ! -L "$target" ]] && [[ "$(cat "$target")" == "$expected" ]]; then
      echo "OK:    $label is up to date"
      return 0
    fi
    echo "DRIFT: $label is out of date; run .codex/build-agents.sh" >&2
    return 1
  fi

  if [[ -f "$target" && ! -L "$target" ]] && [[ "$(cat "$target")" == "$expected" ]]; then
    echo "OK:    $label is up to date"
    return 0
  fi

  mkdir -p "$(dirname "$target")"
  local tmp
  tmp="$(mktemp "${target}.XXXXXX")"
  printf '%s\n' "$expected" >| "$tmp"
  chmod 644 "$tmp"
  command mv -f "$tmp" "$target"
  echo "BUILD: $label"
}

mode="${1:-}"
codex_expected="$(render_codex)"
gemini_expected="$(render_gemini)"

status=0
sync_file ".codex/AGENTS.md" "$codex_target" "$codex_expected" "$mode" || status=1
sync_file ".gemini/config/GEMINI.md" "$gemini_target" "$gemini_expected" "$mode" || status=1
exit "$status"
