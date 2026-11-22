#!/usr/bin/env python3
"""Fetch / apply for cleanup-inbox-mail.

fetch <cat>...       Query categories in parallel, print Markdown tables (JST dates),
                     and save the shown IDs to STATE for `apply`.
apply [--dry-run]    Trash spam / archive+mark-read the IDs saved by the last fetch,
                     re-query to verify, and print the result lines.

Categories: spam purchases social promotions
"""
from __future__ import annotations

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

STATE = Path.home() / ".cache" / "cleanup-inbox-mail" / "last.json"
JST = timezone(timedelta(hours=9))
MAX_FETCH = 100
GWS_TIMEOUT_SECONDS = 60

CATS = {
    "spam": ("迷惑メール", "in:spam"),
    "purchases": ("購入", "category:purchases is:unread"),
    "social": ("ソーシャル", "category:social is:unread"),
    "promotions": ("プロモーション", "category:promotions is:unread"),
}
ORDER = list(CATS)
LABELS = {
    "spam": "迷惑メール削除",
    "purchases": "購入アーカイブ",
    "social": "ソーシャルアーカイブ",
    "promotions": "プロモーションアーカイブ",
}
# Gmail permalink per view. Spam is trashed by `apply`, so link where it lands (#trash);
# archived mail leaves the inbox but stays in All Mail (#all). The ID is the message ID
# from +triage (no extra API call); Gmail resolves it to the thread.
GMAIL_URL = "https://mail.google.com/mail/u/0/#{view}/{id}"
VIEW = {"spam": "trash"}


class GwsError(Exception):
    """Raised when a `gws` command fails or returns an API error."""


def triage(query: str) -> list[dict[str, Any]]:
    try:
        out = subprocess.run(
            ["gws", "gmail", "+triage", "--query", query, "--max", str(MAX_FETCH), "--format", "json"],
            capture_output=True,
            text=True,
            timeout=GWS_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise GwsError(f"gws timeout ({query}): exceeded {GWS_TIMEOUT_SECONDS}s") from exc
    except OSError as exc:
        raise GwsError(f"gws exec failed ({query}): {exc}") from exc

    # Zero hits: exit 0 + non-JSON "No messages found ...". Auth failure: exit 2 +
    # parseable {"error": ...} JSON, which .get("messages", []) would turn into a
    # silent "0 mails" — so check exit code and error key before trusting it.
    # Parse JSON first so a subject containing "No messages found" can't fake 0 hits.
    try:
        data = json.loads(out.stdout)
    except json.JSONDecodeError:
        data = None
    if data is None and out.returncode == 0 and "No messages found" in out.stdout + out.stderr:
        return []
    if out.returncode != 0 or not isinstance(data, dict) or "error" in data:
        raise GwsError(f"gws error ({query}):\n{out.stdout}{out.stderr}")
    messages = data.get("messages", [])
    return messages if isinstance(messages, list) else []


def jst(date: str | None) -> str:
    if not date:
        return ""
    try:
        return parsedate_to_datetime(date).astimezone(JST).strftime("%Y-%m-%d %H:%M")
    except (TypeError, ValueError, IndexError):
        return date


def sender(raw: str | None) -> str:
    text = raw or ""
    name = text.split("<")[0].strip().strip('"').strip()
    return name or text.strip("<>")


def cell(s: str | None) -> str:
    text = s or ""
    return text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ").replace("|", "\\|")


def fetch_all(cats: list[str]) -> dict[str, list[dict[str, Any]]]:
    if not cats:
        return {}

    def run(c: str) -> list[dict[str, Any]]:
        return sorted(triage(CATS[c][1]), key=lambda m: jst(m.get("date")), reverse=True)

    with ThreadPoolExecutor(max_workers=len(cats)) as ex:
        return dict(zip(cats, ex.map(run, cats)))


def link(cat: str, msg_id: str) -> str:
    return f"[開く]({GMAIL_URL.format(view=VIEW.get(cat, 'all'), id=msg_id)})"


def table(cat: str, msgs: list[dict[str, Any]]) -> list[str]:
    if not msgs:
        return ["対象のメールはありません"]
    rows = ["| # | 送信者 | 件名 | 日時 | リンク |", "|---|--------|------|------|--------|"]
    for i, m in enumerate(msgs, 1):
        subj = cell(m.get("subject")) or "(件名なし)"
        rows.append(
            f"| {i} | {cell(sender(m.get('from')))} | {subj} | {jst(m.get('date'))} | {link(cat, m['id'])} |"
        )
    if len(msgs) >= MAX_FETCH:
        rows.append("")
        rows.append(f"> ※ 取得上限（{MAX_FETCH}件）に達しているため、未表示のメールがある可能性があります。")
    return rows


def fetch(cats: list[str]) -> int:
    ordered = [c for c in ORDER if c in cats]
    res = fetch_all(ordered)
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({c: [m["id"] for m in res[c]] for c in ordered}), encoding="utf-8")

    out: list[str] = []
    if "spam" in ordered:
        out += [f"## 削除対象（迷惑メール {len(res['spam'])}件）", ""] + table("spam", res["spam"]) + [""]
    archive = [c for c in ordered if c != "spam"]
    if archive:
        out += ["## アーカイブ対象", ""]
        for c in archive:
            out += [f"### {CATS[c][0]}（{len(res[c])}件）", ""] + table(c, res[c]) + [""]
    print("\n".join(out).rstrip())
    print("\nCOUNTS " + " ".join(f"{c}={len(res[c])}" for c in ordered))
    return 0


