# Skill Execution & Authoring (Claude Code)

## Slash-command rendering expands `$0`–`$9`

**Slash-command rendering expands `$0`–`$9`** before the skill body reaches the model (empty string when no argument), so the block is already broken on arrival. `$0` is included: awk `line[NR] = $0` in convert-hatena-blog-to-obsidian arrived as `line[NR] = <the URL argument>`. Never write `$0`–`$9` in the body of a skill invoked as a slash command; pass values via environment variables instead (`N="${N:-10}" bash <<'SCRIPT'`). In awk, reference the record and fields as `$(0)` / `$(1)`, which awk reads identically. `${...}` outside the heredoc is fine (the outer shell expands it). If a skill "looks broken" around a dollar-digit, Read the SKILL.md file — the rendered prompt likely diverges from the file on disk. When scanning a skill for this, grep `\$[0-9]`, not `\$[1-9]`.

## skill-creator eval limits in this environment (subscription CLI, no API key)

- `run_loop.py` cannot run (needs the `anthropic` package + an API key). Use `run_eval.py` (`claude -p`, no key needed) and improve descriptions by hand.
- `run_eval.py` recall (should_trigger) is meaningless when the real skill is installed — the real skill triggers instead of the stub, producing false FAILs. Precision (should_not_trigger) is trustworthy. Verify recall by actually running the skill.
- Multi-line descriptions: `run_eval.py` reads only line 1 of the frontmatter description; pass the full text explicitly via `--description "<full text>"`. The production harness reads the full description, so real-world triggering is unaffected.
- `aggregate_benchmark.py` requires the exact layout `eval-N/<config>/run-N/grading.json` (the `run-N` subdirectory is mandatory; files directly under `<config>` aggregate to 0%), and grading.json needs a `summary: {pass_rate, passed, failed, total}` field alongside `expectations`.
