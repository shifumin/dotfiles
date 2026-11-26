# CLAUDE.md

> Project-level rules for the `dotfiles` repo only (global rules live in `AGENTS.md`, symlinked to `~/.claude/CLAUDE.md`).

## Symlinks & New Files

- `setup.sh` is the single source of truth for symlinks; never create symlinks manually.
- To add a managed file: place it at its target relative path, register it in `setup.sh` (`dir_links`, `file_links`, or `claude_links`), run `./setup.sh`, and commit both.
- Exceptions: custom skills under `.claude/skills/<name>/` are auto-linked by `./setup.sh` (do not add them to an array); third-party skills go in `.claude/skills.txt`.

## Hygiene

- Keep runtime/cache files out of `.claude/` (only managed files belong in `claude_links`).
- After editing `AGENTS.md` or `.claude/output-styles/emma.md`, run `.codex/build-agents.sh` and commit the generated files (`.codex/AGENTS.md`, `.gemini/config/GEMINI.md`).
