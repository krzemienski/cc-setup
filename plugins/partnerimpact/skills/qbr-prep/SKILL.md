---
name: qbr-prep
description: "Use this skill for any partner review or performance question: prepare a QBR or business review, attainment against plan or target, a partner scorecard, where a review conversation should start, renew or prune a partner. Use it whenever the user gives targets and actuals for a partner. It bands attainment on the connector, reads partner health, and ends on at most three asks with owners on both sides."
metadata:
  author: "Bart Dirksen"
  copyright: "© 2026 PartnerImpact (Bart Dirksen)"
  license: "CC-BY-4.0"
  version: "1.1.2"
---

Prep the QBR for the partner the user named. Run this in the conversation; do not delegate to a subagent.

Read `${CLAUDE_PLUGIN_ROOT}/references/interview.md` and follow it. Your playbook is
`${CLAUDE_PLUGIN_ROOT}/agents/partner-performance.md`.

## Round 1 (AskUserQuestion)

1. **Which quarter?** Offer the most recent quarter first.
2. **Is there a joint business plan with targets?** Yes · Informal targets · No
3. **Where does partner revenue come from here?** Sourced by the partner · Influenced · Co-sold · A mix
4. **Anything changed on their side?** No · Sponsor left · Headcount pulled · Don't know. On "Don't
   know", send `"unknown"` for both flags if the health tool accepts that value, otherwise send
   neither, and say that sponsor and headcount status were not confirmed.

## Round 2

Ask these as three separate short messages, in this order, and skip any the user has already
answered. Never put all three in one message.

- **The numbers (text):** "paste or type target and actual for each metric you track, for example:
  partner-sourced revenue 300k / 210k". If there is no plan, ask for the actuals and last quarter.
- **Health (AskUserQuestion, two calls):** Green · Amber · Red · Don't know for production,
  activation, engagement, relationship, commitment and economics.
- **In a sentence each (text):** what worked, what is stuck, and what you need them to decide.

## Numbers

Run every figure through the PartnerImpact connector, never in your head: call `partner_calculator` with mode `describe` for the inputs, then mode `run` with the inputs. For this skill that means `qbr-attainment` on the numbers, `partner-health` on the six reads, then `churn-risk`, `concentration-risk` or `attribution-comparator` where the conversation needs them. Pass every input explicitly, show the inputs you used, and say which were the user's and which you proposed. The rules, including what to do when the connector is unavailable, are in the house rules (`${CLAUDE_PLUGIN_ROOT}/references/house-rules.md`).

## Produce

Run QBR Attainment first, then check the production rating against it before running Partner
Health: if revenue or deals came in Red on attainment and the user rated production Green or Amber,
say so and ask whether the rating stands. A health result that reads better than the attainment
table needs that sentence next to it. Write the health recommendation from the rule that fired, not
from the connector's recommendation line.

Lead with attainment and the health result with the rule that fired, then the honest read on what is
off track and why, then **up to three asks**, one per red metric and no more than the reds justify,
each with an owner on both sides and a date. Owners and dates the user has not given are marked
"(proposed)" or listed under "Still open". If revenue is quoted, say which attribution
basis it rests on. Add a tier trajectory if the numbers justify one. Then one next step.

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
