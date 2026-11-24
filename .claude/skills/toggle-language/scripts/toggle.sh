#!/usr/bin/env bash
# Toggle Claude Code's outputStyle in ~/.claude/settings.json while preserving symlinks.
# Exit 1 with "ERROR: SETTINGS_NOT_FOUND" or "ERROR: NO_BACKUP" is by design.
set -euo pipefail

SETTINGS_FILE="${CLAUDE_SETTINGS_FILE:-${HOME}/.claude/settings.json}"
BACKUP_FILE="${CLAUDE_OUTPUTSTYLE_BACKUP:-${HOME}/.claude/.outputstyle_backup}"

if [[ ! -f "${SETTINGS_FILE}" ]]; then
  echo "ERROR: SETTINGS_NOT_FOUND"
  exit 1
fi

# Resolve symlink target so atomic replace does not overwrite the symlink with a regular file.
REAL_SETTINGS="$(readlink -f "${SETTINGS_FILE}")"
REAL_DIR="$(dirname "${REAL_SETTINGS}")"

TMP_FILE="$(mktemp "${REAL_DIR}/.settings.json.XXXXXX")"
trap 'command rm -f "${TMP_FILE}"' EXIT

CURRENT="$(jq -r '.outputStyle // empty' "${REAL_SETTINGS}")"

if [[ -n "${CURRENT}" ]]; then
  printf '%s\n' "${CURRENT}" >| "${BACKUP_FILE}"
  jq 'del(.outputStyle)' "${REAL_SETTINGS}" >| "${TMP_FILE}"
  command mv -f "${TMP_FILE}" "${REAL_SETTINGS}"
  echo "TOGGLED: OFF (backup: ${CURRENT})"
else
  if [[ ! -f "${BACKUP_FILE}" ]]; then
    echo "ERROR: NO_BACKUP"
    exit 1
  fi
  RESTORED="$(tr -d '\r\n' < "${BACKUP_FILE}")"
  if [[ -z "${RESTORED}" ]]; then
    echo "ERROR: NO_BACKUP"
    exit 1
  fi
  jq --arg style "${RESTORED}" '.outputStyle = $style' "${REAL_SETTINGS}" >| "${TMP_FILE}"
  command mv -f "${TMP_FILE}" "${REAL_SETTINGS}"
  echo "TOGGLED: ON (restored: ${RESTORED})"
fi
