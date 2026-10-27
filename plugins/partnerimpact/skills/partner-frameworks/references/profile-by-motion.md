# Ideal partner profile by motion

One profile does not fit six kinds of partner. A referrer is judged on reach and on whether anything
in their work makes your product the next conversation. A reseller is judged on whether their sales
motion and margin work. A service firm is judged on delivery. Scoring all of them on the same seven
dimensions produces a ranking nobody trusts.

This file holds a starter profile for each motion. A starter is a first draft to change: the user
renames, adds and drops dimensions, moves the weights, and rewrites the anchors in their own
products, regions and customers. The default seven-dimension profile in `ideal-partner-profile.md`
remains the fallback when the user has no profile of their own.

## What makes a profile sound

- **Five to seven dimensions.** Fewer and one rating decides everything. More and no weight is
  large enough to matter.
- **Weights sum to 100, and they are unequal.** A flat spread says nothing about what matters. No
  dimension below 5: if it is worth that little, drop it.
- **Every dimension has a measure and three anchors.** The measure says what is being judged. The
  anchors say what a 1, a 3 and a 5 look like, in terms a colleague could check. "Strong fit" is not
  an anchor. "More than 20 shared customers in the target regions" is.
- **Anchors are written in the user's world.** Their product names, their regions, their customer
  type. A starter anchor that still reads generically after the interview has not been finished.
