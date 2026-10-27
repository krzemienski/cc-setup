# Worked Examples

One per input type. Outputs are condensed where marked — real outputs expand every phase.

## Example 1 — Voice transcript → Task Document (Mode A)

Input:
"Okay so the dashboard the managers use, charts only refresh on reload which is annoying, performance is bad past a few thousand rows, the date picker filter changes the display but doesn't actually filter, CSV export sometimes has wrong columns, mobile is completely broken, and we need a new inventory metrics section — I think there's a websocket thing for the real-time stuff, check the existing code first, quarterly review is coming so this is really important"

Clarity gate: proceed — objective clear; assumptions logged (React stack; websocket acceptable; "a few thousand rows" ≈ 5,000 test target).

Output (condensed):
# Task: Manager Dashboard Overhaul for Quarterly Review

<task_context> five defects + one feature, deadline = quarterly review; date-filter and CSV fixes sequenced first (correctness), then performance, real-time, inventory section, mobile. Assumptions: React; Socket.io-class websocket acceptable. </task_context>

<research_phase> R1: real-time (SWR/React Query + Socket.io), virtualization (ag-Grid/recharts windowing); R3: official docs for selections; R5: full codebase read. </research_phase>

<orchestration> High tier — 10–20 agent ceiling; parallel workstreams (codebase analysis, real-time design, performance research, mobile audit, API analysis); sequential phases: critical fixes → performance → real-time → inventory → mobile → validation. </orchestration>

<implementation> Phase 1: date-picker filter rebind + CSV column mapping fix. Phase 2: virtualization/memoization to 5,000+ rows. Phase 3: websocket + data-fetching layer, connection status, reconnection. Phase 4: inventory section reusing existing section patterns. Phase 5: responsive fixes, touch interactions. </implementation>

<validation> live-data real-time check; filter correctness across views; CSV column parity; 5,000-row performance test; iOS/Android validation; no regressions. </validation>

## Example 2 — Structured document → Task Document (Mode A)

Input: an uploaded PRD with sections Overview / Goals / Non-Goals / Requirements R1–R8 / Acceptance Criteria / Deadline.

Playbook §3 applied:
- PRD Requirements R1–R8 become Implementation checkboxes verbatim (no paraphrase drift).
- PRD Acceptance Criteria become the Validation section verbatim.
- Non-Goals become scope boundaries in <task_context>.
- Gaps the PRD lacks — research tracks, orchestration plan, memory/documentation sections — are added and marked as filled gaps (assumptions).

Output (condensed):
# Task: [PRD title]

<task_context> Background from PRD Overview; definition of done = all acceptance criteria met; non-goals listed as scope boundaries; assumptions: gaps filled (research, orchestration, validation defaults). </task_context>
<research_phase> R1+R3 for each capability in R1–R8; R4 if any requirement touches regulated data. </research_phase>
<orchestration> tier from requirement count and coupling; parallel/sequential from the PRD's own dependency hints. </orchestration>
<implementation> one phase per requirement cluster, checkboxes quoting requirement IDs. </implementation>
<validation> the PRD's acceptance criteria, one checkbox each, plus regression and real-data items. </validation>

## Example 3 — Existing prompt → Enhanced Prompt (Mode B)

Input: "Here's my prompt: 'You are a helpful assistant. Summarize meetings. Don't be too long. NEVER invent action items.' Make it better."

Playbook §4 applied — intent preserved, structure upgraded, negative rules converted, contradictions checked.

Output:
<identity>You are a meeting-intelligence specialist: an expert executive-assistant AI that turns raw meeting transcripts into decisions, action items, and context-preserving summaries a reader can act on without attending.</identity>
<purpose>Given a meeting transcript (with or without speaker labels), produce one structured summary and nothing else — no preamble, no commentary.</purpose>
<context>The reader was not in the room. Transcripts may be messy: cross-talk, transcription errors, topic jumps. Speaker labels may be missing or wrong.</context>
<task>1) Reconstruct the discussion by topic, not chronology. 2) Extract: decisions made (with who decided), action items (owner, task, deadline if stated), open questions, key context. 3) Emit exactly one markdown document with sections: Summary (≤150 words), Decisions, Action Items (table), Open Questions. 4) Target length: the Summary section ≤150 words; the full document ≤1 page per 30 minutes of meeting.</task>
<constraints>- Record only action items explicitly stated or clearly committed to in the transcript; if ownership is ambiguous, mark the owner "unassigned" rather than guessing. - Keep the Summary within its length target. - Flag transcription-garbled passages as "[unclear]" instead of reconstructing them.</constraints>
<examples>[one input/output pair: 6-line messy transcript → the four-section document]</examples>

## Example 4 — Mixed bundle → one Task Document (Mode A)

Input: voice memo ("consolidate the payment processors, it's urgent") + uploaded legacy spec (describes the old single-processor design) + draft prompt snippet ("always test in production").

Playbook §6 applied:
- Voice memo supplies objective and urgency; spec supplies current-state constraints (§3: its decisions are constraints); prompt snippet supplies a rule candidate (§4).
- Conflict: memo says "consolidate to one place," spec documents two services — precedence: current explicit instruction wins; consolidation proceeds.
- Rule candidate upgraded: "always test in production" → "validate with real data in production or production-like environments" (recorded in design notes of the artifact).

Output: one Task Document (Critical tier, multi-repo analysis, verification pass on idempotency), with the merge resolutions listed in <task_context> Assumptions.

## Example 5 — Clarity gate in action

Input: "Make the reports faster and move us off the old system sometime this quarter."

Gate evaluation: "faster" → assumable default (set measurable target, log it). "Off the old system" → target system unspecified; migration destination changes what gets built → ASK.

Questions emitted (2, not 10):
1. Migrate reporting to which platform — the existing warehouse (recommended, already hosts 80% of data) or a new BI tool?
2. Performance target: is <2s p95 load time acceptable (recommended), or stricter?
Fallback stated: "Proceeding with warehouse + 2s p95 if unanswered."
