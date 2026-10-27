# Visual Experience Audit — Depth Protocol

The Phase 2 visual depth playbook. The universal 8-item visual checklist
in `ui-experience-audit` catches the obvious — overlapping text, contrast,
spacing, viewport overflow. This file catches what a senior designer
would catch on the second pass and a one-page checklist would never
surface: state coverage, design-system drift, regression, motion quality,
and the rendering details that make an app *feel* finished.

Read this on Phase 2 of the very first cycle. Skim it on later cycles
unless a specific dimension came back open.

## Why this matters (the framing)

A screenshot is one visual moment. The visual *experience* is many
moments — every state of every element on every screen, the consistency
of those states across screens, the continuity from screen to screen,
and the quality of the transitions between. Auditing visuals well means
systematically reaching all of those moments and looking at them with
intent. Most auditing tools produce a single capture per screen and call
it done; this protocol pushes the audit to where the bugs actually live.

## The visual experience taxonomy (what to audit)

### Per interactive element — 5+ visual states

For every button, link, field, toggle, card-as-tap-target, and gesture
area in the inventory, audit ALL of these states:

| State | Trigger | What you're checking |
|-------|---------|----------------------|
| **default** | rest | the resting visual signal — does it look interactive? |
| **hover** | mouse over (web) | does *something* visually change? subtle is fine; invisible is not |
| **focus** | tab key (always) | is the focus ring visible? at sufficient contrast against the background it lands on? |
| **active** | mid-press | does the press register visually? (depressed, color shift, scale, etc.) |
| **disabled** | unavailable | distinguishable from default but not invisible (≥3:1 still applies) |
| **loading** | async in flight | does the user know to wait? spinner, skeleton, progress, disabled+pulse, or just frozen? |
| **success** | post-success | confirmation visible; doesn't disappear before user can read it |
| **error** | post-error | error visible *near* the element that caused it, not in a banner the user has to scan to find |

A button with `:hover` invisible from `:default`, no `:focus` ring, and
identical `:active` is technically working code with a broken visual
experience. This is the most common HIGH finding the depth audit catches.

### Per screen — 6 state variants

For every screen in the inventory, audit each variant the screen can
exhibit:

| Variant | Typical cause | Visual checklist |
|---------|---------------|------------------|
| **empty** | no data yet (new user, cleared filters) | meaningful empty state? CTA toward first action? not just blank? |
| **loading** | data in flight | skeleton matches eventual content shape? spinner placement makes sense? layout doesn't jank when data arrives? |
| **populated** | typical data | normal flow; the screen the designer probably designed |
| **overflow** | huge data, long names, wide tables | does anything truncate without ellipsis? horizontal-scroll trap? text wrap into ugly L-shapes? |
| **error** | API/network failure | error visible? recovery action provided? user knows what happened? |
| **first-launch** | new user, never seen this | onboarding clarity? CTA to populate? doesn't dump user into empty state with no guidance? |

The audit "passes" each screen ONLY when each applicable variant has
been visited and captured. Skipping variants because "the happy path
looks fine" is the #1 source of post-ship visual bugs.

### Per mode — light / dark / motion / contrast

| Mode | When to audit |
|------|---------------|
| **light** | always (the baseline) |
| **dark** | if the app supports dark mode (per `run-config.md` coverage axes) |
| **reduced-motion** | if the app has motion (most apps do — at least loading spinners) |
| **high-contrast** | if the platform/OS supports it AND the app is positioned for accessibility-conscious users |

`prefers-reduced-motion` is often un-implemented; capture by setting it
and confirming animations are minimized or removed. Capture is real
evidence because the "minimized" version is itself a designed state, not
a bug.

### Contrast — measuring against the right yardstick

Two algorithms are in active use; pick the right one for the context:

**WCAG 2.x ratio (4.5:1 / 3:1)** — the legal-compliance baseline. Use it
for everything that has a regulatory requirement. Known weaknesses:
treats contrast as static regardless of font weight/size, badly mismodels
dark-mode pairs (4.5:1 on dark backgrounds is often functionally
unreadable; the algorithm overstates contrast at low luminances).

