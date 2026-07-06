# Skill Execution & Authoring

## Run skill bash blocks verbatim

`bash <<'SCRIPT'` blocks in SKILL.md are finished artifacts — copy them to the Bash tool unmodified. A single dropped character (`$1`, `!`, `&&`, backslash) can fail silently: awk `$1==f` mistyped as `==f` matches every line, breaking dedup without any error. If a block needs changing, update the skill first, then run it — never improvise mid-run.

**Slash-command rendering expands `$1`–`$9`** before the skill body reaches the model (empty string when no argument), so the block is already broken on arrival. Never write `$1`–`$9` in the body of a skill invoked as a slash command; pass values via environment variables instead (`N="${N:-10}" bash <<'SCRIPT'`). `${...}` outside the heredoc is fine (the outer shell expands it). If a skill "looks broken" around `$1`, Read the SKILL.md file — the rendered prompt likely diverges from the file on disk.

## Sanity-check regexes before committing them into a skill

Test grep/regex patterns on typical domain data first: Markdown with lists/headings/code blocks, JSON with arrays/null/escapes. "Intuitively correct" patterns often misfire — e.g. counting diff deletions with `^-[^-]` drops Markdown list lines (`-- xxx` = diff prefix + list dash). When excluding something, verify the pattern doesn't also exclude what must be kept. When a subagent reports "this command doesn't work as expected", suspect a bug in the skill's pattern FIRST, not the subagent's usage.

## Skill arguments beat global shortcuts

If a skill defines its own argument table, interpret arguments by that table before global shortcut meanings (`y` = YES, etc.). Real failure: `/carry-over-tasks y` means "yesterday" per the skill, not YES.

## skill-creator eval limits in this environment (subscription CLI, no API key)

- `run_loop.py` cannot run (needs the `anthropic` package + an API key). Use `run_eval.py` (`claude -p`, no key needed) and improve descriptions by hand.
- `run_eval.py` recall (should_trigger) is meaningless when the real skill is installed — the real skill triggers instead of the stub, producing false FAILs. Precision (should_not_trigger) is trustworthy. Verify recall by actually running the skill.
- Multi-line descriptions: `run_eval.py` reads only line 1 of the frontmatter description; pass the full text explicitly via `--description "<full text>"`. The production harness reads the full description, so real-world triggering is unaffected.
- `aggregate_benchmark.py` requires the exact layout `eval-N/<config>/run-N/grading.json` (the `run-N` subdirectory is mandatory; files directly under `<config>` aggregate to 0%), and grading.json needs a `summary: {pass_rate, passed, failed, total}` field alongside `expectations`.
