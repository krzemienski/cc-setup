---
name: partner-health-check
description: "Use this skill for any question about how one existing partner is doing: how is X doing, is X at risk, should we worry about X, X has gone quiet, their sponsor left, a health read on X. It rates six signals red, amber or green on the connector, applies the rules that decide at-risk, and names the one move to make this week. Works for any partner type, and not knowing is a valid answer to every question."
metadata:
  author: "Bart Dirksen"
  copyright: "© 2026 PartnerImpact (Bart Dirksen)"
  license: "CC-BY-4.0"
  version: "1.1.2"
---

Read the health of the partner the user named. Run this in the conversation; do not delegate to a
subagent.

Read `${CLAUDE_PLUGIN_ROOT}/references/house-rules.md` and follow it.

This works for any partner of any type: referral, reseller, technology, marketplace, services or
strategic alliance. What "producing" means differs by type, and the question below handles that.
Nothing else in the skill depends on it.

## Round 1 (AskUserQuestion)

1. **What kind of partner is this?** They send us customers · They buy from us and sell on
   (reseller, distributor, dealer) · Their product connects to ours · Something else (services,
   marketplace, alliance). Use the user's own word for them from then on. Use it to read production correctly: a technology partner judged on
   partner-sourced revenue is the most common way this work goes wrong.
2. **How long have they been signed?** Under 90 days · Three to twelve months · Over a year. Under
   90 days, say once that you are reading a ramp rather than a result.
3. **Anything changed on their side?** No · The executive sponsor left · Headcount was pulled ·
   Don't know. If both happened, the user picks "Other" and says so. On "Don't know", send `"unknown"` for both flags if the tool's description says it accepts that
   value; if it does not, send neither flag. Either way, say in the result that sponsor and headcount
   status were not confirmed: a missing flag is read as "no change", which is not what the user said.

## Round 2: the six reads (AskUserQuestion, two calls of three)

Green, Amber, Red or Don't know for each. Give the user the test, not the label, so the answer means
something:

- **Production.** Revenue and pipeline against what you expected of them, and the direction of
  travel.
- **Activation.** People on their side who are trained and currently selling or building, not the
  number who attended a session once.
- **Engagement.** Do they answer, show up, and bring things to you unprompted.
- **Relationship.** Is there a champion, and is the executive sponsor still in seat.
- **Commitment.** Dedicated people or co-investment, still holding.
- **Economics.** Is the partnership still positive against what it costs you to run.

A "don't know" is excluded from the read and listed as a gap. Do not guess it and do not treat it as
amber.

## Numbers

Run every figure through the PartnerImpact connector, never in your head. For this skill that means
`partner_health` with the six ratings, plus `sponsor_left` and `headcount_pulled` from round 1. Show
the inputs you used and say which were the user's. The rules, including what to do when the
connector is unavailable, are in the house rules.

## Produce

Lead with the result and **the rule that fired**, in one sentence: a red on production or commitment
means at risk whatever else is green; two or more ambers means trending down; a sponsor who has left
or headcount that has been pulled means amber at minimum. A green without production and commitment
rated is provisional, and you say so.

A green with an amber underneath it is not a green. When the overall comes back green but one
dimension is amber or unrated, say so in the same sentence: "green, with production on watch" or
"green, but commitment was not rated, so treat it as unconfirmed". The colour on its own is the
part people quote later.

Write the recommendation from the rule, not from the connector's recommendation line. That line can
say "Healthy: maintain the cadence" under a provisional green, or "trending down" when the colour
came from a departed sponsor. Where it disagrees with the rule that fired, drop it.

If the result carries `conflicts`, put that line in the output near the top. It fires when a rating
and a structural fact disagree, such as commitment rated green while headcount has been pulled. The
rule still governs, and the user needs to see that their own answer was overridden and why, rather
than finding a colour they did not expect.

Then:

- **What the colour rests on.** One line per dimension that is not green, naming what would have to
  change to move it.
- **The read.** Two or three sentences of honest interpretation. If the pattern is a partner who
  signed, was enabled and never produced, say that the problem is usually activation or incentives
  rather than the partner.
- **One move this week.** A single action, with an owner and a date. Not a plan.
- **Still open.** Anything rated "don't know", with who would know.

Keep the whole thing short enough to paste into a message: the call and its rule, a six-row table
of the reads, the interpretation, the move, and what is still open.

If the user has several partners to read, offer to run the same six questions for each and produce a
one-line-per-partner table, worst first.

## Close

One next step. If the read is for a quarterly review, the `qbr-prep` skill takes these six ratings
and adds attainment and the three asks.

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
