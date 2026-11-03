#!/bin/bash
# Build the generated .codex/AGENTS.md (symlinked to ~/.codex/AGENTS.md).
# Codex cannot import files, so concatenate the shared AGENTS.md with the
# Codex-only .codex/AGENTS.codex.md.
#
# Usage:
#   .codex/build-agents.sh          # (re)generate; no-op when already current
#   .codex/build-agents.sh --check  # exit 1 if the generated file has drifted
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "$0")/.." && pwd)"
shared="$DOTFILES_DIR/AGENTS.md"
codex_only="$DOTFILES_DIR/.codex/AGENTS.codex.md"
target="$DOTFILES_DIR/.codex/AGENTS.md"

render() {
  cat <<'EOF'
<!--
  GENERATED FILE — DO NOT EDIT.
  Built by .codex/build-agents.sh from:
    - AGENTS.md              (shared rules for Claude Code and Codex)
    - .codex/AGENTS.codex.md (Codex-only additions)
  Edit those sources, then run .codex/build-agents.sh and commit the result.
-->

EOF
  cat "$shared"
  printf '\n---\n\n'
  cat "$codex_only"
}

expected="$(render)"

if [[ "${1:-}" == "--check" ]]; then
  if [[ -f "$target" && ! -L "$target" ]] && [[ "$(cat "$target")" == "$expected" ]]; then
    echo "OK:    .codex/AGENTS.md is up to date"
    exit 0
  fi
  echo "DRIFT: .codex/AGENTS.md is out of date; run .codex/build-agents.sh" >&2
  exit 1
fi

if [[ -f "$target" && ! -L "$target" ]] && [[ "$(cat "$target")" == "$expected" ]]; then
  echo "OK:    .codex/AGENTS.md is up to date"
  exit 0
fi

tmp="$(mktemp "${target}.XXXXXX")"
printf '%s\n' "$expected" >| "$tmp"
chmod 644 "$tmp"
mv -f "$tmp" "$target"
echo "BUILD: .codex/AGENTS.md"
