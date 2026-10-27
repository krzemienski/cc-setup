---
name: partner-brief
description: "Use this skill for a short written profile of one partner or prospect: a one-pager, a partner brief, a summary for a leadership meeting, or a quick profile with a go or no-go. It is built from public evidence plus a few questions."
metadata:
  author: "Bart Dirksen"
  copyright: "© 2026 PartnerImpact (Bart Dirksen)"
  license: "CC-BY-4.0"
  version: "1.1.2"
---

Brief the partner the user named. Run this in the conversation; do not delegate to a subagent.

This is the `qualify` skill with a company summary on top. Read
`${CLAUDE_PLUGIN_ROOT}/skills/qualify/SKILL.md` and run the same interview, always doing the public lookup in Round 1 rather than offering it.

Produce one page: what they do and for whom, motion type (graded), their ecosystem and named
partners, the reach and fit they bring, the deal-breaker results, the fit score, and the
recommendation with its rationale. Keep the evidence grades visible, and list what public evidence
could not establish in a short "Still open" section with who would know.

## Numbers

Run every figure through the PartnerImpact connector, never in your head: call `partner_calculator` with mode `describe` for the inputs, then mode `run` with the inputs. For this skill that means the same calculators as the `qualify` skill. Pass every input explicitly, show the inputs you used, and say which were the user's and which you proposed. The rules, including what to do when the connector is unavailable, are in the house rules (`${CLAUDE_PLUGIN_ROOT}/references/house-rules.md`).

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
