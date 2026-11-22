#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: launch-herdr.sh <handoff-file> [--kind <agent-kind>] [--direction right|down]
EOF
  exit 2
}

if [ "$#" -lt 1 ]; then
  usage
fi

HANDOFF_FILE=""
KIND=""
DIR="right"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --kind)
      [ "$#" -ge 2 ] || usage
      KIND="$2"
      shift 2
      ;;
    --direction)
      [ "$#" -ge 2 ] || usage
      DIR="$2"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    -*)
      echo "Unknown option: $1" >&2
      usage
      ;;
    *)
      [ -z "$HANDOFF_FILE" ] || usage
      HANDOFF_FILE="$1"
      shift
      ;;
  esac
done

[ -n "$HANDOFF_FILE" ] || usage

case "$DIR" in
  right|down) ;;
  *)
    echo "Invalid --direction: $DIR (expected right or down)" >&2
    exit 2
    ;;
esac

if [ "${HERDR_ENV:-}" != "1" ]; then
  echo "Not running inside Herdr (HERDR_ENV!=1)" >&2
  exit 1
fi

if [ ! -s "$HANDOFF_FILE" ]; then
  echo "Handoff file missing or empty: $HANDOFF_FILE" >&2
  exit 1
fi

if [ -z "$KIND" ]; then
  if [ -n "${HERDR_PANE_ID:-}" ]; then
    KIND=$(herdr agent get "$HERDR_PANE_ID" 2>/dev/null | jq -r '.result.agent.kind // .result.kind // empty' || true)
  fi
  if [ -z "$KIND" ]; then
    echo "Could not determine current agent kind; pass --kind <kind>" >&2
    exit 1
  fi
fi

NAME="handoff-$(date +%m%d-%H%M%S)"
SPLIT_OUT=$(herdr pane split --current --direction "$DIR" --cwd "$PWD" --no-focus)
PANE=$(printf '%s\n' "$SPLIT_OUT" | jq -r '.result.pane.pane_id // empty')
if [ -z "$PANE" ]; then
  printf 'Failed to parse pane_id from herdr pane split:\n%s\n' "$SPLIT_OUT" >&2
  exit 1
fi

# Retry while the newly split pane's shell is still initializing.
STARTED=0
START_ERR=""
for _ in 1 2 3 4 5 6 7 8 9 10; do
  if START_ERR=$(herdr agent start "$NAME" --kind "$KIND" --pane "$PANE" --timeout 60000 2>&1); then
    STARTED=1
    break
  fi
  printf '%s\n' "$START_ERR" | grep -q agent_pane_busy || {
    printf 'herdr agent start failed (pane=%s, kind=%s):\n%s\n' "$PANE" "$KIND" "$START_ERR" >&2
    exit 1
  }
  sleep 1
done

if [ "$STARTED" -ne 1 ]; then
  printf 'herdr agent start timed out waiting for pane %s:\n%s\n' "$PANE" "$START_ERR" >&2
  exit 1
fi

PROMPT_EXIT=0
PROMPT_ERR=$(herdr agent prompt "$NAME" "$(cat "$HANDOFF_FILE")" --wait --timeout 180000 2>&1) || PROMPT_EXIT=$?
echo "pane=$PANE agent=$NAME kind=$KIND file=$HANDOFF_FILE"

if [ "$PROMPT_EXIT" -ne 0 ]; then
  printf 'herdr agent prompt exited with %d (do not re-send without checking output below):\n%s\n' "$PROMPT_EXIT" "$PROMPT_ERR" >&2
  herdr agent read "$NAME" --source recent-unwrapped --lines 40 | tail -25 || true
  exit "$PROMPT_EXIT"
fi

herdr agent read "$NAME" --source recent-unwrapped --lines 40 | tail -25
