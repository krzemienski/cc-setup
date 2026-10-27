---
name: program-architecture
description: "This skill should be used when designing or refining a partner program, tier structure, benefit stacks, partner incentives, MDF, or the enablement and certification path, including tier economics, quotas, MDF allocation, activation readiness and onboarding tracking. Provides embedded design references for program architecture."
metadata:
  author: "Bart Dirksen"
  copyright: "© 2026 PartnerImpact (Bart Dirksen)"
  license: "CC-BY-4.0"
  version: "1.1.2"
---

# Program Design

The architecture a partner experiences: what tier they're in, what they get, what they're
paid, and how they get enabled. Program design is where strategy becomes something a partner can
feel. Get it wrong and even well-qualified partners go inactive.

All references are embedded in this skill's `references/` folder.

## When to load this skill

- Standing up a partner program from scratch
- Restructuring tiers or the benefit stack
- Designing partner incentives or an MDF program
- Building the enablement and certification path

## The references

### 1. Tiers & Benefits
`${CLAUDE_PLUGIN_ROOT}/skills/program-architecture/references/tiers-benefits.md`

How to structure tiers and the benefit stack each earns: the value exchange, requirements, and the
give/get balance that keeps partners investing.

### 2. Incentives & MDF
`${CLAUDE_PLUGIN_ROOT}/skills/program-architecture/references/incentives-mdf.md`

Partner incentive design (margin, rebates, SPIFFs) and market development funds: how to structure
them so they change behavior instead of subsidizing it.

### 3. Enablement Architecture
`${CLAUDE_PLUGIN_ROOT}/skills/program-architecture/references/enablement-architecture.md`

The certification ladder and enablement path that turns a signed partner into a producing one, with
the activation checkpoints that matter.

## Calculators

These run on the PartnerImpact connector: `partner_calculator` with the id below, mode `describe`
for the inputs, method and how to read the result, then mode `run`. The list on the tool governs;
this table is a guide to which one answers which question.

| Calculator | Use it to | Id |
|---|---|---|
| Tier & Incentive Designer | What the benefit stack costs per tier, and where incentive runs rich against revenue | `tier-incentive` |
| Tier & Investment Canvas | What each tier costs against what its actual partners return, and attainment against target | `tier-canvas` |
| Per-Partner Quota Setter | Split a partner revenue target into tier-weighted quotas that sum exactly | `quota-setter` |
| MDF Allocation Planner | Split a fixed MDF budget by expected return, against a proportional suggestion | `mdf-planner` |
| Activation-Readiness Scorer | Whether a signed partner is ready to count as active, with gating items | `activation-readiness` |
| 90-Day Onboarding Tracker | Whether onboarding is on track, and which milestones are overdue | `onboarding-tracker` |

## How to use them

Design against the maturity model: don't build tiers a partner base can't fill, or an MDF program
the measurement function can't hold accountable. Every structure ships as a default the user
calibrates.

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
