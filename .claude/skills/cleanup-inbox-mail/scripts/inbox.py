#!/usr/bin/env python3
"""Fetch / apply for cleanup-inbox-mail.

fetch <cat>...       Query categories in parallel, print Markdown tables (JST dates),
                     and save the shown IDs to STATE for `apply`.
apply [--dry-run]    Trash spam / archive+mark-read the IDs saved by the last fetch,
                     re-query to verify, and print the result lines.

Categories: spam purchases social promotions
"""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

STATE = Path.home() / ".cache" / "cleanup-inbox-mail" / "last.json"
JST = timezone(timedelta(hours=9))
CATS = {
    "spam": ("迷惑メール", "in:spam"),
    "purchases": ("購入", "category:purchases is:unread"),
    "social": ("ソーシャル", "category:social is:unread"),
    "promotions": ("プロモーション", "category:promotions is:unread"),
}
ORDER = list(CATS)
# Gmail permalink per view. Spam is trashed by `apply`, so link where it lands (#trash);
# archived mail leaves the inbox but stays in All Mail (#all). The ID is the message ID
# from +triage (no extra API call); Gmail resolves it to the thread.
GMAIL_URL = "https://mail.google.com/mail/u/0/#{view}/{id}"
VIEW = {"spam": "trash"}


def triage(query):
    out = subprocess.run(
        ["gws", "gmail", "+triage", "--query", query, "--max", "100", "--format", "json"],
        capture_output=True, text=True,
    )
    # Zero hits: exit 0 + non-JSON "No messages found ...". Auth failure: exit 2 +
    # parseable {"error": ...} JSON, which .get("messages", []) would turn into a
    # silent "0 mails" — so check the exit code and error key before trusting it.
    # Parse JSON first so a subject containing "No messages found" can't fake 0 hits.
    try:
        data = json.loads(out.stdout)
    except json.JSONDecodeError:
        data = None
    if data is None and out.returncode == 0 and "No messages found" in out.stdout + out.stderr:
        return []
    if out.returncode != 0 or not isinstance(data, dict) or "error" in data:
        sys.exit(f"gws error ({query}):\n{out.stdout}{out.stderr}")
    return data.get("messages", [])


def jst(date):
    try:
        return parsedate_to_datetime(date).astimezone(JST).strftime("%Y-%m-%d %H:%M")
    except (TypeError, ValueError):
        return date


def sender(raw):
    name = raw.split("<")[0].strip().strip('"').strip()
    return name or raw.strip("<>")


def cell(s):
    return s.replace("|", "\\|").replace("\n", " ")


def fetch_all(cats):
    def run(c):
        return sorted(triage(CATS[c][1]), key=lambda m: jst(m["date"]), reverse=True)

    with ThreadPoolExecutor(len(cats)) as ex:
        return dict(zip(cats, ex.map(run, cats)))


def link(cat, msg_id):
    return f"[開く]({GMAIL_URL.format(view=VIEW.get(cat, 'all'), id=msg_id)})"


def table(cat, msgs):
    if not msgs:
        return ["対象のメールはありません"]
    rows = ["| # | 送信者 | 件名 | 日時 | リンク |", "|---|--------|------|------|--------|"]
    for i, m in enumerate(msgs, 1):
        rows.append(
            f"| {i} | {cell(sender(m['from']))} | {cell(m['subject'])} | {jst(m['date'])} | {link(cat, m['id'])} |"
        )
    return rows


def fetch(cats):
    cats = [c for c in ORDER if c in cats]
    res = fetch_all(cats)
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({c: [m["id"] for m in res[c]] for c in cats}))
    out = []
    if "spam" in cats:
        out += [f"## 削除対象（迷惑メール {len(res['spam'])}件）", ""] + table("spam", res["spam"]) + [""]
    archive = [c for c in cats if c != "spam"]
    if archive:
        out += ["## アーカイブ対象", ""]
        for c in archive:
            out += [f"### {CATS[c][0]}（{len(res[c])}件）", ""] + table(c, res[c]) + [""]
    print("\n".join(out).rstrip())
    print("\nCOUNTS " + " ".join(f"{c}={len(res[c])}" for c in cats))


def gws(args, dry):
    """Run one write; return an error string, or None on success."""
    if dry:
        print("DRY", " ".join(args))
        return None
    out = subprocess.run(["gws", "gmail", "users", "messages", *args], capture_output=True, text=True)
    if out.returncode != 0 or '"error"' in out.stdout:
        return f"{args[0]}: {out.stdout.strip()} {out.stderr.strip()}"
    return None


def apply(dry):
    state = json.loads(STATE.read_text())
    jobs = []
    for c, ids in state.items():
        if not ids:
            continue
        if c == "spam":
            for i in ids:
                jobs.append(["trash", "--params", json.dumps({"userId": "me", "id": i})])
        else:
            jobs.append(["batchModify", "--params", '{"userId":"me"}', "--json",
                         json.dumps({"ids": ids, "removeLabelIds": ["INBOX", "UNREAD"]})])
    with ThreadPoolExecutor(8) as ex:
        errors = [e for e in ex.map(lambda a: gws(a, dry), jobs) if e]
    if dry:
        return
    after = fetch_all(list(state))
    labels = {"spam": "迷惑メール削除", "purchases": "購入アーカイブ",
              "social": "ソーシャルアーカイブ", "promotions": "プロモーションアーカイブ"}
    print("## クリーンアップ完了\n")
    for c in ORDER:
        if c not in state:
            continue
        ids = state[c]
        now = {m["id"] for m in after[c]}
        left = [i for i in ids if i in now]
        new = len(now - set(ids))
        if not ids:
            line = f"- **{CATS[c][0]}**: 対象なし"
        elif left:
            line = f"- **{labels[c]}**: {len(ids) - len(left)}件 ✅ / 失敗 {len(left)}件 ❌ ({', '.join(left)})"
        else:
            line = f"- **{labels[c]}**: {len(ids)}件 ✅"
        if new:
            line += f"（処理中に新着 {new}件、未処理）"
        print(line)
    if errors:
        # The re-query above decides success; these are only to explain any ❌ rows.
        print("\n## gwsエラー\n")
        for e in dict.fromkeys(errors):
            print(f"- {e}")
    STATE.unlink()


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("fetch", "apply"):
        sys.exit(__doc__)
    if sys.argv[1] == "fetch":
        cats = sys.argv[2:] or ORDER
        bad = [c for c in cats if c not in CATS]
        if bad:
            sys.exit(f"unknown category: {bad}")
        fetch(cats)
    else:
        apply("--dry-run" in sys.argv)
