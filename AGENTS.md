# AGENTS.md

> **Scope**: Global — shared rules for ALL coding agents (Claude Code and Codex) in ALL projects
> **Source**: `~/ghq/github.com/shifumin/dotfiles/AGENTS.md` — the single source of truth; edit here, commit in dotfiles repo
> **Mechanism**: Claude Code imports this file from `.claude/CLAUDE.md`. Codex cannot import, so `.codex/build-agents.sh` concatenates this file with `.codex/AGENTS.codex.md` into the generated `.codex/AGENTS.md` (symlinked to `~/.codex/AGENTS.md`). **After editing this file, run `.codex/build-agents.sh` and commit the regenerated `.codex/AGENTS.md`** (`.codex/build-agents.sh --check` exits 1 on drift)
> **Layout**: shared rules → this file; Claude-only → `.claude/CLAUDE.md` and `.claude/rules/*.md`; Codex-only → `.codex/AGENTS.codex.md`. Auth, permissions, and sessions are never shared

---

## Core Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | Skills first | Check and use Skills before MCP tools. Use `gh skill search <keyword>` when looking for an installable skill |
| 2 | Fetch before update | When updating external documents (GitHub PR/issue descriptions, Jira tickets, Notion pages, etc.), fetch the latest remote state first and base the update on it. Concurrent human edits must not be overwritten |
| 3 | Recommend on merit | When proposing options, recommend the one with the best result. Do not let the cost of applying the change (number of edits, files touched, rework) bias the recommendation — for an AI that cost is near zero. Mention cost only when it falls on a human (manual work, review burden) or the change is hard to reverse |

---

## User

The user's name is shifumin (しふみん). When a persona (Claude Code: the `emma` Output Style; Codex: the Persona section) specifies an address form (the "〜ちゃん" suffix), apply it to this name — do not substitute persona example names.

---

## I/O Rules

| Category | Rule |
|----------|------|
| Japanese output | No coined words; use English terms when Japanese translation is unnatural |
| Document language | README.md, AGENTS.md, CLAUDE.md, and `.claude/rules/*.md` are written in English |
| Voice input | User input is often voice-transcribed (Japanese via SuperWhisper). Silently infer intended meaning for homophones, misrecognized technical terms (e.g. "cloud.md" → CLAUDE.md / AGENTS.md), and slightly unnatural phrasing; do not ask about obvious transcription errors |

---

## Shortcuts

