# Visual-Explainer Patterns — Reusable Front-End Reference

Distilled from the `visual-explainer` skill (v0.5.1, nicobailon). Patterns for building an
**interactive proposal webpage** + **slide deck**. All output is single-file HTML, vanilla JS,
no framework, no build step. CSS theming via custom properties (`--bg`, `--surface`, `--accent`, etc.;
every accent gets a `-dim` variant). Source: `templates/*.html`, `references/{slide,css}-patterns.md`, `libraries.md`.

---

## 1. Deck / Slide Engine

### Scroll-snap structure
`.deck` is a y-mandatory scroll-snap container; each `.slide` is exactly `100dvh`. One `<section>` per slide.

```html
<body><div class="deck">
  <section class="slide slide--title">...</section>
  <section class="slide slide--content">...</section>
</div></body>
```
```css
.deck { height:100dvh; overflow-y:auto; scroll-snap-type:y mandatory; scroll-behavior:smooth; -webkit-overflow-scrolling:touch; }
.slide { height:100dvh; scroll-snap-align:start; overflow:hidden; position:relative;
  display:flex; flex-direction:column; justify-content:center;
  padding:clamp(40px,6vh,80px) clamp(40px,8vw,120px); isolation:isolate; /* contain z-index */ }
body { overflow:hidden; }  /* page itself never scrolls; only .deck does */
```

### `.reveal` staggered child animation (driven by IntersectionObserver adding `.visible`)
```css
.slide { opacity:0; transform:translateY(40px) scale(.98);
  transition:opacity .6s cubic-bezier(.16,1,.3,1), transform .6s cubic-bezier(.16,1,.3,1); }
.slide.visible { opacity:1; transform:none; }
.slide .reveal { opacity:0; transform:translateY(20px);
  transition:opacity .5s cubic-bezier(.16,1,.3,1), transform .5s cubic-bezier(.16,1,.3,1); }
.slide.visible .reveal { opacity:1; transform:none; }
.slide.visible .reveal:nth-child(1){transition-delay:.1s} /* …:nth-child(2){.2s} … up to (6){.6s} */
@media (prefers-reduced-motion:reduce){ .slide,.slide .reveal{opacity:1!important;transform:none!important;transition:none!important} }
```

