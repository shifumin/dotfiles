# CLAUDE.md

> **Scope**: Project-level (`dotfiles` repo only)
> **Global settings**: `.claude/CLAUDE.md` (symlinked to `~/.claude/CLAUDE.md`)

## Symlink Management

`setup.sh` is the single source of truth for symlinks. Update `setup.sh` instead of creating symlinks manually.

## Prohibitions

| Rule | Reason |
|------|--------|
| Keep runtime/cache files out of `.claude/` | Only managed files belong in `claude_links`; runtime data stays local |
| Do not duplicate workflow docs across files | `README.md` is for humans; `.claude/rules/dotfiles.md` is for Claude Code |

## References

| Topic | Path |
|-------|------|
| Repository overview | `README.md` |
| Dotfiles editing workflow | `.claude/rules/dotfiles.md` |
| Sheldon plugin management | `.config/sheldon/plugins.toml` |
| Symlink definitions | `setup.sh` |