**APCA (Lightness Contrast / `Lc`)** — the WCAG 3 candidate, perceptually
calibrated. Use it as a *second* check, especially for dark mode, and
specifically for non-text contrast where WCAG 2.x is known to fail. APCA
thresholds (reference font Helvetica/Arial):

| Lc threshold | Use case |
|--------------|----------|
| **Lc 90** | preferred for fluent body text (≥14px @400 weight or ≥18px @300) |
| **Lc 75** | minimum for body text (≥18px @400, ≥16px @500, ≥14px @700) |
| **Lc 60** | minimum for large non-body text (≥24px @400) |
| **Lc 45** | minimum for large bold (≥36px bold) |
| **Lc 30** | minimum for icon strokes / borders / non-text UI elements |
| **Lc 15** | invisibility threshold — below this, content is unreadable for many users |

When a pair passes WCAG 2.x AA but fails APCA Lc 75, that's almost
always a dark-mode pair; flag it as MEDIUM with a note "perceptually
substandard despite WCAG compliance — consider APCA alongside."

**Tools that compute both** (use whichever is on hand):
- `axe DevTools` browser extension — flags WCAG failures with cited rules
- `Lighthouse` accessibility audit — bundled with Chrome DevTools
- `WAVE` (WebAIM) — visual annotation of issues on the page
- Atmos contrast checker — paste foreground/background, get both values
- `@weable/a11y-color-utils` — programmatic API for both algorithms
- `pa11y` CLI — automatable in CI

### Cross-screen — design-system integrity

After per-screen audits, do a dedicated comparison pass:

| Dimension | Question | How to detect |
|-----------|----------|---------------|
| Color tokens | Are "primary", "background", "text" the same hex everywhere? | grep / diff a sample of computed colors across screen captures |
| Type scale | Same H1 size on every screen? Same body line-height? | Pull computed font-size + line-height per screen via DevTools or via grep on CSS |
| Component shape | Same corner radius on cards? Same shadow on modals? | Visual scan of cropped components side-by-side |
| Spacing rhythm | Same gap between hero and content on every screen? | Measure baseline grid adherence via overlay |
| Iconography | Same stroke weight, same set, same scale? | Pull all icons used onto a single contact-sheet canvas |
| Nav continuity | Active-state treatment identical across nav items? Breadcrumb visible where expected? | Side-by-side of two nav-active screens |
| Modal/sheet style | Same animation, same backdrop, same dismiss affordance across modals? | Open multiple modals; capture each |

Token / scale / shape drift across screens is what makes apps feel
"assembled" rather than "designed." It's also a predictor of fragility:
an app with 4 near-blue primaries usually has 4 sets of dependent
components downstream of each.

### Cross-cycle — regression diff

After Phase 4 fixes in cycle N, before Phase 2 in cycle N+1: compare
each screen's current capture against its baseline (or against the
prior-cycle capture). Anything visually different that wasn't part of
the fix's intended scope is a finding.

`agent-browser diff screenshot --baseline cycle-01/.../screen.png` is
the canonical command. iOS uses `compare` from ImageMagick or a similar
pixel-diff. Differences less than ~1% of pixels can be noise (font
rendering jitter, sub-pixel anti-aliasing); larger differences need
explanation.

## Multi-state capture protocol

For each element in the cycle's inventory:

1. Navigate to the screen
2. Snapshot to get the element's reference (`agent-browser snapshot -i`)
3. Capture default state
4. Hover (web): `agent-browser hover @eN` then screenshot
5. Focus: `agent-browser focus @eN` then screenshot — watch for invisible focus ring
6. Active: there is no perfect way to capture mid-press programmatically;
   inspect the `:active` CSS rules statically and confirm something
   non-trivial is set
