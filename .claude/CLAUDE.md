# CLAUDE.md

> **Scope**: Global — applies to all projects via symlink `~/.claude/CLAUDE.md`
> **Source**: `~/ghq/github.com/shifumin/dotfiles/.claude/CLAUDE.md` (managed by `setup.sh`; do not copy manually)
> **Layout**: shared rules (Claude Code + Codex + Antigravity) live in `AGENTS.md`, imported below; Claude-only rules live here and in `.claude/rules/*.md`. Edit `AGENTS.md` and run `.codex/build-agents.sh` for shared changes

@~/ghq/github.com/shifumin/dotfiles/AGENTS.md

---

## Claude Code Additions

### Persona

The persona SSOT is the `emma` Output Style (`.claude/output-styles/emma.md`), propagated to Codex (`.codex/AGENTS.md`) and Antigravity (`.gemini/config/GEMINI.md`) by `.codex/build-agents.sh`. Apply the address-form rule in `AGENTS.md` ("User").

### Tool Mapping

| Shared rule | Claude Code tool |
|-------------|------------------|
| `q` shortcut — structured question tool | `AskUserQuestion` |
| Web fetch — built-in fetch tool | `WebFetch` |

### Hook Enforcement

The `mise exec --` rule in `AGENTS.md` ("Shell Commands") is enforced by `~/.claude/hooks/mise-exec-guard.sh` (PreToolUse on Bash).
