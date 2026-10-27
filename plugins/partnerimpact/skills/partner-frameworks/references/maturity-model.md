# Partner Program Maturity Model

A diagnostic for how developed a partner function is. Twelve assessment domains, four dimensions
each, every dimension scored 1 to 10. The twelve roll up into the seven domains of the Partner
Operating Model; the mapping is below. The score is not the point. The sequencing is: a low score in
one domain forbids work in another, and most partner programs fail because they built a co-sell
motion on top of a measurement function that could not tell sourced from influenced.

Calibrate domain emphasis to the motion. A marketplace-led motion leans on Partner Program Design and
Data & Attribution; a high-touch alliance motion leans on Co-Sell & GTM Execution and Governance &
Cadence.

The full rubric, all 240 anchor bands and 48 interventions, is served by the PartnerImpact
connector (`partner_maturity_outline` with `detail: "full"`). Fetch it when you are running an
assessment interview. This file is enough for scoring, sequencing and diagnosis.

## Scoring scale

Every dimension scores 1 to 10. Five written anchor bands, 2 points each.

| Band | Range |
|---|---|
| Critical | 1 to 3 |
| Developing | 3 to 5 |
| Defined | 5 to 7 |
| Managed | 7 to 9 |
| Optimised | 9 to 10 |

Each of the five written anchor bands spans two points. Score on evidence. Where evidence is thin, score conservatively and say the confidence is low.

Domain score is the unweighted mean of its scored dimensions. Overall is the unweighted mean of
all scored dimensions. Dimensions you skip are excluded from the average, never counted as zero.

## The twelve assessment domains

### 1. Ecosystem Design & Strategy

*Does the company know what kind of partner program it's building and why?*

- **Strategic direction and partner rationale** `strategy_direction`
- **Partner type definition and prioritisation** `strategy_types`
- **Whitespace and build/buy/partner framework** `strategy_whitespace`
- **Investment thesis and board narrative** `strategy_boardnarrative`

### 2. Commercial Model Design

*Can the program generate, structure, and defend partner economics?*

- **Revenue type definition (sourced vs. influenced)** `commercial_revtypes`
- **Incentive structure and tier alignment** `commercial_incentives`
- **Partner economics modelling** `commercial_economics`
- **MSA and hyperscaler transaction terms** `commercial_hyperscaler`

### 3. Partner Organization Design

*Is the team structured to scale the program rather than just manage it?*

- **Role differentiation and specialisation** `org_roles`
- **Coverage model and PAM ratios** `org_coverage`
- **Regional pod structure and specialist overlays** `org_pods`
- **Reporting line and headcount planning** `org_reporting`

### 4. Partner Program Design

*Is the program designed to produce behaviour, not just sign agreements?*

- **Tier structure and outcome-based criteria** `program_tiers`
- **Benefit stack (funded and deliverable)** `program_benefits`
- **Program economics and NPS** `program_progeconomics`
- **Partner experience and program differentiation** `program_experience`

### 5. Partner Enablement

*Can partners sell and implement independently?*

- **Onboarding structure and milestones** `enablement_onboarding`
- **Sales playbook and ICP enablement** `enablement_sales`
- **Technical enablement and certification** `enablement_technical`
- **Self-service portal and enablement independence** `enablement_selfservice`

### 6. Partner Marketing

*Is the partner channel generating its own demand, or just riding the direct sales motion?*

- **Co-marketing budget and programme** `marketing_budget`
- **Partner-generated lead tracking** `marketing_leadtracking`
- **ABM campaigns with partners** `marketing_abm`
- **Digital presence and partner-led demand generation** `marketing_presence`

### 7. Co-Sell & GTM Execution

*Are partners integrated into the sales motion, or working in parallel to it?*

- **Rules of Engagement and deal registration** `cosell_roe`
- **Account mapping overlap** `cosell_mapping`
- **MEDDICC × partner plays by type** `cosell_meddic`
- **Co-sell pipeline visibility and win rate** `cosell_pipeline`

### 8. Partner Process & Operations

*Are the operational mechanics of the partner program reliable and scalable?*

- **Core operational infrastructure (PRM/CRM)** `ops_infrastructure`
- **Deal registration and agreement workflow** `ops_workflow`
- **PRM/CRM integration and automation** `ops_integration`
- **Operational resilience and process documentation** `ops_fallback`

### 9. Data & Attribution

*Does the company know what partners are contributing and how to prove it?*

- **Attribution methodology** `data_methodology`
- **CRM data quality and partner tagging** `data_crmquality`
- **Partner reporting infrastructure** `data_reporting`
- **Predictive analytics and automated alerts** `data_predictive`

