# Skill Execution & Authoring (Claude Code)

When creating or updating skills (e.g. via the `k` shortcut), use the `skill-creator` plugin.

## Slash-command `$0`–`$9` expansion

Slash-command rendering substitutes `$0`–`$9` (`$0` = argument string or empty) before the skill body reaches the model, breaking inline scripts.

- Never write `$0`–`$9` in a slash-command skill body; pass values via env vars (`N="${N:-10}" bash <<'SCRIPT'`).
- In `awk`, write `$(0)` / `$(1)` instead of `$0` / `$1` (`${...}` outside heredocs is unaffected).
- If a skill misbehaves around `$<digit>`, read `SKILL.md` on disk and scan with `\$[0-9]`.

## `skill-creator` eval limits (subscription CLI, no API key)

- `run_loop.py` requires `anthropic` + API key; use `run_eval.py` (`claude -p`) and refine descriptions manually.
- `run_eval.py` recall (`should_trigger`) false-fails when the real skill is installed; trust precision (`should_not_trigger`) and test recall directly.
- `run_eval.py` reads only line 1 of multi-line frontmatter descriptions; pass `--description "<full text>"` explicitly.
- `aggregate_benchmark.py` requires `eval-N/<config>/run-N/grading.json` (`run-N` subdir mandatory) with `summary: {pass_rate, passed, failed, total}` alongside `expectations`.
