#!/usr/bin/env python3
"""Fetch paginated GitHub PR review comments/threads/review-bodies or resolve a review thread.

Handles full REST pagination (`--paginate --slurp`) and GraphQL cursor pagination
so PRs with >30 comments or >100 review threads never silently drop findings.

Subcommands:
  fetch <url>            Parse PR / review / comment URL and return structured JSON
  resolve <thread_id>    Resolve a GraphQL review thread by node ID

Exit codes:
  0: ok
  1: gh CLI / API error or target ID not found
  2: invalid URL / argument
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from typing import Any

PR_URL_RE = re.compile(
    r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull/(?P<number>\d+)"
    r"(?:/[^#]*)?(?:#(?P<frag>.+))?$"
)
FRAG_DISCUSSION_RE = re.compile(r"^discussion_r(\d+)$")
FRAG_ISSUE_COMMENT_RE = re.compile(r"^issuecomment-(\d+)$")
FRAG_REVIEW_RE = re.compile(r"^pullrequestreview-(\d+)$")

THREADS_QUERY = """
query($o:String!, $r:String!, $n:Int!, $cursor:String) {
  repository(owner:$o, name:$r) {
    pullRequest(number:$n) {
      reviewThreads(first:100, after:$cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          originalLine
          comments(first:50) {
            nodes {
              databaseId
              author { login }
              body
              createdAt
              path
              line
              originalLine
              originalCommit { oid }
              pullRequestReview { databaseId }
            }
          }
        }
      }
    }
  }
}
"""

RESOLVE_MUTATION = """
mutation($id:ID!) {
  resolveReviewThread(input:{threadId:$id}) {
    thread { id isResolved }
  }
}
"""


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def run_gh_json(args: list[str], *, timeout: int = 45) -> tuple[Any, str | None]:
    try:
        proc = subprocess.run(["gh", *args], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as exc:
        return None, str(exc)
    if proc.returncode != 0:
        return None, (proc.stderr or proc.stdout).strip() or f"gh exited {proc.returncode}"
    out = proc.stdout.strip()
    if not out:
        return None, None
    try:
        return json.loads(out), None
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON from gh: {exc}"


def flatten_slurp(data: Any) -> list[dict[str, Any]]:
    if not isinstance(data, list):
        return []
    result: list[dict[str, Any]] = []
    for item in data:
        if isinstance(item, list):
            result.extend(x for x in item if isinstance(x, dict))
        elif isinstance(item, dict):
            result.append(item)
    return result


def fetch_paginated_rest(endpoint: str) -> tuple[list[dict[str, Any]], str | None]:
    data, err = run_gh_json(["api", "--paginate", "--slurp", endpoint])
    if err:
        return [], err
    return flatten_slurp(data), None


def fetch_all_threads(owner: str, repo: str, number: int) -> tuple[list[dict[str, Any]], str | None]:
    threads: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        cmd = [
            "api", "graphql",
            "-F", f"o={owner}",
            "-F", f"r={repo}",
            "-F", f"n={number}",
            "-f", f"query={THREADS_QUERY}",
        ]
        if cursor:
            cmd.extend(["-f", f"cursor={cursor}"])
        data, err = run_gh_json(cmd)
        if err:
            return [], err
        rt = (
            ((data or {}).get("data") or {})
            .get("repository", {})
            .get("pullRequest", {})
            .get("reviewThreads", {})
        )
        nodes = rt.get("nodes") or []
        threads.extend(n for n in nodes if isinstance(n, dict))
        page_info = rt.get("pageInfo") or {}
        if not page_info.get("hasNextPage") or not page_info.get("endCursor"):
            break
        cursor = str(page_info["endCursor"])
    return threads, None


def simplify_thread(t: dict[str, Any]) -> dict[str, Any]:
    comments = []
    for c in ((t.get("comments") or {}).get("nodes") or []):
        if not isinstance(c, dict):
            continue
        comments.append({
            "id": c.get("databaseId"),
            "user": ((c.get("author") or {}).get("login") if isinstance(c.get("author"), dict) else None),
            "path": c.get("path"),
            "line": c.get("line"),
            "original_line": c.get("originalLine"),
            "original_commit_id": ((c.get("originalCommit") or {}).get("oid") if isinstance(c.get("originalCommit"), dict) else None),
            "review_id": ((c.get("pullRequestReview") or {}).get("databaseId") if isinstance(c.get("pullRequestReview"), dict) else None),
            "created_at": c.get("createdAt"),
            "body": c.get("body", ""),
        })
    return {
        "thread_id": t.get("id"),
        "is_resolved": bool(t.get("isResolved")),
        "is_outdated": bool(t.get("isOutdated")),
        "path": t.get("path"),
        "line": t.get("line"),
        "original_line": t.get("originalLine"),
        "comments": comments,
    }


def parse_target_url(url: str) -> dict[str, Any]:
    m = PR_URL_RE.match(url.strip())
    if not m:
        raise ValueError(f"GitHub PR/コメント/レビューURLの形式ではありません: {url!r}")
    owner = m.group("owner")
    repo = m.group("repo")
    number = int(m.group("number"))
    frag = (m.group("frag") or "").strip()

    mode = "pr"
    target_id: int | None = None
    if frag:
        if md := FRAG_DISCUSSION_RE.match(frag):
            mode, target_id = "discussion_comment", int(md.group(1))
        elif mi := FRAG_ISSUE_COMMENT_RE.match(frag):
            mode, target_id = "issue_comment", int(mi.group(1))
        elif mr := FRAG_REVIEW_RE.match(frag):
            mode, target_id = "review", int(mr.group(1))

    return {"owner": owner, "repo": repo, "number": number, "mode": mode, "target_id": target_id}


def cmd_fetch(args: argparse.Namespace) -> int:
    try:
        parsed = parse_target_url(args.url)
    except ValueError as exc:
        emit({"status": "invalid_url", "error": str(exc)})
        return 2

    owner, repo, number = parsed["owner"], parsed["repo"], parsed["number"]
    mode, target_id = parsed["mode"], parsed["target_id"]
    full_repo = f"{owner}/{repo}"

    pr_info, err = run_gh_json([
        "pr", "view", str(number), "--repo", full_repo,
        "--json", "title,body,state,author,headRefName,baseRefName,url",
    ])
    if err:
        emit({"status": "error", "step": "pr_view", "error": err})
        return 1

    threads_raw, err = fetch_all_threads(owner, repo, number)
    if err:
        emit({"status": "error", "step": "review_threads", "error": err})
        return 1
    threads = [simplify_thread(t) for t in threads_raw]

    issue_comments_raw, err = fetch_paginated_rest(f"repos/{full_repo}/issues/{number}/comments")
    if err:
        emit({"status": "error", "step": "issue_comments", "error": err})
        return 1
    issue_comments = [
        {
            "id": c.get("id"),
            "user": (c.get("user") or {}).get("login"),
            "created_at": c.get("created_at"),
            "body": c.get("body", ""),
        }
        for c in issue_comments_raw
    ]

    reviews_raw, err = fetch_paginated_rest(f"repos/{full_repo}/pulls/{number}/reviews")
    if err:
        emit({"status": "error", "step": "reviews", "error": err})
        return 1
    reviews = [
        {
            "id": r.get("id"),
            "user": (r.get("user") or {}).get("login"),
            "state": r.get("state"),
            "submitted_at": r.get("submitted_at"),
            "commit_id": r.get("commit_id"),
            "body": r.get("body", ""),
        }
        for r in reviews_raw
    ]

    result: dict[str, Any] = {
        "status": "ok",
        "mode": mode,
        "owner": owner,
        "repo": repo,
        "number": number,
        "target_id": target_id,
        "pr": pr_info,
    }

    if mode == "discussion_comment":
        matched_thread = next(
            (t for t in threads if any(c.get("id") == target_id for c in t["comments"])),
            None,
        )
        if matched_thread is None:
            emit({"status": "not_found", "mode": mode, "target_id": target_id, "error": "指定コメントIDが見つかりません"})
            return 1
        result["thread"] = matched_thread
        result["target_comment"] = next(c for c in matched_thread["comments"] if c.get("id") == target_id)
    elif mode == "issue_comment":
        matched = next((c for c in issue_comments if c.get("id") == target_id), None)
        if matched is None:
            emit({"status": "not_found", "mode": mode, "target_id": target_id, "error": "指定issue comment IDが見つかりません"})
            return 1
        result["target_comment"] = matched
        result["issue_comments"] = issue_comments
    elif mode == "review":
        matched_review = next((r for r in reviews if r.get("id") == target_id), None)
        if matched_review is None:
            emit({"status": "not_found", "mode": mode, "target_id": target_id, "error": "指定review IDが見つかりません"})
            return 1
        result["review"] = matched_review
        result["threads"] = [
            t for t in threads if any(c.get("review_id") == target_id for c in t["comments"])
        ]
        result["issue_comments"] = issue_comments
    else:
        result["unresolved_threads"] = [t for t in threads if not t["is_resolved"]]
        result["resolved_thread_count"] = sum(1 for t in threads if t["is_resolved"])
        result["reviews_with_body"] = [r for r in reviews if (r.get("body") or "").strip()]
        result["issue_comments"] = issue_comments

    emit(result)
    return 0


def cmd_resolve(args: argparse.Namespace) -> int:
    tid = args.thread_id.strip()
    if not tid:
        emit({"status": "invalid_argument", "error": "thread_id が空です"})
        return 2
    data, err = run_gh_json([
        "api", "graphql",
        "-F", f"id={tid}",
        "-f", f"query={RESOLVE_MUTATION}",
    ])
    if err:
        emit({"status": "error", "thread_id": tid, "error": err})
        return 1
    thread = (((data or {}).get("data") or {}).get("resolveReviewThread") or {}).get("thread") or {}
    if not thread.get("isResolved"):
        emit({"status": "error", "thread_id": tid, "error": "resolveReviewThread did not confirm isResolved=true", "raw": data})
        return 1
    emit({"status": "resolved", "thread_id": thread.get("id", tid), "is_resolved": True})
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="GitHub PR review comments fetcher & thread resolver")
    sub = ap.add_subparsers(dest="command", required=True)

    p_fetch = sub.add_parser("fetch", help="Fetch PR/review/comment details with full pagination")
    p_fetch.add_argument("url", help="GitHub PR, review (#pullrequestreview-...), or comment (#discussion_r... / #issuecomment-...) URL")
    p_fetch.set_defaults(func=cmd_fetch)

    p_res = sub.add_parser("resolve", help="Resolve a review thread by GraphQL node ID")
    p_res.add_argument("thread_id", help="GraphQL thread node ID (e.g. PRRT_...)")
    p_res.set_defaults(func=cmd_resolve)

    return ap


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
