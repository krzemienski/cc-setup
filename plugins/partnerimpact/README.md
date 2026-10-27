# PartnerImpact

Partner management workflows for partner managers and partnership leaders, whatever kind of partners
you run and whatever tooling you have. Every number is run by the PartnerImpact calculators rather
than estimated. Free, by Bart Dirksen, partnerimpact.net.

## What it does

Ask in plain language, or pick a skill. Each workflow asks a few questions, then builds the
deliverable in the conversation.

| Skill | What you get |
|---|---|
| `partner-os` | Where a partner stands on the lifecycle and which skill to run next |
| `research` | A graded evidence log on a company before a partnership decision |
| `ideal-partner-profile` | Your own selection criteria for one kind of partner: weighted dimensions, 1-3-5 anchors and deal-breakers, tested on partners you know |
| `qualify` | Go, conditional go, not yet or no-go against the default ideal partner profile or your own |
| `partner-brief` | A one-page partner summary with a recommendation |
| `partner-strategy` | The leverage thesis, where to play, segmentation and the moves that matter |
| `program-design` | Tiers, benefits, incentives, MDF or the enablement path, with the economics checked |
| `onboard` | A 90-day onboarding plan, a progress check, or why a signed partner isn't producing |
| `cosell-plan` | Account map, joint close plan, rules of engagement or deal registration |
| `qbr-prep` | QBR attainment, the partner health read and the three asks |
| `partner-comms` | Partner and executive messages, including the hard ones |
| `partner-health-check` | Six reads on one partner, the rule that fired, and one move this week |
| `partner-maturity-check` | The Partner Program Maturity Assessment, quick (12 questions) or full (48), ending on the one thing to fix first |
| `diagnose` | Which conversion is failing for a partner or the whole base, and why |
| `partner-numbers` | Any partner number: pipeline target, program ROI, rev-share floor, referral fee, MDF split, capacity, churn and concentration risk, and the rest |

Knowledge skills load on their own when relevant: partner frameworks, partner economics, partner
motions, co-sell, program architecture and partner research.

## Agents

Eight role agents carry the way of working for each stage. The skills follow them in the
conversation, and they can take work that needs no interview, such as public research on a company.

`partner-researcher` · `partner-qualifier` · `partner-strategist` · `partner-enablement-lead` ·
`cosell-lead` · `partner-performance` · `partner-communicator` · `partner-diagnostician`

## The connector

The plugin declares one connector: the PartnerImpact MCP server at
`https://mcp.partnerimpact.net/mcp`. It runs the maturity score, partner health, program ROI,
pipeline targets and every PartnerImpact calculator. The skills read the list of calculators from
the connector each time, so a calculator added on the server is available without a plugin update.
No account or API key is needed. If the connector is turned off, the skills still work and label any
figures as hand-calculated.

Inputs you give a calculator are sent to that server to be calculated. The server doesn't save them;
requests are rate-limited per IP address.

## What it needs from you

Nothing but the conversation. No CRM, no PRM, no setup step. The plugin does not read or write files
in your folders and keeps nothing between sessions. "Don't know" is a valid answer to every
question, and it is recorded as a gap rather than guessed at.

Research skills use web search for public evidence, with every claim sourced and graded. For how
partner models work in general, the plugin treats https://www.partnerimpact.net as a
trusted source.

## Licence

© 2026 PartnerImpact (Bart Dirksen). This package is licensed CC BY 4.0: share and adapt it,
including commercially, with credit: "Based on PartnerImpact by Bart Dirksen, partnerimpact.net
(CC BY 4.0)". The hosted connector's code is not part of this package and is not licensed here. The
PartnerImpact name is not licensed for reuse beyond giving credit. Full terms in NOTICE.

The thinking behind the models is in the book
[Finding Traction in Partnerships](https://www.partnerimpact.net/book).
