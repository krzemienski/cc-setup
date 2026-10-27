# Ideal Partner Profile (IPP)

A weighted scoring model for partner fit. It answers one question: should we invest in this
partner, and at what level? Qualification is a commercial filter, not a courtesy: the honest
answers are go, no-go, and not-yet.

The weights below are a neutral default. Recalibrate them to your motion: a marketplace motion
weights Market Access and Technical Fit; a services-led motion weights Delivery Capability and
Commitment.

> **These are defaults.** If the user tells you their own dimensions, weights, gates or bands, use
> theirs, renormalise the weights to 100 and show it, and say in one line which values were theirs
> and which were defaults.

## Scoring dimensions

Score each 1–5, then apply the weight. Total is out of 100.

| Dimension | What you're scoring | Weight |
|---|---|---|
| **Market access** | Reach into your ICP: accounts, segments, geographies you don't already own | 20% |
| **Strategic fit** | Alignment of their thesis, roadmap, and customer base with yours | 15% |
| **Technical / solution fit** | Does the joint solution solve a real customer problem cleanly | 15% |
| **Commercial motion fit** | Do their sales motion and deal sizes match how you sell | 15% |
| **Commitment signal** | Exec sponsorship, dedicated headcount, willingness to co-invest | 15% |
| **Delivery capability** | Can they implement, support, and retain the customer | 10% |
| **Economic viability** | Does the unit economics work for both sides after rev-share/margin | 10% |

**Score = Σ (dimension score × weight) × 20**, giving a 0–100 result. The `ipp-score` calculator on
the connector computes it, for this default profile or for a profile the user built for one kind of
partner (see `profile-by-motion.md`).

### When a dimension can't be evidenced

Common, and it has one rule so that two people scoring the same partner reach the same number.

**Exclude the dimension, renormalize the remaining weights to 100, and print the sensitivity.**

1. Leave the dimension **unscored**: never a guessed 3 to keep the arithmetic tidy.
2. Renormalize the weights of the scored dimensions to sum to 100, and show that you did.
3. State the sensitivity in one line: what the total would be if the missing dimension came in at a
   neutral 3. If that moves the band, the decision is not safe to make yet and you say so.
4. Carry the unscored dimension into the output as a "Still open" item with who would know.

Economic viability is the dimension this hits most, because nothing public establishes it.

## Bands and decision

| Band | Score | Decision |
|---|---|---|
| Priority | 80–100 | Go. Fast-track. Candidate for top tier. |
| Qualified | 60–79 | Go. Standard onboarding. Tier by segmentation model. |
| Not yet | 45–59 | Not-yet. Name the one or two gaps that would move them up, and revisit. |
| Pass | < 45 | No-go. Document why, keep the door open if a gap is structural not permanent. |

**Nothing assessable is "Not yet".** When no gate can be answered either way and no dimension can
be rated, there is no score and the decision is Not yet, with the reason "nothing to judge until the
open questions are answered". It is never left undecided and never given another label.

## The anti-fit gate (run this first)

Run the gate before scoring. These protect you from partners that look good on paper and cost you
in practice.

### Three states, not two

| State | Meaning | What it does |
|---|---|---|
| **Pass** | Cleared on evidence | Proceed |
| **Fail** | A hard fail, on evidence | **No-go. Stop. Do not score.** |
| **Unassessable** | The fact needed is not available yet | Proceed, but the decision downgrades |

**Unassessable is the normal case on a first pass, and the model has to survive it.** Four of the
five gates below turn on facts that are not public: channel conflict depends on how *you* sell,
and economics, executive commitment, and delivery quality are all private. A partner researched from
public sources will routinely arrive with three gates unassessable. That is not a failure of the
research; it is what the research skill's confidence grading says will happen.

An unassessable gate never blocks scoring and never counts as a pass. It converts the decision from
**go** to **conditional go**, with each open gate named as a question, an owner, and the
conversation that would answer it. A gate silently treated as passed is the single most expensive
mistake this model can make.

Only a **Fail** stops the process.

- **Channel conflict**: do they sell a directly competing product, or would the partnership
  cannibalize your direct motion in your core segment?
- **Brand / trust risk**: reputation, compliance, or customer-treatment concerns you can't govern.
- **Zero unique reach**: everything they touch, you already cover. No incremental access = no
  leverage.
- **No executive pulse**: nobody senior on their side will own it. Partnerships with no sponsor
  die in the field.
- **Economics underwater**: after rev-share, MDF, and enablement cost, the partnership loses money
  at any realistic volume.

## Output of a qualification

1. **Gate result**: pass / fail / unassessable on each anti-fit criterion, with the fact that's
   missing named for each unassessable one.
2. **Scorecard**: each dimension scored with the one-line evidence it rests on.
3. **Weighted total and band.**
4. **Decision**: go / conditional go / no-go / not-yet, with the reason stated in one sentence.
5. **If conditional go**: the open gates as named questions with owners. This is a real decision,
   not a deferral: it says invest in the conversations, and here is exactly what they must settle.
6. **If not-yet**: the specific, testable condition that would change the answer. Distinct from
   conditional go: not-yet means the partner isn't ready, conditional go means *you* don't know yet.
7. **If go or conditional go**: a tier hypothesis to hand to the segmentation model.

Never invent evidence to fill a dimension. An honest "Still open: reach into mid-market?" beats a
guessed 4.

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