### 10. Partner Performance Measurement

*Are partners held accountable to outcomes, and does the program reward what it intends to?*

- **Core KPI suite per partner tier** `measurement_kpis`
- **Active vs. signed partner ratio management** `measurement_activeratio`
- **Leading indicators and partner health scoring** `measurement_leading`
- **Benchmarking and program improvement loop** `measurement_benchmarking`

### 11. Governance & Cadence

*Is the program systematically managed, or does it run on memory and urgency?*

- **Partner-facing QBR cadence** `governance_qbr`
- **Internal partner review cadence** `governance_internalcadence`
- **Action tracking and accountability** `governance_actiontracking`
- **Partner Advisory Board (PAB)** `governance_pab`

### 12. Partner-First Culture

*Does the rest of the company enable the partner program, or resist it?*

- **Executive sponsorship and CRO trust** `culture_executive`
- **AE incentive alignment** `culture_aeincentives`
- **Cross-functional integration (Product, Marketing, Finance)** `culture_crossfunctional`
- **External recognition and partner-first identity** `culture_external`

## How the twelve roll up into the Partner Operating Model

The Partner Operating Model on partnerimpact.net describes a partner function in seven domains, in
three groups, on an AI and automation foundation. The assessment scores the same function at finer
grain. Each assessment domain belongs to exactly one operating-model domain.

| Group | Operating-model domain | Assessment domains |
|---|---|---|
| Design | 01 Strategy & Ecosystem | Ecosystem Design & Strategy; Commercial Model Design |
| Design | 02 Organization Design | Partner Organization Design |
| Operate | 03 Program Architecture | Partner Program Design; Partner Enablement |
| Operate | 04 GTM & Co-Sell Execution | Co-Sell & GTM Execution; Partner Marketing |
| Operate | 05 Technology & Infrastructure | Partner Process & Operations |
| Sustain | 06 Data & Measurement | Data & Attribution; Partner Performance Measurement |
| Sustain | 07 Governance & Culture | Governance & Cadence; Partner-First Culture |

Use it to say where a finding sits when the user thinks in the seven domains: a binding constraint
in Partner Enablement is a Program Architecture problem. The scores, gates and benchmarks stay on
the twelve. Do not average assessment scores into an operating-model score by hand. The model is
described at https://www.partnerimpact.net/insights/partner-program-is-a-system.

## Sequencing gates

A domain scoring below 3.6 (the Critical band) closes the gate below it.
Investment in a later domain leaks out through the gap in an earlier one. The gates run in the
order below, so the **binding constraint is the earliest closed gate**: it closes everything after
it. Say plainly which one it is.

| Domain below 3.6 | What you are not allowed to build yet |
|---|---|
| Ecosystem Design & Strategy | No program or process investment yet. |
| Commercial Model Design | No recruitment at scale until the commercial model is decided. |
| Partner Organization Design | No new partner type until someone owns the current one end to end. |
| Partner Program Design | No tier-based recruitment until the benefit stack is funded. |
| Partner Enablement | No recruitment push until onboarding capacity exists. |
| Partner Marketing | No MDF program or co-marketing spend until a joint value proposition exists that the field can say out loud. |
| Co-Sell & GTM Execution | No field-facing play until rules of engagement and deal registration exist. |
| Partner Process & Operations | No PRM purchase and no automation until the manual process is documented and followed. |
| Data & Attribution | No co-sell scaling and no partner revenue target until attribution can separate sourced from influenced. |
| Partner Performance Measurement | No tier promotion, demotion or pruning decisions yet. |
| Governance & Cadence | Any new play requires a QBR cadence and pipeline hygiene first. |
| Partner-First Culture | No partner-first commitment in external messaging. |

### Why each gate holds

- **Ecosystem Design & Strategy.** A funded program built on an unclear thesis produces partners nobody can explain the reason for, and the first budget review kills it.
- **Commercial Model Design.** Signing partners before margin, rev-share and crediting are settled means renegotiating every agreement individually, and the terms drift apart.
- **Partner Organization Design.** Adding a motion to an org with unclear recruitment, activation and performance ownership spreads the same person thinner and slows all of them.
- **Partner Program Design.** Tiers you cannot pay for are a promise the partner eventually discovers is empty, which costs more trust than having no tiers at all.
- **Partner Enablement.** Recruiting past activation capacity produces signed, inactive partners, the most common and most expensive failure in the model.
- **Partner Marketing.** MDF against an unclear JVP funds activity rather than pipeline, and the spend is impossible to defend at renewal.
- **Co-Sell & GTM Execution.** Sending sellers into partner deals without routing logic creates channel conflict faster than it creates pipeline.
- **Partner Process & Operations.** Automating an undefined process buys an expensive record of the confusion.
- **Data & Attribution.** Every number reported above this line is contested, and contested numbers lose the budget argument.
- **Partner Performance Measurement.** A tier change you cannot defend with a metric reads as politics to the partner, and it gets reversed.
- **Governance & Cadence.** Plays without a review rhythm get launched and then quietly abandoned, and nobody can say when.
- **Partner-First Culture.** Promising partner-led GTM the field does not believe in produces public commitments the organisation walks back.

