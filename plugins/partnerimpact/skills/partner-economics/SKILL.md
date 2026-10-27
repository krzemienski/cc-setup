---
name: partner-economics
description: "This skill should be used when working on partner economics, revenue attribution (sourced/influenced/co-sold), rev-share and margin models, partner CAC, MDF ROI, program ROI, a multi-year business case, pipeline targets, KPIs, QBR attainment, referral fees, co-marketing ROI, alliance valuation, build/partner/buy, the most a partner can be paid, portfolio concentration, or revenue at risk. Provides embedded references and calculators for the commercial math of partnerships."
metadata:
  author: "Bart Dirksen"
  copyright: "© 2026 PartnerImpact (Bart Dirksen)"
  license: "CC-BY-4.0"
  version: "1.1.2"
---

# Partner Economics

The commercial math that decides whether a partnership is worth running. Partner revenue claims are
routinely inflated by loose attribution; partner programs are routinely funded without anyone
checking the return. This skill is the discipline against both.

All references are embedded in this skill's `references/` folder.

## When to load this skill

- Defining or cleaning up revenue attribution (sourced vs. influenced vs. co-sold)
- Modeling rev-share, margin, or partner CAC
- Evaluating whether MDF or incentive spend is paying back
- Building the economic case for or against a partnership

## The references

### 1. Revenue Attribution
`${CLAUDE_PLUGIN_ROOT}/skills/partner-economics/references/revenue-attribution.md`

The sourced / influenced / co-sold / direct model, the attribution decision tree, and the CRM fields
and windows that make it hold up.

### 2. Rev-share & Margin
`${CLAUDE_PLUGIN_ROOT}/skills/partner-economics/references/rev-share-margin.md`

Rev-share and margin structures by partner type, and partner CAC vs. blended CAC: whether the
channel is cheaper.

### 3. MDF ROI
`${CLAUDE_PLUGIN_ROOT}/skills/partner-economics/references/mdf-roi.md`

How to measure the return on market development funds and incentive spend, and when to renew or kill
it.

## Calculators

These run on the PartnerImpact connector: `partner_calculator` with the id below, mode `describe`
for the inputs, method and how to read the result, then mode `run`. The list on the tool governs;
this table is a guide to which one answers which question.

| Calculator | Use it to | Id |
|---|---|---|
| Program ROI | Return on the program against its cost, and break-even revenue | `program-roi` |
| Business Case | Multi-year pro-forma with payback, NPV and ROI, to fund or defend the program | `business-case` |
| Pipeline Target Planner | Work back from a revenue number to deals, opportunities and partner-sourced pipeline | `pipeline-target` |
| Rev-share Affordability Floor | The most you can pay a partner, and whether a proposed rate clears your contribution floor | `rev-share-floor` |
| Attribution Comparator | The same revenue credited three ways, and how much the headline depends on the policy | `attribution-comparator` |
| Concentration Risk | How much of the book leans on a few partners, and how many it behaves like | `concentration-risk` |
| Churn & Revenue at Risk | Probability-weighted exposure, high-risk exposure, GRR and NRR | `churn-risk` |
| Partnership KPIs | Sourced share of pipeline, pipeline and revenue per active partner, close rate | `kpi` |
| QBR Attainment | Attainment against plan per metric, banded, to lead the QBR | `qbr-attainment` |
| Referral Fee | What a referral is worth and how it lands over the term, by payment timing | `referral-fee` |
| Co-marketing Campaign ROI | What a joint campaign returns on your share of the spend | `co-marketing-roi` |
| Strategic Alliance Valuation | NPV of a flagship alliance, with strategic value weighted by confidence | `alliance-valuation` |
| Build vs Partner vs Buy | Three routes compared on NPV and a strategic scorecard, with the disagreement made explicit | `build-partner-buy` |

## How to use them

Every number is only as good as its attribution. When you present partner-sourced revenue, show the
attribution rule behind it. When you model economics, state your assumptions and mark the ones the
user must supply. Never present a partner revenue figure without its attribution category.

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
