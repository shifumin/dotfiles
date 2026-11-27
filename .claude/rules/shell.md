# Shell Pitfalls (Bash tool)

## Bash tool runs zsh

zsh does not word-split unquoted variables (`for x in $LIST` loops once; `$CMD args` is one command name) and aborts on unmatched globs (`no matches found`). Run scripts that rely on bash semantics inside `bash <<'SCRIPT' ... SCRIPT`.

## Non-ASCII scripts

Do not pass scripts containing Japanese via stdin (`python3 - <<'PY'` fails with `Non-UTF-8 code`). Write them to a scratchpad file and run that (`mise exec -- ruby <file>` or `python3 -I <file>`).

## Sandbox

- Tools like `diff` cannot open `/dev/fd` paths, so `<(...)` arguments and `... | diff -` fail; use temp files or `$(...)` comparisons.
- Run git commands that write the working tree or `.git` (`switch`, `checkout`, `reset`, `stash`, `pull`, `rebase`, `branch <name> <remote-ref>`, and `add`/`commit` in a linked worktree) with `dangerouslyDisableSandbox: true` from the start. In the sandbox they abort partway on read-only paths (`.npmrc`, `.claude/skills`, `.git/worktrees/*`, `.git/config`) and leave a half-applied state. Keep `Operation not permitted` visible in output, and check `git status` before retrying a failed command.
