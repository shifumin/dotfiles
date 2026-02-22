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

echo -e "ctx ${COLOR}${BAR}${RESET} ${USED_K}k/${TOTAL_K}k | tok ${TOK_K}k | ⏱ ${DURATION}"
