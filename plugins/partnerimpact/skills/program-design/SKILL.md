---
name: program-design
description: "Use this skill to design or change a partner program: tiers and tier criteria, benefits, incentives, MDF, a certification path, tier economics, or how to tier an existing partner base."
metadata:
  author: "Bart Dirksen"
  copyright: "© 2026 PartnerImpact (Bart Dirksen)"
  license: "CC-BY-4.0"
  version: "1.1.2"
---

Design the part of the program the user asked about. Run this in the conversation; do not delegate to a
subagent.

Read `${CLAUDE_PLUGIN_ROOT}/references/interview.md` and follow it. Your playbook is
`${CLAUDE_PLUGIN_ROOT}/agents/partner-strategist.md`, with the `program-architecture` skill.

## Round 1 (AskUserQuestion)

1. **What are you designing?** (multi-select) Tiers and benefits · Incentives and margin · MDF
   allocation · Enablement and certification path
2. **How many partners will this cover?** Under 20 · 20 to 100 · Over 100
3. **Is there a program today?** Yes, redesigning · Partly · Starting from scratch

## Round 2 (text, one message), only what the design needs

- Tiers: how many you want, and what should earn a partner a higher tier.
- Incentives: gross margin, what it costs to serve a partner, and the minimum contribution you must
  keep (for the Rev-share Affordability Floor).
- MDF: the budget and the partners competing for it, with a rough expected return for each.
- Enablement: the partner types and what "activated" should mean.

## Numbers

Run every figure through the PartnerImpact connector, never in your head: call `partner_calculator` with mode `describe` for the inputs, then mode `run` with the inputs. For this skill that means `tier-incentive` and `tier-canvas` for tier economics, `rev-share-floor` before promising margin, `quota-setter` for quotas, `mdf-planner` for the budget, `activation-readiness` for the enablement gates. Pass every input explicitly, show the inputs you used, and say which were the user's and which you proposed. The rules, including what to do when the connector is unavailable, are in the house rules (`${CLAUDE_PLUGIN_ROOT}/references/house-rules.md`).

## Produce

The designed pieces, each as a table the user can adopt, with the numbers checked by the calculators: Tier &
Incentive Designer or Tier & Investment Canvas for tier economics, the Rev-share Affordability Floor
before any margin is promised, MDF Allocation Planner for the budget. Balance what a partner gives
and gets at every tier, and don't design tiers the partner base can't fill. Name the biggest lever to
calibrate. Then one next step.

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