### Nav model (keyboard / wheel / touch / dots / progress / counter)
The `SlideEngine` builds chrome dynamically, binds events, and observes slides. **Key gotcha — event
delegation prevents inner scroll/zoom from hijacking slide nav**: keydown bails out if focus is inside
interactive content via `e.target.closest(...)`.
```js
function SlideEngine(){ this.deck=document.querySelector('.deck');
  this.slides=[].slice.call(document.querySelectorAll('.slide'));
  this.current=0; this.total=this.slides.length;
  this.buildChrome(); this.bindEvents(); this.observe(); this.update(); }

SlideEngine.prototype.bindEvents=function(){ var self=this;
  document.addEventListener('keydown',function(e){
    // THE delegation guard: skip nav when inside zoomable/scrollable/editable regions
    if(e.target.closest('.mermaid-wrap,.table-scroll,.code-scroll,input,textarea,[contenteditable]'))return;
    if(['ArrowDown','ArrowRight',' ','PageDown'].indexOf(e.key)>-1){e.preventDefault();self.next();}
    else if(['ArrowUp','ArrowLeft','PageUp'].indexOf(e.key)>-1){e.preventDefault();self.prev();}
    else if(e.key==='Home'){e.preventDefault();self.goTo(0);}
    else if(e.key==='End'){e.preventDefault();self.goTo(self.total-1);}
    self.fadeHints(); });
  var tY; this.deck.addEventListener('touchstart',function(e){tY=e.touches[0].clientY;},{passive:true});
  this.deck.addEventListener('touchend',function(e){var dy=tY-e.changedTouches[0].clientY;
    if(Math.abs(dy)>50){dy>0?self.next():self.prev();}}); };

SlideEngine.prototype.observe=function(){ var self=this;
  var obs=new IntersectionObserver(function(entries){entries.forEach(function(en){
    if(en.isIntersecting){en.target.classList.add('visible');
      self.current=self.slides.indexOf(en.target); self.update();}});},{threshold:.5});
  this.slides.forEach(function(s){obs.observe(s);}); };

SlideEngine.prototype.goTo=function(i){this.slides[Math.max(0,Math.min(i,this.total-1))].scrollIntoView({behavior:'smooth'});};
SlideEngine.prototype.next=function(){if(this.current<this.total-1)this.goTo(this.current+1);};
SlideEngine.prototype.prev=function(){if(this.current>0)this.goTo(this.current-1);};
SlideEngine.prototype.update=function(){
  this.bar.style.width=((this.current+1)/this.total*100)+'%';
  var c=this.current; this.dots.forEach(function(d,i){d.classList.toggle('active',i===c);});
  this.counter.textContent=(this.current+1)+' / '+this.total; };
```
`buildChrome()` appends 4 fixed elements (all `z-index:100`, `position:fixed`): `.deck-progress` (3px bar,
`width` = % through deck), `.deck-dots` (one `<button>` per slide, `onclick→goTo(i)`, `.active` = scale 1.5 + accent),
`.deck-counter` (`N / total`, tabular-nums), `.deck-hints` (auto-`.faded` after 4s via `setTimeout`).
Dots/counter use `backdrop-filter:blur(4px)` + `color-mix(...,var(--bg) 60%,transparent)` or `text-shadow` so they stay legible on any slide bg.

**Wheel/keyboard nav is via scroll-snap itself** (native), not a wheel listener — `scrollIntoView` does the moving. Wheel is only intercepted *inside* `.mermaid-wrap` for ctrl/cmd-zoom (see §4).

### `autoFit()` — required safety net, call **before** `new SlideEngine()`
```js
function autoFit(){
  document.querySelectorAll('.mermaid svg').forEach(function(svg){ // force Mermaid SVG to fill, not intrinsic size
    svg.removeAttribute('height'); svg.style.width='100%'; svg.style.maxWidth='100%';
    svg.style.height='auto'; svg.parentElement.style.width='100%'; });
  document.querySelectorAll('.slide__kpi-val').forEach(function(el){ // shrink overflowing hero numbers
    if(el.scrollWidth>el.clientWidth){var s=el.clientWidth/el.scrollWidth;
      el.style.transform='scale('+s+')'; el.style.transformOrigin='left top';}});
  document.querySelectorAll('.slide--quote blockquote').forEach(function(el){ // proportional shrink for long quotes
    var len=el.textContent.trim().length; if(len>100){var sc=Math.max(.5,100/len);
      var fs=parseFloat(getComputedStyle(el).fontSize); el.style.fontSize=Math.max(16,Math.round(fs*sc))+'px';}}); }
// init: mermaid.run().then(()=>{ autoFit(); new SlideEngine(); });  // or DOMContentLoaded if no Mermaid
```

### Slide typography & types
2–3× larger than a page. Display `clamp(48px,10vw,120px)`; heading `clamp(28px,5vw,48px)`; body `clamp(16px,2.2vw,24px)`; label = mono/uppercase. 10 slide types: **Title, Divider, Content, Split, Diagram, Dashboard, Table, Code, Quote, Full-Bleed**. Each is one viewport, never scrolls — overflow → split into more slides. Content density caps (per slide): Content ≤6 bullets; Table ≤8 rows; Code ≤10 lines; Dashboard ≤6 KPIs (hero values ≤6 chars); Quote ≤~150 chars.

