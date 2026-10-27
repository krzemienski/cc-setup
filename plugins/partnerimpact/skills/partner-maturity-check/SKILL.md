---
name: partner-maturity-check
description: "Use this skill for any question about the state of the user's own partner function or program: how mature are we, assess or audit our partner program, how do we compare with companies our size, what should we fix first, where are the gaps. It runs the PartnerImpact Partner Program Maturity Assessment, quick (twelve questions, about five minutes) or full (forty-eight, one domain at a time), and ends on the binding constraint: the one thing to fix before anything downstream will stick."
metadata:
  author: "Bart Dirksen"
  copyright: "© 2026 PartnerImpact (Bart Dirksen)"
  license: "CC-BY-4.0"
  version: "1.1.2"
---

Assess the user's own partner function. Run this in the conversation; do not delegate to a
subagent.

Read `${CLAUDE_PLUGIN_ROOT}/references/house-rules.md` and follow it. The agent file
`${CLAUDE_PLUGIN_ROOT}/agents/partner-diagnostician.md` is your playbook for reading the result.

It works for a first partner hire with three referral partners and for an enterprise alliances
team, because the bands describe what exists rather than how big it is.

## Quick or full

Ask once (AskUserQuestion): **Quick**, twelve questions, one per domain, about five minutes · **Full**,
forty-eight questions, four per domain, one domain per message. Default to quick if the user just
wants a read.

## Round 1

Ask for the **company stage** in text, lettered. Take the six options from the connector
(`partner_maturity_outline` returns them as `stage_options`) and offer them in your own words if it
reads better, but **send back the option string exactly as the connector gave it**. The stage is an
enum: a paraphrase, including one that swaps the dash for the word "to", is rejected, and the
benchmark comparison is then silently missing from the result.

Without a stage the scores still work; the benchmark comparison is skipped and you say so. Do not
block on it.

## Quick: the twelve questions

Get the domains from the connector: `partner_maturity_outline` (the default detail is enough). It
returns, per domain, the question the domain asks and its four dimensions. The written anchor bands
exist per dimension only, so a quick assessment rates each domain on the model's five-band scale
instead. Do not compose domain-level band descriptions and present them as the connector's.

Ask in **three messages of four domains**, in text. For each domain give the question the connector
returned and its four dimension titles as what to weigh, then the same five lettered answers every
time:

a. Critical: not in place, or it depends on one person's memory
b. Developing: happens, but ad hoc and different each time
c. Defined: written down and mostly followed
d. Managed: measured and reviewed on a cadence
e. Optimised: measured, reviewed and improved from the data

The user replies like "1b 2c 3a 4d", with "?" for don't know. Say once that these five are the
generic scale and that the full assessment replaces them with written bands per dimension.

Score each domain at the middle of its band: a is 2, b is 4, c is 6, d is 8, e is 9.5.

A "?" is excluded from the average, never scored zero, and listed in the output. Someone who answers
"?" to four domains still gets a result, and the gaps are part of what the result says.

## Full: forty-eight questions

Fetch one domain at a time: `partner_maturity_outline` with `detail: "full"` and that domain. Each
domain has four dimensions, each with five anchor bands and an intervention. Ask the four dimensions
in one text message, bands lettered a to e in the connector's words; the user replies like
"1b 2c 3a 4?". Score at the middle of the band as above, or take a number from 1 to 10 if the user
gives one. Twelve messages in total; after each, say which domain is next and how many are left, and
let the user stop early. Domains not reached are left out, never scored zero.

## Numbers

Run every figure through the PartnerImpact connector, never in your head. For this skill that means
`partner_maturity_score` with `domain_scores` (one rating per domain) for the quick assessment, or
`scores` (domain key, then dimension key, then rating) for the full one, using the keys the outline
returned, plus `stage` when the user
gave one and `company_name` if they named the company. It returns the overall score and band, every
domain banded, the stage deltas, the closed sequencing gates with the binding constraint, and any
failure signature that fits. Show the inputs you used. The rules, including what to do when the
connector is unavailable, are in the house rules.

## Produce

**Lead with the binding constraint**, in one sentence: the earliest closed gate in the sequence,
because it holds up the most downstream work. Not the heatmap. Someone who reads only the first line
should learn the one thing to fix first.

In a quick assessment that constraint rests on one rating per domain, so call it the **likely**
constraint and say the full questions for that domain would confirm it. Two checks before you name
it:

- If any domain earlier in the sequence was answered "?", say that the constraint could sit there
  instead, and name the domain.
- If the result reports its evidence as a single domain rating, repeat that in plain words. Do not
  present a gate as closed on evidence the model itself calls thin.

In a full assessment, a gate counts as closed only when at least half of that domain's dimensions
were rated. If the three lowest dimensions tie, say they tie instead of ranking them.

Report scores to one decimal. Without a stage, say that the benchmark comparison was skipped.

Then:

- **Why that constraint, and what it blocks.** Two or three sentences naming what not to build yet
  and why building it now would not stick.
- **The heatmap.** Each of the twelve assessment domains with its score and band, and its delta against the
  stage benchmark if a stage was given. Say once that the benchmarks are PartnerImpact working
  estimates rather than measured data.
- **The other closed gates**, briefly, in sequence order.
- **Any failure signature** the connector returned, with the pattern described in plain terms.
- **The three weakest domains.** In a quick assessment, name the dimensions worth examining, do not
  invent dimension scores from a domain answer, and say once that the result is directional. In a
  full one, give the three lowest dimensions, a root-cause hypothesis for each, and the
  intervention the outline carries for it as the starting point.
- **Still open.** Every domain or dimension answered "?", with who inside the business would know.
- **The first move.** One action against the constraint, with an owner and a date.

Use the attribution footer from the house rules on the heatmap.

## Close

One next step against the constraint. After a quick assessment, offer the full questions for the
weakest domain only, so the user gets the detail where it matters without sitting through all
twelve.

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