7. Disabled: if the element has a disabled state in the codebase, force
   it (toggle a feature flag, mock a precondition, or capture a
   different instance of the same element type that is in disabled
   state on another screen)
8. Loading / success / error: trigger via state-forcing recipes (next
   section)

Save each capture with descriptive names:
`<screen>-<element-id>-<state>.png` — e.g.,
`dashboard-save-btn-default.png`, `dashboard-save-btn-hover.png`,
`dashboard-save-btn-focus.png`. The lead reads each in turn.

In degraded mode (no `agent-browser`), substitute static-analysis: read
the CSS for `:hover`, `:focus`, `:active`, `:disabled`, and
`@media (prefers-reduced-motion)` rules. Missing rules ARE findings.
Specifically:

- No `:focus` rule on a tappable element → HIGH finding
- `:hover` rule that only changes `cursor:` (no visible feedback) → MEDIUM
- `:active` rule absent or identical to default → LOW (but compounds)
- No `prefers-reduced-motion` query and the app has animations → MEDIUM

## State-forcing recipes (the practical part)

You can't audit empty / loading / error states without a way to make
them appear. These recipes are what the audit actually does to reach
each state.

### Web (with `agent-browser`)

#### Empty state

```bash
# Option A: clear local storage to reset to first-run
agent-browser eval "localStorage.clear(); sessionStorage.clear()"
agent-browser reload

# Option B: use a fresh browser profile / session
agent-browser --session-name fresh-empty open <url>

# Option C: stub the API to return empty arrays (override fetch in-page)
agent-browser eval --stdin <<'EVALEOF'
window.fetch = (orig => async (url, opts) => {
  if (url.includes('/api/sessions')) return new Response('{"items":[]}', {headers:{'content-type':'application/json'}});
  return orig(url, opts);
})(window.fetch);
EVALEOF
agent-browser reload   # let the page re-fetch
```

Option C is preferred when the empty state is hard to reach via real
data manipulation — it doesn't touch the backend.

#### Loading state

```bash
# DevTools Slow 3G via agent-browser's network-throttle
agent-browser network slow-3g
# Capture during the load — race the screenshot
agent-browser open <url> & sleep 0.3; agent-browser screenshot loading.png; wait

# OR: inject a delay into fetch
agent-browser eval --stdin <<'EVALEOF'
window.fetch = (orig => async (...args) => {
  await new Promise(r => setTimeout(r, 5000));
  return orig(...args);
})(window.fetch);
EVALEOF
agent-browser reload
sleep 1   # capture mid-loading
agent-browser screenshot loading.png
```

#### Error state

```bash
# Force fetches to return 500
agent-browser eval --stdin <<'EVALEOF'
window.fetch = async () => new Response('{"error":"forced"}', {status: 500, headers:{'content-type':'application/json'}});
EVALEOF
agent-browser reload
agent-browser screenshot error.png
```

#### Overflow state

Two paths: seed real data, or substitute long strings.

```bash
# String substitution via DOM manipulation
agent-browser eval --stdin <<'EVALEOF'
document.querySelectorAll('.item-title').forEach(el => {
  el.textContent = 'a'.repeat(200);
});
EVALEOF
agent-browser screenshot overflow.png

# Or: drive the form fields with very long input
agent-browser fill @e1 "$(python3 -c 'print("a"*500)')"
```

#### First-launch state

```bash
# Fresh profile + cleared storage
agent-browser close
agent-browser --session-name first-launch open <url>
agent-browser eval "localStorage.clear(); sessionStorage.clear(); document.cookie.split(';').forEach(c => document.cookie = c.split('=')[0].trim()+'=;expires=Thu, 01 Jan 1970 00:00:00 GMT')"
agent-browser reload
agent-browser screenshot first-launch.png
```

### iOS (with `xcrun simctl`)

#### Empty state

```bash
# Fresh install wipes app sandbox
xcrun simctl uninstall "$UDID" "$BUNDLE_ID"
xcrun simctl install "$UDID" "$APP_PATH"
xcrun simctl launch "$UDID" "$BUNDLE_ID"
sleep 3
xcrun simctl io "$UDID" screenshot empty.png
```