- **Content** (asymmetric): `.slide__inner{display:grid;grid-template-columns:3fr 2fr;gap:clamp(24px,4vw,60px);align-items:center}` (swap to `2fr 3fr` for right-heavy). Bullets are `list-style:none` with an absolutely-positioned `::before` dot.
- **Split** (before/after, edge-to-edge): `.slide--split{padding:0}` + `.slide__panels{display:grid;grid-template-columns:3fr 2fr;height:100%}`; panels get distinct `--surface`/`--surface2` bg.
- **Divider**: giant decorative `.slide__number{font-size:clamp(100px,22vw,260px);font-weight:200;opacity:.06;position:absolute;top:50%;left:50%;transform:translate(-50%,-55%)}`.
- **CSS Pipeline slide** (use instead of Mermaid for simple linear A→B→C flows — Mermaid renders tiny in a viewport): `.pipeline{display:flex;flex:1;align-items:stretch}` with each `.pipeline__step{flex:1}` so steps fill width, arrows are inline SVG between them. Mobile: `flex-direction:column` + rotate arrow 90deg.

Compositional variety rule: consecutive slides must alternate centered / left-heavy / right-heavy / split / full-bleed. Vary per-slide background glow position (`:nth-child(odd/even)` radial-gradient).

---

## 2. Data-Table Pattern

Full anatomy: **KPI cards → legend → scroll wrapper → sticky-header table (staggered rows, status badges, footer) → collapsible detail.** Use a real `<table>` (accessibility + copy-paste).

```html
<div class="kpi-row animate" style="--i:2">
  <div class="kpi-card"><div class="kpi-card__value">14</div><div class="kpi-card__label">Items</div></div>
  <div class="kpi-card"><div class="kpi-card__value kpi-card__value--green">13</div><div class="kpi-card__label">Match</div></div>
  <div class="kpi-card"><div class="kpi-card__value" style="color:var(--accent)">93%</div><div class="kpi-card__label">Coverage</div></div>
</div>
<div class="table-wrap"><div class="table-scroll">            <!-- horizontal-scroll wrapper -->
  <table class="data-table">
    <thead><tr><th class="wide">Request</th><th class="wide">Plan</th><th>Status</th></tr></thead>
    <tbody>
      <tr style="--i:4"><td class="wide">Scope to <code>template</code></td>
          <td class="wide">Plan matches.<small>secondary detail</small></td>
          <td><span class="status status--match">Match</span></td></tr>
      <tr style="--i:5"><td class="wide">…</td><td>…</td><td><span class="status status--gap">Gap</span></td></tr>
    </tbody>
    <tfoot><tr><td>14 items</td><td></td><td>13 match · 1 gap</td></tr></tfoot>
  </table>
</div></div>
<details class="collapsible"><summary>Gap Analysis Detail</summary>
  <div class="collapsible__body"><strong>Gap:</strong> explanation…</div></details>
```
```css
.kpi-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:14px;margin-bottom:20px}
.kpi-card{background:var(--surface-elevated);border:1px solid var(--border);border-radius:10px;padding:18px;box-shadow:0 2px 8px rgba(0,0,0,.05)}
.kpi-card__value{font-size:32px;font-weight:400;line-height:1.1;font-variant-numeric:tabular-nums}
.kpi-card__label{font-family:var(--font-mono);font-size:10px;text-transform:uppercase;letter-spacing:1.2px;color:var(--text-dim);margin-top:6px}

.table-wrap{background:var(--surface);border:1px solid var(--border);border-radius:12px;overflow:hidden}
.table-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}   /* the horizontal-scroll wrapper */
.data-table{width:100%;border-collapse:collapse;font-size:13px;line-height:1.55}
.data-table thead{position:sticky;top:0;z-index:2}                /* sticky header */
.data-table th{background:var(--surface2);font-family:var(--font-mono);font-size:10px;font-weight:600;
  text-transform:uppercase;letter-spacing:1.2px;color:var(--text-dim);text-align:left;
  padding:14px 16px;border-bottom:2px solid var(--border-bright);white-space:nowrap}
.data-table td{padding:14px 16px;border-bottom:1px solid var(--border);vertical-align:top}
.data-table tbody tr:last-child td{border-bottom:none}
.data-table .wide{min-width:220px;max-width:440px}               /* let text columns wrap, don't truncate */
.data-table tbody tr:nth-child(even){background:var(--accent-dim)}/* alternating rows */
.data-table tbody tr{transition:background .15s ease;            /* row hover + staggered entrance via --i */
  animation:fadeUp .35s ease-out both; animation-delay:calc(var(--i,0)*.04s)}
.data-table tbody tr:hover{background:var(--border)}
.data-table small{display:block;color:var(--text-dim);font-size:11px;margin-top:3px}
.data-table td.num,.data-table th.num{text-align:right;font-variant-numeric:tabular-nums;font-family:var(--font-mono)}
.data-table tfoot td{background:var(--surface2);font-weight:600;border-top:2px solid var(--border-bright);border-bottom:none}

/* Status badges — styled spans, NEVER emoji. Dot via ::before. */
.status{display:inline-flex;align-items:center;gap:5px;font-family:var(--font-mono);font-size:10px;
  font-weight:600;padding:3px 10px;border-radius:6px;white-space:nowrap}
.status::before{content:'';width:6px;height:6px;border-radius:50%;background:currentColor}
.status--match{background:var(--green-dim);color:var(--green)}
.status--gap{background:var(--red-dim);color:var(--red)}
.status--partial{background:var(--orange-dim);color:var(--orange)}
```
Sticky **first** column (very wide tables): add `position:sticky;left:0;z-index:1;background:var(--surface)` to `th:first-child,td:first-child`. `@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}`.

