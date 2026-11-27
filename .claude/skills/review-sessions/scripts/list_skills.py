#!/usr/bin/env python3
"""List installed skills with the scope that decides how a finding is handled.

Usage: list_skills.py --out FILE [--index index.tsv] [--project-dir DIR ...]

scope values:
  own-global  dotfiles/.claude/skills (used everywhere; editable on user approval)
  own-vault   my-vault/.claude/skills (used only in personal vault; editable on user approval)
  vendored    upstream copies inside dotfiles/vault; report upstream or override locally
  team        a project repository's skills (proposal only)
  external    ~/.agents/skills and enabled Claude Code plugins (proposal only)
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
from pathlib import Path

HOME = Path.home()
SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_DOTFILES_ROOT = SCRIPT_PATH.parents[4]
DEFAULT_OWNER_ROOT = DEFAULT_DOTFILES_ROOT.parent
DEFAULT_DOTFILES_SKILLS = DEFAULT_DOTFILES_ROOT / ".claude" / "skills"
DEFAULT_VAULT_ROOT = Path(os.environ["REVIEW_SESSIONS_VAULT"]) if os.environ.get("REVIEW_SESSIONS_VAULT") else DEFAULT_OWNER_ROOT / "my-vault"
DEFAULT_VAULT_SKILLS = DEFAULT_VAULT_ROOT / ".claude" / "skills"
DEFAULT_EXTERNAL_SKILLS = HOME / ".agents" / "skills"
DEFAULT_PLUGINS_JSON = HOME / ".claude" / "plugins" / "installed_plugins.json"
DEFAULT_SETTINGS_JSON = HOME / ".claude" / "settings.json"

# Upstream copies vendored into dotfiles or personal vault.
VENDORED = {
    "agent-browser",
    "herdr",
    "japanese-tech-writing",
    "playwright-cli",
    "obsidian-markdown",
    "obsidian-cli",
    "obsidian-bases",
}


def tsv_safe(value: str) -> str:
    return re.sub(r"[\t\r\n]+", " ", value).strip()


def parse_description(skill_md: Path) -> str:
    try:
        text = skill_md.read_text(encoding="utf-8", errors="replace")[:8000]
    except OSError:
        return ""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""

    fm_lines: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        fm_lines.append(line)
    else:
        return ""

    desc_parts: list[str] = []
    in_desc = False
    is_block = False
    for line in fm_lines:
        if not in_desc:
            m = re.match(r"^description:\s*(.*)$", line)
            if m:
                val = m.group(1).strip()
                if val in ("|", ">", "|-", ">-", "|+", ">+") or not val:
                    in_desc = True
                    is_block = True
                else:
                    desc_parts.append(val)
                    # Single-line quoted string closed on the same line: stop immediately.
                    if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
                        break
                    in_desc = True
        else:
            if not is_block and not line.startswith((" ", "\t")):
                break
            if re.match(r"^[A-Za-z0-9_-]+:", line):
                break
            desc_parts.append(line.strip())

    raw = " ".join(p for p in desc_parts if p).strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ('"', "'"):
        raw = raw[1:-1]
    return tsv_safe(raw)[:300]


def collect_skills(base: Path, scope_fn) -> list[tuple[str, str, str, str]]:
    if not base.is_dir():
        return []
    rows: list[tuple[str, str, str, str]] = []
    for skill_md_str in sorted(glob.glob(str(base / "*" / "SKILL.md"))):
        skill_md = Path(skill_md_str)
        name = skill_md.parent.name
        rows.append((scope_fn(name), name, str(skill_md.resolve()), parse_description(skill_md)))
    return rows


def find_repo_root(cwd: Path) -> Path:
    cur = cwd.resolve()
    for parent in (cur, *cur.parents):
        if (parent / ".git").exists():
            return parent
    return cur


def load_cwds_from_index(index_path: Path) -> list[Path]:
    if not index_path.is_file():
        return []
    cwds: list[Path] = []
    lines = index_path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines:
        return []
    header = lines[0].split("\t")
    if "cwd" not in header:
        return []
    cwd_idx = header.index("cwd")
    for line in lines[1:]:
        cols = line.split("\t")
        if len(cols) > cwd_idx and cols[cwd_idx].strip():
            p = Path(cols[cwd_idx].strip())
            if p.is_dir():
                cwds.append(find_repo_root(p))
    return cwds


def load_enabled_plugins(settings_json: Path) -> set[str] | None:
    if not settings_json.is_file():
        return None
    try:
        data = json.loads(settings_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    enabled = data.get("enabledPlugins") if isinstance(data, dict) else None
    if not isinstance(enabled, dict):
        return None
    return {k for k, v in enabled.items() if v}


def collect_installed_plugins(
    plugins_json: Path,
    enabled_plugins: set[str] | None = None,
) -> list[tuple[str, str, str, str]]:
    if not plugins_json.is_file():
        return []
    try:
        data = json.loads(plugins_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    plugins = data.get("plugins", {}) if isinstance(data, dict) else {}
    if not isinstance(plugins, dict):
        return []

    rows: list[tuple[str, str, str, str]] = []
    seen_skill_names: set[str] = set()
    for plugin_id, entries in sorted(plugins.items()):
        if enabled_plugins is not None and plugin_id not in enabled_plugins:
            continue
        if not isinstance(entries, list):
            continue
        # Prefer user-scoped entry, then latest updated entry, to avoid duplicate versions.
        valid_entries = [e for e in entries if isinstance(e, dict) and isinstance(e.get("installPath"), str) and e["installPath"]]
        valid_entries.sort(key=lambda e: str(e.get("lastUpdated", "")), reverse=True)
        valid_entries.sort(key=lambda e: 0 if e.get("scope") == "user" else 1)
        for entry in valid_entries:
            install_path = Path(entry["installPath"])
            for row in collect_skills(install_path / "skills", lambda _n: "external"):
                if row[1] not in seen_skill_names:
                    seen_skill_names.add(row[1])
                    rows.append(row)
    return rows


def is_under(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="List installed skills with scope classification")
    ap.add_argument("--out", required=True, help="Output TSV file")
    ap.add_argument("--index", help="Optional index.tsv from extract_sessions.py to auto-discover project dirs")
    ap.add_argument("--project-dir", action="append", default=[], help="Additional project directory to scan")
    ap.add_argument("--dotfiles-skills", default=str(DEFAULT_DOTFILES_SKILLS), help=argparse.SUPPRESS)
    ap.add_argument("--vault-skills", default=str(DEFAULT_VAULT_SKILLS), help=argparse.SUPPRESS)
    ap.add_argument("--external-skills", default=str(DEFAULT_EXTERNAL_SKILLS), help=argparse.SUPPRESS)
    ap.add_argument("--plugins-json", default=str(DEFAULT_PLUGINS_JSON), help=argparse.SUPPRESS)
    ap.add_argument("--settings-json", default=str(DEFAULT_SETTINGS_JSON), help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    dotfiles_skills = Path(args.dotfiles_skills)
    vault_skills = Path(args.vault_skills)
    external_skills = Path(args.external_skills)
    plugins_json = Path(args.plugins_json)
    settings_json = Path(args.settings_json)

    own_roots = [
        root for root in (dotfiles_skills.parent.parent, vault_skills.parent.parent)
        if root.is_dir()
    ]

    rows = collect_skills(dotfiles_skills, lambda n: "vendored" if n in VENDORED else "own-global")
    rows += collect_skills(vault_skills, lambda n: "vendored" if n in VENDORED else "own-vault")
    own_paths = {r[2] for r in rows}

    project_dirs: list[Path] = []
    if args.index:
        project_dirs.extend(load_cwds_from_index(Path(args.index)))
    project_dirs.extend(Path(p) for p in args.project_dir if p)

    scanned_projects: set[Path] = set()
    for proj in project_dirs:
        if not proj.is_dir():
            continue
        resolved = proj.resolve()
        if resolved in scanned_projects:
            continue
        scanned_projects.add(resolved)
        if any(is_under(resolved, root) for root in own_roots):
            continue
        for sub in (".claude/skills", ".agents/skills"):
            rows += [r for r in collect_skills(resolved / sub, lambda _n: "team") if r[2] not in own_paths]

    rows += [r for r in collect_skills(external_skills, lambda _n: "external") if r[2] not in own_paths]
    enabled_plugins = load_enabled_plugins(settings_json)
    rows += [r for r in collect_installed_plugins(plugins_json, enabled_plugins) if r[2] not in own_paths]

    seen: set[str] = set()
    unique: list[tuple[str, str, str, str]] = []
    for r in rows:
        if r[2] not in seen:
            seen.add(r[2])
            unique.append(r)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        fh.write("scope\tname\tpath\tdescription\n")
        for r in unique:
            fh.write("\t".join(tsv_safe(v) for v in r) + "\n")

    counts: dict[str, int] = {}
    for r in unique:
        counts[r[0]] = counts.get(r[0], 0) + 1
    print(f"skills={len(unique)} {counts} -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
