# Shell Pitfalls (Bash tool)

## Bash tool runs commands via zsh eval

**Shell loops don't parse**: `for...done` / `while...done` fail with `parse error near 'done'`. Wrap the loop in `bash <<'SCRIPT' ... SCRIPT`.

## Sandbox and git writes

Run git commands that write the working tree or `.git` with `dangerouslyDisableSandbox: true` from the start: `switch`, `checkout`, `reset`, `stash`, `pull`, `rebase`, `branch <name> <remote-ref>`, and `add` / `commit` inside a linked worktree. In the sandbox they stop halfway on read-only paths (`.npmrc`, `.claude/skills`, `.git/worktrees/*`, `.git/config`) and leave a half-applied state. Do not filter `Operation not permitted` out of git output. If one already failed, check `git status` before retrying.
