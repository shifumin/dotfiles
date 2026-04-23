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
| 5 | Sync docs | Update project-level CLAUDE.md and README.md only when changes affect public API, external behavior, documented workflows, or commands users invoke. Skip for purely internal refactors |
| 6 | Skills first | Check and use Skills before MCP tools. Use `find-skills` skill when unsure whether a relevant skill exists |

---

## I/O Rules

| Category | Rule |
|----------|------|
| Japanese output | No coined words; use English terms when Japanese translation is unnatural |
| Document language | README.md and CLAUDE.md are written in English |
| Voice input | User input is often voice-transcribed (Japanese via SuperWhisper). Silently infer intended meaning from context when encountering: homophones (同音異義語), misrecognized technical terms (e.g., "cloud.md" → CLAUDE.md), or slightly unnatural phrasing. Do not ask for clarification on obvious transcription errors |
| Shortcut input | `ba` input = Before/After: show proposed changes in before/after format |
| Shortcut input | `k` input = Kaizen: reflect on this session, find process/artifact improvements (CLAUDE.md, rules, skills, workflows, etc.), and apply them. Use skill-creator skill when improving skills |
| Shortcut input | `q` input = Question: ask clarifying questions using AskUserQuestion repeatedly until all ambiguities are resolved, then wait for explicit instruction to proceed |
| Shortcut input | `y` input = YES / Done — interpret from context and proceed |
| Shortcut input | `z` input = Evaluate from zero-base: ignore existing content/approach, assess from ideal state, propose improvements by back-casting from the ideal |

### Where to register a "shortcut"

When the user asks to add a "shortcut", choose the destination by intent:

| Intent | Destination |
|--------|-------------|
| Single-character input alias for Claude Code session (`ba`, `k`, `q`, `y`, `z`, etc.) | `.claude/CLAUDE.md` → `I/O Rules` table (Shortcut input row) |
| Shell alias / function (e.g. `gst`, `glog`) | `.zshrc.custom` |
| Frequently-typed CLI command sequence as documentation reference | Project-level `CLAUDE.md` (not global) |
| Claude Code slash command | `.claude/commands/` or skill |

Default to asking which intent is meant only when truly ambiguous.

---

## Tool Constraints

| Tool | Constraint | Workaround |
|------|-----------|------------|
| WebFetch | Blocked by bot protection (403) | Use playwright-cli (`--headed --persistent`) |

---

## Shell Commands

### mise exec Required

These commands must run via `mise exec --`:

| Category | Commands |
|----------|----------|
| Ruby | `bundle`, `rails`, `rspec`, `ruby` |
| Node.js | `pnpm`, `node`, `npm` |

Reason: Ensures correct environment variables managed by mise.

Compound commands: prefix only the outermost listed binary. Examples:
- `mise exec -- bundle exec rspec` (not `mise exec -- bundle exec mise exec -- rspec`)
- `mise exec -- pnpm run lint`
- `mise exec -- bundle install && mise exec -- bundle exec rails db:migrate` (chain each subcommand separately)

