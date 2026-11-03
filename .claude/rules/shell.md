# Shell Pitfalls (Bash tool)

## Bash tool runs commands via zsh eval

**Shell loops don't parse**: `for...done` / `while...done` fail with `parse error near 'done'`. Wrap the loop in `bash <<'SCRIPT' ... SCRIPT`.
