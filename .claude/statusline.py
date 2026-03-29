#!/usr/bin/env python3
"""Claude Code statusline - Braille dots style with TrueColor gradient."""
import json
import os
import sys
from datetime import datetime, timezone

data = json.load(sys.stdin)

BRAILLE = " ⣀⣄⣤⣦⣶⣷⣿"
R = "\033[0m"
DIM = "\033[2m"


def gradient(pct):
    if pct < 50:
        r = int(pct * 5.1)
        return f"\033[38;2;{r};200;80m"
    else:
        g = int(200 - (pct - 50) * 4)
        return f"\033[38;2;255;{max(g, 0)};60m"


def braille_bar(pct, width=8):
    pct = min(max(pct, 0), 100)
    level = pct / 100
    bar = ""
    for i in range(width):
        seg_start = i / width
        seg_end = (i + 1) / width
        if level >= seg_end:
            bar += BRAILLE[7]
        elif level <= seg_start:
            bar += BRAILLE[0]
        else:
            frac = (level - seg_start) / (seg_end - seg_start)
            bar += BRAILLE[min(int(frac * 7), 7)]
    return bar


def fmt_reset_time(value):
    try:
        if isinstance(value, (int, float)):
            dt = datetime.fromtimestamp(value, tz=timezone.utc)
        else:
            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        local_dt = dt.astimezone()
        return local_dt.strftime("%H:%M")
    except (ValueError, AttributeError, OSError, TypeError):
        return ""


def fmt(label, pct, reset_time=""):
    p = round(pct)
    suffix = f" ↻{reset_time}" if reset_time else ""
    return f"{DIM}{label}{R} {gradient(pct)}{braille_bar(pct)}{R} {p}%{suffix}"


# CWD
home = os.environ.get("HOME", "")
cwd = data.get("workspace", {}).get("current_dir") or data.get("cwd", "")
cwd_display = cwd.replace(home, "~", 1) if cwd else "--"

parts = [f"📁 {cwd_display}"]

# Context window
ctx = data.get("context_window", {}).get("used_percentage")
if ctx is not None:
    parts.append(fmt("ctx", ctx))

# 5-hour rate limit
five_hour = data.get("rate_limits", {}).get("five_hour", {})
five_pct = five_hour.get("used_percentage")
if five_pct is not None:
    reset = fmt_reset_time(five_hour.get("resets_at", ""))
    parts.append(fmt("5h", five_pct, reset))

# 7-day rate limit
seven_day = data.get("rate_limits", {}).get("seven_day", {})
seven_pct = seven_day.get("used_percentage")
if seven_pct is not None:
    parts.append(fmt("7d", seven_pct))

print(f" {DIM}│{R} ".join(parts), end="")
