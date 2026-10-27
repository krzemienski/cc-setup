---
name: cosell-plan
description: "Use this skill for any joint deal or co-sell question with a partner: should this co-sell deal be in the forecast, is this joint opportunity real, build a co-sell plan, map accounts with a partner, work a deal together, rules of engagement, deal registration, or why the field is not working a partner. It scores a named deal on the Co-sell Deal Qualifier through the connector and turns the gaps into next steps."
metadata:
  author: "Bart Dirksen"
  copyright: "© 2026 PartnerImpact (Bart Dirksen)"
  license: "CC-BY-4.0"
  version: "1.1.2"
---

Plan co-sell with the partner the user named. Run this in the conversation; do not delegate to a subagent.

Read `${CLAUDE_PLUGIN_ROOT}/references/interview.md` and follow it. Your playbook is
`${CLAUDE_PLUGIN_ROOT}/agents/cosell-lead.md`, with the `co-sell-motion` skill.

## Round 1 (AskUserQuestion)

1. **What do you need?** Full co-sell plan · Account map with a target list · Help with one deal ·
   Rules of engagement and deal registration
2. **Is your field paid or credited for working this partner?** Yes · Partly · No · Don't know
3. **Do your reps know which partner to bring in, and when?** Yes · Some do · No · Don't know

Motion type in text if not already known. A referral partner has no co-sell motion; say so and
suggest what fits instead. If question 2 or 3 is No, that is the blocker: say it plainly before
designing any process, using the 3Is in `sales-partner-alignment.md`.

## Round 2, by what they need

- **Account map:** ask them to paste both account lists, one name per line (text). Run Account
  Mapping & Whitespace.
- **One deal:** deal name and value (text), then rate the six Co-sell Deal Qualifier dimensions in one
  text message, lettered, 1 to 5 or "?".
- **Rules of engagement:** who owns the customer today, how deal registration works now, and the last
  conflict that came up (text).
- **Full plan:** all of the above, in that order, stopping when you have enough.

## Numbers

Run every figure through the PartnerImpact connector, never in your head: call `partner_calculator` with mode `describe` for the inputs, then mode `run` with the inputs. For this skill that means `account-mapping` on the two account lists, `cosell-deal-qualifier` on a named deal. Pass every input explicitly, show the inputs you used, and say which were the user's and which you proposed. The rules, including what to do when the connector is unavailable, are in the house rules (`${CLAUDE_PLUGIN_ROOT}/references/house-rules.md`).

## Produce

The deliverable for the job: a three-zone account map with a short prioritised list and an owner and
ask type (Intel, Influence, Intros) per account; a scored deal with its close plan built around the
gaps; or rules of engagement and a deal-registration policy. Then one
next step.

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
