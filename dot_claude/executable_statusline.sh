#!/bin/bash
input=$(cat)

# Extract values from JSON
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
CTX_SIZE=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')
TOTAL_INPUT=$(echo "$input" | jq -r '.context_window.total_input_tokens // 0')
TOTAL_OUTPUT=$(echo "$input" | jq -r '.context_window.total_output_tokens // 0')
DURATION_MS=$(echo "$input" | jq -r '.cost.total_duration_ms // 0')

# Calculate context used tokens
USED_TOKENS=$(( PCT * CTX_SIZE / 100 ))

# Format tokens as Xk
USED_K=$(( USED_TOKENS / 1000 ))
TOTAL_K=$(( CTX_SIZE / 1000 ))
TOK_K=$(( (TOTAL_INPUT + TOTAL_OUTPUT) / 1000 ))

# Format duration
DURATION_SEC=$(( DURATION_MS / 1000 ))
HOURS=$(( DURATION_SEC / 3600 ))
MINS=$(( (DURATION_SEC % 3600) / 60 ))
if [ "$HOURS" -gt 0 ]; then
  DURATION="${HOURS}h${MINS}m"
else
  DURATION="${MINS}m"
fi

# Progress bar (20 chars)
BAR_WIDTH=20
FILLED=$(( PCT * BAR_WIDTH / 100 ))
EMPTY=$(( BAR_WIDTH - FILLED ))

# Color based on percentage
if [ "$PCT" -lt 50 ]; then
  COLOR="\033[32m"
elif [ "$PCT" -lt 75 ]; then
  COLOR="\033[33m"
else
  COLOR="\033[31m"
fi
RESET="\033[0m"

# Build bar
BAR=""
for ((i=0; i<FILLED; i++)); do BAR+="█"; done
for ((i=0; i<EMPTY; i++)); do BAR+="░"; done

# --- Usage quota (undocumented API with caching) ---
CACHE_FILE="/tmp/claude-usage-cache.json"
CACHE_TTL=60

fetch_usage() {
  local creds token response
  creds=$(security find-generic-password -s "Claude Code-credentials" -a "$(whoami)" -w 2>/dev/null)
  token=$(echo "$creds" | jq -r '.claudeAiOauth.accessToken // empty' 2>/dev/null)
  if [[ -n "$token" ]]; then
    response=$(curl --silent --max-time 5 \
      --header "Authorization: Bearer $token" \
      --header "anthropic-beta: oauth-2025-04-20" \
      "https://api.anthropic.com/api/oauth/usage" 2>/dev/null)
    if echo "$response" | jq -e '.five_hour' >/dev/null 2>&1; then
      echo "$response" > "$CACHE_FILE"
    fi
  fi
}

# Check cache freshness
needs_refresh=true
if [[ -f "$CACHE_FILE" ]]; then
  cache_mtime=$(stat -f %m "$CACHE_FILE" 2>/dev/null || echo 0)
  now=$(date +%s)
  if (( now - cache_mtime < CACHE_TTL )); then
    needs_refresh=false
  fi
fi

if $needs_refresh; then
  fetch_usage
fi

# Parse usage data
USE_PCT="--"
RESET_TIME="--:--"
if [[ -f "$CACHE_FILE" ]]; then
  USE_PCT=$(jq -r '.five_hour.utilization // empty' "$CACHE_FILE" 2>/dev/null | cut -d. -f1)
  RESETS_AT=$(jq -r '.five_hour.resets_at // empty' "$CACHE_FILE" 2>/dev/null)
  if [[ -n "$USE_PCT" && -n "$RESETS_AT" ]]; then
    # Convert UTC ISO 8601 to local time HH:MM
    UTC_DATETIME=$(echo "$RESETS_AT" | sed 's/\..*//')
    EPOCH=$(date -juf "%Y-%m-%dT%H:%M:%S" "$UTC_DATETIME" "+%s" 2>/dev/null)
    if [[ -n "$EPOCH" ]]; then
      RESET_TIME=$(date -jf "%s" "$EPOCH" "+%H:%M" 2>/dev/null || echo "--:--")
    fi
  else
    USE_PCT="--"
  fi
fi

# Color for usage percentage
USE_COLOR=""
if [[ "$USE_PCT" != "--" ]]; then
  if [ "$USE_PCT" -lt 50 ] 2>/dev/null; then
    USE_COLOR="\033[32m"
  elif [ "$USE_PCT" -lt 75 ] 2>/dev/null; then
    USE_COLOR="\033[33m"
  else
    USE_COLOR="\033[31m"
  fi
fi

echo -e "ctx ${COLOR}${BAR}${RESET} ${USED_K}k/${TOTAL_K}k | tok ${TOK_K}k | ⏱ ${DURATION} | ${USE_COLOR}use ${USE_PCT}%${RESET} ↻${RESET_TIME}"