#### Loading state

```bash
# Use simctl's network conditioner if your sim supports it (iOS 17+)
# Or rely on a backend with deliberate delay
# Or screenshot quickly after launch before data load completes
sleep 0.5   # not 3 — capture mid-load
xcrun simctl io "$UDID" screenshot loading.png
```

#### Error state

```bash
# Stop the backend before launch — app shows error UI
pkill -f <backend-process>
xcrun simctl launch "$UDID" "$BUNDLE_ID"
sleep 3
xcrun simctl io "$UDID" screenshot error.png
# Restart backend before next test
```

#### Overflow state

```bash
# Seed UserDefaults / Core Data / SwiftData with long strings
# Or use a dev-mode build flag your app honors

# Quick approach: launch with overflow seed args (if app supports them)
xcrun simctl launch "$UDID" "$BUNDLE_ID" --seed-overflow
```

#### First-launch state

```bash
# Heavyweight: erase the entire simulator
xcrun simctl shutdown "$UDID"
xcrun simctl erase "$UDID"
xcrun simctl boot "$UDID"
sleep 5
# Then re-do all of Phase 0 setup (status bar, install, etc.)

# Lightweight: just uninstall + install (data wipe but device prefs preserved)
xcrun simctl uninstall "$UDID" "$BUNDLE_ID"
xcrun simctl install "$UDID" "$APP_PATH"
```

## Static-analysis visual playbook (degraded mode)

When `agent-browser` isn't available, visuals are still auditable via
source. The grep patterns that catch the most common visual bugs:

| Bug class | grep pattern | Why |
|-----------|--------------|-----|
| Hardcoded near-white text on white | `color:\s*#[bcd][bcd0-9a-f]{4,5}` (light grays) | < AA contrast almost always |
| Hardcoded color literals (drift risk) | `(#[0-9a-fA-F]{3,8}\|rgb\(\|rgba\()` outside a tokens file | each one is a maintenance liability and a drift opportunity |
| Inline styles | `style=` in JSX/HTML | inline styles bypass the design system; usually a smell |
| `cursor: pointer` without `onClick` / `:focus` | `cursor:\s*pointer` then check the same selector for handlers | false-affordance generator |
| Missing `:focus` rules on interactive elements | grep selector lists for `button`, `a`, `[role="button"]`, etc., then check `:focus` rule presence | invisible focus = WCAG fail |
| `:hover` rule that doesn't change a visual property | `:hover` blocks containing only `cursor:` | "hovering" without feedback |
| No `@media (prefers-reduced-motion)` | absence of that query in stylesheet | accessibility miss |
| Hardcoded font sizes below 14px | `font-size:\s*(?:1[0-3]px\|0\.[5-8]\d*rem)` | usually a typography mistake |
| Mixed icon libraries | imports from multiple icon packages in same file | iconography inconsistency |
| Unscoped global `!important` | `!important` outside a reset/print stylesheet | a fix that breaks something else |
| Z-index hardcodes | `z-index:\s*(9999\|999\|9)` | layering free-for-all |
| Px values not on 4pt/8pt grid | `(margin\|padding\|gap):\s*(?:[1357]\|[1-9]\d?)px` (odd values) | grid drift |

Run these greps once per cycle's Phase 1 — they often precede the
per-screen captures and pre-flag findings to verify in Phase 2.

## Visual evidence quality standards

A capture is "good" evidence when:

- [ ] **Whole-viewport** or clearly cropped. Cropped captures need a
      caption stating what was excluded
