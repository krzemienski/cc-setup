---
name: website-bug-hunt
description: >
  Black-box website bug hunt: take any URL — no codebase access needed — and
  exhaustively audit it in a live browser. Crawls every page, exercises every
  element and form at three viewports, runs deep visual QA plus a
  UX-heuristics pass, and pursues every finding to the kill: boundary probe,
  root symptom, blast radius. Every flag is a finding — severity orders,
  never dismisses. Supports relentless bug-quota mode ("find 15 bugs no
  matter what") with depth escalation. Outputs a bug report with repro steps,
  screenshots, and validation-gated fix prompts, plus one MASTER-FIX-PROMPT.md
  remediation artifact for a coding agent. Use whenever the user gives a URL
  and asks to "find bugs", "audit this site", "QA this URL", "test my
  deployed app", "click through everything", "check the site on mobile",
  "find N bugs", or wants a functional + visual + UX sweep of a live site —
  even without the word "bug". A URL plus any testing, inspecting, or
  auditing request = this skill.
compatibility: Requires Playwright (default engine, auto-installed by scripts/setup.sh — works in restricted/ARM64 sandboxes) or the agent-browser CLI, plus network access to the target URL. Parallel mode requires subagent dispatch.
---

# Website Bug Hunt

Audit a live website the way a ruthless QA contractor would on day one: no
source code, no insider knowledge — just the URL, a browser, and the
discipline to click everything, look at everything, and write down every
defect with proof.

This skill is **black-box by design**. Everything you learn about the site,
you learn by driving it. That constraint is also the discipline: a bug you
can't reproduce through the browser isn't a finding, and a finding without a
screenshot doesn't go in the report.

## The Iron Rule

```
Interact with the REAL site. Never simulate, assume, or infer an interaction
you didn't perform. Every finding cites evidence you captured yourself:
a screenshot, a console error, a network response, a DOM snapshot.
A bug without reproduction steps + evidence does not exist.
```

## The Flag Rule

```
If it's flagged, it's a finding. There is no such thing as a "non-high"
that gets waved through. Severity (CRITICAL/HIGH/MEDIUM/LOW) orders the
remediation queue — it NEVER gates whether a finding is logged, evidenced,
prompted, or counted. A LOW contrast failure and a CRITICAL dead checkout
both get an ID, a repro, evidence, a fix prompt, and a slot in the master
prompt. UX findings are findings, not footnotes.
```

The only things that are *not* findings: features the site never advertised
(no dark mode on a site that never promised one), and anything you could not
reproduce or evidence. Everything else you noticed and flagged goes in.

## Run-start questions (ASK BEFORE STARTING)

Ask these once, together, then proceed. Don't drip-feed questions mid-run.

1. **Target URL** — if not already given.
2. **What is this site supposed to do?** One or two sentences from the user
   about the site's purpose and the 2-3 most important user journeys. This
   calibrates "bug vs. intentional". If the user doesn't know or doesn't
   answer, infer the purpose from the landing page and state your inference
   in the report header.
3. **Stop condition** — pick one:
   - `full-coverage` *(recommended default)*: stop when every discovered
     page × viewport has been audited and every interactive element exercised
   - `bug-quota <N>` *(relentless)*: do **not stop until N confirmed
     findings are logged — no matter what**. If the standard sweep completes
     with fewer than N, do not declare victory; escalate depth and keep
     hunting (see *Depth escalation ladder* below). Coverage achieved is
     still reported. If N is genuinely unreachable after exhausting the
     ladder, say so plainly with the escalation log as proof of effort.
   - `time-box <minutes>`: best-effort within the budget, prioritized P0→P2

   **Depth escalation ladder** (for relentless quota runs, in order):
   1. Standard sweep — all pages × 3 viewports, all inventory elements
   2. Interaction-state pass — hover, keyboard focus, disabled, loading,
      error, and empty states on every P0/P1 element
   3. Edge-input pass — boundary values in every form field: max-length
      strings, unicode/emoji, leading/trailing whitespace, `0`, negatives,
      script tags (reflected-unescaped = finding), paste vs. type
   4. UX-heuristics deep pass — full Nielsen walk per page (Phase 3 step 3)
      at maximum scrutiny; every violation is a finding
   5. Environment pass — throttled network (slow 3G), rapid double-clicks,
      back/forward navigation, page refresh mid-interaction, deep-link
      directly into inner pages
   6. Extra viewports — 320×568 (small phone), 1920×1080, landscape mobile
   Log each rung entered in `run-config.md` so the report can show the
   escalation trail.
4. **Credentials / gated areas** — "If I hit a login wall or paywall, do you
   have credentials for me?" Collect them up front if possible.
5. **Execution mode** — solo or parallel subagents? Recommend parallel when
   the site has more than ~8 pages and subagent dispatch is available;
   otherwise solo. If subagents aren't available, fall back to solo and say so.

## Tooling

**Playwright (chromium headless) is the default engine.** Set it up and read
the script templates in `references/playwright-engine.md` before Phase 1:

```bash
bash scripts/setup.sh ./hunt-workspace   # installs playwright + chromium, patches missing libs, smoke-tests
source ./hunt-workspace/engine/env.sh    # required before every node invocation
```

`setup.sh` is idempotent and handles restricted sandboxes (no root, ARM64,
missing shared libs like `libXdamage.so.1` — it fetches them unprivileged
via `apt-get download`). Do not start the hunt until its smoke test prints
`SMOKE OK`. Playwright is preferred because it runs where `agent-browser`
cannot (no Chrome-for-Testing build on Linux ARM64), crawls in parallel via
multiple pages in one browser, and attaches console/network/page-error
hooks per page (Template 5) — the invisible-bug detectors.

`agent-browser` is the alternative driver when it's already installed and
running on the host (its daemon keeps the session alive between calls). The
core loop there is: `open` → `wait --load networkidle` → `snapshot -i` →
interact via `@eN` refs → re-snapshot after every navigation:

```bash
agent-browser open <url> && agent-browser wait --load networkidle
agent-browser snapshot -i -C        # -C catches divs with onclick/cursor:pointer
agent-browser screenshot --full <name>.png
```

Command examples in the phases below are written driver-neutrally or in
agent-browser syntax; `references/playwright-engine.md` has the 1:1
translation table plus proven templates for crawl, time-to-content, the
three-viewport pass, interaction outcomes, and error capture. Whichever
driver runs, record it in `run-config.md` and the report header.

Set the viewport per pass (see Phase 3). Always capture console errors and
failed network requests — a silent 500 behind a button that "looks fine" is
a classic HIGH bug. And verify hard HTTP status with `curl` when a "Not
Found" page appears: SPAs often serve soft-404s with HTTP 200
(playwright-engine.md Template 6).

## The 6-Phase Protocol

```
Phase 0  Intake & recon           (ask questions, first-load smoke test)
Phase 1  Crawl & inventory        (map every page and interactive element)
Phase 2  Auth & gated areas       (detect walls, ask user, unlock coverage)
Phase 3  Audit sweep              (per page × per viewport: act + inspect)
Phase 4  Bug confirmation         (reproduce twice, capture evidence)
Phase 5  Report                   (markdown report + fix prompts)
```

### Phase 0 — Intake & recon

Ask the run-start questions. Then load the URL once at desktop viewport and
do a 2-minute smoke test: does the page render, does the console stay clean,
what kind of site is this (marketing page, docs, SPA, dashboard, store)?
Write `hunt-workspace/run-config.md` recording URL, stated purpose, stop
condition, mode, and viewports. Create the evidence tree:

```
hunt-workspace/
├── run-config.md
├── inventory.md
├── bugs/            (one directory per confirmed finding)
├── screenshots/     (page-slug/viewport/state.png)
├── REPORT.md
└── MASTER-FIX-PROMPT.md
```

### Phase 1 — Crawl & inventory

Goal: a structured map of everything auditable. You can't be exhaustive
about a site you haven't mapped.

1. From the landing page, harvest every same-origin link: nav menus, footers,
   in-content links, buttons that navigate. Check `sitemap.xml` and
   `robots.txt` — free coverage.
2. Breadth-first crawl each discovered page, harvesting links as you go, until
   no new same-origin URLs appear (cap at 50 pages unless the user raises it;
   list the uncrawled remainder in the report).
3. On each page, `snapshot -i -C` and record every interactive element:
   links, buttons, form fields, dropdowns, toggles, tabs, accordions, modals,
   carousels, video players, search boxes.
4. Write `inventory.md` — one row per element:
   `| ID | Page | Element | Kind | Expected behavior (your inference) | Priority |`
   Priority: P0 = core journey (checkout, search, play button), P1 =
   secondary, P2 = edge. Infer expected behavior from labels and context —
   a button labeled "Download" that does nothing is a bug precisely because
   you wrote down what it promised.

Assign element IDs once; never renumber. Everything downstream cites them.

### Phase 2 — Auth & gated areas

When the crawl hits a login form, signup wall, or paywall:

1. Log it in the inventory as a gate.
2. If the user provided credentials, authenticate (prefer
   `agent-browser auth save` / `auth login` so the password never enters the
   transcript; `state save` to persist the session across passes and
   subagents).
3. If not, pause and ask: "I found a login at <URL>. Do you have credentials,
   or should I audit only the public surface?" Continue auditing public pages
   while waiting — never idle on a question.
4. Never brute-force, guess credentials, or bypass access controls. Gated
   areas without credentials are reported as "not covered", not as bugs.

### Phase 3 — Audit sweep (the heart of the hunt)

For every page in the inventory, at **each of three viewports**:

| Pass | Viewport | Size |
|------|----------|------|
| Desktop | 1440×900 | primary functional pass |
| Tablet | 768×1024 | layout + touch-target pass |
| Mobile | 375×812 | layout + nav-collapse pass |

Per page × viewport, in order:

1. **Load & settle** — `open` the page, wait for networkidle, then capture
   `screenshots/<page>/<viewport>/initial.png` (full-page).
2. **Visual inspection (deep)** — read the screenshot yourself (never just
   confirm it exists) and walk the `visual-inspection` skill's checklist if
   installed; otherwise apply its core checks inline: overflow/clipping,
   spacing/alignment, contrast (4.5:1 body text, 3:1 large text/UI),
   truncation, touch targets ≥24px, broken images, empty states, horizontal
   scrollbars at mobile width, nav collapsing into a working hamburger.
   Then go beyond first paint — inspect, per page:
   - **Content quality**: typos, placeholder text ("Lorem ipsum", "TODO",
     "undefined", "NaN", "[object Object]"), broken markdown/code-block
     rendering, mixed date/currency formats, mojibake
   - **Scroll-state visuals**: screenshot at top, mid, and bottom of long
     pages — sticky headers overlapping content, footer collisions, and
     lazy-load failures live below the fold
   - **Interaction-state visuals**: capture and read hover, keyboard-focus
     (visible focus ring?), disabled, loading, error, and empty states for
     P0/P1 elements — a missing focus ring or a spinner that never resolves
     is a finding
   - **Zoom check** (desktop pass only): 200% browser zoom — content must
     reflow without loss
3. **UX-experience pass** — walk Nielsen's 10 heuristics against the page
   (use the `ui-experience-audit` skill's protocol if installed; otherwise
   inline): visibility of system status (does every action give feedback
   within ~1s?), match to the real world (jargon-free labels), user control
   (can you undo/cancel/escape modals?), consistency (same action, same
   look, everywhere), error prevention (destructive actions confirmed?),
   recognition over recall (is state visible or memorized?), flexibility
   (keyboard path exists?), minimalist design (noise burying the P0
   journey?), error recovery (do error messages say what to *do*?), and
   help/affordances (do clickable things look clickable — and vice versa?).
   **Every violation is a finding** — logged with an ID, evidence, and a
   severity like any functional bug, not parked in an observations section.
   Example: a modal with no close button and no Escape handler is at least
   a MEDIUM (`UX — modal traps user, no visible dismissal`), evidenced by
   the screenshot and the failed `press Escape` interaction.
4. **Functional pass** — exercise every inventory element on this page.
   Clicking is not enough; verify the *outcome* against the expected
   behavior column:
   - Links: navigate, confirm no 404/500, confirm destination matches label
   - Buttons: click, diff the snapshot (`agent-browser diff snapshot`) —
     a button that changes nothing is a finding
   - Forms: submit empty (validation should catch it), submit valid dummy
     data (should succeed or clearly explain), submit junk (no raw stack
     traces). Use obviously-fake data — never real personal information —
     and don't complete real purchases or destructive account actions.
   - Media: play/pause/seek video and audio; mute; fullscreen
   - Search: query something that exists and something that doesn't
   - Capture `after-<elementID>.png` whenever an interaction changes state
   The full desktop pass exercises everything; tablet/mobile passes re-test
   P0 elements plus anything layout-sensitive (menus, modals, carousels).
5. **Console & network check** — after the functional pass, collect console
   errors and 4xx/5xx responses observed on this page. Each unique one is a
   candidate bug even when the UI looks fine.

**Parallel mode**: dispatch one subagent per page group, each with its own
`--session <name>` so browser state never collides. Sessions are exclusive
per subagent; screenshots and inventory rows are append-only and
parallel-safe. The lead merges findings and personally reads every
screenshot cited by a subagent before accepting its findings — subagents
report, the lead verifies. Auth-gated pages share one authenticated state
file created in Phase 2.

### Phase 4 — Bug confirmation & pursuit (the kill)

A flag is not a write-up. Once flagged, **pursue every finding to the kill**
— you have the authority and the obligation to fully characterize it before
it enters the report. Candidate finding → confirmed finding only after all
six steps:

1. **Reproduce it a second time**, from a fresh page load, following your own
   draft steps exactly. Flaky-once issues get logged as `INTERMITTENT` with
   both attempts described — they are still findings.
2. **Boundary probe** — map exactly where the defect lives and where it
   doesn't. Test the adjacent cases: the other two viewports, logged-in vs.
   logged-out (if auth exists), a second browser page/session, direct
   deep-link vs. in-app navigation. Record the result as a matrix in the
   evidence bundle (e.g., `desktop:PASS tablet:FAIL mobile:FAIL`). A bug
   whose boundary you know is half-diagnosed.
3. **Root-symptom characterization** — capture the DOM snapshot, console
   output, and network trace *at the moment of defect*, then state the
   smallest black-box-visible cause you can defend from evidence: "the
   `POST /api/cart` returns 500 with `TypeError: null price` in the body"
   beats "add-to-cart is broken". Never claim more than the evidence shows.
4. **Blast radius** — sweep the inventory for sibling elements and pages
   likely to share the root symptom (same component, same form pattern,
   same endpoint) and test at least 2–3 of them. Confirmed siblings join
   the finding's "also affects" list.
5. **Minimal repro steps** — trim to the shortest numbered path from URL to
   defect. A stranger with a browser must be able to follow them.
6. **Evidence bundle** in `bugs/BUG-NNN/`: the "before" screenshot, the
   defect screenshot (annotated where the driver supports it), the boundary
   matrix, console/network captures, and DOM snapshot when relevant.

**Severity — ordering, never a gate.** Assign one of:

- `CRITICAL` — data loss, crash, broken core journey (can't buy, can't
  log in, can't play), security-relevant exposure
- `HIGH` — feature doesn't work as labeled, dead P0/P1 controls, broken
  layout that blocks reading or tapping, UX traps (no escape from modal,
  destructive action with no confirmation)
- `MEDIUM` — wrong-but-usable: misalignment, contrast failures, truncation,
  console errors with no visible symptom, most heuristic violations
- `LOW` — cosmetic polish, minor copy issues

Severity decides remediation *order* in the report and master prompt.
It never decides whether a finding is logged, evidenced, prompted, or
counted toward a quota. Per the Flag Rule: if it's flagged, it ships in
the report with the full treatment.

**De-duplicate** — same root symptom on many pages is one finding with an
"affected pages" list (blast radius makes this rigorous), not ten findings.
Quota runs count it once.

### Phase 5 — Report & remediation prompts

Write `REPORT.md` using the exact structure in
`references/report-template.md` (read it before writing). The essentials:
a summary table (pages audited, elements exercised, coverage %, findings by
severity including UX findings), then one section per finding containing —
in this order — title with severity, affected URL(s) and viewport(s), the
boundary matrix, numbered reproduction steps, expected vs. actual, root-
symptom statement, embedded screenshot references, and a **fix prompt**:
a self-contained, copy-pasteable prompt written for a coding agent that has
the codebase, restating the repro, evidence, root symptom, and evidence-
based acceptance criteria (the template has the format). Close the report
with the not-covered list (gated areas, uncrawled pages), the escalation
trail (relentless-quota runs), and an intake note recording the user's
stated purpose or your inference.

**Then write `MASTER-FIX-PROMPT.md`** — a single, self-contained
remediation prompt that orchestrates fixing *every* finding in one
autonomous coding-agent run. Compose it using your prompt-engineering
skills when installed — `create-meta-prompts` for the staged
research→plan→implement pipeline structure, `transform-validation-prompt`
to embed evidence-based validation gates, and `optimize-prompt` /
`deepen-prompt-plan` for final hardening — otherwise apply their principles
inline. The master prompt must contain, in XML-structured sections:

1. **Context** — site URL, stated purpose, driver used, full findings index
2. **Iron Rule** — real-system validation only; no mocks, stubs, or test
   files; a fix is not done until the repro is re-run against the running
   site and evidenced with a screenshot
3. **Per-finding work orders** — ordered CRITICAL→LOW, each embedding the
   finding's repro, boundary matrix, root symptom, and acceptance criteria
   verbatim (no "see report")
4. **Validation gate after every fix** — re-run that finding's repro steps
   live, capture proof, gate-block on failure before moving on
5. **Final gate** — after the last fix, re-run the repro for *all* findings
   plus a smoke pass of the P0 journeys to catch regressions; the run is
   complete only when every finding's repro no longer produces its defect

The exact template lives in `references/report-template.md`. The master
prompt must stand alone: pasting only that file into Claude Code (or a
`/goal` built from it via `northstar` / `goal-condition-architect`) gives
the agent everything needed to remediate and prove it.

Before delivering, verify: every finding has ≥1 screenshot that you
personally read, a boundary matrix, repro steps that start from a URL, and
a fix prompt; `MASTER-FIX-PROMPT.md` embeds every finding with a validation
gate. Every inventory row is marked PASS / BUG-NNN / NOT-COVERED. If the
stop condition was `bug-quota` or `time-box`, state plainly what was not
audited — and for relentless-quota runs, show the escalation trail.

## Anti-patterns

| Pattern | Why it's wrong | Instead |
|---------|----------------|---------|
| Screenshotting pages without interacting | Most bugs live behind clicks, not on first paint | Exercise every inventory element; diff snapshots |
| Marking a button PASS because the click "worked" | A click that changes nothing is the bug | Verify the outcome against expected behavior |
| Auditing desktop only | Layout bugs cluster at tablet/mobile widths | Three viewports per page, no exceptions |
| Reporting a bug seen once | Flaky repros burn the reader's trust | Reproduce twice or label INTERMITTENT |
| Padding the count with duplicates | Ten symptoms of one root cause is one bug | De-duplicate with an affected-pages list |
| Guessing credentials or probing auth | Out of scope and potentially hostile | Ask the user; report gates as not-covered |
| Trusting subagent PASS reports | Subagents summarize; evidence is the truth | Lead reads every cited screenshot personally |
| Filing "no dark mode" style absences as bugs | Absence of a feature isn't a defect on a black-box audit | Note as observation, not a finding, unless the site advertises it |
| Downgrading a flagged issue to an "observation" | The Flag Rule: flagged = finding; severity orders, never dismisses | Log it with ID, evidence, and fix prompt — mark it LOW if it's LOW |
| Parking UX problems outside the bug list | UX violations are defects users hit every day | Run the heuristics pass; every violation is a finding |
| Writing up a bug the moment it's spotted | An uncharacterized bug wastes the fixer's time | Pursue the kill: boundary probe, root symptom, blast radius first |
| Stopping a relentless-quota run at "sweep complete" | The user said N no matter what | Climb the depth escalation ladder and log each rung |
| Per-bug prompts only, no master prompt | The user needs one artifact to hand an agent | Always emit MASTER-FIX-PROMPT.md with gates |

## Worked examples

**Example 1 — relentless quota.**
User: *"Hunt https://shop.example.com — keep working until you find 15
bugs, no matter what."*
Run: stop condition `bug-quota 15` (relentless). Standard sweep of 12 pages
× 3 viewports yields 9 findings. Do not stop. Climb the ladder:
interaction-state pass finds a submit button with no loading state that
allows double-purchase (HIGH, #10) and a missing focus ring on all nav
links (MEDIUM, #11). Edge-input pass finds the quantity field accepting
`-1` (HIGH, #12) and a 500 on a 300-char coupon code (MEDIUM, #13). UX deep
pass flags a checkout modal with no Escape/close path (HIGH, #14) and error
messages that name no recovery action (MEDIUM, #15). Quota hit at rung 4 —
stop, record rungs 1–4 in the escalation trail, write all 15 up with full
Phase-4 pursuit, per-finding prompts, and the master prompt.

**Example 2 — flag discipline in action.**
During the mobile pass you notice footer links rendering at 11px with
3.9:1 contrast. Old habit says "cosmetic, mention in observations." The
Flag Rule says: it's flagged, so it's `BUG-007 — Footer links illegible on
mobile (contrast + size)` `LOW`, with the screenshot, a boundary matrix
(`desktop:PASS tablet:PASS mobile:FAIL`), repro steps, a fix prompt, and a
slot at the bottom of the master prompt's work orders. It also counts
toward any quota.

**Example 3 — the kill, end to end.**
Flag: "Add to cart does nothing on the product page." Pursuit: reproduce
twice ✓; boundary probe — fails at all three viewports, fails logged-out,
*works* logged-in; root symptom — `POST /api/cart` returns 401 with
`{"error":"no session"}` while the UI swallows the error silently; blast
radius — the wishlist button on the same page and the "buy now" button on
2 of 3 sibling product pages share the symptom. Result: one finding,
`CRITICAL`, "also affects" list of 3, a root-symptom line the fixer can act
on in minutes, and acceptance criteria that include "unauthenticated
add-to-cart either works or surfaces a visible sign-in prompt — silent
failure is a fail."

**Example 4 — master prompt handoff.**
User: *"Audit https://app.example.com and give me one prompt I can paste
into Claude Code to fix everything."*
Run full-coverage, then in Phase 5 read `create-meta-prompts` and
`transform-validation-prompt` (installed), and compose
`MASTER-FIX-PROMPT.md`: XML-structured, findings embedded verbatim in
CRITICAL→LOW work orders, a per-fix live-repro validation gate, and a final
all-findings regression gate. Deliver both files; suggest wrapping the
master prompt in a `/goal` via `northstar` if the user wants it to run
unattended.

## When NOT to use

- You have the codebase and want fixes applied — use `full-ui-experience-audit`
- Single page or single screenshot review — use `ui-experience-audit` or `visual-inspection`
- API-only testing with no UI — use `functional-validation` / curl
- Performance profiling, SEO audits, or security pentesting — out of scope

## Related skills

- `agent-browser` — alternative driver; read it for command syntax and auth vault
- `visual-inspection` — the per-screenshot checklist invoked in Phase 3
- `ui-experience-audit` — single-screen depth + heuristics protocol used by the UX pass
- `full-ui-experience-audit` — white-box sibling that also remediates
- `create-meta-prompts` — pipeline structure for MASTER-FIX-PROMPT.md
- `transform-validation-prompt` — validation-gate injection for all fix prompts
- `optimize-prompt` / `deepen-prompt-plan` — final hardening of the master prompt
- `northstar` / `goal-condition-architect` — wrap the master prompt as a `/goal` for unattended remediation

## Reference files

- `references/playwright-engine.md` — default-engine setup (`scripts/setup.sh`),
  six battle-tested script templates (crawl/inventory, SPA time-to-content,
  three-viewport pass, interaction outcomes, console/network capture,
  soft-404 curl check), and the agent-browser↔Playwright translation table.
  **Read before Phase 1 when running the Playwright engine.**
- `references/report-template.md` — the exact REPORT.md and fix-prompt
  format. **Read before writing the report.**
- `references/parallel-team.md` — subagent prompts, session isolation, and
  the merge protocol. Read only when parallel mode is chosen.

## Security

- Never bypass, brute-force, or probe authentication; use only user-supplied credentials
- Never submit real personal data, complete real purchases, or trigger destructive account actions
- Redact any personal data that appears in screenshots before the report
- Never fabricate evidence — no screenshot, no bug