- **Each dimension is marked public or private.** Public evidence can be researched. Private
  evidence (margin, commitment, delivery quality, conflict with the user's own sales team) has to
  be asked for. A profile that is mostly private dimensions cannot be scored from research.
- **Deal-breakers come before scoring, three to five of them.** Each is a fact that ends the
  conversation whatever the score. A failed deal-breaker is a no-go and nothing is scored. One that
  cannot be answered yet turns a go into a conditional go.
- **Bands.** 80 and above priority, 60 to 79 qualified, 45 to 59 not yet, below 45 pass. Change them
  only if the back-test shows the user's known partners landing in the wrong band.

## How to set weights

Ask the user to rank the dimensions first, then to split 100 points. Two checks before accepting:

1. If the top dimension scored 5 and everything else scored 2, would they sign? If yes, the top
   weight is right or too low. If no, it is too high.
2. Is there a dimension where a 1 should end the conversation? That is a deal-breaker, not a
   weighted dimension. Move it.

## The back-test

Score three partners the user already knows in this motion: one strong, one borderline and one
weak. Use the `ipp-score` calculator on the connector for each. The profile passes when the three
come out in that order and the strong and weak ones land in different bands. When they do not,
change the weight or the anchor that caused it and run the three again. Report the three scores on
the profile card.

## Scoring against a profile

Run `ipp-score` on the connector: `partner_calculator` with id `ipp-score`, mode `describe`, then
`run`. Pass the profile's dimensions with their weights and this partner's ratings, and the
deal-breakers with a state of clear, problem or unknown. Leave a rating out when it cannot be
evidenced. The calculator returns the score, the band, the decision, the score if each excluded
dimension came in at a neutral 3, and how close the score sits to a band edge.

---

## Starter: referrers, agencies and introducers

They send you customers and deliver nothing themselves.

| Dimension | Weight | What it measures | 1 | 3 | 5 | Evidence |
|---|---|---|---|---|---|---|
| Market access | 35 | Their reach into customers you want and do not already cover | Their clients are ones you already sell to | Some new accounts in your target segment | Most of their clients are target customers you have never reached | Public and private |
| Referral trigger | 25 | Whether something in their own work makes your product the natural next conversation | No moment in their work points to you | A trigger exists and comes up now and then | A trigger arises in most of their client engagements | Private |
| Client trust | 20 | How much weight their recommendation carries with their clients | Transactional supplier, advice not sought | Trusted on their own subject | Clients ask them what to buy and act on it | Private |
| Commitment | 15 | Whether someone there has a reason to remember you exist | Nobody owns it | A named contact, no targets | A named owner with referral targets or pay tied to it | Private |
| Economic viability | 5 | Whether the fee works for both sides at the deal sizes involved | Fee asked exceeds what the deal can carry | Affordable with little room | Affordable with clear room, and worth their effort | Private |

**Deal-breakers**
1. They already refer to a direct competitor and will not stop.
2. Their client relationship is too transactional for a referral to carry trust.
3. They want a fee for introductions they were already making.

**The qualifying question:** what happens in their business that makes your product the obvious
next conversation?

## Starter: resellers, distributors and dealers

They buy from you and sell on. The customer's experience becomes theirs.

| Dimension | Weight | What it measures | 1 | 3 | 5 | Evidence |
|---|---|---|---|---|---|---|
| Commercial motion fit | 25 | Whether their deal sizes, sales cycle and buyer match how your product is sold | Different buyer and deal size | Same buyer, different cycle or deal size | Same buyer, deal size and cycle as your own sales | Public and private |
| Delivery and support | 20 | Whether they can install, support and keep the customer | No support capacity, intends to pass issues back | Can support with your help | Supports and renews customers on their own | Private |
| Economic viability | 20 | Whether the margin works for both sides at realistic volume | Margin asked is above your pricing floor | Works at volume they have not yet shown | Works at their current volume | Private |
| Market access | 15 | Reach into regions or segments your own team does not cover | Same accounts as your direct team | Some new territory | A territory or segment you cannot reach directly | Public |
| Portfolio fit | 10 | Where your product sits in what they already sell | Competes with a line they favour | Sits alongside, sold on request | Attaches naturally to what they sell every week | Public and private |
| Commitment | 10 | People and investment they will put behind it | No named people | Named sellers, no certification plan | Certified sellers, a business plan and marketing spend | Private |

**Deal-breakers**
1. They resell a directly competing product and yours becomes the fallback quote.
2. Their margin expectation cannot be met above your pricing floor.
3. They want exclusivity in a territory they cannot cover.
4. They intend to resell without supporting, leaving you the support load.

**The qualifying question:** why is selling your product better for them than selling what they
sell now?

## Starter: technology and integration partners

Their product connects to yours. The value is the joint solution.

| Dimension | Weight | What it measures | 1 | 3 | 5 | Evidence |
|---|---|---|---|---|---|---|
| Solution fit | 25 | Whether the joint solution solves a problem customers have, without overlapping what you sell | Major overlap with your product | Partial overlap, some unique value | Fills a gap customers ask you about | Public and private |
| Shared customers | 20 | Customers you already have in common, and what they do today without the integration | None | A handful, no workaround in use | Many, and they run a manual workaround today | Private |
| Strategic and roadmap fit | 20 | Whether their direction keeps the integration relevant | Roadmap makes it redundant | Stable, no conflict | Their roadmap depends on a product like yours | Public and private |
| Co-sell potential | 15 | Ability and willingness to generate joint pipeline | No overlap in target customers, no interest | Some overlap, will react to leads | High overlap, sales team willing to sell together | Private |
| Feasibility and risk | 10 | Integration effort, interface maturity, compliance and financial stability | Immature interfaces, high risk | Manageable effort and risk | Documented interfaces, stable company, low risk | Public and private |
| Regional traction | 10 | Their presence in your target regions | No customers there | Early customers there | Established customers, references and local team | Public |

**Deal-breakers**
1. They are building the same capability natively.
2. No shared customers and no named demand for the integration.
3. Neither side will commit engineering capacity to build and maintain it.
4. Their roadmap is heading somewhere that makes the integration redundant.

**The qualifying question:** how many customers do you already share, and what are they doing today
because the integration does not exist?

## Starter: marketplaces and catalogues

You are qualifying a channel, not a counterparty. Nobody there commits to you.

| Dimension | Weight | What it measures | 1 | 3 | 5 | Evidence |
|---|---|---|---|---|---|---|
| Buyer presence | 30 | Whether your buyers are there and buy this way | Your buyers do not purchase there | Some do, for smaller purchases | Your buyers have budget committed there and spend it | Public and private |
| Transaction model fit | 25 | Whether the way it transacts matches how you sell | Self-serve only, your sale needs negotiation | Private offers possible with effort | Its transaction model matches your sale | Public |
| Economics after the cut | 25 | What is left after the take rate at your price point | Negative at your price | Thin, works for larger deals | Healthy, or offset by shorter procurement | Private |
| Listing effort | 10 | Engineering and compliance work to list, against the volume it can reach | Heavy work for little volume | Moderate work | Light work, or already done | Public and private |
| Promotion and co-sell | 10 | Whether the marketplace's own programs and sellers will help | No programs open to you | Programs exist, entry bar is high | Programs you qualify for, with seller incentives | Public |

**Deal-breakers**
1. The take rate makes the economics negative at your price point.
2. Its own first-party product competes with yours and gets ranking preference.
3. Your buyer has no procurement access to it.
4. Listing requirements demand engineering work out of proportion to the volume.

**The qualifying question:** does listing here reach a buyer you cannot reach, or does it move
existing deals into someone else's checkout at a worse margin?

## Starter: service firms, consultancies and integrators

They deliver or implement your product. They sit inside accounts and often inside the decision.

| Dimension | Weight | What it measures | 1 | 3 | 5 | Evidence |
|---|---|---|---|---|---|---|
| Delivery capability | 30 | Certified people, relevant references and real capacity | Nobody trained, no plan to train | A few trained people, one reference | A certified team with several references in your segment | Public and private |
| Account access | 20 | Their standing inside the accounts you want | Not present in target accounts | Present, not in the buying decision | Advises the decision-maker in target accounts | Private |
| Services model fit | 20 | Whether how they staff and bill matches how your product is deployed | Rewards long projects, your product deploys fast | Workable with a packaged offer | Their offer is built around a deployment like yours | Private |
| Economic preference | 15 | Whether implementing you earns them more than what they would otherwise recommend | Earns more on a competing platform | About the same | Your product is their better business | Private |
| Commitment | 10 | Investment in a practice around your product | No practice, opportunistic | Named lead, small team | A practice with targets and its own marketing | Private |
| Regional coverage | 5 | Delivery people where your customers are | None in target regions | Some regions | All target regions | Public |

**Deal-breakers**
1. No certified delivery capacity and no plan to build it.
2. They make more money on a competing platform and will steer accordingly.
3. They will take the work and subcontract it to people you have never assessed.
4. Their billing model rewards long engagements and your product is built to deploy fast.

**The qualifying question:** does implementing your product make them more money than the
alternative they would otherwise recommend?

## Starter: strategic alliances

One large joint relationship. Run the scorecard to discipline the enthusiasm, and weight it
differently from every other motion.

| Dimension | Weight | What it measures | 1 | 3 | 5 | Evidence |
|---|---|---|---|---|---|---|
| Strategic fit | 25 | What the two companies can do together that neither can do alone | Nothing a normal partnership could not do | One joint offer of real value | A joint position that changes how both go to market | Public and private |
| Executive commitment | 25 | Sponsors on both sides with authority and a personal stake | No sponsor with authority | A sponsor on one side | Sponsors on both sides with targets tied to it | Private |
| Market impact | 20 | Whether it changes the size of your business or only adds to it | Adds a few deals | Opens one new segment | Opens a market you could not enter alone | Public and private |
| Aggregate economics | 15 | Return across every motion in the relationship, after the cost of running it | Negative once coordination cost is counted | Positive, slow to pay back | Clearly positive across motions | Private |
| Capacity to run it | 10 | Whether your organisation can absorb the senior attention it takes | No one senior has the time | A part-time owner | A dedicated alliance lead and executive time set aside | Private |
| Solution fit | 5 | Whether the joint offer works for the customer | Two products in a diagram | Works with effort | Works cleanly, customers already combine them | Public and private |

**Deal-breakers**
1. No executive sponsor on either side with real authority and a reason to care.
2. Competitive overlap large enough that legal or product will block the interesting parts.
3. It is an announcement with the implementation plan to follow later.
4. Your organisation cannot absorb the coordination cost.

**The qualifying question:** what can you do together that neither can do alone, and is it worth
the executive attention it will consume?

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
