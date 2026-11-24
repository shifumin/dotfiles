#!/usr/bin/env python3
"""Gmail CLI helper wrapping `gws gmail` with JST formatting, Base64 decoding,
chunked batchModify, and per-ID trash reporting.

Never runs `gws auth logout` or `gws auth login`; exits 2 on auth errors.

Exit codes:
  0: success
  1: CLI/API or partial batch error
  2: auth error or invalid arguments
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import email.utils
import html
from html.parser import HTMLParser
import json
import re
import shutil
import subprocess
import sys
from typing import Any

JST = dt.timezone(dt.timedelta(hours=9))
GWS_TIMEOUT_SEC = 60
BATCH_CHUNK_SIZE = 100

LABEL_JA = {
    "INBOX": "受信トレイ",
    "SENT": "送信済み",
    "DRAFT": "下書き",
    "TRASH": "ゴミ箱",
    "SPAM": "迷惑メール",
    "UNREAD": "未読",
    "STARRED": "スター付き",
    "IMPORTANT": "重要",
    "CATEGORY_PERSONAL": "メイン",
    "CATEGORY_SOCIAL": "ソーシャル",
    "CATEGORY_PROMOTIONS": "プロモーション",
    "CATEGORY_UPDATES": "新着",
    "CATEGORY_FORUMS": "フォーラム",
}

AUTH_ERROR_MARKERS = (
    "Failed to get token",
    "insufficientPermissions",
    "ACCESS_TOKEN_SCOPE_INSUFFICIENT",
    "invalid_grant",
    "UNAUTHENTICATED",
    "401 Unauthorized",
    "token expired",
)


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style"):
            self._skip += 1
        elif tag in ("br", "p", "div", "li", "tr"):
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style") and self._skip > 0:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if self._skip == 0:
            self._parts.append(data)

    def get_text(self) -> str:
        text = html.unescape("".join(self._parts))
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def gws_cmd(args: list[str]) -> list[str]:
    if shutil.which("gws"):
        return ["gws", *args]
    return ["mise", "exec", "--", "gws", *args]


def is_auth_error(text: str) -> bool:
    lower = text.lower()
    if any(m.lower() in lower for m in AUTH_ERROR_MARKERS):
        return True
    if "403" in text and ("permission" in lower or "scope" in lower or "auth" in lower):
        return True
    return False


def run_gws(args: list[str], *, allow_no_messages_text: bool = False) -> tuple[Any | None, int]:
    try:
        proc = subprocess.run(
            gws_cmd(args),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=GWS_TIMEOUT_SEC,
        )
    except FileNotFoundError:
        print("ERROR: gws コマンドが見つかりません", file=sys.stderr)
        return None, 1
    except subprocess.TimeoutExpired:
        print(f"ERROR: gws コマンドが {GWS_TIMEOUT_SEC} 秒でタイムアウトしました", file=sys.stderr)
        return None, 1

    stdout = proc.stdout.strip()
    stderr = proc.stderr.strip()
    combined = "\n".join(p for p in (stdout, stderr) if p)

    # Parse JSON first so error payloads are caught even if returncode is 0 or 2.
    parsed: Any = None
    json_ok = False
    if stdout:
        try:
            parsed = json.loads(stdout)
            json_ok = True
        except json.JSONDecodeError:
            pass

    if json_ok and isinstance(parsed, dict) and "error" in parsed:
        err_text = json.dumps(parsed["error"], ensure_ascii=False)
        if is_auth_error(err_text) or proc.returncode == 2:
            print(f"AUTH_ERROR: {err_text}", file=sys.stderr)
            return None, 2
        print(f"ERROR: API エラー: {err_text}", file=sys.stderr)
        return None, 1

    if is_auth_error(combined):
        print(f"AUTH_ERROR: 認証エラーです（自動再認証は行いません）:\n{combined[-500:]}", file=sys.stderr)
        return None, 2

    if proc.returncode != 0:
        print(f"ERROR: gws 実行に失敗しました (exit {proc.returncode}):\n{combined[-500:]}", file=sys.stderr)
        return None, 1

    if not stdout:
        return None, 0

    if json_ok:
        return parsed, 0

    if allow_no_messages_text and "no messages" in stdout.lower():
        return {"messages": [], "resultSizeEstimate": 0}, 0

    print(f"ERROR: gws 出力の JSON パースに失敗しました:\n{stdout[-300:]}", file=sys.stderr)
    return None, 1


def format_jst(raw_date: str) -> str:
    if not raw_date:
        return "-"
    try:
        parsed = email.utils.parsedate_to_datetime(raw_date)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed.astimezone(JST).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return raw_date.strip()


def translate_labels(label_ids: list[str] | None) -> list[str]:
    return [LABEL_JA.get(lid, lid) for lid in (label_ids or [])]


def decode_b64url(data: str) -> str:
    pad = "=" * (-len(data) % 4)
    raw = base64.urlsafe_b64decode(data + pad)
    return raw.decode("utf-8", errors="replace")


def extract_body_and_attachments(payload: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    plain_parts: list[str] = []
    html_parts: list[str] = []
    attachments: list[dict[str, Any]] = []

    def walk(part: dict[str, Any]) -> None:
        filename = (part.get("filename") or "").strip()
        mime = (part.get("mimeType") or "").lower()
        body = part.get("body") or {}
        if filename:
            attachments.append({
                "filename": filename,
                "mimeType": mime or "application/octet-stream",
                "size": int(body.get("size") or 0),
            })
        elif body.get("data"):
            decoded = decode_b64url(body["data"])
            if mime == "text/plain":
                plain_parts.append(decoded)
            elif mime == "text/html":
                html_parts.append(decoded)
        for child in part.get("parts") or []:
            if isinstance(child, dict):
                walk(child)

    walk(payload)
    if plain_parts:
        text = "\n".join(p.strip() for p in plain_parts if p.strip()).strip()
    elif html_parts:
        parser = _TextExtractor()
        parser.feed("\n".join(html_parts))
        text = parser.get_text()
    else:
        text = ""
    return text, attachments


def format_size(num_bytes: int) -> str:
    if num_bytes >= 1024 * 1024:
        return f"{num_bytes / (1024 * 1024):.1f} MB"
    if num_bytes >= 1024:
        return f"{num_bytes / 1024:.1f} KB"
    return f"{num_bytes} B"


def escape_cell(text: str) -> str:
    return re.sub(r"[\r\n]+", " ", text).replace("|", r"\|").strip()


def cmd_search(args: argparse.Namespace) -> int:
    if args.max < 1:
        print("ERROR: --max は 1 以上を指定してください", file=sys.stderr)
        return 2

    cmd = ["gmail", "+triage", "--query", args.query, "--max", str(args.max), "--format", "json"]
    if args.labels:
        cmd.append("--labels")

    data, code = run_gws(cmd, allow_no_messages_text=True)
    if code != 0:
        return code

    messages = (data or {}).get("messages") or []
    estimate = (data or {}).get("resultSizeEstimate")

    normalized: list[dict[str, Any]] = []
    for msg in messages:
        labels_raw = msg.get("labels") or msg.get("labelIds") or []
        normalized.append({
            "id": msg.get("id", ""),
            "from": msg.get("from", ""),
            "subject": msg.get("subject", "(件名なし)") or "(件名なし)",
            "date": format_jst(msg.get("date", "")),
            "labels": translate_labels(labels_raw),
        })

    if args.format == "json":
        print(json.dumps({
            "query": args.query,
            "count": len(normalized),
            "resultSizeEstimate": estimate,
            "ids": [m["id"] for m in normalized if m["id"]],
            "messages": normalized,
        }, ensure_ascii=False, indent=2))
        return 0

    if args.format == "table":
        if not normalized:
            print("対象のメールはありません。")
            return 0
        heading = args.heading or f"対象メール一覧（{len(normalized)}件）"
        print(f"## {heading}\n")
        print("| # | 送信者 | 件名 | 日時 | ID |")
        print("|---:|---|---|---|---|")
        for idx, m in enumerate(normalized, start=1):
            print(f"| {idx} | {escape_cell(m['from'])} | {escape_cell(m['subject'])} | {m['date']} | `{m['id']}` |")
        if isinstance(estimate, int) and estimate > len(normalized):
            print(f"\n（全 {estimate} 件中、最新 {len(normalized)} 件を表示）")
        return 0

    # markdown (default search output)
    if not normalized:
        print("該当するメールが見つかりませんでした")
        return 0
    print(f"## メール検索結果（{len(normalized)}件）\n")
    print(f"検索クエリ: `{args.query}`\n")
    for idx, m in enumerate(normalized, start=1):
        print(f"### {idx}. {m['subject']}")
        print(f"- **From**: {m['from']}")
        print(f"- **Date**: {m['date']}")
        print(f"- **ID**: `{m['id']}`")
        if args.labels and m["labels"]:
            print(f"- **Labels**: {', '.join(m['labels'])}")
        print("\n---")
    if isinstance(estimate, int) and estimate > len(normalized):
        print(f"\n（全 {estimate} 件中、最新 {len(normalized)} 件を表示）")
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    params = json.dumps({"userId": "me", "id": args.message_id}, ensure_ascii=False)
    data, code = run_gws(["gmail", "users", "messages", "get", "--params", params, "--format", "json"])
    if code != 0:
        return code
    if not isinstance(data, dict):
        print("ERROR: メッセージの取得結果が空です", file=sys.stderr)
        return 1

    payload = data.get("payload") or {}
    headers = {h.get("name", "").lower(): h.get("value", "") for h in (payload.get("headers") or []) if isinstance(h, dict)}
    body, attachments = extract_body_and_attachments(payload)
    if args.max_body > 0 and len(body) > args.max_body:
        body = body[: args.max_body] + "\n...(省略)"

    labels_ja = translate_labels(data.get("labelIds"))

    print("## メール詳細\n")
    print(f"- **件名**: {headers.get('subject') or '(件名なし)'}")
    print(f"- **From**: {headers.get('from') or '-'}")
    print(f"- **To**: {headers.get('to') or '-'}")
    print(f"- **Date**: {format_jst(headers.get('date', ''))}")
    print(f"- **Labels**: {', '.join(labels_ja) if labels_ja else '-'}")
    print("\n### 本文\n")
    print(body if body else "(本文なし)")

    if attachments:
        print(f"\n### 添付ファイル（{len(attachments)}件）\n")
        print("| ファイル名 | 種類 | サイズ |")
        print("|---|---|---|")
        for att in attachments:
            print(f"| {escape_cell(att['filename'])} | {att['mimeType']} | {format_size(att['size'])} |")
    return 0


def cmd_trash(args: argparse.Namespace) -> int:
    ids = [i.strip() for i in args.ids if i.strip()]
    if not ids:
        print("ERROR: 対象メッセージ ID を 1 件以上指定してください", file=sys.stderr)
        return 2

    ok = 0
    failed: list[str] = []
    for mid in ids:
        params = json.dumps({"userId": "me", "id": mid}, ensure_ascii=False)
        _, code = run_gws(["gmail", "users", "messages", "trash", "--params", params, "--format", "json"])
        if code == 2:
            return 2
        if code == 0:
            ok += 1
        else:
            failed.append(mid)

    if not failed:
        print("## ゴミ箱に移動完了\n")
        print(f"- **対象件数**: {len(ids)}件")
        print(f"- **処理成功**: {ok}件")
        print("- **結果**: 成功")
        return 0

    print("## ゴミ箱に移動結果\n")
    print(f"- **対象件数**: {len(ids)}件")
    print(f"- **処理成功**: {ok}件")
    print(f"- **失敗**: {len(failed)}件")
    print(f"- **失敗ID**: {', '.join(failed)}")
    return 1


def cmd_modify(args: argparse.Namespace) -> int:
    ids = [i.strip() for i in args.ids if i.strip()]
    if not ids:
        print("ERROR: --ids を 1 件以上指定してください", file=sys.stderr)
        return 2
    if not args.add and not args.remove:
        print("ERROR: --add または --remove の少なくとも一方を指定してください", file=sys.stderr)
        return 2

    ok = 0
    failed_ids: list[str] = []
    for start in range(0, len(ids), BATCH_CHUNK_SIZE):
        chunk = ids[start : start + BATCH_CHUNK_SIZE]
        body: dict[str, Any] = {"ids": chunk}
        if args.add:
            body["addLabelIds"] = args.add
        if args.remove:
            body["removeLabelIds"] = args.remove
        _, code = run_gws([
            "gmail", "users", "messages", "batchModify",
            "--params", json.dumps({"userId": "me"}),
            "--json", json.dumps(body, ensure_ascii=False),
        ])
        if code == 2:
            return 2
        if code == 0:
            ok += len(chunk)
        else:
            failed_ids.extend(chunk)

    op = args.operation_name or "ラベル変更"
    if not failed_ids:
        print(f"## {op}完了\n")
        print(f"- **対象件数**: {len(ids)}件")
        print(f"- **処理成功**: {ok}件")
        print("- **結果**: 成功")
        return 0

    print(f"## {op}結果\n")
    print(f"- **対象件数**: {len(ids)}件")
    print(f"- **処理成功**: {ok}件")
    print(f"- **失敗**: {len(failed_ids)}件")
    print(f"- **失敗ID**: {', '.join(failed_ids)}")
    return 1


def cmd_auth_status(_args: argparse.Namespace) -> int:
    data, code = run_gws(["auth", "status"])
    if code != 0:
        return code
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Gmail CLI wrapper using gws.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="Search messages via +triage")
    p_search.add_argument("--query", required=True)
    p_search.add_argument("--max", type=int, default=20)
    p_search.add_argument("--labels", action="store_true")
    p_search.add_argument("--format", choices=("markdown", "table", "json"), default="markdown")
    p_search.add_argument("--heading", default=None)
    p_search.set_defaults(func=cmd_search)

    p_get = sub.add_parser("get", help="Fetch and decode a message by ID")
    p_get.add_argument("message_id")
    p_get.add_argument("--max-body", type=int, default=0, help="Truncate body to N chars (0=full)")
    p_get.set_defaults(func=cmd_get)

    p_trash = sub.add_parser("trash", help="Move messages to Trash one by one with reporting")
    p_trash.add_argument("ids", nargs="+")
    p_trash.set_defaults(func=cmd_trash)

    p_mod = sub.add_parser("modify", help="Batch-modify labels in chunks of 100")
    p_mod.add_argument("--ids", nargs="+", required=True)
    p_mod.add_argument("--add", action="append", default=[])
    p_mod.add_argument("--remove", action="append", default=[])
    p_mod.add_argument("--operation-name", default="ラベル変更")
    p_mod.set_defaults(func=cmd_modify)

    p_auth = sub.add_parser("auth-status", help="Read-only gws auth status check")
    p_auth.set_defaults(func=cmd_auth_status)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
