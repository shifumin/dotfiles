# Shell Pitfalls (Bash tool)

## Bash tool runs via zsh eval

`for...done` and `while...done` fail with `parse error near 'done'`. Wrap loops in `bash <<'SCRIPT' ... SCRIPT`.

## Sandbox and git writes

Run git commands that write the working tree or `.git` (`switch`, `checkout`, `reset`, `stash`, `pull`, `rebase`, `branch <name> <remote-ref>`, and `add`/`commit` in a linked worktree) with `dangerouslyDisableSandbox: true` from the start. In the sandbox they abort partway on read-only paths (`.npmrc`, `.claude/skills`, `.git/worktrees/*`, `.git/config`) and leave a half-applied state. Keep `Operation not permitted` visible in output, and check `git status` before retrying a failed command.