---

## 3. Section / Timeline Rendering (adapt for week-by-week timeline)

`architecture.html` lays out **stacked section cards joined by vertical flow arrows**, plus a **horizontal stepped pipeline with arrow separators and a parallel branch** — both directly reusable as a phase/week timeline.

```html
<div class="diagram">
  <div class="section section--accent" style="--i:0">                <!-- a phase/week card -->
    <div class="section-label"><span class="dot"></span> Week 1</div>
    <div class="inner-grid">                                         <!-- 2-col detail grid -->
      <div class="inner-card"><div class="title">Discovery</div><div class="desc">Audit + <code>scope</code></div></div>
      <div class="inner-card"><div class="title">Setup</div><div class="desc">Env + access</div></div>
    </div>
  </div>
  <div class="flow-arrow" style="--i:1">                             <!-- connector between phases -->
    <svg viewBox="0 0 20 20"><path d="M10 4 L10 16 M6 12 L10 16 L14 12"/></svg> incoming
  </div>
  <!-- horizontal stepped pipeline (tiers) -->
  <div class="pipeline">
    <div class="pipeline-step pipeline-step--teal"><div class="step-num">STEP 0</div><div class="step-name">Pre-filter</div><div class="step-detail">dedup<br>check</div></div>
    <div class="pipeline-arrow">→</div>
    <div class="pipeline-parallel">                                  <!-- parallel branch = two stacked steps -->
      <div class="pipeline-step pipeline-step--orange">…</div>
      <div class="pipeline-step pipeline-step--teal">…</div>
    </div>
  </div>
</div>
```
```css
.diagram{display:grid;grid-template-columns:1fr;gap:24px;max-width:1100px;margin:0 auto}
.section{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px 24px}
.section--hero{background:var(--surface-elevated);box-shadow:0 4px 20px rgba(0,0,0,.06);padding:28px 32px} /* depth tier */
.section--recessed{background:var(--surface2);box-shadow:inset 0 1px 3px rgba(0,0,0,.04)}
.section-label{font-family:var(--font-mono);font-size:11px;font-weight:600;text-transform:uppercase;
  letter-spacing:1.5px;margin-bottom:16px;display:flex;align-items:center;gap:8px}
.section-label .dot{width:8px;height:8px;border-radius:50%}
/* per-color variant: .section--accent .section-label{color:var(--accent)} + .dot{background:var(--accent)} */
.inner-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.inner-card{background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:12px 16px}

.flow-arrow{display:flex;justify-content:center;align-items:center;gap:8px;color:var(--text-dim);
  font-family:var(--font-mono);font-size:12px;padding:4px 0}
.flow-arrow svg{width:20px;height:20px;fill:none;stroke:var(--border-bright);stroke-width:2;stroke-linecap:round;stroke-linejoin:round}

.pipeline{display:flex;gap:0;align-items:stretch;overflow-x:auto;padding-bottom:4px}
.pipeline-step{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:10px 12px;min-width:120px;flex-shrink:0;text-align:center}
.pipeline-arrow{display:flex;align-items:center;padding:0 2px;color:var(--border-bright);flex-shrink:0}
.pipeline-parallel{display:flex;flex-direction:column;gap:4px}
@media(max-width:768px){.inner-grid{grid-template-columns:1fr}.pipeline{flex-wrap:wrap;gap:6px}.pipeline-arrow{display:none}}
```
Staggered entrance: `.section,.flow-arrow{animation:fadeUp .4s ease-out both;animation-delay:calc(var(--i,0)*.06s)}` — using `--i` (not `:nth-child`) survives interleaved arrow/card siblings. Color progression past→future = muted→vivid is just choosing `--i` order + accent variant per card. (Dedicated **Timeline** approach also documented: central CSS line via pseudo-element + alternating cards — but the stacked-section + pipeline pattern above is what the template actually ships.)

