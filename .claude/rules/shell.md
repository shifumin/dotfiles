# Shell Pitfalls (Bash tool / macOS)

Distilled from real failures on this machine. Applies to all projects.

## Bash tool runs commands via zsh eval

1. **Shell loops don't parse**: `for...done` / `while...done` fail with `parse error near 'done'`. Wrap the loop in `bash <<'SCRIPT' ... SCRIPT`.
2. **Always quote `@{...}`**: bare `@{upstream}` / `HEAD@{1}` gets mangled by zsh brace expansion into `fatal: ambiguous argument`. Write `'@{upstream}'` — including in example code inside skills.
3. **noclobber is on**: `>` to an existing file fails with `zsh: file exists` and the file KEEPS ITS OLD CONTENT — a prime source of stale reads and hallucinated success. Use `>|` to force-overwrite, a unique filename per run, or `>>` to append.

## macOS /bin/bash is 3.2

1. No `mapfile` (bash 4.0+). Use `while IFS= read -r line; do ARR+=("$line"); done < <(...)`.
2. `date -j` argument order: put `-v+Nd` BEFORE `-f "fmt"`; placed after, `-v` may be silently ignored. Correct: `date -j -v+Nd -f "fmt" input "+output_fmt"`.
3. `read` with `IFS=$'\t'` collapses consecutive tabs (whitespace IFS), so empty TSV fields shift columns. Use a non-whitespace delimiter (`|`) for intermediate data, or process with `awk -F'\t'` (awk does not collapse).

## Commands that read stdin inside loops

`obsidian`, `ssh`, `ffmpeg`, `docker run`, etc. consume the `while read` input stream, ending the loop after one iteration. Append `</dev/null` to such commands inside loops.

## Verification discipline

- Verify file existence/content with ONE deterministic command: `test -f` alone, or a single read. Bundling checks with `&&`/`echo` interleaves output and has caused "file exists" misreads.
- When a result looks wrong or "same as before", suspect a stale read (noclobber above) before re-running the check repeatedly.
- Never report an API write as successful from the write response alone — read the data back via the API first.

## Node version management (mise)

Global mise config sets `idiomatic_version_file_enable_tools = ["ruby"]`, so `.node-version` is IGNORED by mise. Change node versions by editing `mise.toml` only; never propose creating `.node-version`.
