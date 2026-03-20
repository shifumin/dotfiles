# CLAUDE.md

> **Scope**: Project-level (this dotfiles repo only)
> **Global settings**: `.claude/CLAUDE.md` (symlinked to `~/.claude/CLAUDE.md`, applies to all projects)

## Adding Dotfiles

1. Create the file at the correct relative path in this repo
2. Add the path to `setup.sh` (`dir_links`, `file_links`, or `claude_links` array)
3. Run `./setup.sh` to create the symlink
4. Commit both the new file and the updated `setup.sh`

## Symlink Management

Source of truth: `setup.sh` — defines all symlink targets.
Do NOT manually create symlinks; always update `setup.sh`.

## Prohibitions

| Rule | Reason |
|------|--------|
| Do not add runtime/cache files to `.claude/` | Only managed files are in `claude_links` array; runtime data must remain local |
| Do not duplicate workflow docs across files | Single source: `README.md` for humans, `.claude/rules/dotfiles.md` for Claude Code |

## References

| Topic | Location |
|-------|----------|
| Repository description & contents | `README.md` |
| Dotfiles editing workflow | `.claude/rules/dotfiles.md` |
| Sheldon plugin management | `.config/sheldon/plugins.toml` |
| Symlink definitions | `setup.sh` |
