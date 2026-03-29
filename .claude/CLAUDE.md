# CLAUDE.md

> **Scope**: Global — applies to ALL projects via symlink `~/.claude/CLAUDE.md`
> **Source**: `~/ghq/github.com/shifumin/dotfiles/.claude/CLAUDE.md` — edit here, commit in dotfiles repo
> **Mechanism**: `setup.sh` creates symlink; do not copy this file manually

---

## Core Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | Follow existing code style | Do not deviate from project conventions |
| 2 | Use project tools | Do not introduce new tools or frameworks without approval |
| 3 | Pre-commit checks | Always run linters and tests before committing |
| 4 | Sync tests | Add/update tests when adding/updating implementation |
| 5 | Sync docs | Update project-level CLAUDE.md and README.md when adding/updating implementation |
| 6 | Skills first | Check and use Skills before MCP tools |

---

## I/O Rules

| Category | Rule |
|----------|------|
| Japanese output | No coined words; use English terms when Japanese translation is unnatural |
| Document language | README.md and CLAUDE.md are written in English |
| Voice input | User input is often voice-transcribed (Japanese via SuperWhisper). Silently infer intended meaning from context when encountering: homophones (同音異義語), misrecognized technical terms (e.g., "cloud.md" → CLAUDE.md), or slightly unnatural phrasing. Do not ask for clarification on obvious transcription errors |
| Shortcut input | `ba` input = Before/After: show proposed changes in before/after format |
| Shortcut input | `k` input = Kaizen: reflect on this session, find process/artifact improvements (CLAUDE.md, rules, skills, workflows, etc.), and apply them. Use skill-creator skill when improving skills |
| Shortcut input | `y` input = YES / Done — interpret from context and proceed |
| Shortcut input | `z` input = Evaluate from zero-base: ignore existing content/approach, assess from ideal state, propose improvements by back-casting from the ideal |

---

## Tool Constraints

| Tool | Constraint | Workaround |
|------|-----------|------------|
| Write / Edit | Auto-strips trailing whitespace | Use `cat >| file << 'EOF'` in Bash |
| WebFetch | Blocked by bot protection (403) | Use playwright-cli (`--headed --persistent`) |
| WebFetch | Summarizes content instead of returning full text | Use playwright-cli (`eval` to extract innerText) |

---

## Shell Commands

### mise exec Required

These commands must run via `mise exec --`:

| Category | Commands |
|----------|----------|
| Ruby | `bundle`, `rails`, `rspec`, `ruby` |
| Node.js | `pnpm`, `node`, `npm` |

Reason: Ensures correct environment variables managed by mise.

