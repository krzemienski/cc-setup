---
name: diagnose
description: "Use this skill when partners are not producing and the cause is unclear: why is X not producing, where did this partner stall, we have partners but no pipeline, where is the funnel leaking, partner deals are not closing. It finds which conversion is failing for one partner, one motion or the whole base, and whether the cause is the partner, the program or the incentives."
metadata:
  author: "Bart Dirksen"
  copyright: "© 2026 PartnerImpact (Bart Dirksen)"
  license: "CC-BY-4.0"
  version: "1.1.2"
---

Diagnose the stall the user described. Run this in the conversation; do not delegate to a subagent.

Read `${CLAUDE_PLUGIN_ROOT}/references/interview.md` and follow it. Your playbook is
`${CLAUDE_PLUGIN_ROOT}/agents/partner-diagnostician.md`.

## One partner, or the whole base?

If the user names one partner, work that partner through the lifecycle bowtie. If the stall is
across the base ("partners sign and go quiet", "no partner pipeline"), work the funnel instead. Ask
only if it's unclear. If the doubt is about the whole partner function rather than a stall,
suggest the `partner-maturity-check` skill.

## One partner that stopped converting

Ask for the numbers the user has at each stage (text): signed, onboarded, first opportunity,
closed deals, repeat pipeline, over what period. A conversion that can't be computed because the
data doesn't exist is itself the finding. Find the worst conversion, then ask the incentive question
(AskUserQuestion): is anyone on either side paid or credited for working this partner? Classify the
cause as partner, program or incentive, or say what would separate them.

## A stall across the base

Ask for the funnel the user has: partners recruited, signed, activated, producing, and the pipeline
they carry. Run the Pipeline Leak Finder or the Recruitment-to-Activation Funnel to find the stage
losing the most, Concentration Risk if a few partners carry the number, and the Program Simulator to
show which lever actually moves the result. Then classify the cause the same way.

Close with one next step.

## Conversion rates

The funnel calculators take percentages, not counts. Turn the user's counts into rates in the open
(34 signed, 11 active: 11 / 34 = 32%), label them hand-calculated, then pass the rates on.

## Numbers

Run every figure through the PartnerImpact connector, never in your head: call `partner_calculator` with mode `describe` for the inputs, then mode `run` with the inputs. For this skill that means `pipeline-leak` or `recruitment-funnel` for a stall across the base, `concentration-risk` when a few partners carry the number, `program-simulator` to show which lever moves it. Pass every input explicitly, show the inputs you used, and say which were the user's and which you proposed. The rules, including what to do when the connector is unavailable, are in the house rules (`${CLAUDE_PLUGIN_ROOT}/references/house-rules.md`).

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