- [ ] **Native resolution** — no downscaling, no DPR confusion
- [ ] **Status bar normalized** (iOS: 9:41, full battery; web: no irrelevant
      browser chrome unless that's part of the audit)
- [ ] **Correct mode** — light/dark explicitly, not "whichever happened
      to load"
- [ ] **State labeled in filename** — `default`/`hover`/`focus`/`error`/etc.
- [ ] **Pre-action AND post-action** for any interaction (matched pair)
- [ ] **Animations and transitions disabled or settled** — pre-capture
      injection of `* { animation: none !important; transition: none !important }`
      OR a wait long enough for everything to land. The visual-regression
      community standardizes on the disable-CSS approach because it
      produces reproducible captures across runs (the same `wait 3000`
      can capture mid-animation depending on machine load).
- [ ] **Fonts and images settled** — wait `networkidle` AND verify
      `document.fonts.ready` before capture. A capture mid-FOUT looks
      different every run.
- [ ] **No accidental personal data** — redact emails, usernames, real
      faces, real card numbers before sharing or storing
- [ ] **Filename follows the convention** —
      `<cycle>/<screen>-<element-or-state>-<extra>.png`

A capture failing one or more of these is still useful but should be
flagged in the cycle report so the next cycle re-captures cleanly.

### A visual capture is an assertion, not a screenshot

Borrowed from the visual-regression-testing community (Chromatic,
Percy, Storybook): every capture this skill produces is, conceptually,
*a deterministic assertion that this component in this state looks
like this baseline*. The implications:

- **Same input → same output** is the goal. Disable animations.
  Stub network responses (or wait deterministically). Use a fixed
  viewport. Use a fixed font-loading state.
- **Diff against a baseline, not "did the screen look right today"**.
  Cycle 1 establishes baselines; cycles 2+ diff against them.
- **Interaction-driven captures need a stabilization step**. Click
  → wait `networkidle` → capture. Skipping the wait turns the
  assertion into a coin-flip.

If the target project already uses Storybook, prefer driving captures
through stories with play functions — they're already isolated,
already deterministic, and already enumerate state combinations:

```javascript
// Example play function — drives the component to focus state
export const FocusedState = {
  args: { ...DefaultArgs },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.tab();
  }
};
```

When Storybook exists in the target project, Phase 2 should capture
from stories rather than the live app — faster, more deterministic,
and the captures double as VRT baselines for the team's CI.

## Refactoring UI tactical heuristics

A short opinionated checklist drawn from Wathan & Schoger's
*Refactoring UI* — these catch what the contrast-and-touch-target
checklist misses by category, the "looks fine but feels off"
findings:

| Tactic | What to look for | Example bug |
|--------|------------------|-------------|
| **Whitespace as structure** | Generous padding around primary content; tight padding around secondary | Cards crammed against parent edges; CTAs glued to text |
| **Limit the palette** | Count distinct colors used in computed styles; ≤ 1 primary + 1 accent + 5-7 grays + semantic (success/warn/error) | "We have 4 different blues" bug |
| **Build hierarchy with size + color, not just font-weight** | Headings should be larger AND a different color (or muted body) — both signals working together | All-bold paragraphs that don't actually create hierarchy |
| **Visual weight ≠ font-weight** | Use color (muted text) to demote; use size to promote | Page where everything is `font-weight: 500` |
| **Shadows as a system, tied to elevation** | All raised cards share one shadow recipe; modals deeper; nothing custom-per-component | Shadows that vary by spec rather than by elevation |
| **Type scale, not type values** | Headings/body/caption land on a 5-7 size scale used everywhere | One H2 is 24px, another is 22px (eyeballed) |
| **Consistent border radius** | One radius for cards, one for buttons, one for chips — don't mix | Three near-identical radii (4/6/8) |
| **Colored grays** | Brand-tinted neutrals (cool grays for blue brand, warm for orange) feel intentional | Pure `#888` next to a saturated brand color |
| **Right-size the icons** | Icons match adjacent text weight; not too large in dense lists, not too small in CTAs | Tiny icons in big buttons; oversize in tight rows |
| **Dim non-essential text instead of removing it** | Demote with color (slate-500), keep affordance | Removed labels that should still be visible |

## Iconography consistency

Iconography drift is a top signal of "this app was assembled from many
sources." Audit per cycle:

| Check | Pattern |
|-------|---------|
| One icon set per app | Mix of `lucide` + `heroicons` + custom SVG = HIGH finding |
| Consistent stroke width within a visual layer | Outline icons should all be 1.5px or all 2px |
| One filled-vs-outlined choice per hierarchy level | Mixing filled and outlined at same level is jarring |
| Icon sizes from a token scale (`icon-sm: 16` etc.) | Random `width: 18`, `width: 22` is a smell |
| Icons aligned to text baseline | A 20px icon next to 16px text needs a slight `translateY` |
| Icon meaning matches platform convention | Gear=settings, trash=delete — don't reinvent |

Per cycle: paste every distinct icon used into a single contact-sheet
row. Style/weight/size mismatches are visible in seconds.

## Performance / responsiveness as part of experience

The audit doesn't profile performance, but five rules from Apple HIG /
Material Design responsiveness specs are part of "experience" and
worth flagging:

| Rule | Source | How to check |
|------|--------|--------------|
| Tap feedback within 100ms | Apple HIG | Pre-render the active state in CSS, not via JS |
| Input latency < 100ms | Material Design | DevTools Performance; "feels laggy" is a signal |
| Per-frame work < 16ms (60fps) | Browser default | DevTools Performance; jank during scroll |
| Reserve space for async content (no CLS) | Core Web Vitals | DevTools > Web Vitals; visual jump on load |
| Skeleton/shimmer over spinner for >1s waits | Apple HIG / Material | Search source for `<Spinner>` used during slow loads |
| Virtualize lists > 50 items | Material / general | Search for `<FlatList>` / `react-window` / `react-virtual` |
| Lazy-load below-the-fold images | Performance | Search for `loading="lazy"` |

LOW-MEDIUM severity unless the experience is broken (then HIGH). Phase 3
often surfaces these incidentally — a screen that takes 4 seconds to
render and shows a generic spinner the whole time is a recordable
finding even if technically "everything works."

## Accessible-widget patterns (ARIA APG reference)

Custom interactive widgets (anything that isn't a native `<button>`,
`<input>`, etc.) have expected keyboard and ARIA-state behaviors. The
W3C ARIA Authoring Practices Guide (APG) is the canonical source. When
the audit finds a custom widget, check it against the corresponding
APG pattern:

| Widget | APG pattern | Required keyboard | Required ARIA |
|--------|-------------|-------------------|---------------|
| Dialog/Modal | dialog | Esc closes, focus trap, return focus on close | `role="dialog"`, `aria-modal="true"`, `aria-labelledby` |
| Tabs | tabs | ←→ navigates, Home/End to ends, Enter/Space activates | `role="tablist"`, `role="tab"`, `aria-selected`, `aria-controls` |
| Combobox / autocomplete | combobox | ↓ opens, ↑↓ navigates, Esc clears/closes | `role="combobox"`, `aria-expanded`, `aria-controls`, `aria-activedescendant` |
| Menu / dropdown | menu, menubar | ↓↑ navigates, Esc closes, Enter activates | `role="menu"`, `role="menuitem"`, `aria-haspopup`, `aria-expanded` |
| Slider | slider | ←→ adjusts, PgUp/PgDn larger steps, Home/End ends | `role="slider"`, `aria-valuemin`, `aria-valuemax`, `aria-valuenow` |
| Tree | tree | ↓↑ navigates, →← expands/collapses, Enter activates | `role="tree"`, `role="treeitem"`, `aria-expanded`, `aria-level` |
| Listbox | listbox | ↓↑ navigates, Enter activates, Type-ahead | `role="listbox"`, `role="option"`, `aria-selected` |
| Disclosure / Accordion | disclosure | Enter/Space toggles | `aria-expanded`, `aria-controls` |

Findings: a custom widget that *looks* like a tab strip but lacks
`role="tablist"` + `aria-selected` keyboard navigation is a HIGH
finding (assistive-tech-invisible). The APG also documents test cases
per pattern (`https://www.w3.org/WAI/ARIA/apg/patterns/`) — link to
the relevant pattern in findings.json's `evidence_paths` so the
fixer agent has the spec.

## Cross-screen consistency audit (one pass per cycle)

After per-screen audits complete, run this dedicated pass. It's fast
(20-30 minutes for a 10-screen app) and catches design-system drift
that no per-screen audit can.

1. **Color sampling**: pull 3-5 representative screen captures into a
   tool (or use `agent-browser eval` to extract `getComputedStyle`).
   Sample primary, background, text, accent, success, error, warn —
   list the exact hexes in use. If "primary" varies by ≥1 hex on the
   sRGB scale across screens, that's a finding.
2. **Type scale spot-check**: pick H1, H2, body, caption from 3 screens.
   Confirm font-family, font-size, line-height match. Drift here is
   often a code smell — a forked component or copy-paste-and-tweak.
3. **Component shape diff**: capture a card from screens A, B, C. Side
   by side — same border-radius, same shadow, same border weight?
4. **Nav active-state diff**: capture nav at a different "active" item
   on each screen. Active treatment identical?
5. **Modal style diff**: open three different modals. Compare backdrop
   color, dismiss-affordance position, animation duration.
6. **Iconography contact sheet**: paste every icon used into a single
   row. Look for stroke-weight or style mismatches (one filled icon in
   a row of outlined ones is jarring).

Findings from this pass are CRITICAL or HIGH — design-system drift is
expensive to fix later.

## Motion / transition quality (briefly)

Motion is hard to audit from screenshots. Three practical approaches:

1. **`agent-browser record start <file>`** captures session video; play
   back and assess. Crude but real.
2. **iOS `xcrun simctl io recordVideo`** same idea.
3. **Static analysis**: grep for `transition:`, `animation:`,
   `@keyframes` declarations. Note duration and easing. Durations
   ≥ 500ms or eases like `linear` deserve a second look. Missing
   `prefers-reduced-motion` overrides are findings.

Don't over-invest here — motion findings are usually MEDIUM/LOW unless
something obviously janks.

## Anti-patterns specific to visual auditing

| Anti-pattern | Why it's wrong | Do this instead |
|--------------|----------------|-----------------|
| Auditing one capture per screen and calling visuals "passed" | Misses 80% of state-dependent visual bugs | Multi-state capture loop per element + per-screen variant capture |
| Skipping focus state because "it's accessibility, not visual" | Invisible focus is a visual signaling failure first, accessibility failure second | Capture focus on every interactive element |
| Treating dark mode as a checkbox ("we have dark mode") | Dark mode bugs are common — text on glass, white on light blue | Capture every screen + every state in dark mode if it's `yes` in coverage |
| Using `agent-browser eval` to "fake" hover for the screenshot | Eval doesn't fire :hover pseudo-class via JS | Use `agent-browser hover @eN` (the real subcommand) |
| Capturing happy-path only because "we know it works" | Empty/error/overflow states are where designers and engineers disagree most often | Force each variant via the recipes above |
| Comparing cycle-N captures against cycle-N captures | No regression detection | Always diff against baseline OR cycle-1 capture |
| Auditing visuals only on desktop | Mobile / iOS Safari rendering catches a different category of bugs | Capture mobile via `-p ios --device` profile |
| Hardcoding the audit to one design language | Skills shouldn't impose Material vs HIG — audit *consistency*, not adherence to any one system | Inspect the app's own design intent and audit drift from it |

## When this protocol is overkill

For a 1-screen utility app or a single feature audit, multi-state
capture × all variants × dark mode is too much. Scale down: pick the
most-trafficked element, capture 3 states (default, focus, disabled).
Pick the riskiest variant (usually error or overflow). Skip cross-screen
since there's only one screen. The full protocol earns its complexity
on apps with 5+ screens.

## Complementary public skills (use as reference, not replacement)

The visual-experience audit composes well with these public Claude
skills. Each covers a slice — none does the full loop the parent
skill does, but their checklists / data are valuable inputs:

| Skill | Repo / source | What it brings |
|-------|---------------|----------------|
| **AccessLint** | accesslint/claude-marketplace | 4 a11y micro-skills (contrast-checker, refactor, use-of-color, link-purpose) + a contrast MCP server. If installed, the audit can call `accesslint:contrast-checker` instead of computing contrast itself |
| **Vercel Web Design Guidelines** | vercel-labs/web-interface-guidelines | 100+ rules covering accessibility, performance, UX best practices. Their canonical rule set is a good cross-reference for Phase 2 findings |
| **bencium refactoring-ui-skill** | bencium/bencium-claude-code-design-skill | Visual-hierarchy/spacing/shadow/palette audits — the Refactoring-UI tactics this file lifts from |
| **iOS HIG Design** | rshankras/claude-code-apple-skills | Apple-specific: safe areas, Dynamic Island, Dynamic Type, semantic colors, VoiceOver. Phase 2 on iOS should defer to this skill if installed |
| **UI/UX Pro Max** | nextlevelbuilder/ui-ux-pro-max-skill | 99 UX guidelines, performance rules (100ms tap feedback, 16ms frame budget, virtualize 50+) — the perf rules in this file are drawn from theirs |
| **identify-ux-problems** | (Marie Claire Dean's collection) | Heuristic-evaluation-style audit. Compose with this skill's Phase 2 UX heuristics step |
| **Vercel webapp-testing** | (Anthropic skills) | Playwright-based UI testing — useful for projects that don't have `agent-browser` available, though this skill prefers `agent-browser` |

When any of these is installed in the user's environment, the audit's
Phase 2 should detect them via `tool_search` (or the equivalent) and
delegate the corresponding sub-checks rather than re-running the same
analysis. The orchestration map in SKILL.md should be updated when
this skill notices new complementary skills available.

## Standards & specs the audit conforms to

| Standard | Use |
|----------|-----|
| **WCAG 2.2** | Compliance baseline; cite specific success criteria in findings (e.g., "fails 2.4.7 Focus Visible") |
| **APCA / WCAG 3 candidate** | Perceptual contrast, especially dark mode |
| **POUR** (WCAG meta) | Frame findings as Perceivable / Operable / Understandable / Robust |
| **WAI-ARIA 1.2 / APG** | Custom-widget patterns (role, state, keyboard) |
| **Apple HIG** | iOS-specific (responsiveness, Dynamic Type, safe areas, VoiceOver) |
| **Material Design 3** | Android/web responsiveness specs (input latency, frame budget) |
| **Inclusive Design Principles** (Microsoft / Heydon Pickering) | Multiple input methods, predictability, controlled motion, alternative formats |
| **Refactoring UI** (Wathan/Schoger) | Visual tactics — whitespace, palette, hierarchy, shadows-as-system |
| **Core Web Vitals** | Layout stability (CLS), input latency (INP), load (LCP) |

Cite the relevant standard's specific success criterion in
findings.json's `suggested_fix` field so the fixer agent has a
direct reference, not just "improve contrast."

## Reference tools (link, don't bundle)

The audit doesn't bundle tooling, but lists what to reach for when
deeper checks are needed:

- **Contrast**: axe DevTools, Lighthouse, WAVE, Atmos, `@weable/a11y-color-utils`
- **A11y scan**: axe-core, pa11y, accessibility-checker.org, Deque a11y
- **Visual regression** (when team has Storybook): Chromatic, Percy, Playwright Visual, Applitools
- **Performance**: Chrome DevTools Performance, Lighthouse, WebPageTest
- **Color picker / sampling**: ColorSlurp, Sip, Chrome DevTools color picker
- **Design-system linting** (Figma side): Design Lint plugin, Style Dictionary, Token Studio
