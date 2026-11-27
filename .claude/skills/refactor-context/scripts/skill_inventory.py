#!/usr/bin/env python3
"""Collect skill inventory metrics across skill repositories and Claude Code logs.

Outputs for each skill:
  - description character length (and total across all skills)
  - Claude Code invocation counts from ~/.claude/projects/**/*.jsonl,
    split into manual (<command-name>) and auto (Skill tool_use)
  - references from other skills
  - last updated date (git log, falling back to mtime)

Usage:
  python3 -B skill_inventory.py [--root DIR ...] [--claude-projects-dir DIR] [--json]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

COMMAND_NAME_RE = re.compile(r"<command-name>/?([^<\s]+)</command-name>")
YAML_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$")


def parse_frontmatter(text: str) -> dict[str, str]:
    """Extract top-level scalar fields from YAML frontmatter without external deps."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return {}

    result: dict[str, str] = {}
    i = 1
    while i < end_idx:
        line = lines[i]
        m = YAML_KEY_RE.match(line)
        if not m:
            i += 1
            continue
        key, raw_val = m.group(1), m.group(2).strip()
        if raw_val in ("|", ">", "|-", ">-", "|+", ">+"):
            block_lines: list[str] = []
            i += 1
            while i < end_idx and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                block_lines.append(lines[i].strip())
                i += 1
            joiner = "\n" if raw_val.startswith("|") else " "
            result[key] = joiner.join(block_lines).strip()
            continue
        if len(raw_val) >= 2 and raw_val[0] == raw_val[-1] and raw_val[0] in ('"', "'"):
            val = raw_val[1:-1]
            if raw_val[0] == '"':
                val = val.replace('\\"', '"').replace("\\\\", "\\")
            result[key] = val
        else:
            result[key] = raw_val
        i += 1
    return result


def discover_default_roots() -> list[Path]:
    """Auto-discover dotfiles (from this script) and current workspace if distinct."""
    roots: list[Path] = []
    # <repo>/.claude/skills/refactor-context/scripts/skill_inventory.py -> parents[4] is <repo>
    script_repo = Path(__file__).resolve().parents[4]
    if (script_repo / ".claude" / "skills").is_dir():
        roots.append(script_repo)

    cwd = Path.cwd().resolve()
    if (cwd / ".claude" / "skills").is_dir() and cwd not in roots:
        roots.append(cwd)

    return roots


def collect_skills(roots: list[Path]) -> list[dict[str, Any]]:
    """Scan skill directories under each root (skipping symlinks)."""
    skills: list[dict[str, Any]] = []
    seen_real_dirs: set[Path] = set()

    for root in roots:
        repo_name = root.name
        for rel_parent in (".claude/skills", ".gemini/skills"):
            parent = root / rel_parent
            if not parent.is_dir():
                continue
            for entry in sorted(parent.iterdir()):
                if entry.is_symlink() or not entry.is_dir():
                    continue
                skill_md = entry / "SKILL.md"
                if not skill_md.is_file():
                    continue
                real_dir = entry.resolve()
                if real_dir in seen_real_dirs:
                    continue
                seen_real_dirs.add(real_dir)

                text = skill_md.read_text(encoding="utf-8", errors="replace")
                fm = parse_frontmatter(text)
                name = fm.get("name") or entry.name
                desc = fm.get("description", "")
                dmi = fm.get("disable-model-invocation", "").lower() == "true"

                skills.append(
                    {
                        "repo": repo_name,
                        "root": root,
                        "dir": entry,
                        "skill_md": skill_md,
                        "name": name,
                        "dir_name": entry.name,
                        "description_len": len(desc),
                        "disable_model_invocation": dmi,
                        "manual_count": 0,
                        "auto_count": 0,
                        "referenced_by": [],
                        "last_updated": get_last_updated(root, entry),
                    }
                )
    return skills


def get_last_updated(repo_root: Path, skill_dir: Path) -> str:
    try:
        rel = skill_dir.relative_to(repo_root)
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "log", "-1", "--format=%cs", "--", str(rel)],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        out = proc.stdout.strip()
        if proc.returncode == 0 and out:
            return out
    except (OSError, ValueError, subprocess.TimeoutExpired):
        pass
    try:
        mtime = (skill_dir / "SKILL.md").stat().st_mtime
        return dt.date.fromtimestamp(mtime).isoformat()
    except OSError:
        return "-"


