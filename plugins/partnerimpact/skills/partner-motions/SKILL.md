---
name: partner-motions
description: "This skill should be used when the partner's motion type matters, qualifying, enabling, pricing, or co-selling with a referral partner, reseller, technology/integration partner, marketplace, services SI, or strategic alliance. Provides the per-type deltas: what shifts in qualification, economics, enablement, and co-sell for each."
metadata:
  author: "Bart Dirksen"
  copyright: "© 2026 PartnerImpact (Bart Dirksen)"
  license: "CC-BY-4.0"
  version: "1.1.2"
---

# Partner Motions

Six motion types, and they share almost nothing operationally. A marketplace listing and a services
SI are both "partners" in the same slide and nothing alike in practice: different qualification
weights, different money, different definition of activated, and in one case no co-sell at all.

Programs that treat all six identically produce a tier structure nobody fits and an enablement path
most partners abandon. This skill carries the deltas. The base frameworks stay in
`partner-frameworks`, `program-architecture`, `partner-economics`, and `co-sell-motion`: these
references say what changes.

All references are embedded in this skill's `references/` folder.

## When to load this skill

- Qualifying a partner whose motion type is known, which dimensions should dominate
- Designing enablement: what "activated" means for this type
- Modeling economics: whether money changes hands at all, and in which direction
- Building a co-sell plan, or establishing that there is no co-sell motion here

## The references

| Motion type | Reference |
|---|---|
| Referral / agency | `references/referral-agency.md` |
| Reseller / VAR | `references/reseller-var.md` |
| Technology / integration | `references/technology-integration.md` |
| Marketplace | `references/marketplace.md` |
| Services / SI | `references/services-si.md` |
| Strategic alliance | `references/strategic-alliance.md` |

Each covers four deltas in the same order: **Qualification** (which IPP dimensions carry the
weight, and the type-specific anti-fit), **Economics** (how money moves), **Enablement** (what
activated means and how long it takes), **Co-sell** (the motion, or its absence).

## When the motion type is not obvious

Run **Which Partner Motion?** on the connector: `partner_calculator` with id `motion-selector`, mode
`describe`, then `run`.
Five questions rank the six motion types by fit and name the trade-off the leading one commits you
to. It ranks; it does not decide, and a close top two is a real answer.

## How to use them

Establish the motion type first. It is the single most useful fact about a partner, and it
determines which of these references applies.

**Two motions is the common case, not the exception.** An order-management platform that both
integrates and runs a certified agency network is a technology partner and a services partner at
once. When a partner runs two, read the **primary** reference in full and the
secondary for its deltas only, then say in one line which motion the relationship is built
on. That's the one whose activation definition and economics govern. Where the two references
disagree (a technology partner has no real co-sell motion, a services partner does), the primary
wins and you name the tension rather than averaging it.

If the user has said they do not run a motion type, don't recommend it: they have excluded it
deliberately.

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
