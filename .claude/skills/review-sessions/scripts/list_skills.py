#!/usr/bin/env python3
"""List installed skills with the scope that decides how a finding is handled.

Usage: list_skills.py --out FILE [--project-dir DIR ...]

scope values:
  own-global  dotfiles/.claude/skills (used everywhere; editable on user approval)
  own-vault   my-vault/.claude/skills (used only in my-vault; editable on user approval)
  vendored    copied from upstream into dotfiles/my-vault; fix upstream or add a local override
  team        a project repository's skills (proposal only)
  external    ~/.agents/skills and plugins: org or third-party (proposal only)
"""
import argparse
import glob
import os
import re

HOME = os.path.expanduser("~")
GHQ = f"{HOME}/ghq/github.com"
DOTFILES = f"{GHQ}/shifumin/dotfiles/.claude/skills"
VAULT = f"{GHQ}/shifumin/my-vault/.claude/skills"
# Upstream copies. Sources: comments in dotfiles/.claude/skills.txt (herdr, japanese-tech-writing),
# my-vault/CLAUDE.md (kepano/obsidian-skills), and playwright-cli synced from the installed tool.
VENDORED = {"herdr", "japanese-tech-writing", "playwright-cli", "obsidian-markdown", "obsidian-cli",
            "obsidian-bases"}


def description(skill_md):
    try:
        with open(skill_md, encoding="utf-8", errors="replace") as fh:
            text = fh.read(6000)
    except OSError:
        return ""
    m = re.search(r"^description:\s*(.*?)(?=^\w[\w-]*:|^---)", text, re.S | re.M)
    return re.sub(r"\s+", " ", m.group(1)).strip().strip("|>").strip()[:300] if m else ""


def collect(base, scope_fn):
    rows = []
    for skill_md in sorted(glob.glob(f"{base}/*/SKILL.md")):
        name = os.path.basename(os.path.dirname(skill_md))
        rows.append((scope_fn(name), name, os.path.realpath(skill_md), description(skill_md)))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--project-dir", action="append", default=[])
    args = ap.parse_args()

    rows = collect(DOTFILES, lambda n: "vendored" if n in VENDORED else "own-global")
    rows += collect(VAULT, lambda n: "vendored" if n in VENDORED else "own-vault")
    own_paths = {r[2] for r in rows}
    for project in args.project_dir:
        if os.path.realpath(project).startswith(f"{GHQ}/shifumin/"):
            continue
        for sub in (".claude/skills", ".agents/skills"):
            rows += [r for r in collect(f"{project}/{sub}", lambda n: "team") if r[2] not in own_paths]
    rows += [r for r in collect(f"{HOME}/.agents/skills", lambda n: "external") if r[2] not in own_paths]

    seen, unique = set(), []
    for r in rows:
        if r[2] not in seen:
            seen.add(r[2])
            unique.append(r)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write("scope\tname\tpath\tdescription\n")
        for r in unique:
            fh.write("\t".join(r) + "\n")
    counts = {}
    for r in unique:
        counts[r[0]] = counts.get(r[0], 0) + 1
    print(f"skills={len(unique)} {counts} -> {args.out}")


if __name__ == "__main__":
    main()
