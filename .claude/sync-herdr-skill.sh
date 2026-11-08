#!/bin/bash
# Sync the vendored herdr skill with the copy bundled in the installed herdr binary.
#
# `herdr --skill` prints the SKILL.md that matches the installed release, so the
# skill never documents commands the local CLI lacks (upstream master can run ahead
# of the Homebrew release). Run after upgrading herdr, then commit the result.
#
# Usage: .claude/sync-herdr-skill.sh [--check]
#   --check  report drift without writing; exits 1 on drift
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "$0")/.." && pwd)"
target="$DOTFILES_DIR/.claude/skills/herdr/SKILL.md"

if ! command -v herdr &>/dev/null; then
  echo "SKIP (herdr not installed): herdr skill sync"
  exit 0
fi

version="$(herdr --version 2>/dev/null || echo unknown)"
bundled="$(herdr --skill 2>/dev/null)" || {
  echo "ERROR: 'herdr --skill' failed ($version); update herdr or sync manually" >&2
  exit 2
}
if [[ "$bundled" != ---* ]]; then
  echo "ERROR: 'herdr --skill' did not print a SKILL.md ($version)" >&2
  exit 2
fi

if [[ -f "$target" ]] && [[ "$bundled" == "$(cat "$target")" ]]; then
  echo "OK (herdr skill matches $version)"
  exit 0
fi

if [[ "${1:-}" == "--check" ]]; then
  echo "DRIFT: herdr skill differs from $version bundled copy; run .claude/sync-herdr-skill.sh"
  exit 1
fi

printf '%s\n' "$bundled" >| "$target"
echo "UPDATE: herdr skill synced to $version"
