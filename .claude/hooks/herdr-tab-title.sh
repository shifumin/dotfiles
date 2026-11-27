#!/bin/sh
# Stop hook: set the Herdr tab label to the session title.
# Uses the latest /rename title (custom-title), falling back to the generated title (ai-title).
set -eu

[ "${HERDR_ENV:-}" = "1" ] || exit 0
[ -n "${HERDR_TAB_ID:-}" ] || exit 0
command -v herdr >/dev/null 2>&1 || exit 0

title="$(/usr/bin/python3 -I -c '
import json, sys
path = json.load(sys.stdin).get("transcript_path") or ""
custom = ai = ""
try:
    with open(path, encoding="utf-8") as f:
        for line in f:
            if "-title\"" not in line:
                continue
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("type") == "custom-title" and entry.get("customTitle"):
                custom = entry["customTitle"]
            elif entry.get("type") == "ai-title" and entry.get("aiTitle"):
                ai = entry["aiTitle"]
except OSError:
    pass
print((custom or ai).replace("\n", " ").strip()[:40])
')"

[ -n "$title" ] || exit 0
herdr tab rename "$HERDR_TAB_ID" "$title" >/dev/null 2>&1 || true
