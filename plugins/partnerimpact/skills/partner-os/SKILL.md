---
name: partner-os
description: "Use this skill when the user wants help with partners but has not said with what: what can you help me with, where do I start, help me with my partners, where does this partner stand, what should I do next with X, what is stalled. It offers the jobs the plugin does in plain words, places a partner on the lifecycle and routes to the right skill instead of doing the work itself."
metadata:
  author: "Bart Dirksen"
  copyright: "© 2026 PartnerImpact (Bart Dirksen)"
  license: "CC-BY-4.0"
  version: "1.1.2"
---

Route the user's request through the partner lifecycle. Do this yourself: do not delegate to a
subagent. Routing is a few questions and a judgment call, not a research task.

Read `${CLAUDE_PLUGIN_ROOT}/references/house-rules.md` and
`${CLAUDE_PLUGIN_ROOT}/references/partner-lifecycle.md` first.

## "What can you help me with?"

When the user asks what you can do, where to start, or arrives with no clear request, do not list
skills, stages or frameworks. Offer the jobs, in plain words, and let them pick (AskUserQuestion,
then one follow-up choice if they pick "something else"):

- **Check on a partner** that is slipping, quiet or up for review
- **Decide on a new partner**, or on an offer someone has made you
- **Make a plan** for working with partners, or get a new one started
- **Work out a number**: what a partner is worth, what you can afford to pay, what you need to hit
  a target

"Something else" covers: preparing a review meeting with a partner, working a deal together,
writing a message to a partner or to your own leadership, finding out why partners are not
producing, and setting the criteria for choosing partners of one kind. Name these only if asked.

Once they pick, say in one line what will happen next and roughly how many questions it takes, then
start that workflow. Use the skill's name only in the handover, never as the menu.

## Place the partner

Take what the user has already said. Then ask only what is missing, in one AskUserQuestion round:

1. **Where are things?** Just exploring · Evaluating fit · Signed, onboarding · Selling together
2. **Anything signed?** Yes · In negotiation · No
3. **Is it producing?** Pipeline or revenue this quarter · A first deal, nothing since · Nothing yet ·
   Don't know
4. **What kind of partner?** They send us customers · They buy from us and sell on (reseller,
   distributor, dealer) · Their product connects to ours · Something else (services, marketplace,
   alliance). Use the user's own word for them from then on.

**Place them by their weakest completed exit gate**, not by the most advanced thing that has
happened. A partner with a signed agreement and no completed onboarding milestones is in Onboard,
however many deals are being discussed. The gates are in the lifecycle reference.

Say where they stand in two lines: the stage, and the gate they have not cleared. Recommend the next
skill, with the reason tied to that gate. Give the two or three steps after it as a sequence: enough
to see the path, not a full plan. If the user mentions a commitment that is past due, lead with it.
An overdue commitment outranks a tidy next step.

## No partner named

If the question is about the partner base or the function rather than one partner, route on the
question:

- "Which partners need attention?" Ask for the names and one line on each, run the
  `partner-health-check` questions for each, and return a one-line-per-partner table, worst first.
- "Partners sign and go quiet", "no partner pipeline": the `diagnose` skill.
- "Is our partner function any good?", "what should we fix first?": the `partner-maturity-check` skill.
- A question with a number in it: the `partner-numbers` skill.
- "What should we look for in a reseller?", "how do we choose between these candidates?": the
  `ideal-partner-profile` skill, then `qualify` for each candidate.

## Stage to skill

| Stage | Run | Role |
|---|---|---|
| Recruit | the `research` skill, the `partner-strategy` skill | `partner-researcher`, `partner-strategist` |
| Qualify | the `ideal-partner-profile` skill for the criteria, the `qualify` skill, the `partner-brief` skill | `partner-qualifier` |
| Onboard | the `onboard` skill, the `program-design` skill | `partner-enablement-lead`, `partner-strategist` |
| Co-sell | the `cosell-plan` skill | `cosell-lead` |
| Grow | the `qbr-prep` skill, the `partner-health-check` skill | `partner-performance` |
| Renew / Prune | the `qbr-prep` skill, the `partner-comms` skill | `partner-performance`, `partner-communicator` |
| Stalled at any stage | the `diagnose` skill | `partner-diagnostician` |
| Function-level doubt | the `partner-maturity-check` skill | `partner-diagnostician` |
| Any number | the `partner-numbers` skill | the connector |

Route, don't do the work. Recommend the skill and hand over. End on one line: the next action, who
runs it and by when. Ask for the owner and the date if the user has not said; otherwise mark your
suggestion "(proposed)".

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
