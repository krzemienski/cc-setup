---
name: partner-numbers
description: "Use this skill for every question that needs a partner-related figure, even when the arithmetic looks simple enough to do directly: how much pipeline a revenue target needs and how much of it partners must source, the rev-share, margin or referral fee a partner can be paid, program ROI or payback, MDF split, partner manager capacity, churn or concentration risk, build versus partner versus buy, KPIs. It runs the matching PartnerImpact calculator on the connector instead of working by hand, shows which inputs were the user's and which were defaults, and leads with the decision the number supports."
metadata:
  author: "Bart Dirksen"
  copyright: "© 2026 PartnerImpact (Bart Dirksen)"
  license: "CC-BY-4.0"
  version: "1.1.2"
---

Answer the partner number the user asked for. Run this in the conversation; do not delegate to a
subagent.

Read `${CLAUDE_PLUGIN_ROOT}/references/house-rules.md` and follow it. Section 3 governs every
figure here: the connector calculates, you interpret.

## Pick the calculator

The calculators live on the connector, not in this plugin. The list of what exists is the set of
allowed values of the `calculator` parameter on the `partner_calculator` tool, and the tool's own
description says what each group is for. Read the list from the tool every time rather than from
memory: calculators are added on the server without a plugin release.

The groups, to help you match a question to an id: program economics (business case, program ROI,
rev-share affordability floor, referral fee, co-marketing ROI, alliance valuation, build against
partner against buy), measurement (KPIs, attribution comparison, QBR attainment), risk (churn,
concentration), program design (tier incentives, tier canvas, quotas, MDF allocation, activation
readiness, onboarding tracking), planning (pipeline target, program simulator, pipeline leak,
recruitment funnel, channel mix, ecosystem coverage, manager capacity, team budget), co-sell (deal
qualifier, account mapping), which partner motion fits, partner health, and what AI is worth to a
partner team.

If two calculators could answer the question, call `describe` on both and pick the one whose
`answers` line matches; if it is still ambiguous, ask once with AskUserQuestion, offering the two.
If nothing on the connector answers it, say so in one line and do not improvise a formula.

The five most common questions, with the dedicated tool where one exists:

| The question | Calculator | Tool |
|---|---|---|
| "What pipeline do we need for this target?" Coverage, deals and opportunities behind a revenue number | `pipeline-target` | `plan_partner_pipeline_target` |
| "Is the program paying back?" Investment, net return, ROI, break-even revenue | `program-roi` | `calculate_partner_roi` |
| "How many partners can one manager carry?" Workload, ceiling, headcount needed | `capacity` | `partner_calculator` |
| "What does the team cost and what does it cover?" Budget, coverage, the headcount gap | `team-budget` | `partner_calculator` |
| "Are we producing?" Partner-sourced share, pipeline and revenue per active partner, close rate | `kpi` | `partner_calculator` |

## Ask for the inputs

Call `partner_calculator` with the chosen id and mode `describe` first. It returns the inputs, what
each one means, the method, how to read the result and a realistic example. The typical figures live
in that example, not in the input defaults. Ask for the inputs in one text message, lettered, with
the typical value offered inline so the user can accept it in a word: "win rate: typical is 22%, use
that?".

The user will not have all of them. That is expected, and it is handled by naming the typical value
and passing it explicitly.

Pass every input, including the ones you proposed. An input you leave out is not estimated for
you: depending on the calculator it comes back as an error, takes the calculator's default, or is
counted as zero, which changes the answer quietly. The result reports `inputs_used`, split into what
came from you and what was defaulted or counted as zero: read it back and say which values were the
user's, which were yours and which were defaults.

## Run it

Run the calculation through the connector, never in your head. Use the dedicated tool where the
table above names one, or where `describe` returns a note pointing to one; otherwise
`partner_calculator` with mode `run`. The rules, including what to
do when the connector is unavailable, are in the house rules.

## Produce

**Lead with the decision the number supports**, not the number. "You are 2.4 times short of the
pipeline this target needs, so either the target moves or partner sourcing has to roughly double"
tells the reader something. "Total pipeline: €13.6M" on its own does not, and "€13,636,364" claims a
precision the inputs never had.

Then:

- **The result**, in a small table, with plain metric names.
- **The inputs**, marked as the user's or as a default. Every default is a place the answer could be
  wrong, and the user is the only one who can correct it.
- **What the number does not say.** Every calculator has a real limit, and stating it is what
  separates a usable figure from a slide. Take it from `how_to_read` in the result. For the common
  five:
  - Pipeline target is arithmetic. It sizes the ask; it says nothing about whether the partner base
    can carry it.
  - Program ROI is a gross-profit return, not cash payback, and it rests entirely on the
    attribution behind the gross profit. If sourced and influenced cannot be separated cleanly, the
    input is contested and so is the answer.
  - Capacity counts hours, not quality. A manager at 80% load with the wrong partners is not
    healthy. The calculator also models **one manager**: its load percentage and "over capacity"
    flag are for a single person carrying the whole book. Ask how many managers there are. If `describe` lists a
    `managers` input, pass it; if not, divide the monthly hours by that number and report load per
    manager (hand-calculated, shown). Never
    repeat the single-manager percentage for a team. The AI capacity calculator has the same limit.
  - Team budget assumes the coverage ratios you gave it are the right ones.
  - KPIs describe one period. A single quarter is a reading, not a trend.
- **The sensitivity that matters.** Name the one input that moves the result most, and what happens
  at a plausible alternative value.
- **The next action**, with an owner.

If the user is building a case for a CRO or a board, say which single figure to lead with and which
to keep in the appendix.

## Close

One next step. If the answer exposed a structural problem rather than a number problem, say so: a
pipeline target that needs the partner base to triple is a strategy question, not an arithmetic
one.

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
