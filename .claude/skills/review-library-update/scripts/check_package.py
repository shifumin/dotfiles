#!/usr/bin/env python3
"""Package metadata, supply-chain diff, and GitHub Advisory checker for library update PRs.

Subcommands:
  npm        Compare old/new npm package metadata (age, publisher, maintainers, install scripts, provenance)
  rubygems   Fetch RubyGems metadata and release age
  advisories Query GitHub Advisory Database with URL-safe params and compare old vs new versions

Exit codes:
  0: ok
  1: upstream CLI / network error
  2: invalid argument
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

INSTALL_SCRIPT_KEYS = ("preinstall", "install", "postinstall")


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def parse_iso_utc(raw: str | None) -> dt.datetime | None:
    if not raw:
        return None
    try:
        parsed = dt.datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return None


def calc_age_days(created_iso: str | None, now: dt.datetime | None = None) -> float | None:
    ts = parse_iso_utc(created_iso)
    if ts is None:
        return None
    ref = now or dt.datetime.now(dt.timezone.utc)
    return round((ref - ts).total_seconds() / 86400.0, 2)


def npm_cmd_prefix() -> list[str]:
    if shutil.which("mise"):
        return ["mise", "exec", "--", "npm"]
    return ["npm"]


def run_json_cmd(cmd: list[str], *, timeout: int = 45) -> tuple[Any, str | None]:
    try:
        proc = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as exc:
        return None, str(exc)
    if proc.returncode != 0:
        return None, (proc.stderr or proc.stdout).strip() or f"exit {proc.returncode}"
    out = proc.stdout.strip()
    if not out:
        return None, None
    try:
        return json.loads(out), None
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON from {cmd[0]}: {exc}"


def normalize_maintainers(raw: Any) -> list[str]:
    if not raw:
        return []
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list):
        result: list[str] = []
        for item in raw:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict):
                name = item.get("name", "")
                email = item.get("email", "")
                result.append(f"{name} <{email}>".strip() if email else name)
        return sorted(set(x for x in result if x))
    return []


def extract_npm_user(raw: Any) -> str | None:
    if isinstance(raw, dict):
        name = raw.get("name", "")
        email = raw.get("email", "")
        return f"{name} <{email}>".strip() if email else (name or None)
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    return None


def extract_install_scripts(scripts: Any) -> dict[str, str]:
    if not isinstance(scripts, dict):
        return {}
    return {k: str(scripts[k]) for k in INSTALL_SCRIPT_KEYS if k in scripts and scripts[k]}


def cmd_npm(args: argparse.Namespace) -> int:
    prefix = npm_cmd_prefix()
    pkg = args.package.strip()
    new_spec = f"{pkg}@{args.new}" if args.new else pkg
    new_data, err = run_json_cmd([*prefix, "view", new_spec, "--json"])
    if err or not isinstance(new_data, dict):
        emit({"status": "error", "package": pkg, "error": err or "unexpected npm view output"})
        return 1

    old_data: dict[str, Any] | None = None
    old_err: str | None = None
    if args.old:
        raw_old, old_err = run_json_cmd([*prefix, "view", f"{pkg}@{args.old}", "--json"])
        if isinstance(raw_old, dict):
            old_data = raw_old

    # `time` map lives on package-level view (without @version for some registries)
    time_map = new_data.get("time") if isinstance(new_data.get("time"), dict) else None
    if time_map is None:
        raw_time, _ = run_json_cmd([*prefix, "view", pkg, "time", "--json"])
        if isinstance(raw_time, dict):
            time_map = raw_time

    new_ver = args.new or str(new_data.get("version", ""))
    published_at = time_map.get(new_ver) if isinstance(time_map, dict) else None
    age_days = calc_age_days(published_at)

    new_user = extract_npm_user(new_data.get("_npmUser"))
    old_user = extract_npm_user(old_data.get("_npmUser")) if old_data else None
    new_maintainers = normalize_maintainers(new_data.get("maintainers"))
    old_maintainers = normalize_maintainers(old_data.get("maintainers")) if old_data else []
    new_scripts = extract_install_scripts(new_data.get("scripts"))
    old_scripts = extract_install_scripts(old_data.get("scripts")) if old_data else {}
    new_att = bool((new_data.get("dist") or {}).get("attestations"))
    old_att = bool((old_data.get("dist") or {}).get("attestations")) if old_data else None

    repo = new_data.get("repository")
    repo_url = repo.get("url") if isinstance(repo, dict) else (repo if isinstance(repo, str) else None)

    signals: list[str] = []
    if age_days is not None and age_days < 3.0:
        signals.append(f"recent_release ({age_days}d)")
    if old_data is not None:
        if old_user and new_user and old_user != new_user:
            signals.append(f"publisher_changed ({old_user} -> {new_user})")
        added_m = sorted(set(new_maintainers) - set(old_maintainers))
        removed_m = sorted(set(old_maintainers) - set(new_maintainers))
        if added_m or removed_m:
            signals.append(f"maintainers_changed (+{len(added_m)}/-{len(removed_m)})")
        added_scripts = {k: v for k, v in new_scripts.items() if k not in old_scripts or old_scripts[k] != v}
        if added_scripts:
            signals.append(f"install_scripts_added_or_changed ({', '.join(added_scripts)})")
        if old_att is True and not new_att:
            signals.append("provenance_lost")
    elif new_scripts:
        signals.append(f"has_install_scripts ({', '.join(new_scripts)})")

    emit({
        "status": "ok",
        "ecosystem": "npm",
        "package": pkg,
        "old_version": args.old,
        "new_version": new_ver,
        "repository_url": repo_url,
        "published_at": published_at,
        "age_days": age_days,
        "engines": new_data.get("engines"),
        "peerDependencies": new_data.get("peerDependencies"),
        "publisher": {"old": old_user, "new": new_user},
        "maintainers": {
            "added": sorted(set(new_maintainers) - set(old_maintainers)) if old_data else [],
            "removed": sorted(set(old_maintainers) - set(new_maintainers)) if old_data else [],
            "new_count": len(new_maintainers),
        },
        "install_scripts": {"old": old_scripts, "new": new_scripts},
        "provenance": {"old": old_att, "new": new_att},
        "signals": signals,
        "old_fetch_error": old_err,
    })
    return 0


def fetch_http_json(url: str, *, timeout: int = 20) -> tuple[Any, str | None]:
    req = urllib.request.Request(url, headers={"User-Agent": "review-library-update/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return None, str(exc)


def cmd_rubygems(args: argparse.Namespace) -> int:
    gem = urllib.parse.quote(args.gem.strip(), safe="")
    base = args.api_base.rstrip("/")
    info, err = fetch_http_json(f"{base}/api/v1/gems/{gem}.json")
    if err or not isinstance(info, dict):
        emit({"status": "error", "gem": args.gem, "error": err or "unexpected RubyGems response"})
        return 1

    versions, ver_err = fetch_http_json(f"{base}/api/v1/versions/{gem}.json")
    ver_by_num: dict[str, dict[str, Any]] = {}
    if isinstance(versions, list):
        for v in versions:
            if isinstance(v, dict) and v.get("number"):
                # Prefer ruby platform when multiple platform builds exist
                num = str(v["number"])
                if num not in ver_by_num or v.get("platform") == "ruby":
                    ver_by_num[num] = v

    new_ver = args.new or str(info.get("version", ""))
    new_meta = ver_by_num.get(new_ver)
    old_meta = ver_by_num.get(args.old) if args.old else None

    published_at = new_meta.get("created_at") if new_meta else None
    age_days = calc_age_days(published_at)

    signals: list[str] = []
    if age_days is not None and age_days < 3.0:
        signals.append(f"recent_release ({age_days}d)")
    if old_meta and new_meta and old_meta.get("authors") != new_meta.get("authors"):
        signals.append("authors_changed")

    emit({
        "status": "ok",
        "ecosystem": "rubygems",
        "gem": args.gem,
        "old_version": args.old,
        "new_version": new_ver,
        "source_code_uri": info.get("source_code_uri"),
        "changelog_uri": info.get("changelog_uri"),
        "homepage_uri": info.get("homepage_uri"),
        "required_ruby_version": (new_meta or {}).get("ruby_version") or info.get("metadata", {}).get("required_ruby_version"),
        "published_at": published_at,
        "age_days": age_days,
        "authors": {
            "old": old_meta.get("authors") if old_meta else None,
            "new": new_meta.get("authors") if new_meta else info.get("authors"),
        },
        "sha": new_meta.get("sha") if new_meta else info.get("sha"),
        "signals": signals,
        "versions_fetch_error": ver_err,
    })
    return 0


def query_advisories(ecosystem: str, package: str, version: str) -> tuple[list[dict[str, Any]], str | None]:
    affects = f"{package}@{version}"
    data, err = run_json_cmd([
        "gh", "api", "--method", "GET", "/advisories",
        "-f", f"ecosystem={ecosystem}",
        "-f", f"affects={affects}",
    ])
    if err:
        return [], err
    if not isinstance(data, list):
        return [], None
    out: list[dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        out.append({
            "ghsa_id": item.get("ghsa_id"),
            "cve_id": item.get("cve_id"),
            "severity": item.get("severity"),
            "summary": item.get("summary"),
            "html_url": item.get("html_url"),
        })
    return out, None


def cmd_advisories(args: argparse.Namespace) -> int:
    if not args.old and not args.new:
        emit({"status": "invalid_argument", "error": "--old または --new の少なくとも一方を指定してください"})
        return 2

    old_list: list[dict[str, Any]] = []
    new_list: list[dict[str, Any]] = []
    errors: dict[str, str] = {}

    if args.old:
        old_list, err = query_advisories(args.ecosystem, args.package, args.old)
        if err:
            errors["old"] = err
    if args.new:
        new_list, err = query_advisories(args.ecosystem, args.package, args.new)
        if err:
            errors["new"] = err

    if errors and not old_list and not new_list:
        emit({"status": "error", "errors": errors})
        return 1

    old_ids = {a["ghsa_id"] for a in old_list if a.get("ghsa_id")}
    new_ids = {a["ghsa_id"] for a in new_list if a.get("ghsa_id")}

    fixed = [a for a in old_list if a.get("ghsa_id") not in new_ids]
    remaining = [a for a in new_list if a.get("ghsa_id") in old_ids]
    only_new = [a for a in new_list if a.get("ghsa_id") not in old_ids]

    emit({
        "status": "ok",
        "ecosystem": args.ecosystem,
        "package": args.package,
        "old_version": args.old,
        "new_version": args.new,
        "fixed_by_update": fixed,
        "remaining_in_new": remaining,
        "new_version_only": only_new,
        "errors": errors or None,
    })
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Library update package & advisory checker")
    sub = ap.add_subparsers(dest="command", required=True)

    p_npm = sub.add_parser("npm", help="Compare old/new npm package metadata")
    p_npm.add_argument("package", help="npm package name (scoped supported)")
    p_npm.add_argument("--old", help="Previous version")
    p_npm.add_argument("--new", help="Updated version")
    p_npm.set_defaults(func=cmd_npm)

    p_gem = sub.add_parser("rubygems", help="Fetch RubyGems metadata and release age")
    p_gem.add_argument("gem", help="Ruby gem name")
    p_gem.add_argument("--old", help="Previous version")
    p_gem.add_argument("--new", help="Updated version")
    p_gem.add_argument("--api-base", default="https://rubygems.org", help=argparse.SUPPRESS)
    p_gem.set_defaults(func=cmd_rubygems)

    p_adv = sub.add_parser("advisories", help="Query GitHub Advisory Database for old/new versions")
    p_adv.add_argument("--ecosystem", required=True, choices=("npm", "rubygems", "actions", "pip", "go", "rust", "composer", "maven", "nuget"))
    p_adv.add_argument("--package", required=True, help="Package name")
    p_adv.add_argument("--old", help="Previous version")
    p_adv.add_argument("--new", help="Updated version")
    p_adv.set_defaults(func=cmd_advisories)

    return ap


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
