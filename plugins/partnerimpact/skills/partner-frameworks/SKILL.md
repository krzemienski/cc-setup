---
name: partner-frameworks
description: "This skill should be used when sizing the partner team or funnel, simulating the program, choosing a channel mix, assessing a partner function, scoring a prospective partner, designing tiers or segmentation, or diagnosing why a partner program underperforms. Provides the core embedded frameworks: partner function maturity model, ideal-partner profile, lifecycle bowtie, and tiering & segmentation."
metadata:
  author: "Bart Dirksen"
  copyright: "© 2026 PartnerImpact (Bart Dirksen)"
  license: "CC-BY-4.0"
  version: "1.1.2"
---

# Partner Frameworks

The core diagnostic and design frameworks for partner work. All are embedded in this skill's
`references/` folder. Nothing points outside the plugin. Each is a neutral default built to be
calibrated to the user's business.

## When to load this skill

- Assessing the maturity of a partner function
- Scoring a prospective or existing partner for fit
- Designing partner tiers or segmenting a partner base
- Diagnosing root causes of ecosystem or program underperformance
- Mapping where partners drop off in the lifecycle and what KPI to watch

## The frameworks

### 1. Partner Program Maturity Model
`${CLAUDE_PLUGIN_ROOT}/skills/partner-frameworks/references/maturity-model.md`

Twelve assessment domains, four dimensions each, every dimension scored 1 to 10 against five written
anchor bands. They roll up into the seven domains of the Partner Operating Model, and the reference
carries the mapping. `maturity-model.md` carries the structure, the scale, the sequencing gates that tell you what
you are not allowed to build yet, the failure signatures, and the expected score per domain by
company stage. That file is enough for scoring, sequencing and diagnosis.

The 240 anchor bands and the 48 interventions are served by the connector: `partner_maturity_outline`
with `detail: "full"`, one domain at a time. The band text is the answer menu you read to the user
during an assessment. The `partner-maturity-check` skill runs it.

### 2. Ideal Partner Profile (IPP)
`${CLAUDE_PLUGIN_ROOT}/skills/partner-frameworks/references/ideal-partner-profile.md`

A weighted scoring model for partner fit, plus an anti-fit / where-we-won't-play gate. Use for
qualification and go/no-go decisions. Output is a score, a band, and a decision.

The default profile is one set of seven dimensions. A profile built for one kind of partner
separates candidates better: `${CLAUDE_PLUGIN_ROOT}/skills/partner-frameworks/references/profile-by-motion.md`
holds a starter per motion with weights, 1-3-5 anchors and deal-breakers, and the
`ideal-partner-profile` skill turns one into the user's own.

### 3. Partner Lifecycle Bowtie
`${CLAUDE_PLUGIN_ROOT}/skills/partner-frameworks/references/lifecycle-bowtie.md`

The partner journey as a bowtie (Recruit → Qualify → Onboard → Co-sell → Grow → Renew/Prune) with
the conversion metric that governs each transition. Use to locate where partners stall and which
metric to manage.

### 4. Tiering & Segmentation
`${CLAUDE_PLUGIN_ROOT}/skills/partner-frameworks/references/tiering-segmentation.md`

Two-axis segmentation (motion type × fit score) and a points-based tiering model with the
investment and cadence each tier earns. Use to structure a partner base and set differentiated
investment.

## Calculators

These run on the PartnerImpact connector: `partner_calculator` with the id below, mode `describe`
for the inputs, method and how to read the result, then mode `run`. The list on the tool governs;
this table is a guide to which one answers which question.

| Calculator | Use it to | Id |
|---|---|---|
| Partner Health | Apply the canonical health model: six red/amber/green reads and the three rules that decide at-risk | `partner-health` |
| Partner Program Maturity Score | Turn 1-10 ratings into domain scores, stage deltas, the gates now closed and the binding constraint | `maturity-score` |
| Ideal Partner Profile Score | Score one partner against the default profile or the user's own dimensions and weights, with deal-breakers checked first and the distance to the band edge shown | `ipp-score` |
| Recruitment-to-Activation Funnel | Work back from producing partners to the recruits it takes, and find the weakest stage | `recruitment-funnel` |
| Pipeline Leak Finder | The partner funnel against a revenue target: required versus current volume at every stage | `pipeline-leak` |
| Partner Program Simulator | Where the program lands if recruitment, activation, productivity and churn stay as they are | `program-simulator` |
| GTM Channel-Mix Optimizer | How much revenue should run through partners versus direct | `channel-mix` |
| Ecosystem Coverage vs TAM | The market partners reach that direct cannot, and the whitespace nobody reaches | `ecosystem-coverage` |
| Partner Manager Capacity | How many partners one manager can carry, and the headcount the book needs | `capacity` |
| Team Budget & Coverage | What the partner team costs and covers, and what full coverage requires | `team-budget` |

Partner Health is the canonical health model; it also has a dedicated tool, `partner_health`, and
the `partner-health-check` skill runs it. The maturity score has `partner_maturity_score`.

## Calibration

The ideal partner profile and the tiering model ship with default dimensions, weights, gates, bands,
tier signals and tier names. They are starting points. If the user tells you theirs differ, use
theirs for the rest of the conversation, renormalise any weighted set to 100 and show it, and say
in one line which values were the user's and which were defaults.

## How to use them

Read the relevant reference in full before scoring or designing. State what evidence you scored
on. Use the user's own numbers, not the reference defaults, when they have given them. Never
present a score as more precise than its inputs.

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
