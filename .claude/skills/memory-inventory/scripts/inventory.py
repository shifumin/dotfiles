#!/usr/bin/env python3
"""Helper for the memory-inventory skill: backup, measure, dump, and safe archive."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path

MAX_INDEX_LINES = 200
MAX_INDEX_BYTES = 25000
HOOK_CHAR_LIMIT = 150

MD_LINK_RE = re.compile(r"\]\(([^)]+\.md)\)")
WIKILINK_RE = re.compile(r"\[\[([^\[\]]+)\]\]")
DATE_LINK_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
INLINE_CODE_RE = re.compile(r"`[^`]*`")


def encode_project_path(project_path: Path) -> str:
    resolved = str(project_path.resolve())
    return re.sub(r"[^A-Za-z0-9-]", "-", resolved)


def resolve_mem_dir(mem_dir: str | None, project: str | None) -> Path:
    if mem_dir:
        path = Path(mem_dir).expanduser().resolve()
    else:
        if project:
            proj_path = Path(project).expanduser().resolve()
        else:
            proc = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                proj_path = Path(proc.stdout.strip())
            else:
                proj_path = Path.cwd()
        encoded = encode_project_path(proj_path)
        path = Path.home() / ".claude" / "projects" / encoded / "memory"

    if not path.is_dir():
        print(f"ERROR: memory directory not found: {path}", file=sys.stderr)
        sys.exit(1)
    return path


def topic_files(mem_dir: Path) -> list[Path]:
    return sorted(
        p
        for p in mem_dir.iterdir()
        if p.is_file()
        and p.suffix == ".md"
        and p.name != "MEMORY.md"
        and not p.name.startswith(".")
    )


def strip_matching_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def parse_markdown(path: Path) -> tuple[dict[str, str], str]:
    """Return (frontmatter key->value map, body text)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    fm: dict[str, str] = {}
    body_start = 0

    if lines and lines[0].strip() == "---":
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                body_start = idx + 1
                for fm_line in lines[1:idx]:
                    m = re.match(r"^\s*([A-Za-z0-9_-]+)\s*:\s*(.*)$", fm_line)
                    if m:
                        key, val = m.group(1), m.group(2).strip()
                        if val and key not in fm:
                            fm[key] = strip_matching_quotes(val)
                break

    body = "\n".join(lines[body_start:])
    return fm, body


def strip_code(body: str) -> str:
    """Remove fenced code blocks and inline code spans so examples are ignored."""
    out: list[str] = []
    in_fence = False
    fence_char = ""
    for line in body.splitlines():
        m = FENCE_RE.match(line)
        if m:
            ch = m.group(1)[0]
            if not in_fence:
                in_fence = True
                fence_char = ch
                continue
            if ch == fence_char:
                in_fence = False
                continue
        if not in_fence:
            out.append(INLINE_CODE_RE.sub("", line))
    return "\n".join(out)


def cmd_backup(args: argparse.Namespace) -> int:
    mem_dir = resolve_mem_dir(args.mem_dir, args.project)
    if args.dest_dir:
        dest_root = Path(args.dest_dir).expanduser().resolve()
        if not dest_root.is_dir():
            print(f"ERROR: backup destination directory not found: {dest_root}", file=sys.stderr)
            return 1
    else:
        dest_root = Path(tempfile.gettempdir())

    slug = mem_dir.parent.name.lstrip("-") or "memory"
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = dest_root / f"memory-backup-{slug}-{stamp}"
    counter = 1
    while backup_path.exists():
        backup_path = dest_root / f"memory-backup-{slug}-{stamp}_{counter}"
        counter += 1
    shutil.copytree(mem_dir, backup_path)

    print(f"MEM_DIR={mem_dir}")
    print(f"BACKUP={backup_path}")

    state_file = mem_dir / ".inventory-state.md"
    if state_file.is_file():
        print("\n--- .inventory-state.md ---")
        print(state_file.read_text(encoding="utf-8", errors="replace").rstrip())
    else:
        print("\n--- .inventory-state.md ---\n(none)")
    return 0


