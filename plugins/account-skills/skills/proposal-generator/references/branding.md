# WithAgents branding — Operator Console

Canonical visual system for every WithAgents surface. Mirrors `DESIGN.md §6`
of the blog-series repo (which itself mirrors `wa/project/design-systems/design-systems.jsx` → `console.vars`).
The deprecated "Midnight Observatory" indigo palette (`#6366f1` / `#0f172a`) must **never** appear in a proposal.

The machine-readable source of truth is `assets/tokens.css`. This file is the human/agent explainer.

## Aesthetic
**Operator Console / hyper-black editorial** — a utilitarian dashboard, not a poster. Dense rows,
traffic-light status pills, layered translucency over a warm-black page with two faint corner glows.
Cockpit, not brochure. Depth comes from 1px borders + translucent fills, **never** drop shadows.

## Color
| Token | Value | Role |
|---|---|---|
| `--bg-page` | `#08080a` | warm-black page background |
| glow top-right | `radial-gradient(ellipse 1000px 600px at 90% -10%, rgba(255,61,82,0.08), transparent 60%)` | crimson ambient |
| glow bottom-left | `radial-gradient(ellipse 900px 500px at -10% 120%, rgba(122,61,255,0.08), transparent 60%)` | violet ambient |
| `--accent` | `#FF3D52` | crimson — eyebrows, CTAs, focus rings, status dots, key numbers |
| fill ladder | `rgba(255,255,255, .02 / .04 / .05 / .08)` | quiet → default → hover → active surfaces |
| rule lines | `rgba(255,255,255, .06 / .08 / .12)` | hairline → card border → emphasis |
| text | `#f4f3ee` (100%) · `rgba(244,243,238,.72)` body · `.4` tertiary · `.3` footnote | warm off-white, never pure white |
| `--pass` | `#34D08C` | green — included, complete, positive |
| `--fail` | `#FF3D52` | red (== accent) |
| `--warn` | `#FFB84D` | amber — attention, cost callouts |
| `--info` | `#5EE6F2` | cyan — metrics, neutral data |
| violet | `#B84DFF` | secondary decorative accent |

Status traffic-light is consistent everywhere: a "PASS" / "included" is always green, a cost/attention flag is always amber.
Six approved accent presets exist (Crimson, Magenta `#EC4899`, Violet `#B84DFF`, Emerald `#34D08C`, Cyan `#5EE6F2`, Amber `#FFB84D`) — pick one per surface, never combine. Proposals default to **Crimson**.

## Typography
- **Inter** — UI, body, headlines. Weights 400/500/600/700/800.
  - hero 88–120px / letter-spacing -3px / weight 800
  - section 48–72px / -1.5px / 700
  - h2 32–40px / -0.8px / 700
  - h3 22px / 600
  - body 16–17px / line-height 1.6 / 400
- **Fraunces** *italic* — surgical display only: one or two words inside an Inter headline. Never body.
- **JetBrains Mono** — labels, eyebrows, status pills, code, file paths, numeric callouts. ALL CAPS, 10.5–11.5px, letter-spacing 1.4–2.4px, weight 600–700.

Fonts load from Google Fonts (`fonts.googleapis.com`, CSP-allowed): `Inter:wght@400;500;600;700;800`, `Fraunces:ital,opsz,wght@1,9..144,400;1,9..144,500`, `JetBrains+Mono:wght@400;500;600;700`.

## Form
- Radii: 6px sm (chips), 8px md (inputs/ghost CTAs), 12px lg (cards, default), 16px xl (large cards), 999px pill.
- 1px borders everywhere. **No decorative shadows.** Only two real shadow uses: status-pill dot glow (`box-shadow: 0 0 10px <accent>`) and card-hover lift (`translateY(-2px)` + brighter border).
- Easing: `cubic-bezier(0.2, 0.6, 0.2, 1)` (house easing). Durations: 120ms hover, 160ms focus, 280ms reveal.
- Hovers raise 2px and brighten the border; color does **not** change on hover.
- No photography or illustration. Visual interest = animated SVG/canvas, code excerpts, bar charts, fail/pass tables, the WAMark logo.

## Logo / wordmark
No raster asset is bundled. Render the wordmark as text: `with` in `rgba(244,243,238,.72)` + `agents` in `--accent` crimson, Inter 700, plus a small square "WAMark" chip (crimson border, mono initial). The proposal header uses this lockup; the client gets a circular initial chip in the same frame.

## Dark-only
WithAgents renders dark-only by design. `prefers-color-scheme: light` is a no-op — do not author a light stylesheet or a theme toggle. The print stylesheet (`assets/print.css`) is the one exception: PDFs invert to ink-on-paper for printing economy while keeping crimson as the single accent.