| Input | Meaning |
|-------|---------|
| `ba` | Before/After: show proposed changes in before/after format |
| `k` | Kaizen: reflect on this session, find process/artifact improvements (AGENTS.md, CLAUDE.md, rules, skills, workflows, etc.), and apply them. Use skill-creator skill when improving skills |
| `q` | Question: ask clarifying questions repeatedly (with the agent's structured question tool when available) until all ambiguities are resolved, then wait for explicit instruction to proceed |
| `r` | Recommended — proceed with the recommended option from the most recent proposal |
| `rr` | Remove Redundancy: trim duplicates, restatements, and padding from the argument file (else the last file worked on), then report what was cut and what was kept. Keep a rule's reason even if its conclusion is stated elsewhere |
| `y` | YES / Done — interpret from context and proceed |
| `z` | Zero-base: ignore existing content/approach, assess from ideal state, propose improvements by back-casting from the ideal |

---

## Tool Constraints

| Tool | Constraint | Workaround |
|------|-----------|------------|
| Web fetch | Built-in web fetch tools (e.g. WebFetch) are often bot-blocked (403) and cost tokens; ax cannot execute JS | Default to `ax` for API calls, static-page extraction, and page exploration (see ax skill; local fetch often passes where built-in fetch is blocked, e.g. Amazon). Use a built-in fetch tool only when AI distillation of a long page is the goal. When ax cannot render the page, escalate per the Browser automation row below |
| Browser automation | Three tools overlap (agent-browser / playwright-cli / claude-in-chrome); picking the wrong one wastes a browser launch and can hang the call | Escalate in this order: **`ax` → `agent-browser` → `playwright-cli`**. agent-browser is the default browser tool (JS-rendered SPAs, an empty `<body>` from ax, most login-gated pages). Drop to playwright-cli only when the task needs the real Chrome via `attach --cdp=chrome` (AI service sessions), or the site has a proven playwright-cli-specific workaround: Cloudflare/queue-it → plain Chromium persistent (never `--browser=chrome`), general auth sites → `--persistent --headed`. **Never pass `--persistent`/`--headed` to a page that needs no login** — the profile launch is slow enough to hang the call (real failure: a municipal SPA timed out at 120s under `--headed --persistent`, then loaded instantly with a bare `agent-browser open`) |

---

## Shell Commands

Ruby (`bundle`, `rails`, `rspec`, `ruby`) and Node.js (`pnpm`, `node`, `npm`) commands run via `mise exec --`, e.g. `mise exec -- bundle exec rspec`. In compound commands, prefix each subcommand separately (`mise exec -- bundle install && mise exec -- bundle exec rails db:migrate`), but only the outermost listed binary (not `mise exec -- bundle exec mise exec -- rspec`). Reason: ensures correct environment variables managed by mise.

---

## Shell Pitfalls (macOS)

Distilled from real failures on this machine.

### Interactive zsh behavior

- **Always quote `@{...}`**: bare `@{upstream}` / `HEAD@{1}` gets mangled by zsh brace expansion into `fatal: ambiguous argument`. Write `'@{upstream}'` — including in example code inside skills.
- **noclobber is on**: `>` to an existing file fails with `zsh: file exists` and the file KEEPS ITS OLD CONTENT — a prime source of stale reads and hallucinated success. Use `>|` to force-overwrite, a unique filename per run, or `>>` to append.

### macOS /bin/bash is 3.2

1. No `mapfile` (bash 4.0+). Use `while IFS= read -r line; do ARR+=("$line"); done < <(...)`.
2. `date -j` argument order: put `-v+Nd` BEFORE `-f "fmt"`; placed after, `-v` may be silently ignored. Correct: `date -j -v+Nd -f "fmt" input "+output_fmt"`.
3. `read` with `IFS=$'\t'` collapses consecutive tabs (whitespace IFS), so empty TSV fields shift columns. Use a non-whitespace delimiter (`|`) for intermediate data, or process with `awk -F'\t'` (awk does not collapse).

### Commands that read stdin inside loops

`obsidian`, `ssh`, `ffmpeg`, `docker run`, etc. consume the `while read` input stream, ending the loop after one iteration. Append `</dev/null` to such commands inside loops.

### Deletion

Plain `rm` is aliased to `-i` on this machine, so it prompts. An agent shell is non-interactive: the prompt reads EOF as "no", the file survives, and the command still **exits 0** — a deletion that reports success without happening (hit for real: `rm <symlink> && echo deleted` printed "deleted" with the symlink still in place). Delete with `/bin/rm -f` (or `command rm -f`), then verify each path individually with `[ -e ]` / `[ -L ]`.

### Verification discipline

- Verify file existence/content with ONE deterministic command: `test -f` alone, or a single read. Bundling checks with `&&`/`echo` interleaves output and has caused "file exists" misreads.
- When a result looks wrong or "same as before", suspect a stale read (noclobber above) before re-running the check repeatedly.
- Never report an API write as successful from the write response alone — read the data back via the API first.

### Node version management (mise)

Global mise config sets `idiomatic_version_file_enable_tools = ["ruby"]`, so `.node-version` is IGNORED by mise. Change node versions by editing `mise.toml` only; never propose creating `.node-version`.

---

## Git Conventions

### Commit Messages

Language: English only.
Format: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, etc.).
Project-level instructions (AGENTS.md / project CLAUDE.md) that specify a different commit format take precedence over this rule.
Body: Add details after a blank line when needed (in English).

### Batch Operation Pitfalls

These produce "looked successful, actually not applied":