def cmd_measure(args: argparse.Namespace) -> int:
    mem_dir = resolve_mem_dir(args.mem_dir, args.project)
    index_path = mem_dir / "MEMORY.md"
    topics = topic_files(mem_dir)

    print(f"MEM_DIR: {mem_dir}")
    if index_path.is_file():
        index_raw = index_path.read_bytes()
        index_text = index_raw.decode("utf-8", errors="replace")
        index_lines = index_text.splitlines()
        line_cnt = len(index_lines)
        byte_cnt = len(index_raw)
        print(
            f"MEMORY.md: {line_cnt} 行 ({line_cnt / MAX_INDEX_LINES * 100:.1f}% / {MAX_INDEX_LINES}) / "
            f"{byte_cnt} bytes ({byte_cnt / MAX_INDEX_BYTES * 100:.1f}% / {MAX_INDEX_BYTES})"
        )
    else:
        index_text = ""
        index_lines = []
        print("MEMORY.md: (missing)")

    print(f"トピックファイル数: {len(topics)}")

    index_links: set[str] = set()
    for match in MD_LINK_RE.findall(index_text):
        target = match.strip()
        if target.startswith(("http://", "https://", "#")):
            continue
        index_links.add(target)

    type_counts: Counter[str] = Counter()
    orphans: list[str] = []
    name_mismatches: list[str] = []
    thin_files: list[str] = []
    rows: list[tuple[str, str, int, int, str]] = []
    known_stems = {p.stem for p in topics}
    known_names: dict[str, str] = {}
    topic_bodies: dict[str, str] = {}

    for path in topics:
        fm, body = parse_markdown(path)
        topic_bodies[path.name] = body
        stat_info = path.stat()
        mtime_date = datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d")
        mod = fm.get("modified", "")[:10] or mtime_date
        mtype = fm.get("type", "(none)")
        name = fm.get("name", "")
        if name:
            known_names[name] = path.name

        type_counts[mtype] += 1
        if path.name not in index_links:
            orphans.append(path.name)
        if name != path.stem:
            name_mismatches.append(f"{path.name} (name: {name or '(missing)'})")

        non_empty_body_lines = sum(1 for ln in body.splitlines() if ln.strip())
        body_bytes = len(body.strip().encode("utf-8"))
        byte_size = stat_info.st_size
        if non_empty_body_lines <= args.thin_lines and body_bytes <= args.thin_bytes:
            thin_files.append(f"{path.name} ({non_empty_body_lines} 行 / 本文 {body_bytes} B)")
        rows.append((mod, mtype, non_empty_body_lines, byte_size, path.name))

    print("\n--- type 分布 ---")
    for mtype, count in type_counts.most_common():
        print(f"  {count:3d}  {mtype}")

    print("\n--- ファイル一覧 (更新日 / type / 本文行数 / bytes / ファイル) ---")
    for mod, mtype, blines, bsize, fname in sorted(rows, key=lambda r: (r[0], r[4])):
        print(f"  {mod:10s}  {mtype:10s}  {blines:4d}行  {bsize:6d}B  {fname}")

    broken_links = sorted(link for link in index_links if not (mem_dir / link).is_file())

    unresolved_wiki: set[str] = set()
    for body in topic_bodies.values():
        cleaned = strip_code(body)
        for raw_target in WIKILINK_RE.findall(cleaned):
            target = raw_target.split("|", 1)[0].split("#", 1)[0].strip()
            if not target or DATE_LINK_RE.match(target):
                continue
            if target in known_stems:
                continue
            if target in known_names:
                unresolved_wiki.add(f"{target} (name一致 -> {known_names[target]})")
            else:
                unresolved_wiki.add(target)

    long_hooks: list[str] = []
    for lineno, line in enumerate(index_lines, start=1):
        if line.startswith("- [") and len(line) > HOOK_CHAR_LIMIT:
            long_hooks.append(f"L{lineno} ({len(line)} 字): {line[:50]}...")

    def print_section(title: str, items: list[str]) -> None:
        print(f"\n--- {title} ({len(items)}) ---")
        for item in items:
            print(f"  - {item}")

    print_section(f"薄いファイル (本文 <= {args.thin_lines} 行 かつ <= {args.thin_bytes} B)", sorted(thin_files))
    print_section("孤児ファイル (MEMORY.md 未掲載)", sorted(orphans))
    print_section("name 不一致", sorted(name_mismatches))
    print_section("リンク切れ (MEMORY.md)", broken_links)
    print_section("未解決 [[ ]]", sorted(unresolved_wiki))
    print_section(f"{HOOK_CHAR_LIMIT}字超のフック行", long_hooks)
    return 0


