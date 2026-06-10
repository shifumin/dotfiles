# CLAUDE.md

> **Scope**: Global — applies to ALL projects via symlink `~/.claude/CLAUDE.md`
> **Source**: `~/ghq/github.com/shifumin/dotfiles/.claude/CLAUDE.md` — edit here, commit in dotfiles repo
> **Mechanism**: `setup.sh` creates symlink; do not copy this file manually

---

## Core Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | Skills first | Check and use Skills before MCP tools. Use `find-skills` skill when unsure whether a relevant skill exists |
| 2 | Fetch before update | When updating external documents (GitHub PR/issue descriptions, Jira tickets, Notion pages, etc.), fetch the latest remote state first and base the update on it. Concurrent human edits must not be overwritten |

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
| Shortcut input | `r` input = Recommended — proceed with the recommended option from the most recent proposal |
| Shortcut input | `y` input = YES / Done — interpret from context and proceed |
| Shortcut input | `z` input = Evaluate from zero-base: ignore existing content/approach, assess from ideal state, propose improvements by back-casting from the ideal |

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

