#!/usr/bin/env python3
"""Scan agent context documents for changes and static contamination signals.

Usage:
  python3 -B scan_context.py [--workspace DIR] [--extra-root DIR ...]
                             [--since YYYY-MM-DD | --all]
                             [--state-file PATH] [--mark-done] [--json]

Scans:
  - Global ~/.claude/ and ~/.gemini/ instructions, rules, output-styles, and skills
  - Workspace (and repo roots under --extra-root): AGENTS.md, CLAUDE.md, CLAUDE.local.md,
    .claude/{rules,agent_docs,skills,commands,output-styles}, .gemini/skills
  - Checks ~/.claude/projects/*/memory/ for index/contamination hints (delegates cleanup to memory-inventory)
Skips generated files marked with "GENERATED FILE".
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

DEFAULT_STATE_FILE = Path.home() / ".cache" / "refactor-context" / "last-audit.txt"
FENCE_RE = re.compile(r"^[ \t]*(`{3,}|~{3,})")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
QUOTED_LIST_RE = re.compile(r"(?:「[^」]{1,20}」[・、,/\s]*){3,}")

DATE_RE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
DIARY_PHRASE_RE = re.compile(
    r"(実例あり|実績あり|実証済み|検証時|に発生|に指摘された|に修正済み|real failure|hit for real|verified empirically)",
    re.I,
)
STRONG_EMPHASIS_RE = re.compile(
    r"(激しく|突破不能|全滅|一発で|時間を溶かす|厳禁|絶対禁止|圧倒的|絶対(?!パス|URL|日付|値))"
)
TOOL_LEAK_RE = re.compile(r"\b(AskUserQuestion|WebFetch)\b|(Read|Edit|Write)ツール|\bscratchpad\b")
MEMORY_LINK_RE = re.compile(r"\]\(([^)#]+\.md)\)")


def is_generated_file(text: str) -> bool:
    head = "\n".join(text.splitlines()[:8])
    return "GENERATED FILE" in head


def strip_fences_and_frontmatter(text: str) -> tuple[str, str]:
    """Return (frontmatter_text, body_without_code_fences)."""
    lines = text.splitlines()
    start = 0
    fm_lines: list[str] = []
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                fm_lines = lines[1:i]
                start = i + 1
                break

    body_lines: list[str] = []
    fence_char: str | None = None
    fence_len = 0
    for line in lines[start:]:
        if fence_char is not None:
            if re.match(rf"^[ \t]*{re.escape(fence_char)}{{{fence_len},}}[ \t]*$", line):
                fence_char = None
                fence_len = 0
            continue
        m = FENCE_RE.match(line)
        if m:
            fence_char = m.group(1)[0]
            fence_len = len(m.group(1))
            continue
        body_lines.append(line)
    return "\n".join(fm_lines), "\n".join(body_lines)


def clean_prose_for_signals(body: str) -> str:
    """Drop inline code and multi-item quoted negative-example enumerations to avoid false positives."""
    cleaned_lines: list[str] = []
    for line in body.splitlines():
        s = INLINE_CODE_RE.sub("", line)
        s = QUOTED_LIST_RE.sub("", s)
        cleaned_lines.append(s)
    return "\n".join(cleaned_lines)


class GitHelper:
    """Cache git root and remote slug per directory to minimize subprocess calls."""

    def __init__(self) -> None:
        self._dir_to_root: dict[Path, str | None] = {}
        self._root_to_slug: dict[str, str] = {}

    def _repo_root(self, directory: Path) -> str | None:
        if directory in self._dir_to_root:
            return self._dir_to_root[directory]
        try:
            proc = subprocess.run(
                ["git", "-C", str(directory), "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            root = proc.stdout.strip() if proc.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired):
            root = None
        self._dir_to_root[directory] = root
        return root

    def _repo_slug(self, repo_root: str) -> str:
        if repo_root in self._root_to_slug:
            return self._root_to_slug[repo_root]
        slug = ""
        try:
            proc = subprocess.run(
                ["git", "-C", repo_root, "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if proc.returncode == 0:
                url = proc.stdout.strip().removesuffix(".git")
                m = re.search(r"[:/]([^/:]+/[^/:]+)$", url)
                slug = m.group(1) if m else url
        except (OSError, subprocess.TimeoutExpired):
            pass
        self._root_to_slug[repo_root] = slug
        return slug

    def info(self, path: Path) -> tuple[str, float | None]:
        repo_root = self._repo_root(path.parent)
        if not repo_root:
            return "", None
        slug = self._repo_slug(repo_root)
        ts: float | None = None
        try:
            proc = subprocess.run(
                ["git", "-C", repo_root, "log", "-1", "--format=%ct", "--", str(path)],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if proc.returncode == 0 and proc.stdout.strip().isdigit():
                ts = float(proc.stdout.strip())
        except (OSError, subprocess.TimeoutExpired):
            pass
        return slug, ts


def parse_skill_description(fm: str) -> tuple[str, bool]:
    """Return (description text, is_multiline)."""
    lines = fm.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("description:"):
            val = line.split(":", 1)[1].strip()
            if val in (">", "|", ">-", "|-", ""):
                parts: list[str] = []
                for nxt in lines[i + 1 :]:
                    if nxt.startswith((" ", "\t")):
                        parts.append(nxt.strip())
                    else:
                        break
                return " ".join(parts), len(parts) > 1
            parts = [val.strip("\"'")]
            for nxt in lines[i + 1 :]:
                if nxt.startswith((" ", "\t")):
                    parts.append(nxt.strip())
                else:
                    break
            return " ".join(parts), len(parts) > 1
    return "", False


def collect_memory_hints(claude_home: Path) -> list[dict[str, Any]]:
    """Summarize memory directories that have index or prose signals for memory-inventory."""
    projects_dir = claude_home / "projects"
    if not projects_dir.is_dir():
        return []
    hints: list[dict[str, Any]] = []
    for proj_dir in sorted(projects_dir.iterdir()):
        mem_dir = proj_dir / "memory"
        if not mem_dir.is_dir():
            continue
        signals: list[str] = []
        idx_signals = check_memory_dir(mem_dir)
        for s_list in idx_signals.values():
            signals.extend(s_list)

        prose_flagged = 0
        for p in sorted(mem_dir.glob("*.md")):
            if p.name.startswith(".") or p.name == "MEMORY.md":
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
            _, body = strip_fences_and_frontmatter(text)
            prose = clean_prose_for_signals(body)
            if STRONG_EMPHASIS_RE.search(prose) or DIARY_PHRASE_RE.search(prose):
                prose_flagged += 1
        if prose_flagged:
            signals.append(f"prose_signals({prose_flagged}files)")

        if signals:
            hints.append({"mem_dir": str(mem_dir.resolve()), "signals": signals})
    return hints


def check_memory_dir(mem_dir: Path) -> dict[Path, list[str]]:
    """Return index-level signals (limits, broken links, orphan files) for a memory directory."""
    extra: dict[Path, list[str]] = {}
    idx_file = mem_dir / "MEMORY.md"
    if not idx_file.is_file():
        return extra

    md_files = [p for p in sorted(mem_dir.glob("*.md")) if not p.name.startswith(".")]
    idx_text = idx_file.read_text(encoding="utf-8", errors="replace")
    idx_lines = len(idx_text.splitlines())
    idx_bytes = idx_file.stat().st_size

    idx_signals: list[str] = []
    if idx_lines > 180 or idx_bytes > 20480:
        idx_signals.append(f"memory_index_near_limit({idx_lines}L/{idx_bytes}B)")

    linked = {Path(m).name for m in MEMORY_LINK_RE.findall(idx_text)}
    actual = {p.name for p in md_files if p.name != "MEMORY.md"}
    missing = sorted(linked - actual)
    orphans = sorted(actual - linked)
    if missing:
        idx_signals.append(f"broken_links({','.join(missing[:3])})")
    if orphans:
        idx_signals.append(f"orphan_files({','.join(orphans[:3])})")
    if idx_signals:
        extra[idx_file.resolve()] = idx_signals
    return extra


def collect_repo_context(repo_dir: Path, add_fn) -> None:
    """Collect context files directly from a repo root (avoids walking unrelated subtrees)."""
    if not repo_dir.is_dir():
        return
    add_fn("rule", repo_dir / "AGENTS.md")
    add_fn("rule", repo_dir / "CLAUDE.md")
    add_fn("rule", repo_dir / "GEMINI.md")
    add_fn("local-rule", repo_dir / "CLAUDE.local.md")

    for cfg_name in (".claude", ".gemini"):
        cfg = repo_dir / cfg_name
        if not cfg.is_dir():
            continue
        add_fn("rule", cfg / "CLAUDE.md")
        add_fn("rule", cfg / "GEMINI.md")
        for sub, kind in (("rules", "rule"), ("agent_docs", "rule"), ("commands", "command"), ("output-styles", "output-style")):
            d = cfg / sub
            if d.is_dir():
                for p in sorted(d.glob("*.md")):
                    add_fn(kind, p)
        skills_dir = cfg / "skills"
        if skills_dir.is_dir():
            for d in sorted(skills_dir.iterdir()):
                if d.is_dir():
                    add_fn("skill", d / "SKILL.md")


def discover_repo_roots(root: Path, max_depth: int = 3) -> list[Path]:
    """Find git repo roots (or context-bearing dirs) up to max_depth without walking inside repos."""
    roots: list[Path] = []

    def walk(cur: Path, depth: int) -> None:
        if not cur.is_dir():
            return
        if (
            (cur / ".git").exists()
            or (cur / "AGENTS.md").is_file()
            or (cur / "CLAUDE.md").is_file()
            or (cur / "GEMINI.md").is_file()
            or (cur / ".claude").is_dir()
            or (cur / ".gemini").is_dir()
        ):
            roots.append(cur)
            return
        if depth >= max_depth:
            return
        for child in sorted(cur.iterdir()):
            if child.is_dir() and not child.name.startswith(".") and child.name not in ("node_modules", "vendor"):
                walk(child, depth + 1)

    walk(root, 0)
    return roots


def collect_candidates(
    workspace: Path | None,
    extra_roots: list[Path],
    claude_home: Path,
    gemini_home: Path,
) -> list[tuple[str, Path]]:
    found: list[tuple[str, Path]] = []
    seen: set[Path] = set()

    def add(kind: str, p: Path) -> None:
        if not p.is_file():
            return
        try:
            real = p.resolve()
        except OSError:
            return
        if real in seen:
            return
        seen.add(real)
        found.append((kind, real))

    # 1. Global ~/.claude and ~/.gemini
    for home_cfg in (claude_home, gemini_home):
        if not home_cfg.is_dir():
            continue
        add("rule", home_cfg / "CLAUDE.md")
        add("rule", home_cfg / "GEMINI.md")
        for sub, kind in (("rules", "rule"), ("output-styles", "output-style")):
            d = home_cfg / sub
            if d.is_dir():
                for p in sorted(d.glob("*.md")):
                    add(kind, p)
        skills_dir = home_cfg / "skills"
        if skills_dir.is_dir():
            for d in sorted(skills_dir.iterdir()):
                if d.is_dir():
                    add("skill", d / "SKILL.md")

    # 2. Workspace and extra roots
    if workspace is not None:
        collect_repo_context(workspace, add)
    for root in extra_roots:
        for repo_dir in discover_repo_roots(root):
            collect_repo_context(repo_dir, add)

    return found


def analyze_file(
    kind: str,
    path: Path,
    since_ts: float | None,
    extra_signals: dict[Path, list[str]],
    git_helper: GitHelper,
) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    if is_generated_file(text):
        return None

    lines = text.splitlines()
    size_bytes = path.stat().st_size
    mtime = path.stat().st_mtime

    repo_slug, commit_ts = ("", None) if kind == "memory" else git_helper.info(path)
    effective_ts = max(mtime, commit_ts) if commit_ts is not None else mtime
    changed = True if since_ts is None else (effective_ts > since_ts)

    fm, body = strip_fences_and_frontmatter(text)
    prose = clean_prose_for_signals(body)
    signals: list[str] = list(extra_signals.get(path, []))

    date_hits = DATE_RE.findall(prose)
    diary_hits = DIARY_PHRASE_RE.findall(prose)
    if len(date_hits) >= 2 or diary_hits:
        signals.append(f"date_diary(dates={len(date_hits)},phrases={len(diary_hits)})")

    emph_hits = STRONG_EMPHASIS_RE.findall(prose)
    if emph_hits:
        uniq = sorted(set(emph_hits))[:3]
        signals.append(f"strong_emphasis({','.join(uniq)})")

    is_claude_only = kind in ("memory", "output-style") or path.name == "CLAUDE.md" or path.parent.name == "rules"
    if not is_claude_only:
        leak_hits = TOOL_LEAK_RE.findall(prose)
        if leak_hits:
            signals.append(f"tool_leak({len(leak_hits)})")

    if kind == "skill":
        desc, multiline = parse_skill_description(fm)
        if len(desc) > 240 or multiline:
            signals.append(f"long_description({len(desc)}ch{'/multiline' if multiline else ''})")

    if kind in ("rule", "output-style") and (len(lines) > 250 or size_bytes > 12288):
        signals.append(f"large_always_on({len(lines)}L/{size_bytes}B)")

    return {
        "kind": kind,
        "path": str(path),
        "repo": repo_slug,
        "lines": len(lines),
        "bytes": size_bytes,
        "mtime": dt.datetime.fromtimestamp(effective_ts).strftime("%Y-%m-%dT%H:%M"),
        "changed": changed,
        "signals": signals,
    }


def load_since_ts(since_arg: str | None, show_all: bool, state_file: Path) -> tuple[float | None, str]:
    if show_all:
        return None, "all"
    if since_arg:
        try:
            d = dt.datetime.fromisoformat(since_arg)
        except ValueError:
            sys.exit(f"Error: invalid --since format (expected YYYY-MM-DD or ISO8601): {since_arg}")
        return d.timestamp(), f"since:{since_arg}"
    if state_file.is_file():
        raw = state_file.read_text(encoding="utf-8").strip()
        if raw:
            try:
                return dt.datetime.fromisoformat(raw).timestamp(), f"last-audit:{raw}"
            except ValueError:
                print(f"WARN: invalid timestamp in {state_file}: {raw!r}; scanning all", file=sys.stderr)
    return None, "first-run(all)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan agent context files for changes and contamination signals.")
    parser.add_argument("--workspace", default=".", help="Primary workspace directory to scan (default: .)")
    parser.add_argument("--extra-root", action="append", default=[], help="Additional root directory to scan (repeatable)")
    parser.add_argument("--claude-home", default=str(Path.home() / ".claude"), help="Override ~/.claude directory")
    parser.add_argument("--gemini-home", default=str(Path.home() / ".gemini"), help="Override ~/.gemini directory")
    parser.add_argument("--no-memory", action="store_true", help="Skip ~/.claude/projects/*/memory/")
    parser.add_argument("--since", default=None, help="Only flag changes after YYYY-MM-DD (or ISO8601)")
    parser.add_argument("--all", action="store_true", help="Include unchanged and unflagged files in output")
    parser.add_argument("--state-file", default=str(DEFAULT_STATE_FILE), help="Path storing last audit timestamp")
    parser.add_argument("--mark-done", action="store_true", help="Record current timestamp as last audit and exit")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args(argv)

    state_file = Path(args.state_file).expanduser()
    if args.mark_done:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        now_s = dt.datetime.now().isoformat(timespec="seconds")
        state_file.write_text(now_s + "\n", encoding="utf-8")
        print(f"MARKED_DONE: {now_s} ({state_file})")
        return 0

    since_ts, mode_label = load_since_ts(args.since, args.all, state_file)
    claude_home = Path(args.claude_home).expanduser()
    gemini_home = Path(args.gemini_home).expanduser()
    workspace = Path(args.workspace).expanduser().resolve() if args.workspace else None
    extra_roots = [Path(r).expanduser().resolve() for r in args.extra_root]

    candidates = collect_candidates(workspace, extra_roots, claude_home, gemini_home)
    memory_hints = [] if args.no_memory else collect_memory_hints(claude_home)

    git_helper = GitHelper()
    results = []
    for kind, path in candidates:
        res = analyze_file(kind, path, since_ts, {}, git_helper)
        if res is not None:
            results.append(res)

    changed_count = sum(1 for r in results if r["changed"])
    flagged_count = sum(1 for r in results if r["signals"])
    shown = results if args.all else [r for r in results if r["changed"] or r["signals"]]

    if args.json:
        print(
            json.dumps(
                {
                    "mode": mode_label,
                    "scanned": len(results),
                    "changed": changed_count,
                    "flagged": flagged_count,
                    "items": shown,
                    "memory_hints": memory_hints,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    print(
        f"SUMMARY: mode={mode_label} scanned={len(results)} changed={changed_count} "
        f"flagged={flagged_count} memory_hints={len(memory_hints)}"
    )
    if not shown:
        print("CLEAN: 対象に新規変更・汚染シグナルはありません")
    else:
        for r in shown:
            flags = []
            if r["changed"]:
                flags.append("CHANGED")
            flags.extend(r["signals"])
            repo_part = f" repo={r['repo']}" if r["repo"] else ""
            flag_str = " | ".join(flags) if flags else "-"
            print(f"[{r['kind']}] {r['path']} ({r['lines']}L/{r['bytes']}B{repo_part}) :: {flag_str}")

    for hint in memory_hints:
        print(f"MEMORY_HINT: {hint['mem_dir']} :: {' | '.join(hint['signals'])} (run memory-inventory)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