---

## 4. Interactivity Model (vanilla JS, no framework)

Three mechanisms only: **(a) native `<details>/<summary>`** (zero JS, accessible), **(b) `addEventListener` + `classList.toggle`** for show/hide and active states, **(c) inline `onclick` handlers** wired to small global functions. No state library, no reactivity.

### (a) Collapsible — `<details>` (use for "click a week to expand")
```css
details.collapsible{border:1px solid var(--border);border-radius:10px;overflow:hidden}
details.collapsible summary{padding:14px 20px;background:var(--surface);font-family:var(--font-mono);
  font-size:12px;font-weight:600;cursor:pointer;list-style:none;display:flex;align-items:center;gap:8px;color:var(--text)}
details.collapsible summary::-webkit-details-marker{display:none}
details.collapsible summary::before{content:'▸';font-size:11px;color:var(--text-dim);transition:transform .15s ease}
details.collapsible[open] summary::before{transform:rotate(90deg)}   /* chevron rotates open */
details.collapsible .collapsible__body{padding:16px 20px;border-top:1px solid var(--border);font-size:13px;line-height:1.6}
```
A week-by-week timeline where each week expands = one `<details class="collapsible">` per week, `<summary>` = week header, body = detail. No JS at all.

### (b) Toggle pattern — interactive cost table (headline ↔ recommended)
The skill's own theme-toggle is the canonical example of swap-via-class + `setAttribute`:
```js
function toggleTheme(){ var c=document.documentElement.getAttribute('data-theme');
  document.documentElement.setAttribute('data-theme', c==='light'?'dark':'light'); }
```
Apply the same shape to a cost table: render both columns, toggle a class on the table root to show one set, or swap a `data-mode` attribute and let CSS reveal the matching cells:
```html
<div class="cost" data-mode="recommended">
  <button onclick="setMode(this,'headline')">Headline</button>
  <button onclick="setMode(this,'recommended')">Recommended</button>
  <table class="data-table"> … <td class="m-headline">$50k</td><td class="m-recommended">$32k</td> … </table>
</div>
<script>
function setMode(btn,m){ var root=btn.closest('.cost'); root.setAttribute('data-mode',m); }
</script>
<style>
.cost[data-mode="headline"]    .m-recommended{display:none}
.cost[data-mode="recommended"] .m-headline   {display:none}
.cost button{cursor:pointer}  /* add .active styling off the data-mode if desired */
</style>
```

