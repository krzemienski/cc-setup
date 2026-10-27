---
name: qualify
description: "Use this skill for any decision about taking on, signing or keeping a specific partner: should we partner with, sign, onboard or resell through X, is X a good fit, qualify or score X, go or no-go on X. Use it even when the user lists the facts and only asks for a verdict. Run it before answering, because it checks five deal-breakers (channel conflict, brand risk, no new reach, no senior owner, economics underwater) ahead of any scoring, then returns go, conditional go, not yet or no-go against the ideal partner profile."
metadata:
  author: "Bart Dirksen"
  copyright: "© 2026 PartnerImpact (Bart Dirksen)"
  license: "CC-BY-4.0"
  version: "1.1.2"
---

Qualify the company the user named. Run this in the conversation; do not delegate to a subagent.

Read `${CLAUDE_PLUGIN_ROOT}/references/interview.md` and follow it. Your playbook for the work is
`${CLAUDE_PLUGIN_ROOT}/agents/partner-qualifier.md`: its anti-fit gate, scoring rules and output. Load the ideal partner profile reference from
`partner-frameworks` for the dimensions and anchors.

## If the user has their own profile

If the user has pasted a card that starts "IDEAL PARTNER PROFILE", score against it and say so in
one line. Its deal-breakers replace the five in Round 2, its dimensions, weights and anchors replace
the default seven in Round 3, and its bands apply. If the card is for a different kind of partner
than this company, say so before scoring and ask whether to go on with it or use the default.

With no card, use the default profile. At the end, say once that a profile built for this kind of
partner would separate candidates better, and that the `ideal-partner-profile` skill builds one.

## Round 1

- **Who approached whom, and who would sell what?** (AskUserQuestion) We want them to sell or refer
  our offer · They want us to sell or refer theirs · Both ways · Not clear yet. If the user is the
  one being recruited, the questions below still apply, read from their side: does selling this
  conflict with what we already sell, does it reach customers we want, does it pay after our costs.
  Say that you are reading it from their side.
- What kind of partnership this would be, in text, using the lettered list from the house rules
  ("What kind of partner").
- **What do you already know about them?** A research log I can paste · Some notes · Just the name
  (AskUserQuestion). With just the name, offer to look up the public facts first (what they sell, to
  whom, their existing partners) and do it with web search before Round 2, grading each claim A, B
  or C with its source. Public evidence can only fill market access, strategic fit, technical fit
  and the public side of commitment.

## Round 2: the deal-breakers (AskUserQuestion, two calls)

Each question: Clear · Problem · Don't know yet.

1. Channel conflict: do they sell a competing product or undercut your direct team?
2. Brand, trust or compliance risk you couldn't govern?
3. Unique reach: do they get you into accounts you don't already cover?
4. Executive pulse: will someone senior on their side own it?
5. Economics: does it still make money at realistic volume after what they'd be paid? If they've
   named a rev-share or referral fee, run the Rev-share Affordability Floor or Referral Fee
   calculator on it and use the result.

Any "Problem" is a no-go: stop, say why, skip scoring. "Don't know yet" never counts as clear; it
makes the result a conditional go at best and becomes a named question with who would know.

## Round 3: fit (text, one message)

List the profile's dimensions with their anchors, lettered: the user's card if they pasted one,
otherwise the default seven from the reference. Ask for a rating on each, or "?" for don't know. Pre-fill any you could evidence from Round 1 and ask the user
to confirm or change them.

## Numbers

Run every figure through the PartnerImpact connector, never in your head: call `partner_calculator` with mode `describe` for the inputs, then mode `run` with the inputs. For this skill that means `rev-share-floor` or `referral-fee` on any rate they have named, to settle the economics gate; `motion-selector` when the motion type is unclear; `ipp-score` for the fit score. Pass every input explicitly, show the inputs you used, and say which were the user's and which you proposed. The rules, including what to do when the connector is unavailable, are in the house rules (`${CLAUDE_PLUGIN_ROOT}/references/house-rules.md`).

## The fit score

Run `ipp-score` on the connector. With the user's own profile, pass `dimensions` as a list of
name, weight and rating. With the default profile, pass `ratings` keyed by dimension. Leave out any
dimension the user could not rate. Pass `deal_breakers` with each one's state: Clear is `clear`,
Problem is `problem`, Don't know yet is `unknown`.

Report what it returns: each dimension's rating and points, any excluded dimension and the score
with it at a neutral 3, the total and band, and the band sensitivity line. If one step on a single
rating would change the band, name that dimension and say the decision rests on it.

## When nothing can be assessed yet

If no deal-breaker could be answered either way and no fit dimension could be rated, the decision is
**Not yet**, every time, with this reason: "there is nothing to judge until these questions are
answered". Do not refuse to give a decision, do not invent a fifth label, and do not compute a
score over zero rated dimensions. List the two or three questions that would make it decidable,
with who would know, and stop.

## Produce

The scorecard: gate results, dimension scores with the one line each rests on, any
excluded dimension with the weights renormalised and the sensitivity line, the weighted score and
band, and the decision in one sentence. For go or conditional go, a tier hypothesis; for not yet,
the specific condition that would change it. Then one next step.

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
