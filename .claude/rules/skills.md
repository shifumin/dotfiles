# Skill Execution & Authoring (Claude Code)

## Slash-command rendering expands `$0`–`$9`

Slash-command rendering substitutes `$0`–`$9` (including `$0` as the argument string, or empty when omitted) before the skill body reaches the model, breaking inline scripts on arrival.

- Never write `$0`–`$9` in a slash-command skill body; pass values via environment variables (`N="${N:-10}" bash <<'SCRIPT'`).
- In `awk`, write `$(0)` / `$(1)` instead of `$0` / `$1` (`${...}` outside heredocs is unaffected).
- When a skill behaves oddly around `$<digit>`, read `SKILL.md` on disk and scan with `\$[0-9]` (not `\$[1-9]`).

## `skill-creator` eval limits (subscription CLI, no API key)

- `run_loop.py` requires the `anthropic` package and an API key; use `run_eval.py` (`claude -p`) and refine descriptions manually.
- `run_eval.py` recall (`should_trigger`) produces false failures when the real skill is installed; trust precision (`should_not_trigger`) and verify recall by running the skill directly.
- `run_eval.py` reads only line 1 of multi-line frontmatter descriptions; pass `--description "<full text>"` explicitly (the production harness reads the full description).
- `aggregate_benchmark.py` requires `eval-N/<config>/run-N/grading.json` (the `run-N` subdirectory is mandatory) with `summary: {pass_rate, passed, failed, total}` alongside `expectations`.