### (c) Inline onclick + closest() — the zoom-controls model (interactive click-to-act)
Buttons carry `onclick`, the handler resolves its container with `.closest()`, mutates an inline style / dataset, and a separate listener distinguishes click-vs-drag. This is the exact recipe to make "click a week/row to expand or open detail":
```js
function zoomDiagram(b,f){var w=b.closest('.mermaid-wrap');var t=w.querySelector('.mermaid');
  var c=parseFloat(t.dataset.zoom||1);var n=Math.min(Math.max(c*f,.5),5);t.dataset.zoom=n;t.style.zoom=n;}
// wheel-zoom ONLY with ctrl/cmd, and click-vs-drag detection so a plain click can open detail:
document.querySelectorAll('.mermaid-wrap').forEach(function(w){
  w.addEventListener('wheel',function(e){ if(!e.ctrlKey&&!e.metaKey)return; e.preventDefault(); /* zoom */ },{passive:false});
  var sX,sY,sTime,didPan;
  w.addEventListener('mousedown',function(e){ if(e.target.closest('.zoom-controls'))return;
    sX=e.clientX;sY=e.clientY;sTime=Date.now();didPan=false; w.classList.add('is-panning');});
  window.addEventListener('mousemove',function(e){ if(!w.classList.contains('is-panning'))return;
    if(Math.abs(e.clientX-sX)>5||Math.abs(e.clientY-sY)>5)didPan=true; /* pan */ });
  window.addEventListener('mouseup',function(){ if(!w.classList.contains('is-panning'))return;
    w.classList.remove('is-panning');
    if(!didPan&&Date.now()-sTime<300) openDetail(w); /* plain click (no drag, <300ms) → act */ });
});
```
Takeaway for the proposal page: a click handler that opens an expanded view should guard with a `didPan`/drag check so dragging-to-select doesn't fire it, and `e.target.closest('.controls')` so clicks on inner buttons don't double-fire.

---

## 5. Self-Containment + Streaming

Single `.html` file. No external assets except CDN `<link>`/`<script>`. Scripts execute after streaming completes, so wrap init in `DOMContentLoaded` (or `mermaid.run().then(...)`).

```html
<!-- Fonts: Google Fonts, always display=swap, with system fallback in the family stack -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">

<!-- Mermaid (diagrams) — ES module from jsDelivr, theme:'base' for full themeVariables control -->
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  const isDark = matchMedia('(prefers-color-scheme: dark)').matches;        // read once; Mermaid can't re-theme
  mermaid.initialize({ startOnLoad:true, theme:'base', look:'classic',
    themeVariables:{ primaryColor:isDark?'#1d2b52':'#fef3e0', lineColor:isDark?'#9a9484':'#7a7468',
      fontSize:'18px', fontFamily:'var(--font-body)' /* …forbidden: #8b5cf6/#7c3aed/#a78bfa */ }});
</script>

<!-- Chart.js (real charts) — UMD bundle -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>

<!-- anime.js (orchestrated multi-element entrances; CSS animation-delay covers most cases) -->
<script src="https://cdn.jsdelivr.net/npm/animejs@3.2.2/lib/anime.min.js"></script>
```
- **Mermaid for**: flowcharts, sequence, ER, state, mindmap, class, C4 (use `graph TD`+`subgraph`, NOT native `C4Context`). Max ~10–12 nodes; prefer `flowchart TD` over `LR`. Multi-line labels use `<br/>` not `\n`; quote labels with special chars. Force text color via CSS `.mermaid .nodeLabel{color:var(--text)!important}` (themeVariables hardcode breaks the opposite scheme).
- **Chart.js for**: bar/line/pie/radar in dashboards. Read `isDark` + `--font-body` at runtime to theme axes/legend. Skip it for simple bars — use a pure-CSS/SVG sparkline or `<div>` progress bar instead.
- **Self-contained images**: `surf gemini "…" --generate-image` → `base64` → embed as `data:image/png;base64,…`. Optional; degrade to CSS gradient if `surf` absent.
- **Output/open**: write to `~/.agent/diagrams/<name>.html`; `open` (macOS) / `xdg-open` (Linux). Optional `share.sh` → Vercel claimable deploy.

