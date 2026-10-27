# Clarification Protocol

The clarity gate sits between input analysis and generation. Its job: resolve ambiguity deliberately — by asking when it matters, by explicit assumption when it doesn't, never by silent guess.

## The ask / assume / proceed decision tree

For each open ambiguity, walk this tree in order:

```
1. Would different answers change WHAT gets built
   (objective, target system, hard constraints, acceptance criteria)?
   ├─ No  → ASSUME: pick the reasonable default, log it, proceed.
   └─ Yes → 2. Can a quick search or file read resolve it?
            ├─ Yes → RESOLVE yourself; record the finding and source.
            └─ No  → 3. Is there a clearly dominant default
                     (what 9 of 10 competent teams would choose)?
                     ├─ Yes → ASSUME, log it prominently, proceed.
                     └─ No  → ASK.
```

Additional ask-triggers regardless of the tree:
- Two inputs conflict and the §6 precedence rules don't resolve it.
- The deliverable itself is unclear (task document vs. enhanced prompt vs. both).
- An irreversible or high-cost action is implied but not stated (data migration, production deploy, paid API spend).

## Asking well

- **Maximum 3 questions** per round. More than 3 means the analysis is incomplete — go back and extract more before asking.
- **Every question carries a recommended default**: "Which database — PostgreSQL (recommended, matches your existing stack) or MySQL?" The user can answer with one word.
- **Questions are concrete and answerable** — never "what do you want?" Ask about the decision, not the mood.
- **Batch all questions in one message**, numbered, with the assumption you'll proceed on if unanswered.
- **State the fallback**: "If I don't hear back, I'll proceed with PostgreSQL and flag it in Assumptions." (When operating in a non-interactive agent harness, skip waiting — proceed on defaults and log.)

## Assumption ledger

Every assumption, from any source, lands in the artifact's Assumptions section in this format:

```
- Assumed: [statement] — basis: [why this is the reasonable default] — impact if wrong: [what breaks / rework cost: low|medium|high]
```

Impact ratings drive behavior:
- **high** → should have been a question; if it slipped through, flag it in the artifact's first line of the Assumptions section.
- **medium/low** → proceed normally.

## Anti-patterns

- Asking about things a search or file read can answer.
- Asking about preferences the artifact can expose as options ("I'll use X; switch to Y by changing one line").
- Re-asking what the input already stated, even indirectly.
- Burying assumptions in prose — they live only in the ledger.
- Letting a question block trivial work: when the core objective is clear, generate the artifact and note open questions inside it rather than stalling.