def has_json_error(stdout: str) -> bool:
    if not stdout.strip():
        return False
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return False
    return isinstance(data, dict) and "error" in data


def gws(args: list[str], dry: bool) -> str | None:
    """Run one write; return an error string, or None on success."""
    if dry:
        print("DRY", " ".join(args))
        return None
    try:
        out = subprocess.run(
            ["gws", "gmail", "users", "messages", *args],
            capture_output=True,
            text=True,
            timeout=GWS_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return f"{args[0]}: timeout after {GWS_TIMEOUT_SECONDS}s"
    except OSError as exc:
        return f"{args[0]}: {exc}"
    if out.returncode != 0 or has_json_error(out.stdout):
        return f"{args[0]}: {out.stdout.strip()} {out.stderr.strip()}".strip()
    return None


def load_state() -> dict[str, list[str]]:
    if not STATE.exists():
        raise GwsError(f"state file not found: {STATE} (run `fetch` first)")
    try:
        data = json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GwsError(f"failed to read state file {STATE}: {exc}") from exc
    if not isinstance(data, dict):
        raise GwsError(f"invalid state format in {STATE}")
    return {c: list(ids) for c, ids in data.items() if c in CATS and isinstance(ids, list)}


def apply(dry: bool) -> int:
    state = load_state()
    jobs: list[list[str]] = []
    for c in ORDER:
        ids = state.get(c, [])
        if not ids:
            continue
        if c == "spam":
            for msg_id in ids:
                jobs.append(["trash", "--params", json.dumps({"userId": "me", "id": msg_id})])
        else:
            jobs.append([
                "batchModify",
                "--params",
                '{"userId":"me"}',
                "--json",
                json.dumps({"ids": ids, "removeLabelIds": ["INBOX", "UNREAD"]}),
            ])

    errors: list[str] = []
    if jobs:
        with ThreadPoolExecutor(max_workers=min(8, len(jobs))) as ex:
            errors = [e for e in ex.map(lambda a: gws(a, dry), jobs) if e]
    if dry:
        return 0

    active_cats = [c for c in ORDER if state.get(c)]
    after = fetch_all(active_cats)

    print("## クリーンアップ完了\n")
    has_failure = False
    for c in ORDER:
        if c not in state:
            continue
        ids = state[c]
        if not ids:
            print(f"- **{CATS[c][0]}**: 対象なし")
            continue
        now = {m["id"] for m in after.get(c, [])}
        left = [i for i in ids if i in now]
        new = len(now - set(ids))
        if left:
            has_failure = True
            line = f"- **{LABELS[c]}**: {len(ids) - len(left)}件 ✅ / 失敗 {len(left)}件 ❌ ({', '.join(left)})"
        else:
            line = f"- **{LABELS[c]}**: {len(ids)}件 ✅"
        if new:
            line += f"（処理中に新着 {new}件、未処理）"
        print(line)

    if errors:
        # The re-query above decides success; these are only to explain any ❌ rows.
        print("\n## gwsエラー\n")
        for e in dict.fromkeys(errors):
            print(f"- {e}")

    STATE.unlink(missing_ok=True)
    return 1 if has_failure else 0


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args or args[0] not in ("fetch", "apply"):
        print(__doc__, file=sys.stderr)
        return 2
    try:
        if args[0] == "fetch":
            cats = args[1:] or ORDER
            bad = [c for c in cats if c not in CATS]
            if bad:
                print(f"unknown category: {bad}", file=sys.stderr)
                return 2
            return fetch(cats)
        return apply("--dry-run" in args[1:])
    except GwsError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
