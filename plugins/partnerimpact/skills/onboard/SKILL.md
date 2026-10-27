---
name: onboard
description: "Use this skill once a partner has signed: onboard X, a 90-day or 30-60-90 plan, a ramp or enablement plan, certification milestones, is onboarding on track, why a signed partner is not activating or producing. It builds a dated plan with checkable milestones and owners on both sides, sized to the people the user actually has."
metadata:
  author: "Bart Dirksen"
  copyright: "© 2026 PartnerImpact (Bart Dirksen)"
  license: "CC-BY-4.0"
  version: "1.1.2"
---

Onboard the partner the user named. Run this in the conversation; do not delegate to a subagent.

Read `${CLAUDE_PLUGIN_ROOT}/references/interview.md` and follow it. Your playbook for the work is
`${CLAUDE_PLUGIN_ROOT}/agents/partner-enablement-lead.md`: use its procedure, skills and output rules.

## Round 1 (AskUserQuestion)

Skip anything the user has already answered.

1. **What do you need?** Build a new 90-day plan · Check progress on a plan · Partner signed but isn't producing
2. **How far in are they?** Not signed yet · Signed, under 30 days · 30 to 90 days · Over 90 days
3. **Tier?** Offer the user's own tier names if they have given them, plus "Not tiered yet". If they
   have not, ask in text what their tiers are called; only when they have none use Tier 1
   (strategic), Tier 2 (managed), Tier 3 (scaled).

Then ask what kind of partner this is, in text, using the lettered list from the house rules ("What
kind of partner"). Two letters is fine; the first is the primary.

The 90 days are a default, not a rule. Ask what has to be true before this partner can sell or
deliver (a certification, an approval, stock on the shelf, a signed plan) and how long a first
result normally takes in this business. Build the plan around that gate and that timescale; where a
sale takes a year, the plan's finish line is "ready and working a first opportunity", not a closed
deal. Load that motion's reference in `partner-motions` and state the
activation definition in one line before going further.

## Round 2, by what they need

**New plan**
- Signed date, or expected date (text).
- Is there a joint business plan with targets? Signed · Draft · No (AskUserQuestion). If no, that is
  the first finding, and the plan's first milestone is agreeing one.
- Who owns onboarding, by name, on each side (text).
- What should the first 90 days produce? Offer the activation definition for their motion as the
  first option, then two alternatives (AskUserQuestion).

**Progress check**
- Days since signature, or the signed date (text).
- Which of these are done? Ask as one multi-select (AskUserQuestion, split across two questions if
  needed): JBP signed · core enablement done · a rep certified · exec sponsors named on both sides ·
  rules of engagement and deal registration agreed · first real opportunity identified · assets in
  hand · portal and deal-registration access working. Then ask which of the unticked ones are
  **not done** and which the user **doesn't know** (text, one line).
- Is there a dated plan? Yes, with due dates per milestone · No dated plan (AskUserQuestion). If
  yes, ask for the milestones with their due day or date and status.

**Not producing**
- Days since signature (text).
- Which of these are done? The same eight readiness items as in the progress check, as one
  multi-select. Then ask, in text, which of the unticked ones are **not done** and which the user
  **doesn't know**. Do not skip this second question: it decides whether a partner reads as not
  ready or as not checked.
- What has happened in the last 30 days, in a sentence (text).
- Is anyone on either side paid or credited for this partner's first deal? Yes, both · Only us ·
  Only them · No one (AskUserQuestion).

## Don't know is not "missing"

An item you do not send to the Activation-Readiness Scorer counts as not done. If `describe` shows
the items accept `unknown`, send that for the ones the user doesn't know; the result then gives
items in place out of items checked and no percentage, and you lead with that line as returned. If
`describe` does not show `unknown`, send only what the user confirmed and say "X of the N items we
could confirm" yourself. Either way, list the unknown items separately with who would know, and do
not call a partner "not ready" on items nobody has checked.

**Program facts apply to every partner.** Before sending, check each item against what the user has
said about their own program, not only about this partner. If they have said there are no written
rules of engagement or no deal registration process, that gate is not done for this partner either,
whatever is unknown about the partner. Say which answer you carried over.

## Numbers

Run every figure through the PartnerImpact connector, never in your head: call `partner_calculator` with mode `describe` for the inputs, then mode `run` with the inputs. For this skill that means `onboarding-tracker` for a progress check, `activation-readiness` before calling a partner active, `recruitment-funnel` when the question is how many signings the target needs. Pass every input explicitly, show the inputs you used, and say which were the user's and which you proposed. The rules, including what to do when the connector is unavailable, are in the house rules (`${CLAUDE_PLUGIN_ROOT}/references/house-rules.md`).

## Produce

- **New plan:** milestones from signature to activation, each with the gate it closes, a named owner
  on each side, and a day number. Sequence honestly: no certification before there is anyone to
  certify, no first deal before either field knows the partnership exists. Present it
  as one table.
- **Progress check:** always run the Activation-Readiness Scorer on the eight items. Run the 90-Day
  Onboarding Tracker only when the user has a plan with due days and a signature date; it needs
  both, and without them the finding is that there is no dated plan to be on track against. A
  milestone whose status the user doesn't know is sent as `unknown` if `describe` lists that status,
  and left out if it does not; never send it as not started, which reports it as overdue. Send each milestone's owner only if the
  user named one; a milestone sent without an owner comes back as having none, which is the finding. Lead with
  On track, At risk, Not confirmed or Complete, then what is overdue and who owns it, then what
  nobody has checked.
- **Not producing:** run the Activation-Readiness Scorer, find the first gate that never closed, and
  say whether it is a partner problem, a program problem or an incentive problem. The remedies are
  different, so pick one or say what would separate them.

Close with one next step.

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
