# AGENTS.md

> Global shared rules for Claude Code, Codex, and Antigravity (SSOT: `~/ghq/github.com/shifumin/dotfiles/AGENTS.md`). After editing this file or `.claude/output-styles/emma.md`, run `.codex/build-agents.sh` and commit the generated files.

## Core Principles

1. **Skills first**: Use matching skills before calling MCP tools directly.
2. **Fetch before update**: Before editing external documents (GitHub PR/issue, Jira, Notion, etc.), fetch the latest remote state to preserve concurrent human edits.
3. **Recommend on merit**: Recommend the best outcome regardless of AI implementation effort; weigh cost only when it falls on humans or is hard to reverse. Apply the same bar to review findings (mark out-of-scope findings as undecided, not unnecessary).

## User

The user is `shifumin` (しふみん).

## I/O Rules

- **Japanese output**: Avoid coined words; keep English technical terms when Japanese translations are unnatural.
- **Document language**: Write `README.md`, `AGENTS.md`, `CLAUDE.md`, and `.claude/rules/*.md` in English.
- **Rules and skills**: Keep text short and plain. Add only what changes behavior; rewrite an existing line instead of appending.
- **Public repositories**: Never include personal, work-related, or secret info (real name, employer, internal IDs/URLs, tokens); use placeholders.
- **Posts as the user**: Slack messages and GitHub comments/replies omit trailing 「。」 and separate sentences with line breaks; use bullet lists in Slack, not tables (PR descriptions and Notion pages exempt).
- **Voice input**: User input is often voice-transcribed Japanese (SuperWhisper); silently infer intended terms and homophones without asking.

## Shortcuts

Skill-specific argument tables override these shortcuts.

- `ba` — Before/After format for proposed changes.
- `k` — Kaizen: reflect on the session and apply improvements to rules, skills, or workflows.
- `q` — Question: ask clarifying questions (use a structured question tool when available) until ambiguities are resolved, then wait for confirmation.
- `r` — Recommended: proceed with the recommended option.
- `rr` — Remove Redundancy: trim duplicates and padding from the target (or last edited) file, keeping distinct rationales, and report what changed.
- `y` — YES / Done: interpret from context and proceed.
- `z` — Zero-base: disregard the current approach and back-cast from the ideal state.

## Tool Constraints

- **Web fetch & browser escalation**: Start with `ax` (never bare `curl` for HTML scraping). Escalate by failure reason:
  - 403 / bot-blocked read-only public page (or known 403 sites like `dic.pixiv.net`, `w.atwiki.jp`) → `cf-md <URL>` (serial; fall back to `agent-browser` if auth unavailable; never auto-route to web archives).
  - HTTP 200 JS-rendered SPA, empty `<body>`, exact DOM/`<title>`, or general login/interaction → `agent-browser`.
  - Real Chrome / company SSO (`attach --cdp=chrome`, e.g. Google Docs/Sheets — check there before asking the user for downloads) or site-specific Playwright workarounds → `playwright-cli` (see skill for flag rules).
  - Use built-in web fetch only when AI distillation of a long page is the goal.
- **Notion MCP writes**: Wrap identifiers, paths, filenames, emails, and dotted words in backticks; build `old_str` from fetched text; use only `[A-Za-z0-9-]` in placeholders; verify by reading back.

## Shell Commands

- Run Ruby (`bundle`, `rails`, `rspec`, `ruby`) and Node.js (`pnpm`, `node`, `npm`) through `mise exec --`, prefixing each subcommand in compound commands (`mise exec -- bundle install && mise exec -- bundle exec rspec`).
- **macOS zsh environment**:
  - `noclobber` is on: use `>|` to overwrite existing files.
  - `rm`, `cp`, `mv` are aliased with `-i`: use `command rm -f` / `command cp -f` / `command mv -f`.
  - Quote `@{...}` (`'@{upstream}'`, `'HEAD@{1}'`) so zsh does not brace-expand it.
  - Global mise enables idiomatic version files for Ruby only: change Node versions in `mise.toml`, never create `.node-version`.

## Git & Code

- **Commits**: English Conventional Commits (`feat:`, `fix:`, `docs:`, etc.) with optional body; project rules override.
- **Tests**: Cover public interfaces only (do not test private methods directly).
- **Ruby YARD**: Add `@param`, `@return`, and `@raise` to public methods you add or modify; do not retrofit untouched methods.
- **Skill bash blocks**: Run `bash <<'SCRIPT'` blocks from `SKILL.md` verbatim; update the skill first if changes are needed.

## Concise Responses

Applies to response prose only (never skip tool calls, verification, error output, security warnings, or destructive-action confirmations) and overrides general tone/persona verbosity.

- Lead with the result in the first sentence; omit preambles, step narration, and closing recaps.
- Default to 1–3 sentences for simple questions; use structure only when it helps, and expand when asked.
- Keep the active persona's voice without filler interjections or emotional padding.
