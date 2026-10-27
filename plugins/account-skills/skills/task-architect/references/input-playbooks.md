# Input Playbooks

How to extract, normalize, and preserve intent per input type. Load the sections matching the classification from SKILL.md Step 1. Every playbook ends at the same place: a coherent internal picture of (a) core objective, (b) definition of done, (c) constraints, (d) technical context, (e) urgency/deadlines, (f) open ambiguities for the clarity gate.

## Contents
- §1 Voice transcript
- §2 Rough brief
- §3 Structured document
- §4 Existing prompt
- §5 File/codebase reference
- §6 Mixed bundle & precedence rules

---

## §1 Voice transcript

Signals: filler words, false starts, repetitions, non-linear order, missing punctuation, transcription errors, run-on topic switches.

Extraction rules:
- Reconstruct intent, not transcript order. Group related statements scattered across the text (the opening and the closing often describe the same requirement twice — merge, don't duplicate).
- Treat repetitions as emphasis: a requirement stated twice is a priority signal, not two requirements.
- Interpret transcription noise charitably but flag guesses: "fable opus k3" may mean real product names — resolve with a quick search when the term matters, otherwise flag it in Assumptions.
- Mine accidental details: names ("Jim's microservice"), vague dates ("built in March or April"), approximations ("a few thousand rows") — record as leads with their uncertainty attached.
- Catch urgency markers ("ASAP", "broken", "customers complaining") and deadline markers ("quarterly review") — they set task ordering.
- Discard pure filler ("okay so", "right?", "you know") and false starts superseded by a later correction — the correction wins.

Voice-pattern routing:
| Pattern | Task shape |
|---|---|
| "fix the thing where…" | Debug: research tools → analyze code completely → root cause → fix with established patterns → validate with real data |
| "make it work with…" | Integration: research SDKs/connectors → map integration points → implement with library patterns → test live |
| "build new feature" | Feature: research existing libraries → evaluate → install/configure → implement → validate with real data |
| "the [X] is broken" | Emergency fix: similar-issue research → complete file analysis → root cause → minimal-change fix → validation first in order |
| "refactor the…" | Refactor: full codebase analysis → pattern research → incremental plan → verify at each step |
| "look at these files and…" | File-specific: read EVERY line of named files → full context → research patterns → implement → verify against requirements |

## §2 Rough brief

Signals: chat-length text, bullet dumps, half-sentences, implicit context the user assumes you share.

Extraction rules:
- Separate stated facts from implied expectations; implied expectations become either questions (clarity gate) or recorded assumptions.
- Expand shorthand into explicit requirements ("make it fast" → measurable performance target, flagged as assumed if not clarified).
- Preserve user's own priorities: order in the brief usually signals importance.
- Watch for scope anchors ("just", "only", "for now") — they bound scope; honor them in the task document.

## §3 Structured document

Signals: headings, sections, numbered requirements, acceptance criteria, tables — a spec, PRD, ticket, RFC, README, wiki, or an existing task document.

Extraction rules:
- Honor the existing structure: map document sections to task-document sections instead of flattening. Decisions already made in the document are constraints, not open questions.
- Extract verbatim: acceptance criteria, constraints, non-goals, deadlines. Quote them; do not paraphrase away precision.
- Identify gaps against the task template (missing validation criteria, missing orchestration plan) and fill them — mark filled gaps as assumptions.
- If the document is itself a task document, enhance rather than rewrite: add missing sections (research, orchestration, validation, memory), upgrade vague items to concrete checkboxes, keep every original requirement.
- Never drop a requirement silently. If two requirements conflict, that conflict goes to the clarity gate.

## §4 Existing prompt

Signals: system-prompt blocks, identity/purpose sections, instruction lists, "improve / combine / merge this prompt", multiple prompts to unify.

Extraction & transformation rules (Mode B output):
- Preserve intent absolutely: every behavioral rule in the source survives the rewrite, unless the user asked for its removal or two rules directly conflict (conflicts → resolve with the stronger/clearer phrasing and note the resolution).
- Upgrade structure to identity / purpose / context / task / constraints / examples.
- Convert negative rules to positive framing; remove caps-shouting; replace fixed reasoning quotas ("think 500 steps") with effort calibration and verification checkpoints.
- Keep the source's examples unless they contradict the upgraded structure; align every example detail with the desired behavior.
- When combining two or more prompts: deduplicate overlapping rules (keep the stricter), merge complementary sections, and document the merge choices inside the prompt's own design-notes section if one exists.
- Check for internal contradictions before emitting — an enhanced prompt with conflicting instructions is a failed enhancement.

## §5 File/codebase reference

Signals: named files or directories, pasted code, "read X and Y first", paths.

Extraction rules:
- Every named file is marked for complete end-to-end reading in the task document — no exceptions.
- If files are accessible in the current environment, read them now and ground the task document in what they actually contain; if not, the task document's first phase is complete reading.
- Pasted code is context, not necessarily the work target — determine from the brief whether to modify, debug, or use it as reference.
- Capture stack signals (imports, frameworks, config files) into the technical-context section.

## §6 Mixed bundle & precedence rules

When several input types arrive together (e.g., a voice memo plus an uploaded spec plus a draft prompt):

1. Run each input through its own playbook; produce one merged picture, not one per input.
2. Precedence when inputs conflict:
   - Explicit user instruction in the current message > structured document > existing prompt > voice/brief interpretation.
   - More recent beats older ("actually, scratch that" in a voice memo voids the earlier statement).
   - Specific beats general ("only PostgreSQL" beats "some database").
3. Never average conflicting requirements — either apply precedence or escalate to the clarity gate if precedence doesn't resolve it.
4. The output is still exactly one artifact. If the bundle contains both work-to-do and a prompt-to-enhance, ask which deliverable is wanted (that's a legitimate clarity-gate question) unless the message makes it obvious.