## Failure signatures

Patterns worth naming when you see them. A strong domain sitting next to a closed gate is usually
more diagnostic than either score alone. Name one only when the high domain is Defined or better
(5 and up), the low domain is below 3.6, and they are at least 2 points apart.

- **High Ecosystem Design & Strategy, low Co-Sell & GTM Execution.** A beautiful deck and no field execution. The classic gap.
- **High Partner Program Design, low Data & Attribution.** Tiers and benefits nobody can prove are working.
- **High Co-Sell & GTM Execution, low Governance & Cadence.** Lots of motion, no cadence to convert it into outcomes.
- **High Partner Enablement, low Commercial Model Design.** Well-trained partners with no reason to sell, because the economics were never made worth their time.
- **High Co-Sell & GTM Execution, low Partner Process & Operations.** Deals get worked, but routing and crediting are decided case by case, so the same argument repeats every quarter.
- **High Partner Marketing, low Partner Enablement.** Leads arrive at partners who cannot deliver on them.
- **High Partner Organization Design, low Partner-First Culture.** A staffed partner team the rest of the company still treats as a side function.
- **High Partner Program Design, low Partner Enablement.** A program that signs partners and never activates them. Tiers, benefits and paperwork are in place, and nobody made the partner able to sell.

## Stage benchmarks

Typical scores by company stage. Use these to say whether a score is a problem: a 4.0 in
Co-Sell is healthy at Series A and a red flag at Scale. Compare, then report the delta, not the raw score.

**The figures are PartnerImpact working estimates of typical scores at each stage, not measured survey data.** Say so whenever you report a delta.

| Domain | Seed | Series A | Series B | Series C | Scale | Enterprise |
|---|---|---|---|---|---|---|
| Ecosystem Design & Strategy | 2.8 | 4.0 | 4.8 | 6.0 | 6.8 | 7.6 |
| Commercial Model Design | 2.4 | 3.2 | 4.0 | 5.2 | 6.4 | 7.2 |
| Partner Organization Design | 2.4 | 3.6 | 4.4 | 5.6 | 6.4 | 7.2 |
| Partner Program Design | 2.0 | 3.2 | 4.0 | 5.2 | 6.4 | 7.2 |
| Partner Enablement | 2.0 | 3.2 | 4.0 | 5.2 | 6.0 | 6.8 |
| Partner Marketing | 2.0 | 2.8 | 3.6 | 4.8 | 6.0 | 6.8 |
| Co-Sell & GTM Execution | 2.0 | 3.2 | 4.0 | 5.2 | 6.0 | 6.8 |
| Partner Process & Operations | 2.0 | 2.8 | 3.6 | 4.8 | 6.0 | 6.8 |
| Data & Attribution | 2.0 | 3.2 | 4.0 | 5.2 | 6.4 | 7.2 |
| Partner Performance Measurement | 2.0 | 2.8 | 3.6 | 4.8 | 6.0 | 6.8 |
| Governance & Cadence | 2.4 | 3.2 | 4.0 | 5.2 | 6.0 | 6.8 |
| Partner-First Culture | 2.4 | 3.6 | 4.0 | 5.2 | 6.0 | 7.2 |

## Output of an assessment

1. **Heatmap.** Twelve assessment domains scored, each banded.
2. **Stage delta.** Each domain against its benchmark for the company stage.
3. **Binding constraint.** The earliest closed gate, which closes the most downstream work. Name it explicitly.
4. **Priority dimensions.** The three lowest, each with a root-cause hypothesis rather than a score. A quick
   assessment scores domains only: name the three weakest domains and the dimensions to examine in them.
5. **Sequenced recommendations.** Ordered by the gates, not by score size.

Interventions per dimension come back from `partner_maturity_outline` with `detail: "full"`.

---

Part of the PartnerImpact plugin. Authored by Bart Dirksen, [partnerimpact.net](https://partnerimpact.net). CC BY 4.0.

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
