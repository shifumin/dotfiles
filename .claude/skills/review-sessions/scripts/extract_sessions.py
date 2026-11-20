#!/usr/bin/env python3
"""Extract compact digests of recent Claude Code and Codex sessions.

Usage: extract_sessions.py --since 7d|YYYY-MM-DD --out DIR [--batch-bytes N]

Writes one digest per session to DIR/sessions/, plus DIR/index.tsv and
DIR/batches.tsv (session digests grouped for parallel analysis).
Only the parts that reveal friction are kept: user messages, assistant text,
tool calls (name + short input), failed or rejected tool results.
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys

HOME = os.path.expanduser("~")
SELF_SKILL = "review-sessions"
USER_MAX = 1500
ASSIST_MAX = 400
TOOL_MAX = 200
RESULT_MAX = 300
CODEX_NOISE = ("# AGENTS.md instructions", "<environment_context>", "<user_instructions>",
               "<permissions instructions>", "<turn_aborted>")
ERROR_RE = re.compile(r"exit code:? ?[1-9]|error|denied|rejected|not permitted|failed|traceback", re.I)
# Harness-injected user turns: kept as one short line, not counted as user messages.
HARNESS_PREFIXES = ("<task-notification>", "<bash-stdout>", "<bash-stderr>", "<local-command-stdout>",
                    "<system-reminder>")
REJECT_MARKERS = ("doesn't want to proceed", "user rejected", "was rejected", "user declined",
                  "The user doesn't want")


def parse_since(value):
    m = re.fullmatch(r"(\d+)d", value)
    if m:
        return dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=int(m.group(1)))
    return dt.datetime.fromisoformat(value).replace(tzinfo=dt.datetime.now().astimezone().tzinfo)


def parse_ts(value):
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def clip(text, limit):
    text = re.sub(r"\s+", " ", text or "").strip()
    return text if len(text) <= limit else text[:limit] + "…"


def project_label(cwd):
    if not cwd:
        return "unknown"
    marker = "/ghq/github.com/"
    return cwd.split(marker, 1)[1] if marker in cwd else cwd.replace(HOME, "~")


def summarize_tool_input(name, data):
    if not isinstance(data, dict):
        return clip(str(data), TOOL_MAX)
    for key in ("command", "skill", "file_path", "pattern", "url", "query", "description", "prompt"):
        if key in data:
            extra = f" args={clip(str(data.get('args')), 80)}" if key == "skill" and data.get("args") else ""
            return f"{key}={clip(str(data[key]), TOOL_MAX)}{extra}"
    return clip(json.dumps(data, ensure_ascii=False), TOOL_MAX)


def read_lines(path):
    if path.endswith(".zst"):
        raw = subprocess.run(["zstd", "-dc", path], capture_output=True, check=False).stdout
        lines = raw.decode("utf-8", "replace").splitlines()
    else:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    for line in lines:
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def claude_session(path, since):
    events, meta = [], {"tool": "claude", "id": os.path.basename(path)[:-6], "title": "", "cwd": ""}
    times, user_count, self_run = [], 0, False
    for rec in read_lines(path):
        kind = rec.get("type")
        if kind == "ai-title":
            meta["title"] = rec.get("aiTitle") or rec.get("title") or meta["title"]
        if kind not in ("user", "assistant") or rec.get("isSidechain"):
            continue
        ts = parse_ts(rec.get("timestamp"))
        if ts is None or ts < since:
            continue
        meta["cwd"] = meta["cwd"] or rec.get("cwd", "")
        times.append(ts)
        stamp = ts.astimezone().strftime("%m-%d %H:%M")
        content = (rec.get("message") or {}).get("content")
        if kind == "user":
            if rec.get("isMeta"):
                continue
            texts = [content] if isinstance(content, str) else [
                item.get("text", "") for item in content or [] if item.get("type") == "text"]
            for text in texts:
                if f"<command-name>/{SELF_SKILL}" in text:
                    self_run = True
                if text.lstrip().startswith(HARNESS_PREFIXES):
                    events.append(f"[{stamp}] HARNESS: {clip(text, 150)}")
                elif "[Request interrupted by user" in text:
                    events.append(f"[{stamp}] U-INTERRUPT")
                else:
                    events.append(f"[{stamp}] U: {clip(text, USER_MAX)}")
                    user_count += 1
            for item in [] if isinstance(content, str) else content or []:
                if item.get("type") == "tool_result":
                    body = item.get("content")
                    if isinstance(body, list):
                        body = " ".join(b.get("text", "") for b in body if isinstance(b, dict))
                    body = body or ""
                    if any(m in body for m in REJECT_MARKERS):
                        events.append(f"[{stamp}] R-REJECTED: {clip(body, RESULT_MAX)}")
                    elif item.get("is_error"):
                        events.append(f"[{stamp}] R-ERROR: {clip(body, RESULT_MAX)}")
        else:
            for item in content or []:
                if item.get("type") == "text" and item.get("text", "").strip():
                    events.append(f"[{stamp}] A: {clip(item['text'], ASSIST_MAX)}")
                elif item.get("type") == "tool_use":
                    name, data = item.get("name", "?"), item.get("input", {})
                    if name == "Skill" and isinstance(data, dict) and data.get("skill") == SELF_SKILL:
                        self_run = True
                    events.append(f"[{stamp}] T: {name} {summarize_tool_input(name, data)}")
    return meta, events, times, user_count, self_run


def codex_session(path, since):
    events, meta = [], {"tool": "codex", "id": os.path.basename(path), "title": "", "cwd": ""}
    times, user_count = [], 0
    for rec in read_lines(path):
        payload = rec.get("payload") or {}
        if rec.get("type") == "session_meta":
            if not isinstance(payload.get("source"), str):
                return None  # guardian / spawned subagent thread
            meta["cwd"] = payload.get("cwd", "")
            meta["id"] = payload.get("id", meta["id"])
            continue
        if rec.get("type") != "response_item":
            continue
        ts = parse_ts(rec.get("timestamp"))
        if ts is None or ts < since:
            continue
        times.append(ts)
        stamp = ts.astimezone().strftime("%m-%d %H:%M")
        ptype = payload.get("type")
        if ptype == "message" and payload.get("role") in ("user", "assistant"):
            text = " ".join(c.get("text", "") for c in payload.get("content") or [] if isinstance(c, dict))
            if payload["role"] == "user":
                if text.lstrip().startswith(CODEX_NOISE) or not text.strip():
                    continue
                events.append(f"[{stamp}] U: {clip(text, USER_MAX)}")
                user_count += 1
            elif text.strip():
                events.append(f"[{stamp}] A: {clip(text, ASSIST_MAX)}")
        elif ptype in ("function_call", "custom_tool_call"):
            args = payload.get("arguments") or payload.get("input") or ""
            events.append(f"[{stamp}] T: {payload.get('name', '?')} {clip(str(args), TOOL_MAX)}")
        elif ptype in ("function_call_output", "custom_tool_call_output"):
            out = payload.get("output")
            out = out if isinstance(out, str) else json.dumps(out, ensure_ascii=False)
            if ERROR_RE.search(out[:600] or ""):
                events.append(f"[{stamp}] R-ERROR?: {clip(out, RESULT_MAX)}")
    return meta, events, times, user_count, False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="7d")
    ap.add_argument("--out", required=True)
    ap.add_argument("--batch-bytes", type=int, default=120_000)
    args = ap.parse_args()
    since = parse_since(args.since)
    out_dir = os.path.join(args.out, "sessions")
    os.makedirs(out_dir, exist_ok=True)

    cutoff = since.timestamp()
    claude_files = [p for p in glob.glob(f"{HOME}/.claude/projects/*/*.jsonl") if os.path.getmtime(p) >= cutoff]
    codex_files = [p for p in glob.glob(f"{HOME}/.codex/sessions/**/rollout-*.jsonl*", recursive=True)
                   if os.path.getmtime(p) >= cutoff]

    rows, skipped = [], {"no_user_msg": 0, "self_run": 0, "codex_subagent": 0}
    for path, fn in [(p, claude_session) for p in claude_files] + [(p, codex_session) for p in codex_files]:
        result = fn(path, since)
        if result is None:
            skipped["codex_subagent"] += 1
            continue
        meta, events, times, user_count, self_run = result
        if self_run:
            skipped["self_run"] += 1
            continue
        if user_count == 0:
            skipped["no_user_msg"] += 1
            continue
        project = project_label(meta["cwd"])
        start, end = min(times).astimezone(), max(times).astimezone()
        name = f"{meta['tool']}_{re.sub(r'[^A-Za-z0-9]+', '-', project)}_{meta['id'][-12:]}.md"
        header = (f"# {meta['tool']} | {project} | {start:%Y-%m-%d %H:%M} – {end:%m-%d %H:%M}\n"
                  f"session: {meta['id']}  source: {path}\n"
                  f"title: {meta['title']}\nuser_messages: {user_count}\n\n")
        body = header + "\n".join(events) + "\n"
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as fh:
            fh.write(body)
        rows.append((name, meta["tool"], project, f"{start:%Y-%m-%d %H:%M}", user_count, len(body.encode())))

    rows.sort(key=lambda r: (r[2], r[3]))
    with open(os.path.join(args.out, "index.tsv"), "w", encoding="utf-8") as fh:
        fh.write("file\ttool\tproject\tstart\tuser_msgs\tbytes\n")
        for r in rows:
            fh.write("\t".join(map(str, r)) + "\n")

    # Pack sessions into batches (same project together, size-capped) for parallel analysts.
    batches, current, size = [], [], 0
    for r in rows:
        if current and size + r[5] > args.batch_bytes:
            batches.append(current)
            current, size = [], 0
        current.append(r[0])
        size += r[5]
    if current:
        batches.append(current)
    with open(os.path.join(args.out, "batches.tsv"), "w", encoding="utf-8") as fh:
        for i, b in enumerate(batches, 1):
            fh.write(f"{i}\t" + ",".join(b) + "\n")

    total = sum(r[5] for r in rows)
    print(f"since={since.isoformat()} sessions={len(rows)} batches={len(batches)} bytes={total} skipped={skipped}")
    for project in sorted({r[2] for r in rows}):
        n = [r for r in rows if r[2] == project]
        print(f"  {project}: {len(n)} sessions ({sum(1 for r in n if r[1] == 'claude')} claude / "
              f"{sum(1 for r in n if r[1] == 'codex')} codex)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