CSS theming contract: define `--bg,--surface,--surface-elevated,--border,--border-bright,--text,--text-dim,--accent,--accent-dim` + 3–5 semantic accents (each with `-dim`) in `:root`, mirror in `@media (prefers-color-scheme)`. Depth tiers: `--hero` (elevated shadow + accent tint) → default → `--recessed` (inset shadow).

---

## 6. Anti-Patterns / Gotchas the templates explicitly warn about

**Layout / CSS**
- **Every grid/flex child needs `min-width:0`** or long text/inline `<code>` blows out the container. Add `body{overflow-wrap:break-word}`.
- **Never `display:flex` on `<li>`** to position a `::before` marker — it creates an anonymous flex item with un-overridable `min-width:auto` that overflows. Use `position:relative` + absolute `::before` instead.
- `<ol>/<ul>` inside a bordered card needs `list-style-position:inside` **or** `padding-left:2em` (default 20px lets markers overlap the border).
- **Code blocks require `white-space:pre-wrap;word-break:break-word`** + a `max-height`/`overflow:auto`, else code runs into an unreadable wall or an endless scroll. Don't dump full source files — show structure + key snippets + collapsible for the rest.
- Directory trees need `white-space:pre` (never `normal`/flex/grid) or the `├──│` connectors lose alignment.

**Mermaid**
- **Never define `.node` as a page-level CSS class** — Mermaid uses `.node` internally; page styles leak in and break layout. Use `.ve-card`. Only style Mermaid's node via `.mermaid .node …`.
- Never use bare `<pre class="mermaid">` (no zoom → unreadable); always wrap in `.mermaid-wrap` with zoom controls. Center with `display:flex;justify-content:center`. Don't set `color:` in `classDef` (hardcodes a scheme-breaking color).
- `stateDiagram-v2` labels can't take `()`, `:`, `<br/>`, entities → silent parse failure; use `flowchart TD` with quoted labels instead. Sequence-diagram messages must be plain text (no `{}[]<>&`).

**Slides**
- A slide must fit 100dvh and never scroll internally — overflow paginates to another slide.
- A small Mermaid diagram alone on a slide = failed slide; use a CSS Pipeline or pair it with annotation in a split.
- KPI hero values >6 chars break at 64px — put long strings in the label, rely on `autoFit()` as backstop.

**"AI-slop" — explicitly forbidden** (any 2+ = regenerate)
- Fonts: **Inter, Roboto, Arial, Helvetica, bare system-ui** as `--font-body`.
- Accents: `#8b5cf6 #7c3aed #a78bfa` (indigo/violet), `#d946ef` fuchsia, the cyan-magenta-pink neon combo, "Tailwind defaults".
- Effects: **gradient text on headings** (`background-clip:text`), **animated glowing box-shadows** / pulsing-breathing on static content, multiple neon radial glows, continuous post-load animation (except progress indicators).
- Chrome clichés: **three-dot (red/yellow/green) window dots** on code blocks; **emoji icons leading section headers** (use mono label + colored dot, or inline SVG); every card identical (no hero/recessed hierarchy); perfectly centered + uniform padding everywhere.
- Prefer **constrained aesthetics** (Blueprint / Editorial / Paper-ink / Terminal-mono) — they have requirements that resist defaulting to slop. Always respect `prefers-reduced-motion`.
