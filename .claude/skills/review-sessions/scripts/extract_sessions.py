#!/usr/bin/env python3
"""Extract compact digests of recent Claude Code and Codex sessions.

Usage: extract_sessions.py --since 7d|YYYY-MM-DD --out DIR [--batch-bytes N]

Writes one digest per session to DIR/sessions/, plus DIR/index.tsv and
DIR/batches.tsv (session digests grouped for parallel analysis).
Only friction-relevant turns are kept: user messages, assistant text,
tool calls (name + clipped input), and failed/rejected tool results.
"""

from __future__ import annotations

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

CODEX_NOISE = (
    "# AGENTS.md instructions",
    "<environment_context>",
    "<user_instructions>",
    "<permissions instructions>",
    "<turn_aborted>",
)
ERROR_RE = re.compile(
    r"exit code:? ?[1-9]|error|denied|rejected|not permitted|failed|traceback",
    re.I,
)
HARNESS_PREFIXES = (
    "<task-notification>",
    "<bash-stdout>",
    "<bash-stderr>",
    "<local-command-stdout>",
    "<system-reminder>",
)
REJECT_MARKERS = (
    "doesn't want to proceed",
    "user rejected",
    "was rejected",
    "user declined",
    "The user doesn't want",
)
SELF_RUN_RE = re.compile(rf"(?:^|[\s\"'`])[/\$]{re.escape(SELF_SKILL)}(?:\b|$)")