def cmd_dump(args: argparse.Namespace) -> int:
    mem_dir = resolve_mem_dir(args.mem_dir, args.project)
    topics = topic_files(mem_dir)
    if not topics:
        print("(no topic files)")
        return 0
    for idx, path in enumerate(topics):
        fm, body = parse_markdown(path)
        if idx > 0:
            print()
        mtype = fm.get("type", "(none)")
        name = fm.get("name", "(missing)")
        print(f"=== {path.name} [type={mtype} name={name}] ===")
        if fm.get("description"):
            print(f"description: {fm['description']}")
        print(body.strip())
    return 0


def cmd_archive(args: argparse.Namespace) -> int:
    mem_dir = resolve_mem_dir(args.mem_dir, args.project)
    targets: list[Path] = []
    seen: set[str] = set()
    for raw_name in args.files:
        name = Path(raw_name).name
        if raw_name != name or name in ("", ".", "..", "MEMORY.md") or name.startswith("."):
            print(f"ERROR: invalid topic filename: {raw_name}", file=sys.stderr)
            return 1
        src = mem_dir / name
        if not src.is_file():
            print(f"ERROR: file not found in {mem_dir}: {name}", file=sys.stderr)
            return 1
        if name not in seen:
            seen.add(name)
            targets.append(src)

    archive_dir = mem_dir / "_archive"
    archive_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    for src in targets:
        dst = archive_dir / src.name
        if dst.exists():
            dst = archive_dir / f"{src.stem}_{stamp}{src.suffix}"
            counter = 1
            while dst.exists():
                dst = archive_dir / f"{src.stem}_{stamp}_{counter}{src.suffix}"
                counter += 1
        shutil.move(str(src), str(dst))
        print(f"archived: {src.name} -> _archive/{dst.name}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect and maintain Claude auto memory.")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--mem-dir", help="Explicit path to memory directory")
        p.add_argument("--project", help="Project root path (default: current git root or cwd)")

    p_backup = sub.add_parser("backup", help="Backup memory directory and print .inventory-state.md")
    add_common(p_backup)
    p_backup.add_argument("--dest-dir", help="Parent directory for backup (default: system temp dir)")
    p_backup.set_defaults(func=cmd_backup)

    p_measure = sub.add_parser("measure", help="Measure MEMORY.md usage and check topic integrity")
    add_common(p_measure)
    p_measure.add_argument("--thin-lines", type=int, default=5, help="Max body lines for thin files (default: 5)")
    p_measure.add_argument("--thin-bytes", type=int, default=500, help="Max body bytes for thin files (default: 500)")
    p_measure.set_defaults(func=cmd_measure)

    p_dump = sub.add_parser("dump", help="Dump metadata and bodies of all topic files")
    add_common(p_dump)
    p_dump.set_defaults(func=cmd_dump)

    p_archive = sub.add_parser("archive", help="Safely move topic files into _archive/ without overwriting")
    add_common(p_archive)
    p_archive.add_argument("files", nargs="+", help="Topic file names (basename only)")
    p_archive.set_defaults(func=cmd_archive)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
