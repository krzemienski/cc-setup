---
name: co-sell-motion
description: "This skill should be used when designing or running a co-sell motion, account mapping, joint close plans, rules of engagement, deal registration, or aligning partner and direct sales teams on a deal. Provides embedded co-sell process references."
metadata:
  author: "Bart Dirksen"
  copyright: "© 2026 PartnerImpact (Bart Dirksen)"
  license: "CC-BY-4.0"
  version: "1.1.2"
---

# Co-sell Motion

Where partner and direct sales work a deal together. Co-sell is the motion partnerships
lives or dies on, and it's an incentives and alignment problem far more than a tooling problem. If
the field ignores the partner, the answer is almost never a new PRM.

All references are embedded in this skill's `references/` folder.

## When to load this skill

- Building a co-sell GTM plan for a specific partnership
- Running account mapping between two sales teams
- Writing rules of engagement or a deal registration policy
- Diagnosing why a co-sell motion isn't producing

## The references

### 1. Co-sell Process (the three asks)
`${CLAUDE_PLUGIN_ROOT}/skills/co-sell-motion/references/cosell-process.md`

The field-level motion, Intel, Influence and Intros, and how to keep partner and direct reps aligned
through a joint deal.

### 2. Sales-Partner Alignment (the 3Is)
`${CLAUDE_PLUGIN_ROOT}/skills/co-sell-motion/references/sales-partner-alignment.md`

Incentives, Information, Involvement. Why your own field does or does not bring partners into deals.
Run this before redesigning a play: co-sell is an incentives problem before it is a tooling problem,
and the three compound downward.

### 3. Rules of Engagement
`${CLAUDE_PLUGIN_ROOT}/skills/co-sell-motion/references/rules-of-engagement.md`

Who does what, who owns the customer, how conflict is resolved. The document that prevents the
fights that kill co-sell.

### 4. Deal Registration
`${CLAUDE_PLUGIN_ROOT}/skills/co-sell-motion/references/deal-registration.md`

How partners register deals, how conflict is adjudicated, and the decision tree for overlapping
claims.

### 5. Account Mapping
`${CLAUDE_PLUGIN_ROOT}/skills/co-sell-motion/references/account-mapping.md`

How to map two account bases to find overlap, whitespace, and the joint target list worth working.

## Calculators

These run on the PartnerImpact connector: `partner_calculator` with the id below, mode `describe`
for the inputs, method and how to read the result, then mode `run`. The list on the tool governs;
this table is a guide to which one answers which question.

| Calculator | Use it to | Id |
|---|---|---|
| Co-sell Deal Qualifier | Score one opportunity on the six things that decide whether it closes, before it goes in the forecast | `cosell-deal-qualifier` |
| Account Mapping & Whitespace | Two account lists in: the shared co-sell list, their whitespace, and your coverage of their base | `account-mapping` |

## How to use them

Co-sell design that ignores incentives and routing is decoration. Before recommending process,
check whether the field is paid and routed to work the partner.

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
