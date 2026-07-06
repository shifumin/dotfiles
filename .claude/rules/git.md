# Git Conventions

## Commit Messages

Language: English only.
Format: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, etc.).
Project-level instructions (AGENTS.md / project CLAUDE.md) that specify a different commit format take precedence over this rule.
Body: Add details after a blank line when needed (in English).

## Batch Operation Pitfalls

These produce "looked successful, actually not applied":

- `git add a b c` aborts entirely (stages NOTHING) if one pathspec doesn't match. Don't mix `git rm`-ed paths into a later `git add`; list only existing files.
- `git push | tail; echo $?` reports tail's exit code, so push failures (no upstream, no remote) look like exit 0. Judge with `if git push --quiet; then`, or verify `git rev-parse HEAD` == `git rev-parse '@{u}'` (quotes required under zsh).
- In multi-repo batch work, final-verify HEAD == upstream per repo, and check `git remote -v` first — some repos have no remote.

## Global .gitignore Scope

Global `~/.gitignore` (symlinked from this repo) is intentionally limited to macOS OS junk and `.claude/settings.local.json` (~30 lines).

- Never add language/framework patterns (Ruby, Rails, Node, ...) globally — they belong in each project's `.gitignore`. Push back if asked.
- If a global pattern is truly warranted, prefer anchored (`/Foo`) or escape-explicit (`Icon\r`) forms; bare names match recursively AND case-insensitively on macOS (a bare `Icon` rule once false-matched `public/icon/` directories).
- Don't reintroduce the Finder `Icon` rule; Finder icon files are rare and harmless to commit.
