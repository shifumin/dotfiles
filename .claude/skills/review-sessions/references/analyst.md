# Analyst brief (one batch of session digests)

Each analyst subagent reads this file and follows the brief below the separator. Substitute `BATCH_FILES`, `SESSIONS_DIR`, and `SKILLS_TSV` from the parent's prompt.

---

You are reviewing past Claude Code and Codex sessions to find where the user's skills should change. Report findings only; edit nothing.

## Input

- Session digests (read every one): `{BATCH_FILES}` under `{SESSIONS_DIR}`
- Skill inventory: `{SKILLS_TSV}` (columns: `scope`, `name`, `path`, `description`)

Digest line prefixes:

| Prefix | Meaning |
|--------|---------|
| `U:` | user message (often voice-transcribed Japanese; ignore transcription noise) |
| `U-INTERRUPT` | user stopped the agent mid-turn |
| `A:` | assistant text (clipped) |
| `T:` | tool call: name and clipped input (`T: Skill skill=x` = skill invoked) |
| `R-ERROR` / `R-ERROR?` / `R-REJECTED` | failed, possibly failed (Codex heuristic), or user-rejected tool call |
| `HARNESS:` | harness-injected turn (task notification etc.), not the user |

When a finding depends on clipped detail, inspect the original transcript in the digest header (`source:`): e.g. `jq -c 'select(.timestamp >= "2026-11-17T03:40")' <source> | head -40` (pipe `.zst` sources through `zstd -dc`).

## What to look for

1. **User corrections / frustration**: 「違う」「そうじゃなくて」「また」「さっきも言った」, repeated re-requests, `U-INTERRUPT`, `R-REJECTED`. Check whether a skill's instructions caused the mistake or failed to prevent it.
2. **Stumbles inside a skill run**: after `T: Skill skill=x`, errors, retries, improvised steps, or skipped steps. Open the current `SKILL.md` (path in `{SKILLS_TSV}`) and verify whether it is wrong, missing, or ambiguous.
3. **Repeated manual work**: the same request or tool sequence recurring across multiple sessions with no covering skill (new-skill candidate). Skip one-off tasks regardless of length.

## Judging a finding

- Locate the cause first: wrong/missing skill instruction → `skill-fix`; model ignoring a clear rule → usually not a skill change (or propose a hook if enforcement is required); environment issue (sandbox, network, auth) → rule/memory unless a skill walks into it.
- Prefer fixing an existing skill over proposing a new one.
- Drop findings already fixed in the current `SKILL.md`.
- Keep only recurring issues with a general lesson.

## Scope rules

Use the inventory's `scope` for existing skills. For new skills:
- `new-global`: useful across projects (dotfiles)
- `new-vault`: specific to the personal Obsidian vault (notes, diary, blog, finances)
- `new-team`: tied to a work repository or team workflow (proposal only)

## Output

Return only the following in Japanese, one block per finding, highest impact first. If nothing qualifies, return `所見なし` and the count.

```
### <short title>
- kind: skill-fix | new-skill | non-skill
- target: <existing skill name | proposed skill name | file such as AGENTS.md / a hook>
- scope: own-global | own-vault | vendored | team | external | new-global | new-vault | new-team | rules | hook | memory
- signal: correction | stumble | repetition
- evidence: <digest file> [MM-DD HH:MM] — <one-line quote or paraphrase>（1件以上。複数セッションなら全部）
- cause: <what in the skill (or its absence) produced the problem>
- proposal: <concrete edit: section + addition/rewrite, or new skill trigger and steps>
- confidence: high | medium | low
```

End with one line: `read: <n> sessions`.
