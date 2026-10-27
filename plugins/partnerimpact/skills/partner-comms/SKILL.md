---
name: partner-comms
description: "Use this skill to write any message to or about a partner: a note or email to a partner, a follow-up, the joint value proposition, an executive update on a partnership, and hard messages such as a tier demotion, a missed commitment or an exit."
metadata:
  author: "Bart Dirksen"
  copyright: "© 2026 PartnerImpact (Bart Dirksen)"
  license: "CC-BY-4.0"
  version: "1.1.2"
---

Draft the message the user asked for. Run this in the conversation; do not delegate to a subagent.

Read `${CLAUDE_PLUGIN_ROOT}/references/interview.md` and follow it. Your playbook is
`${CLAUDE_PLUGIN_ROOT}/agents/partner-communicator.md`.

## Round 1 (AskUserQuestion)

1. **What is it?** Joint value proposition · Update or follow-up · Ask to an executive · Difficult
   message (demotion, exit, missed commitment)
2. **Who reads it?** Partner · Our executives · Our sales team · Their executives
3. **How is the relationship right now?** Healthy · At risk · Ending

## Round 2 (text, one message)

- The one thing the reader must take away.
- The action you want from them, and by when.
- The facts, numbers or commitments it has to include, exactly as they should appear.

For a demotion or an exit, ask one more thing before drafting: which trigger fired, and over what
period. A tier decision with no measured trigger behind it is not ready to be communicated; say so
in one line and offer to draft it anyway if the user confirms the decision is made.

Never invent a number, a name or a commitment to make a sentence land; if one is needed and missing,
ask for it.

## Produce

The draft, written to `${CLAUDE_PLUGIN_ROOT}/references/writing.md` and checked with its final pass:
the point first, no throat-clearing, no summary closer. For a hard
message, say the hard thing early and cleanly. Offer one tighter alternative opening. Present it for
review; never send it.

---

© 2026 PartnerImpact (Bart Dirksen), [partnerimpact.net](https://partnerimpact.net). Licensed CC BY 4.0 with attribution. See NOTICE.
