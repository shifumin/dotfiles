# CLAUDE.md

> **Scope**: Global — applies to ALL projects via symlink `~/.claude/CLAUDE.md`
> **Source**: `~/ghq/github.com/shifumin/dotfiles/.claude/CLAUDE.md` — edit here, commit in dotfiles repo
> **Mechanism**: `setup.sh` creates symlink; do not copy this file manually

---

## Core Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | Skills first | Check and use Skills before MCP tools. Use `gh skill search <keyword>` when looking for an installable skill |
| 2 | Fetch before update | When updating external documents (GitHub PR/issue descriptions, Jira tickets, Notion pages, etc.), fetch the latest remote state first and base the update on it. Concurrent human edits must not be overwritten |

---

## User

The user's name is shifumin (しふみん). When an Output Style specifies an address form (e.g. the `emma` style's "〜ちゃん" suffix), apply it to this name — do not substitute persona example names.

---

## I/O Rules

| Category | Rule |
|----------|------|
| Japanese output | No coined words; use English terms when Japanese translation is unnatural |
| Document language | README.md, CLAUDE.md, AGENTS.md, and `.claude/rules/*.md` are written in English |
| Voice input | User input is often voice-transcribed (Japanese via SuperWhisper). Silently infer intended meaning for homophones, misrecognized technical terms (e.g. "cloud.md" → CLAUDE.md), and slightly unnatural phrasing; do not ask about obvious transcription errors |

---

## Shortcuts

| Input | Meaning |
|-------|---------|
| `ba` | Before/After: show proposed changes in before/after format |
| `k` | Kaizen: reflect on this session, find process/artifact improvements (CLAUDE.md, rules, skills, workflows, etc.), and apply them. Use skill-creator skill when improving skills |
| `q` | Question: ask clarifying questions using AskUserQuestion repeatedly until all ambiguities are resolved, then wait for explicit instruction to proceed |
| `r` | Recommended — proceed with the recommended option from the most recent proposal |
| `y` | YES / Done — interpret from context and proceed |
| `z` | Zero-base: ignore existing content/approach, assess from ideal state, propose improvements by back-casting from the ideal |

---

## Tool Constraints

| Tool | Constraint | Workaround |
|------|-----------|------------|
| Web fetch | WebFetch is often bot-blocked (403) and costs tokens; ax cannot execute JS | Default to `ax` for API calls, static-page extraction, and page exploration (see ax skill; local fetch often passes where WebFetch is blocked, e.g. Amazon). Use WebFetch only when AI distillation of a long page is the goal. When ax cannot render the page, escalate per the Browser automation row below |
| Browser automation | Three tools overlap (agent-browser / playwright-cli / claude-in-chrome); picking the wrong one wastes a browser launch and can hang the call | Escalate in this order: **`ax` → `agent-browser` → `playwright-cli`**. agent-browser is the default browser tool (JS-rendered SPAs, an empty `<body>` from ax, most login-gated pages). Drop to playwright-cli only when the task needs the real Chrome via `attach --cdp=chrome` (AI service sessions), or the site has a proven playwright-cli-specific workaround: Cloudflare/queue-it → plain Chromium persistent (never `--browser=chrome`), general auth sites → `--persistent --headed`. **Never pass `--persistent`/`--headed` to a page that needs no login** — the profile launch is slow enough to hang the call (real failure: a municipal SPA timed out at 120s under `--headed --persistent`, then loaded instantly with a bare `agent-browser open`) |

---

## Shell Commands

Ruby (`bundle`, `rails`, `rspec`, `ruby`) and Node.js (`pnpm`, `node`, `npm`) commands run via `mise exec --`, e.g. `mise exec -- bundle exec rspec`. In compound commands, prefix each subcommand separately. Reason: ensures correct environment variables managed by mise.

Enforced deterministically by `~/.claude/hooks/mise-exec-guard.sh` (PreToolUse on Bash).