def parse_since(value: str) -> dt.datetime:
    raw = value.strip()
    m = re.fullmatch(r"(\d+)d", raw)
    if m:
        days = int(m.group(1))
        if days <= 0:
            raise ValueError(f"--since の日数は 1 以上にしてください: {value!r}")
        return dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
    try:
        parsed = dt.datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError(f"--since は Nd（例: 7d）または YYYY-MM-DD 形式で指定してください: {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.datetime.now().astimezone().tzinfo)
    return parsed


def parse_ts(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def clip(text: str | None, limit: int) -> str:
    compact = re.sub(r"\s+", " ", text or "").strip()
    return compact if len(compact) <= limit else compact[:limit] + "…"


def tsv_safe(value: object) -> str:
    return re.sub(r"[\t\r\n]+", " ", str(value))


def project_label(cwd: str) -> str:
    if not cwd:
        return "unknown"
    marker = "/ghq/github.com/"
    if marker in cwd:
        return cwd.split(marker, 1)[1].rstrip("/")
    return cwd.replace(HOME, "~", 1) if cwd.startswith(HOME) else cwd


def session_id_slug(raw_id: str) -> str:
    cleaned = re.sub(r"\.(?:jsonl(?:\.zst)?|zst)$", "", raw_id)
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", cleaned).strip("-")
    return cleaned[-12:] if cleaned else "unknown"


def summarize_tool_input(name: str, data: object) -> str:
    if not isinstance(data, dict):
        return clip(str(data), TOOL_MAX)
    for key in ("command", "skill", "file_path", "pattern", "url", "query", "description", "prompt"):
        if key in data:
            extra = f" args={clip(str(data.get('args')), 80)}" if key == "skill" and data.get("args") else ""
            return f"{key}={clip(str(data[key]), TOOL_MAX)}{extra}"
    return clip(json.dumps(data, ensure_ascii=False), TOOL_MAX)


def read_lines(path: str):
    if path.endswith(".zst"):
        try:
            proc = subprocess.run(["zstd", "-dc", path], capture_output=True, check=False)
        except FileNotFoundError:
            print(f"WARNING: zstd not found; skipping {path}", file=sys.stderr)
            return
        if proc.returncode != 0:
            err = proc.stderr.decode("utf-8", "replace").strip()
            print(f"WARNING: zstd failed for {path}: {err}", file=sys.stderr)
            return
        lines = proc.stdout.decode("utf-8", "replace").splitlines()
    else:
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                lines = fh.read().splitlines()
        except OSError as exc:
            print(f"WARNING: failed to read {path}: {exc}", file=sys.stderr)
            return
    for line in lines:
        if not line.strip():
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def claude_session(path: str, since: dt.datetime):
    events: list[str] = []
    meta = {"tool": "claude", "id": os.path.basename(path)[:-6], "title": "", "cwd": ""}
    times: list[dt.datetime] = []
    user_count = 0
    self_run = False

    for rec in read_lines(path):
        kind = rec.get("type")
        if kind == "ai-title":
            meta["title"] = rec.get("aiTitle") or rec.get("title") or meta["title"]
            continue
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
            if isinstance(content, str):
                texts = [content]
                blocks = []
            elif isinstance(content, list):
                texts = [item.get("text", "") for item in content if isinstance(item, dict) and item.get("type") == "text"]
                blocks = content
            else:
                texts, blocks = [], []

            for text in texts:
                if f"<command-name>/{SELF_SKILL}" in text or SELF_RUN_RE.search(text):
                    self_run = True
                if text.lstrip().startswith(HARNESS_PREFIXES):
                    events.append(f"[{stamp}] HARNESS: {clip(text, 150)}")
                elif "[Request interrupted by user" in text:
                    events.append(f"[{stamp}] U-INTERRUPT")
                elif text.strip():
                    events.append(f"[{stamp}] U: {clip(text, USER_MAX)}")
                    user_count += 1

            for item in blocks:
                if not isinstance(item, dict) or item.get("type") != "tool_result":
                    continue
                body = item.get("content")
                if isinstance(body, list):
                    body = " ".join(b.get("text", "") for b in body if isinstance(b, dict))
                body = body if isinstance(body, str) else ""
                if any(m in body for m in REJECT_MARKERS):
                    events.append(f"[{stamp}] R-REJECTED: {clip(body, RESULT_MAX)}")
                elif item.get("is_error"):
                    events.append(f"[{stamp}] R-ERROR: {clip(body, RESULT_MAX)}")
        else:
            if isinstance(content, str) and content.strip():
                events.append(f"[{stamp}] A: {clip(content, ASSIST_MAX)}")
            elif isinstance(content, list):
                for item in content:
                    if not isinstance(item, dict):
                        continue
                    if item.get("type") == "text" and item.get("text", "").strip():
                        events.append(f"[{stamp}] A: {clip(item['text'], ASSIST_MAX)}")
                    elif item.get("type") == "tool_use":
                        name, data = item.get("name", "?"), item.get("input", {})
                        if name == "Skill" and isinstance(data, dict) and data.get("skill") == SELF_SKILL:
                            self_run = True
                        events.append(f"[{stamp}] T: {name} {summarize_tool_input(name, data)}")

    return meta, events, times, user_count, self_run


def codex_session(path: str, since: dt.datetime):
    events: list[str] = []
    meta = {"tool": "codex", "id": os.path.basename(path), "title": "", "cwd": ""}
    times: list[dt.datetime] = []
    user_count = 0
    self_run = False

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
            raw_content = payload.get("content")
            if isinstance(raw_content, str):
                text = raw_content
            elif isinstance(raw_content, list):
                text = " ".join(c.get("text", "") for c in raw_content if isinstance(c, dict))
            else:
                text = ""
            if payload["role"] == "user":
                if text.lstrip().startswith(CODEX_NOISE) or not text.strip():
                    continue
                if SELF_RUN_RE.search(text) or f"{SELF_SKILL}/SKILL.md" in text:
                    self_run = True
                events.append(f"[{stamp}] U: {clip(text, USER_MAX)}")
                user_count += 1
            elif text.strip():
                events.append(f"[{stamp}] A: {clip(text, ASSIST_MAX)}")
        elif ptype in ("function_call", "custom_tool_call"):
            raw_args = payload.get("arguments") or payload.get("input") or ""
            args_str = raw_args if isinstance(raw_args, str) else json.dumps(raw_args, ensure_ascii=False)
            if f"{SELF_SKILL}/scripts/extract_sessions.py" in args_str:
                self_run = True
            events.append(f"[{stamp}] T: {payload.get('name', '?')} {clip(args_str, TOOL_MAX)}")
        elif ptype in ("function_call_output", "custom_tool_call_output"):
            out = payload.get("output")
            out_str = out if isinstance(out, str) else json.dumps(out, ensure_ascii=False)
            if ERROR_RE.search(out_str[:600] or ""):
                events.append(f"[{stamp}] R-ERROR?: {clip(out_str, RESULT_MAX)}")

    return meta, events, times, user_count, self_run


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Extract digests of recent Claude Code and Codex sessions")
    ap.add_argument("--since", default="7d", help="Lookback window (e.g. 7d, 14d, 2026-11-01)")
    ap.add_argument("--out", required=True, help="Output directory")
    ap.add_argument("--batch-bytes", type=int, default=120_000, help="Target max bytes per batch")
    ap.add_argument("--claude-dir", default=f"{HOME}/.claude/projects", help="Override Claude projects dir")
    ap.add_argument("--codex-dir", default=f"{HOME}/.codex/sessions", help="Override Codex sessions dir")
    args = ap.parse_args(argv)

    try:
        since = parse_since(args.since)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    out_dir = os.path.join(args.out, "sessions")
    os.makedirs(out_dir, exist_ok=True)

    cutoff = since.timestamp()
    claude_files = [
        p for p in glob.glob(f"{args.claude_dir}/*/*.jsonl")
        if os.path.isfile(p) and os.path.getmtime(p) >= cutoff
    ]
    codex_files = [
        p for p in glob.glob(f"{args.codex_dir}/**/rollout-*.jsonl*", recursive=True)
        if os.path.isfile(p) and os.path.getmtime(p) >= cutoff
    ]

    rows: list[tuple[str, str, str, str, str, int, int]] = []
    used_names: set[str] = set()
    skipped = {"no_user_msg": 0, "self_run": 0, "codex_subagent": 0}

    for path, fn in [(p, claude_session) for p in claude_files] + [(p, codex_session) for p in codex_files]:
        result = fn(path, since)
        if result is None:
            skipped["codex_subagent"] += 1
            continue
        meta, events, times, user_count, self_run = result
        if self_run:
            skipped["self_run"] += 1
            continue
        if user_count == 0 or not times:
            skipped["no_user_msg"] += 1
            continue

        project = project_label(meta["cwd"])
        start, end = min(times).astimezone(), max(times).astimezone()
        proj_slug = re.sub(r"[^A-Za-z0-9]+", "-", project).strip("-") or "unknown"
        id_slug = session_id_slug(meta["id"])
        name = f"{meta['tool']}_{proj_slug}_{id_slug}.md"
        suffix = 2
        while name in used_names:
            name = f"{meta['tool']}_{proj_slug}_{id_slug}_{suffix}.md"
            suffix += 1
        used_names.add(name)

        header = (
            f"# {meta['tool']} | {project} | {start:%Y-%m-%d %H:%M} – {end:%m-%d %H:%M}\n"
            f"session: {meta['id']}  source: {path}\n"
            f"title: {meta['title']}\nuser_messages: {user_count}\n\n"
        )
        body = header + "\n".join(events) + "\n"
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as fh:
            fh.write(body)
        rows.append((name, meta["tool"], project, meta["cwd"], f"{start:%Y-%m-%d %H:%M}", user_count, len(body.encode("utf-8"))))

    rows.sort(key=lambda r: (r[2], r[4]))
    with open(os.path.join(args.out, "index.tsv"), "w", encoding="utf-8") as fh:
        fh.write("file\ttool\tproject\tcwd\tstart\tuser_msgs\tbytes\n")
        for r in rows:
            fh.write("\t".join(tsv_safe(v) for v in r) + "\n")

    # Pack sessions into size-capped batches (same project kept together).
    batches: list[list[str]] = []
    current: list[str] = []
    size = 0
    for r in rows:
        if current and size + r[6] > args.batch_bytes:
            batches.append(current)
            current, size = [], 0
        current.append(r[0])
        size += r[6]
    if current:
        batches.append(current)

    with open(os.path.join(args.out, "batches.tsv"), "w", encoding="utf-8") as fh:
        for i, b in enumerate(batches, 1):
            fh.write(f"{i}\t" + ",".join(b) + "\n")

    total = sum(r[6] for r in rows)
    print(f"since={since.isoformat()} sessions={len(rows)} batches={len(batches)} bytes={total} skipped={skipped}")
    for project in sorted({r[2] for r in rows}):
        n = [r for r in rows if r[2] == project]
        print(
            f"  {project}: {len(n)} sessions ({sum(1 for r in n if r[1] == 'claude')} claude / "
            f"{sum(1 for r in n if r[1] == 'codex')} codex)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