def count_invocations(
    projects_dir: Path, known_names: set[str]
) -> tuple[dict[str, int], dict[str, int], dict[str, Any]]:
    """Count manual (<command-name>) and auto (Skill tool_use) invocations in jsonl logs."""
    manual: dict[str, int] = {name: 0 for name in known_names}
    auto: dict[str, int] = {name: 0 for name in known_names}
    meta: dict[str, Any] = {
        "projects_dir": str(projects_dir),
        "log_files": 0,
        "oldest_date": None,
        "newest_date": None,
    }
    if not projects_dir.is_dir():
        return manual, auto, meta

    mtimes: list[float] = []
    for jsonl_path in projects_dir.rglob("*.jsonl"):
        if not jsonl_path.is_file():
            continue
        meta["log_files"] += 1
        try:
            mtimes.append(jsonl_path.stat().st_mtime)
        except OSError:
            pass
        try:
            with jsonl_path.open("r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if "<command-name>" not in line and '"Skill"' not in line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(obj, dict):
                        continue
                    rec_type = obj.get("type")
                    msg = obj.get("message")
                    if not isinstance(msg, dict):
                        continue
                    content = msg.get("content")

                    if rec_type == "user":
                        texts: list[str] = []
                        if isinstance(content, str):
                            texts.append(content)
                        elif isinstance(content, list):
                            for block in content:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    t = block.get("text")
                                    if isinstance(t, str):
                                        texts.append(t)
                        for text in texts:
                            for m in COMMAND_NAME_RE.finditer(text):
                                cmd = m.group(1)
                                if cmd in manual:
                                    manual[cmd] += 1
                    elif rec_type == "assistant" and isinstance(content, list):
                        for block in content:
                            if (
                                isinstance(block, dict)
                                and block.get("type") == "tool_use"
                                and block.get("name") == "Skill"
                            ):
                                inp = block.get("input")
                                if isinstance(inp, dict):
                                    skill_name = inp.get("skill")
                                    if isinstance(skill_name, str):
                                        skill_name = skill_name.lstrip("/")
                                        if skill_name in auto:
                                            auto[skill_name] += 1
        except OSError:
            continue

    if mtimes:
        meta["oldest_date"] = dt.date.fromtimestamp(min(mtimes)).isoformat()
        meta["newest_date"] = dt.date.fromtimestamp(max(mtimes)).isoformat()
    return manual, auto, meta


def collect_cross_references(skills: list[dict[str, Any]]) -> None:
    """Find mentions of each skill name in other skills' Markdown files."""
    patterns = {
        s["name"]: re.compile(
            rf"(?<![A-Za-z0-9_-]){re.escape(s['name'])}(?![A-Za-z0-9_-])"
        )
        for s in skills
    }
    texts_by_skill: list[tuple[str, str]] = []
    for s in skills:
        parts: list[str] = []
        for md in sorted(s["dir"].rglob("*.md")):
            try:
                parts.append(md.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                continue
        texts_by_skill.append((s["name"], "\n".join(parts)))

    for target in skills:
        tname = target["name"]
        pat = patterns[tname]
        refs: list[str] = []
        for src_name, content in texts_by_skill:
            if src_name == tname:
                continue
            if pat.search(content):
                refs.append(src_name)
        target["referenced_by"] = sorted(set(refs))


def format_markdown(skills: list[dict[str, Any]], meta: dict[str, Any]) -> str:
    total_desc = sum(s["description_len"] for s in skills)
    lines = [
        f"Skills: {len(skills)} | Total description chars: {total_desc}",
        (
            f"Logs: {meta['log_files']} files "
            f"({meta['oldest_date'] or '-'} .. {meta['newest_date'] or '-'}) "
            f"from {meta['projects_dir']}"
        ),
        "",
        "| Repo | Skill | Desc | Manual | Auto | Total | DMI | Referenced By | Last Updated |",
        "|---|---|---:|---:|---:|---:|---|---|---|",
    ]
    for s in sorted(skills, key=lambda x: (x["repo"], x["name"])):
        total = s["manual_count"] + s["auto_count"]
        dmi = "yes" if s["disable_model_invocation"] else ""
        refs = ", ".join(s["referenced_by"]) if s["referenced_by"] else "-"
        lines.append(
            f"| {s['repo']} | {s['name']} | {s['description_len']} | "
            f"{s['manual_count']} | {s['auto_count']} | {total} | "
            f"{dmi} | {refs} | {s['last_updated']} |"
        )
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inventory skills and usage counts.")
    parser.add_argument(
        "--root",
        action="append",
        dest="roots",
        help="Repository root containing .claude/skills (repeatable; defaults to script repo + cwd)",
    )
    parser.add_argument(
        "--claude-projects-dir",
        default=str(Path.home() / ".claude" / "projects"),
        help="Directory holding Claude Code *.jsonl session logs",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    roots = [Path(r).expanduser().resolve() for r in args.roots] if args.roots else discover_default_roots()
    if not roots:
        print("error: no skill repository roots found", file=sys.stderr)
        return 1

    skills = collect_skills(roots)
    known_names = {s["name"] for s in skills}
    manual, auto, meta = count_invocations(Path(args.claude_projects_dir).expanduser(), known_names)
    for s in skills:
        s["manual_count"] = manual.get(s["name"], 0)
        s["auto_count"] = auto.get(s["name"], 0)
    collect_cross_references(skills)

    if args.json:
        payload = {
            "total_skills": len(skills),
            "total_description_chars": sum(s["description_len"] for s in skills),
            "logs": meta,
            "skills": [
                {
                    "repo": s["repo"],
                    "name": s["name"],
                    "description_len": s["description_len"],
                    "disable_model_invocation": s["disable_model_invocation"],
                    "manual_count": s["manual_count"],
                    "auto_count": s["auto_count"],
                    "total_count": s["manual_count"] + s["auto_count"],
                    "referenced_by": s["referenced_by"],
                    "last_updated": s["last_updated"],
                }
                for s in sorted(skills, key=lambda x: (x["repo"], x["name"]))
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(format_markdown(skills, meta))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
