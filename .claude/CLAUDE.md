# CLAUDE.md

> **Scope**: Global — applies to ALL projects via symlink `~/.claude/CLAUDE.md`
> **Source**: `~/ghq/github.com/shifumin/dotfiles/.claude/CLAUDE.md` — edit here, commit in dotfiles repo
> **Mechanism**: `setup.sh` creates symlink; do not copy this file manually
> **Layout**: shared rules (Claude Code + Codex) live in `AGENTS.md`, imported below. This file holds Claude Code-only additions; further Claude-only rules live in `.claude/rules/*.md`. Do not duplicate shared rules here — edit `AGENTS.md` and run `.codex/build-agents.sh`

@~/ghq/github.com/shifumin/dotfiles/AGENTS.md

---

## Claude Code Additions

### Persona

The persona is the `emma` Output Style (`.claude/output-styles/emma.md`). Its Codex mirror is the Persona section of `.codex/AGENTS.codex.md`; keep both in sync. The address-form rule in the shared "User" section applies to it.

### Tool mapping

| Shared rule | In Claude Code |
|-------------|----------------|
| `q` shortcut — structured question tool | Use `AskUserQuestion` |
| Web fetch — built-in fetch tool | `WebFetch` |

### Hook enforcement

The `mise exec --` rule in the shared "Shell Commands" section is enforced deterministically by `~/.claude/hooks/mise-exec-guard.sh` (PreToolUse on Bash).
