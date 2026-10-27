# Interview

How every interactive skill gathers what it needs. The user is the source of truth about their own
business, so ask them, in short rounds, and adapt to what they say. Nothing is read from a file.

## Run it in the conversation

Interactive skills run in the main conversation. Do not hand the work to a subagent: a subagent
cannot stop to ask a question and wait for the answer, so it ends up filling gaps
with placeholders, which is exactly what these skills exist to avoid. Use the owning agent's file as
your playbook for how to do the work, not as someone to delegate to.

If you find yourself running as a subagent anyway, follow the 'If you are running as a subagent'
section of your agent file.

## Before the first question

1. **Take what you already have.** Read the user's request and the conversation so far. Anything the user
   has already said is answered; do not ask it again.
2. **Confirm rather than re-ask.** If the user pasted notes or an earlier output, use it to pre-fill
   answers and check them in one line: "I have Acme as a technology partner in Tier 2, signed 3 June.
   Still right?" Where the user has no tiers, weights or stage names of their own, use the defaults
   in the framework references and say so once, in one line, at the end.
3. **Decide the mode.** Most skills do two or three different jobs (build a plan, check progress,
   diagnose a stall). If the request does not make the job obvious, the first question is which one.

## Asking

- **Rounds of at most four questions.** Ask the questions that most change the output first. Stop
  asking as soon as you can produce a useful first version; a good draft with two stated assumptions
  beats a third round of questions.
- **Use the AskUserQuestion tool whenever the answer is a choice** of two to four options: motion
  type, tier, stage, yes/no/don't know, which job. Put the most likely or recommended option first.
  The user can always pick "Other" and type.
- **Ask in plain text when there are more than four options or the answer is free-form**: names,
  dates, numbers, pasted lists. Letter the options so one short reply answers several questions, for
  example "reply like 1c 2b 3a".
- **"Don't know" is always a valid answer.** Record it as a gap with who would know, never as a zero
  and never as a guess. If AskUserQuestion is not available, ask the same questions in text.
- **Numbers the user doesn't have:** offer the typical value from the calculator's example in the
  question ("typical is 45% of recruits activating; use that?") so they can accept it in one word.
- **If the user says "just draft it" or skips questions**, stop asking. Draft with defaults, and list
  every assumption you made at the top so they can correct it.

## After the answers

1. **Produce the deliverable** in chat, using the skills and calculators the skill
   names. Every number comes from the connector, per "Numbers" below. Write it to
   `${CLAUDE_PLUGIN_ROOT}/references/writing.md` and run its final pass before you show it.
2. **Mark real gaps briefly.** A missing fact the user said they don't know goes in a short "Still
   open" list with who would know. Do not scatter bracketed markers through a document the user
   could have answered in a sentence; ask instead.
3. **Leave it in chat.** The plugin neither reads nor writes files in the user's folders. Do not
   offer to save. If the user asks for a file, that is their request to handle as they see fit.
4. **Suggest one next step**, tied to what the answers revealed.

## Numbers

**Run the calculation through the PartnerImpact connector. Do not do the arithmetic yourself.** Mental
maths is where a plausible wrong number comes from, and a wrong number in a partner business case is
worse than no number.

The plugin connects to the PartnerImpact MCP server (`https://mcp.partnerimpact.net/mcp`). Use its tools:

- `partner_calculator`: every calculator on the server. The ids that exist are the allowed values of
  its `calculator` parameter; read them from the tool rather than from memory, because calculators
  are added on the server without a plugin release. Call it with `calculator: "<id>"` and mode
  `describe` to get the inputs, method, how to read the result and a realistic example; then mode
  `run` with `inputs`.
- `partner_maturity_outline` and `partner_maturity_score`: the maturity assessment.
- `partner_health`, `calculate_partner_roi`, `plan_partner_pipeline_target`: dedicated tools for
  the three most common questions. They return the same numbers as the matching calculators.

Rules:

- Mode `describe` is the reference: it explains what each input means and how to read the result.
  No calculator documentation ships in this plugin, so always describe before you run.
- Pass every input you have, and offer the typical value from the example `describe` returns for
  the ones the user lacks ("win rate: typical is 22%, use that?"). An input you leave out is not
  estimated for you: depending on the calculator it comes back as an error, takes the calculator's
  default, or is counted as zero, which changes the answer quietly. The result reports
  `inputs_used`, split into what came from you and what was defaulted or counted as zero. Read it
  back every time and say which values were the user's, which you proposed and which were
  defaults.
- Where an input is a list of rows, check every row carries every field before you run; a missing
  field is counted as zero without being reported. The house rules say what to do about it.
- Round what comes back to what the inputs can carry, and do not pass on connector prose about
  profiles, records, setup steps or other products. See the house rules.
- Where a skill names a calculator id that the tool no longer lists, say so in one line and pick the
  closest one the tool does list.
- Bad input comes back as a readable error naming the input. Fix it or ask the user, rather than
  working around it.
- Show the inputs you used, then the result. The user must be able to see what the number rests on.

**If the connector's tools are not there**, follow "If the connector is unavailable" in
`${CLAUDE_PLUGIN_ROOT}/references/house-rules.md`: search for the tool first, search once more if
servers are still connecting, and only then fall back.

## When you are a subagent

If you were invoked as a subagent and a required input is missing, do not produce a document full of
placeholders. Return only the questions you need answered, at most five, each with options where it
makes sense, written directly to the person as they should read them. The full rule is the 'If you
are running as a subagent' section of your agent file.

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
