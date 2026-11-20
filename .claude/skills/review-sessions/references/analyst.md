# Analyst brief (one batch of session digests)

Each analyst subagent reads this file and follows the brief below the separator. The parent's prompt gives `BATCH_FILES`, `SESSIONS_DIR`, and `SKILLS_TSV`; substitute them for `{BATCH_FILES}`, `{SESSIONS_DIR}`, and `{SKILLS_TSV}`.

---

You are reviewing past Claude Code and Codex sessions of one user to find where their skills should change. You only report; you edit nothing.

## Input

- Session digests (read every one): {BATCH_FILES} under `{SESSIONS_DIR}`
- Skill inventory: `{SKILLS_TSV}` (columns: scope, name, path, description)

A digest is a time-ordered list of lines:

| Prefix | Meaning |
|--------|---------|
| `U:` | user message (voice-transcribed Japanese; ignore transcription noise) |
| `U-INTERRUPT` | the user stopped the agent mid-turn |
| `A:` | assistant text, clipped |
| `T:` | tool call: name and a clipped input. `T: Skill skill=x` means skill x was invoked |
| `R-ERROR` / `R-ERROR?` / `R-REJECTED` | failed, possibly failed (Codex, heuristic), or user-rejected tool call |
| `HARNESS:` | harness-injected turn (task notifications etc.), not the user |

Lines are clipped. When a finding depends on detail the digest cut off, open the original transcript named in the digest header (`source:`) and read only the lines you need, e.g. `jq -c 'select(.timestamp >= "2026-11-17T03:40")' <source> | head -40`. Codex sources ending in `.zst` need `zstd -dc` first.

## What to look for

1. **User corrections and frustration**: 「違う」「そうじゃなくて」「また」「さっきも言った」, a re-request of the same thing, `U-INTERRUPT`, `R-REJECTED`. Ask what the agent did that the user had to undo, and whether a skill's instructions led it there or failed to stop it.
2. **Stumbles inside a skill run**: after `T: Skill skill=x`, errors, retries, the agent improvising a step the skill does not cover, or skipping one it does. Open the skill's SKILL.md (path in the inventory) and check whether the instructions are wrong, missing, or ambiguous on that point.
3. **Repeated manual work**: the same kind of request or the same tool-call sequence appearing in several sessions (in your batch, or likely across batches) with no skill behind it. These are new-skill candidates. A one-off task is not a candidate, however long it was.

## Judging a finding

- Locate the cause before proposing a fix. A skill instruction that is wrong or missing → skill change. The model ignoring a clear instruction → usually not a skill change (say so, or propose a hook if it must be enforced). An environment problem (sandbox, network, auth) → a rule or memory, unless a skill's procedure walks into it.
- Prefer the existing skill. Propose a new skill only when no skill in the inventory covers the job.
- Check the skill as it is now. If the current SKILL.md already handles the problem (fixed after the session), drop the finding.
- Keep findings that would recur. Skip one-time mistakes with no general lesson.

## Where a fix goes (scope)

Use the inventory's scope for existing skills. For new skills:

- `new-global`: useful across projects → dotfiles
- `new-vault`: only meaningful inside the my-vault repository (Obsidian notes, diary, blog, money) → my-vault
- `new-team`: tied to one work repository or team process (e.g. a work product's repository or a team workflow) → proposal only

## Output

Return only this, in Japanese, one block per finding, most important first. If nothing qualifies, return `所見なし` and the number of sessions read.

```
### <short title>
- kind: skill-fix | new-skill | non-skill
- target: <existing skill name | proposed skill name | file such as AGENTS.md / a hook>
- scope: own-global | own-vault | vendored | team | external | new-global | new-vault | new-team | rules | hook | memory
- signal: correction | stumble | repetition
- evidence: <digest file> [MM-DD HH:MM] — <one-line quote or paraphrase>（1件以上。複数セッションなら全部）
- cause: <what in the skill (or its absence) produced the problem>
- proposal: <the concrete change: which section, what to add or rewrite, or the new skill's trigger and steps>
- confidence: high | medium | low
```

End with one line: `read: <n> sessions`.
