#!/usr/bin/env python3
"""Fetch the authenticated user's recent GitHub PR/Issue comments for style reference.

Usage:
  python3 -B fetch_my_comments.py --repo <owner/repo> [--pr N] [--target-user LOGIN] [--limit 10] [--max-prs 15]

Priority order:
  1. Comments in --pr (PR or Issue number, if given)
  2. Replies to --target-user in recent PRs involving the user (if given)
  3. Other recent PR review replies, review bodies, and issue comments by the user
"""

import argparse
import json
import subprocess
import sys


class GhCommandError(RuntimeError):
    def __init__(self, args, msg):
        super().__init__(f"gh {' '.join(args)}: {msg}")
        self.msg = msg

    @property
    def is_not_found(self):
        return "HTTP 404" in self.msg or "404 Not Found" in self.msg


def run_gh(args):
    proc = subprocess.run(["gh", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        msg = proc.stderr.strip() or proc.stdout.strip() or f"exit {proc.returncode}"
        raise GhCommandError(args, msg)
    return proc.stdout


def gh_json(args, *, ignore_not_found=False):
    try:
        out = run_gh(args).strip()
    except GhCommandError as exc:
        if ignore_not_found and exc.is_not_found:
            return []
        raise
    if not out:
        return []
    return json.loads(out)


def flatten_pages(data):
    return [item for page in data for item in (page if isinstance(page, list) else [page])]


def user_login(obj):
    if not isinstance(obj, dict):
        return ""
    user = obj.get("user")
    return user.get("login", "") if isinstance(user, dict) else ""


def fetch_pr_comments(repo, pr_num, login):
    """Return list of dicts for user's review replies, review bodies, and issue comments on one PR/Issue."""
    results = []

    review_comments = gh_json(
        ["api", "--paginate", "--slurp", f"repos/{repo}/pulls/{pr_num}/comments"],
        ignore_not_found=True,
    )
    flat_review = flatten_pages(review_comments)
    by_id = {c["id"]: c for c in flat_review if isinstance(c, dict) and "id" in c}

    for c in flat_review:
        if not isinstance(c, dict) or user_login(c) != login:
            continue
        reply_to = c.get("in_reply_to_id")
        if reply_to is None:
            continue
        parent = by_id.get(reply_to, {})
        results.append({
            "pr": pr_num,
            "kind": "review_reply",
            "target_user": user_login(parent),
            "created_at": c.get("created_at", ""),
            "html_url": c.get("html_url", ""),
            "body": (c.get("body") or "").strip(),
        })

    reviews = gh_json(
        ["api", "--paginate", "--slurp", f"repos/{repo}/pulls/{pr_num}/reviews"],
        ignore_not_found=True,
    )
    for r in flatten_pages(reviews):
        if not isinstance(r, dict) or user_login(r) != login:
            continue
        body = (r.get("body") or "").strip()
        if not body:
            continue
        results.append({
            "pr": pr_num,
            "kind": "review_body",
            "target_user": "",
            "created_at": r.get("submitted_at", ""),
            "html_url": r.get("html_url", ""),
            "body": body,
        })

    issue_comments = gh_json(["api", "--paginate", "--slurp", f"repos/{repo}/issues/{pr_num}/comments"])
    for c in flatten_pages(issue_comments):
        if not isinstance(c, dict) or user_login(c) != login:
            continue
        results.append({
            "pr": pr_num,
            "kind": "issue_comment",
            "target_user": "",
            "created_at": c.get("created_at", ""),
            "html_url": c.get("html_url", ""),
            "body": (c.get("body") or "").strip(),
        })

    return [r for r in results if r["body"]]


def main():
    parser = argparse.ArgumentParser(description="Fetch authenticated user's recent GitHub PR/Issue comments.")
    parser.add_argument("--repo", required=True, help="Repository in owner/repo format")
    parser.add_argument("--pr", type=int, help="Current PR or Issue number (prioritized first)")
    parser.add_argument("--target-user", default="", help="Reviewer login to prioritize")
    parser.add_argument("--limit", type=int, default=10, help="Max comments to print (default: 10)")
    parser.add_argument("--max-prs", type=int, default=15, help="Max recent PRs to scan (default: 15)")
    args = parser.parse_args()

    if args.limit <= 0 or args.max_prs <= 0:
        sys.exit("Error: --limit and --max-prs must be >= 1")

    target_lower = args.target_user.lower()

    try:
        login = run_gh(["api", "user", "--jq", ".login"]).strip()
        if not login:
            sys.exit("Error: could not resolve authenticated GitHub login")

        pr_numbers = []
        if args.pr is not None:
            pr_numbers.append(args.pr)

        recent = gh_json([
            "pr", "list",
            "--repo", args.repo,
            "--search", "involves:@me sort:updated-desc",
            "--state", "all",
            "--limit", str(args.max_prs),
            "--json", "number",
        ])
        for item in recent:
            num = item.get("number")
            if isinstance(num, int) and num not in pr_numbers:
                pr_numbers.append(num)

        collected = []
        seen_urls = set()
        target_hits = 0
        for num in pr_numbers:
            for item in fetch_pr_comments(args.repo, num, login):
                url = item["html_url"]
                if url and url in seen_urls:
                    continue
                seen_urls.add(url)
                collected.append(item)
                if target_lower and item["target_user"].lower() == target_lower:
                    target_hits += 1
            if not target_lower and len(collected) >= args.limit:
                break
            if target_lower and target_hits >= args.limit:
                break
    except RuntimeError as exc:
        sys.exit(f"Error: {exc}")

    # Sort descending by created_at within priority buckets
    collected.sort(key=lambda x: x["created_at"], reverse=True)
    collected.sort(key=lambda x: (
        0 if (args.pr is not None and x["pr"] == args.pr) else 1,
        0 if (target_lower and x["target_user"].lower() == target_lower) else 1,
    ))

    selected = collected[: args.limit]
    print(f"# login={login} repo={args.repo} total_collected={len(collected)} shown={len(selected)}")
    for item in selected:
        target_info = f" to=@{item['target_user']}" if item["target_user"] else ""
        print(f"#{item['pr']} [{item['kind']}{target_info}] {item['html_url']}")
        print(item["body"])
        print("----")


if __name__ == "__main__":
    main()
