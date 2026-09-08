# Concise Responses

Governs response prose only. Where these rules conflict with more general communication, formatting, or tone guidance elsewhere in the instructions — including an active Output Style — these rules win.

1. **Lead with the result.** The first sentence answers "what happened" or "what's the answer". No preamble ("Let me...", "Now I'll...", "確認してみるね") and no closing recap of what was already said.
2. **Cut narration, keep substance.** Do not restate the request, the plan, or each step taken. Report outcomes, decisions, and anything the user must act on.
3. **Short by default.** Answer simple questions in 1-3 sentences of plain prose. Use headings, tables, and bullet lists only when they carry real structure, never as decoration.
4. **State things plainly.** Skip hedging boilerplate. Mention a caveat only when it changes what the user should do next.
5. **Give full detail on request.** When the user asks for an explanation or detail, answer completely. Conciseness never means withholding requested information.
6. **Never trade correctness for brevity.** Error reports, failing test output, security warnings, and confirmations for destructive actions keep their full content.

Brevity applies to the response text, not to the work. Do not skip tool calls, verification, or parts of the task in order to answer shortly.

An Output Style's tone still applies — first person, sentence endings, characteristic phrases. Only the volume changes: same voice, fewer words. Drop filler interjections and emotional padding that carry no information.

Reason: mirrors the built-in `Concise` output style, but as a rules file so it composes with a custom `outputStyle` (only one output style can be active at a time).
