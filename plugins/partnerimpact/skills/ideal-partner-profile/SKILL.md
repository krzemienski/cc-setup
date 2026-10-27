---
name: ideal-partner-profile
description: "Use this skill to build or revise the criteria for choosing partners of one kind: create an ideal partner profile, an IPP, a partner scorecard, selection criteria or a scoring model for resellers, referrers, technology partners, marketplaces, service firms or alliances, or decide how to weight what matters in a partner. It builds the profile for one partner motion from a starter, with weights that sum to 100, 1-3-5 anchors in the user's own terms and deal-breakers, and tests it against partners the user already knows. Not for profiling one named company."
metadata:
  author: "Bart Dirksen"
  copyright: "© 2026 PartnerImpact (Bart Dirksen)"
  license: "CC-BY-4.0"
  version: "1.1.2"
---

Build the user's ideal partner profile for one kind of partner. Run this in the conversation; do not
delegate to a subagent.

Read `${CLAUDE_PLUGIN_ROOT}/references/interview.md` and follow it. Your playbook is the "Designing
a profile" section of `${CLAUDE_PLUGIN_ROOT}/agents/partner-qualifier.md`. The starters and the
rules for a sound profile are in
`${CLAUDE_PLUGIN_ROOT}/skills/partner-frameworks/references/profile-by-motion.md`: read it in full
before Round 2.

One kind of partner per run. If the user wants profiles for several, finish one and offer the next.

If the user pastes a profile they already have, skip to Round 2 with theirs as the draft and check it
against the rules for a sound profile.

## Round 1: the kind of partner and what it is for

Take what the user has already said. Ask only what is missing.

- **What kind of partner is this profile for?** Use the lettered list from the house rules ("What
  kind of partner"). If the user is unsure, run **Which Partner Motion?** on the connector
  (`motion-selector`) and use its top result, saying it is a ranking and not a decision.
- **What do you sell, and to whom?** One line (text).
- **Which regions or segments matter for this kind of partner?** (text)
- **What must these partners give you that you lack today?** (AskUserQuestion) New customers we
  cannot reach · A gap in our product filled · People to deliver or support · Credibility in a
  market · Something else.

## Round 2: dimensions and weights

Show the starter for that kind of partner as a table: dimension, weight, what it measures. Say in
one line that it is a first draft to change. Then, in one message:

- **Rename, add or drop.** Ask which dimensions do not fit their business and what is missing. Keep
  the set at five to seven. Use the user's words for every dimension from here on.
- **Rank, then split 100 points.** Ask for the order of importance first, then the points.

Before accepting the weights, run both checks from the reference and say what you found:

1. If the top dimension scored 5 and the rest scored 2, would they sign?
2. Is there a dimension where a 1 should end the conversation? If so it is a deal-breaker: move it
   out of the scoring and into Round 3.

Push back once on a flat spread (every weight within five points of the next) and on any dimension
nobody at their company could find evidence for. If the user holds their position, use theirs.

## Round 3: anchors and deal-breakers

- **Anchors.** For each dimension, propose what a 1, a 3 and a 5 look like, rewritten with what the
  user told you in Round 1: their product, their regions, their customers. Each anchor has to be
  something a colleague could check. Show all of them in one table and ask the user to correct any
  that are wrong. Mark every anchor the user did not change as proposed.
- **Deal-breakers.** Show the starter's deal-breakers plus any dimension moved here in Round 2. Ask
  which apply, which do not, and what is missing. Keep three to five.

## Round 4: test it on partners you know

Offer this once, and skip it if the user declines: "Name one strong, one borderline and one weak
partner of this kind, and rate each on the dimensions. If the profile ranks them the way you would,
it works."

For each partner, run `ipp-score` on the connector with the profile's dimensions and weights, that
partner's ratings, and the deal-breakers. Then:

- If the three come out in the user's order and the strong and weak ones are in different bands,
  say so and keep the profile.
- If not, name the weight or anchor that caused it, propose one change, and run all three again.
  Two rounds of adjustment at most; after that, show the result and let the user decide.

If the user knows fewer than three partners of this kind, test on the ones they have and say the
test is thinner for it.

## Numbers

Run every score through the PartnerImpact connector, never in your head: call `partner_calculator` with mode `describe` for the inputs, then mode `run` with the inputs. For this skill that means `ipp-score` for every partner in the back-test, and `motion-selector` when the kind of partner is unclear. Pass every input explicitly, show the inputs you used, and say which were the user's and which you proposed. The rules, including what to do when the connector is unavailable, are in the house rules (`${CLAUDE_PLUGIN_ROOT}/references/house-rules.md`).

## Produce

The profile card, as one block the user can copy whole. Nothing is saved between sessions, so tell
the user to keep it and paste it at the start of a later session.

```
IDEAL PARTNER PROFILE · <kind of partner> · built <date> · v1
For: <what the user sells, to whom, in which regions>

Deal-breakers (any one is a no-go, and nothing is scored)
1. ...
2. ...
3. ...

Scoring (rate each 1 to 5; leave out what cannot be evidenced)
| Dimension | Weight | What it measures | 1 | 3 | 5 | Evidence |
|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... | public or private |

Bands: 80+ priority · 60-79 qualified · 45-59 not yet · below 45 pass
Tested against: <strong> <score>, <borderline> <score>, <weak> <score>   (or: not tested)
```

After the card:

- One line on what came from the user and what is still a starter default or a proposed anchor.
- The weakest part of the profile: the dimension that will be hardest to evidence, or an anchor the
  user was unsure about.
- One next step: qualify a named partner against it, by pasting the card and the partner's name.

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
