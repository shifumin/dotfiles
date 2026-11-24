#!/usr/bin/env python3
"""Fetch the authenticated user's recent GitHub PR comments for style reference.

Usage:
  python3 -B fetch_my_comments.py --repo <owner/repo> [--pr N] [--target-user LOGIN] [--limit 10] [--max-prs 15]

Priority order:
  1. Comments in --pr (if given)
  2. Replies to --target-user in recent PRs (if given)
  3. Other recent PR review replies and issue comments by the authenticated user
"""

import argparse
import json
import subprocess
import sys


def run_gh(args):
    proc = subprocess.run(["gh", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        msg = proc.stderr.strip() or proc.stdout.strip() or f"exit {proc.returncode}"
        raise RuntimeError(f"gh {' '.join(args)}: {msg}")
    return proc.stdout


def gh_json(args):
    out = run_gh(args).strip()
    if not out:
        return []
    return json.loads(out)


def fetch_pr_comments(repo, pr_num, login):
    """Return list of dicts for user's review replies and issue comments on one PR."""
    results = []

    review_comments = gh_json(["api", "--paginate", "--slurp", f"repos/{repo}/pulls/{pr_num}/comments"])
    flat_review = [c for page in review_comments for c in (page if isinstance(page, list) else [page])]
    by_id = {c["id"]: c for c in flat_review if isinstance(c, dict) and "id" in c}

    for c in flat_review:
        if not isinstance(c, dict):
            continue
        if c.get("user", {}).get("login") != login:
            continue
        reply_to = c.get("in_reply_to_id")
        if reply_to is None:
            continue
        parent = by_id.get(reply_to, {})
        target = parent.get("user", {}).get("login", "")
        results.append({
            "pr": pr_num,
            "kind": "review_reply",
            "target_user": target,
            "created_at": c.get("created_at", ""),
            "html_url": c.get("html_url", ""),
            "body": (c.get("body") or "").strip(),
        })

    issue_comments = gh_json(["api", "--paginate", "--slurp", f"repos/{repo}/issues/{pr_num}/comments"])
    flat_issue = [c for page in issue_comments for c in (page if isinstance(page, list) else [page])]
    for c in flat_issue:
        if not isinstance(c, dict):
            continue
        if c.get("user", {}).get("login") != login:
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
    parser = argparse.ArgumentParser(description="Fetch authenticated user's recent GitHub PR comments.")
    parser.add_argument("--repo", required=True, help="Repository in owner/repo format")
    parser.add_argument("--pr", type=int, help="Current PR number (prioritized first)")
    parser.add_argument("--target-user", default="", help="Reviewer login to prioritize")
    parser.add_argument("--limit", type=int, default=10, help="Max comments to print (default: 10)")
    parser.add_argument("--max-prs", type=int, default=15, help="Max authored PRs to scan (default: 15)")
    args = parser.parse_args()

    if args.limit <= 0 or args.max_prs <= 0:
        sys.exit("Error: --limit and --max-prs must be >= 1")

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
            "--author", "@me",
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
        for num in pr_numbers:
            for item in fetch_pr_comments(args.repo, num, login):
                url = item["html_url"]
                if url and url in seen_urls:
                    continue
                seen_urls.add(url)
                collected.append(item)
            # Stop early when we have enough samples (and if target-user is set,
            # gather a small buffer before sorting by priority).
            if not args.target_user and len(collected) >= args.limit:
                break
            if args.target_user and len(collected) >= args.limit * 2:
                break
    except RuntimeError as exc:
        sys.exit(f"Error: {exc}")

    target_lower = args.target_user.lower()

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