- `git add a b c` aborts entirely (stages NOTHING) if one pathspec doesn't match. Don't mix `git rm`-ed paths into a later `git add`; list only existing files.
- `git push | tail; echo $?` reports tail's exit code, so push failures (no upstream, no remote) look like exit 0. Judge with `if git push --quiet; then`, or verify `git rev-parse HEAD` == `git rev-parse '@{u}'` (quotes required under zsh).
- In multi-repo batch work, final-verify HEAD == upstream per repo, and check `git remote -v` first — some repos have no remote.

### Global .gitignore Scope

Global `~/.gitignore` (symlinked from this repo) is intentionally limited to macOS OS junk and `.claude/settings.local.json` (~30 lines).

- Never add language/framework patterns (Ruby, Rails, Node, ...) globally — they belong in each project's `.gitignore`. Push back if asked.
- If a global pattern is truly warranted, prefer anchored (`/Foo`) or escape-explicit (`Icon\r`) forms; bare names match recursively AND case-insensitively on macOS (a bare `Icon` rule once false-matched `public/icon/` directories).
- Don't reintroduce the Finder `Icon` rule; Finder icon files are rare and harmless to commit.

---

## Code Quality

### Test Rules

Tests cover public interfaces only (not private methods). Each public interface's test suite covers normal cases, error cases, and edge cases.

Reason: Avoid coupling to internal implementation, improve refactoring resilience.

### YARD Comments (Ruby only)

Public methods you add or modify have YARD comments: `@param`, `@return`, `@raise`. Do not retrofit YARD onto untouched methods.

Reason: Enables accurate code understanding by AI and IDEs.

---

## Skill Execution & Authoring

### Run skill bash blocks verbatim

`bash <<'SCRIPT'` blocks in SKILL.md are finished artifacts — copy them to the shell unmodified. A single dropped character (`$1`, `!`, `&&`, backslash) can fail silently: awk `$1==f` mistyped as `==f` matches every line, breaking dedup without any error. If a block needs changing, update the skill first, then run it — never improvise mid-run.

### Sanity-check regexes before committing them into a skill

Test grep/regex patterns on typical domain data first: Markdown with lists/headings/code blocks, JSON with arrays/null/escapes. "Intuitively correct" patterns often misfire — e.g. counting diff deletions with `^-[^-]` drops Markdown list lines (`-- xxx` = diff prefix + list dash). When excluding something, verify the pattern doesn't also exclude what must be kept. When a subagent reports "this command doesn't work as expected", suspect a bug in the skill's pattern FIRST, not the subagent's usage.

### Skill arguments beat global shortcuts

If a skill defines its own argument table, interpret arguments by that table before global shortcut meanings (`y` = YES, etc.). Real failure: `/carry-over-tasks y` means "yesterday" per the skill, not YES.

---

## Concise Responses

Governs response prose only. Where these rules conflict with more general communication, formatting, or tone guidance elsewhere in the instructions — including the active persona — these rules win.

1. **Lead with the result.** The first sentence answers "what happened" or "what's the answer". No preamble ("Let me...", "Now I'll...", "確認してみるね") and no closing recap of what was already said.
2. **Cut narration, keep substance.** Do not restate the request, the plan, or each step taken. Report outcomes, decisions, and anything the user must act on.
3. **Short by default.** Answer simple questions in 1-3 sentences of plain prose. Use headings, tables, and bullet lists only when they carry real structure, never as decoration.
4. **State things plainly.** Skip hedging boilerplate. Mention a caveat only when it changes what the user should do next.
5. **Give full detail on request.** When the user asks for an explanation or detail, answer completely. Conciseness never means withholding requested information.
6. **Never trade correctness for brevity.** Error reports, failing test output, security warnings, and confirmations for destructive actions keep their full content.

Brevity applies to the response text, not to the work. Do not skip tool calls, verification, or parts of the task in order to answer shortly.

The persona's tone still applies — first person, sentence endings, characteristic phrases. Only the volume changes: same voice, fewer words. Drop filler interjections and emotional padding that carry no information.
