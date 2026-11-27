---
name: agent-browser
description: Browser automation CLI (Rust + CDP). Use to interact with websites - navigate, fill forms, click, take screenshots, extract data, or automate any browser task. Check this before defaulting to playwright-cli or claude-in-chrome.
allowed-tools: Bash(agent-browser:*)
---

# agent-browser

Browser automation CLI (Rust + CDP, no Playwright/Puppeteer dependency). This skill has no command reference: the CLI ships version-matched docs, so load them below instead of guessing syntax from memory.

## Before using any command

```bash
agent-browser --version               # confirm it's installed
agent-browser skills get core --full  # full command reference: snapshot/ref model,
                                       # waiting, sessions, eval, auth, troubleshooting
```

Load a specialized skill when the target isn't a standard web page:

```bash
agent-browser skills get electron        # Electron desktop apps (VS Code, Slack, Discord, Figma...)
agent-browser skills get slack           # Slack workspace automation
agent-browser skills get dogfood         # exploratory testing / QA / bug hunts
agent-browser skills get vercel-sandbox  # Vercel Sandbox microVMs
agent-browser skills get agentcore       # AWS Bedrock AgentCore cloud browser
```

## Local lessons

- **Never let a `--profile <dir>` directory get committed to git.** It's a real Chrome user-data-dir (Cookies, Login Data, History, Local/Session Storage — actual session secrets, not config). Add the directory to `.gitignore` *before* first use, especially in a vault/repo with an auto-commit tool (e.g. Obsidian Git) running in the background — auto-commit races the moment the profile is created and won't wait for you to gitignore it.
- Core loop: `open <url>` → `snapshot -i` → `click @eN` / `fill @eN` → re-snapshot after anything that changes the page. Refs go stale the instant the page changes.
- Persistent login across separate command invocations: `--session <name> --profile <dir> --headed open <url>`. The exact same command works whether the session is brand new or already running in the background daemon — no need to branch on "does a session already exist" (unlike playwright-cli's `list` → branch pattern).
- `eval --stdin` (heredoc) runs JS directly in the page context — no `async page => {...}` wrapper like playwright-cli's `run-code`. For multi-step logic with waits, use an async IIFE: `(async () => { ...; await new Promise(r => setTimeout(r, 5000)); ...; return result; })()`. Returning a plain object (not a pre-stringified JSON string) prints pretty-printed, parseable JSON.
- Prefer `eval --stdin` over inline `eval "..."` for anything beyond trivial expressions — shell quoting with nested quotes is error-prone.

## Installation

```bash
npm install -g agent-browser && agent-browser install   # or: brew install agent-browser
```
