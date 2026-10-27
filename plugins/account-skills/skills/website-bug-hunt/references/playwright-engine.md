# Playwright Engine — setup and battle-tested script templates

Playwright is the **default engine** for this skill. It runs headless in
restricted Linux sandboxes (including ARM64 hosts where `agent-browser`
cannot run — Chrome for Testing ships no Linux ARM64 build), parallelizes
crawls with multiple pages/contexts in one process, and gives you console,
network, and page-error hooks for free on every page.

These templates were proven on a real 148-URL audit (awesome.video,
2026-07-10). Adapt, don't rewrite.

## Setup (once per run)

```bash
bash scripts/setup.sh ./hunt-workspace     # installs playwright + chromium, fixes missing libs
source ./hunt-workspace/engine/env.sh      # REQUIRED before every node invocation
```

`setup.sh` handles the two sandbox traps:

1. **No global npm prefix** — installs playwright locally in
   `hunt-workspace/engine/`.
2. **Missing shared libraries, no root** — `ldd`-checks the chromium
   headless shell, downloads any missing lib as a `.deb` via unprivileged
   `apt-get download`, extracts it, and writes an `env.sh` exporting
   `LD_LIBRARY_PATH`. (Observed in the wild: `libXdamage.so.1` was the only
   missing dep; this fix took chromium from unlaunchable to working.)

Run scripts from the engine dir so `require('playwright')` resolves:

```bash
cd hunt-workspace/engine && node /tmp/hunt-script.js
```

**Verify before proceeding**: `setup.sh` ends with a smoke test
(`SMOKE OK: <title>`). If it prints `SMOKE FAIL`, stop and fix — do not
start the audit on a broken engine.

## Template 1 — Crawl & inventory (Phase 1)

Collects every unique same-origin URL from the landing page, then visits
each with N parallel pages, recording per URL: HTTP status, title, main-text
length + first 120 chars, element counts, horizontal overflow, soft-404
text, and deduped console errors. Writes `crawl-results.json`.

```js
const { chromium } = require('playwright');
const BASE = process.env.HUNT_URL;                 // e.g. https://example.com
(async () => {
  const b = await chromium.launch({ headless: true });
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
  const p0 = await ctx.newPage();
  await p0.goto(BASE, { waitUntil: 'networkidle', timeout: 30000 });
  const hrefs = await p0.evaluate(() => {
    const m = new Map();
    document.querySelectorAll('a[href]').forEach(a => {
      const h = a.getAttribute('href');
      if (h && h.startsWith('/') && !m.has(h)) m.set(h, (a.textContent||'').trim().slice(0,50));
    });
    return [...m.entries()];
  });
  await p0.close();
  const results = [], queue = [...hrefs], CONC = 8;
  async function worker() {
    const p = await ctx.newPage();
    const errs = [];
    p.on('console', m => { if (m.type()==='error') errs.push(m.text().slice(0,150)); });
    while (queue.length) {
      const [href, label] = queue.shift(); errs.length = 0;
      const r = { href, label };
      try {
        const resp = await p.goto(BASE + href, { waitUntil: 'domcontentloaded', timeout: 15000 });
        r.status = resp ? resp.status() : null;
        await p.waitForTimeout(1200);
        Object.assign(r, await p.evaluate(() => {
          const main = document.querySelector('main') || document.body;
          const txt = (main.innerText||'').trim();
          return { title: document.title.slice(0,80), txtLen: txt.length,
            first120: txt.slice(0,120).replace(/\n/g,' | '),
            overflowX: document.documentElement.scrollWidth > window.innerWidth,
            notFound: /404|not found|nothing here/i.test(txt.slice(0,600)) };
        }));
        r.consoleErrs = [...new Set(errs)].slice(0,3);
      } catch (e) { r.error = e.message.slice(0,120); }
      results.push(r);
    }
    await p.close();
  }
  await Promise.all(Array.from({ length: CONC }, worker));
  require('fs').writeFileSync('crawl-results.json', JSON.stringify(results, null, 1));
  console.log('crawled', results.length);
  await b.close();
})();
```

**Trap:** a short post-load wait (1.2s) flags SPA pages as "Loading…" that
are merely slow to hydrate. Never file those as bugs from the crawl alone —
confirm with Template 2.

## Template 2 — Time-to-content confirmation (SPA pages)

Polls main-content text every 500ms and records how long until real content
replaces the loading state. Distinguishes "slow hydration" (finding: LOW)
from "stuck forever" (finding: HIGH).

```js
let loaded = -1, txt = '';
const t0 = Date.now();
await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 20000 });
for (let i = 0; i < 24; i++) {                     // up to 12s
  txt = await p.evaluate(() => ((document.querySelector('main')||document.body).innerText||'').trim());
  if (txt.length > 100 && !/^Loading/i.test(txt)) { loaded = Date.now() - t0; break; }
  await p.waitForTimeout(500);
}
console.log(url, 'time-to-content(ms):', loaded);   // -1 = never loaded → HIGH bug
```

## Template 3 — Three-viewport responsive pass (Phase 3)

Per viewport: horizontal-overflow check, nav-collapse check, sub-32px
touch-target count, screenshot. Use `isMobile`/`hasTouch` for the mobile
context — media queries and touch handlers behave differently.

```js
for (const [name, vp, mob] of [
  ['desktop', { width:1440, height:900 }, false],
  ['tablet',  { width:768,  height:1024 }, false],
  ['mobile',  { width:375,  height:812 }, true],
]) {
  const ctx = await b.newContext({ viewport: vp, isMobile: mob, hasTouch: mob });
  const p = await ctx.newPage();
  for (const href of PAGES) {
    await p.goto(BASE + href, { waitUntil: 'networkidle', timeout: 25000 });
    await p.waitForTimeout(800);
    const d = await p.evaluate(() => ({
      overflowX: document.documentElement.scrollWidth > window.innerWidth,
      hamburger: !!document.querySelector('[aria-label*=menu i], [data-sidebar=trigger], button[class*=trigger]'),
      smallTargets: [...document.querySelectorAll('main a, main button')]
        .filter(el => { const r = el.getBoundingClientRect();
          return r.width > 0 && r.height > 0 && (r.height < 32 || r.width < 32); }).length
    }));
    console.log(name, href, JSON.stringify(d));
    await p.screenshot({ path: `screenshots/${slug(href)}/${name}/initial.png`, fullPage: true });
  }
  // mobile: prove the hamburger actually opens
  if (mob) {
    const trig = p.locator('[data-sidebar=trigger], button[aria-label*=idebar], button[aria-label*=enu]').first();
    if (await trig.count()) { await trig.click(); await p.waitForTimeout(800);
      await p.screenshot({ path: 'screenshots/home/mobile/nav-open.png' }); }
    else console.log('BUG CANDIDATE: no nav trigger found at 375px');
  }
  await ctx.close();
}
```

## Template 4 — Functional interaction pass (Phase 3)

Patterns for the outcome-verification rule (a click that changes nothing is
a finding):

```js
// Keyboard-shortcut search: press "/", confirm focus moved, type, verify results
await p.keyboard.press('/');
const focused = await p.evaluate(() => document.activeElement?.tagName + ':' +
  (document.activeElement?.getAttribute('placeholder') || ''));
await p.keyboard.type('known-term'); await p.waitForTimeout(1500);
// then press Enter and confirm URL/result count changed

// Card/element click: record URL before and after
const before = p.url();
await p.locator('main [class*=card]').first().click();
await p.waitForTimeout(1500);
console.log('navigated:', before, '->', p.url());   // unchanged URL + unchanged DOM = finding

// External-link hygiene on any page
const ext = await p.evaluate(() => [...document.querySelectorAll('a[href^="http"]')]
  .filter(a => !a.href.includes(location.hostname))
  .map(a => ({ h: a.href.slice(0,60), target: a.target, rel: a.rel })).slice(0,10));
// target="_blank" without rel="noopener noreferrer" = MEDIUM finding
```

## Template 5 — Console, network, and page-error capture

Attach BEFORE `goto`, per page:

```js
const consoleErrs = [], failedReqs = [], pageErrs = [];
p.on('console', m => { if (m.type() === 'error') consoleErrs.push(m.text().slice(0,200)); });
p.on('response', r => { if (r.status() >= 400) failedReqs.push(r.status() + ' ' + r.url().slice(0,120)); });
p.on('pageerror', e => pageErrs.push(e.message.slice(0,200)));
```

Aggregate across the crawl and count occurrences — "CSP blocks
`<script src>` on 148/148 pages" is one site-wide HIGH bug, not 148 bugs.
CSP violations, blocked analytics endpoints, and 4xx on first-party APIs
are classic invisible findings: the UI looks fine, the console tells the truth.

## Template 6 — Hard-status truths (curl beats the browser)

SPAs often render a pretty "Not Found" page with HTTP 200 (soft-404 — an
SEO bug). Always verify with a raw request:

```bash
curl -s -o /dev/null -w "%{http_code}\n" "$BASE/this-page-does-not-exist-xyz"
```

## Playwright ↔ agent-browser protocol map

Same discipline, different driver. If a phase instruction is written in
agent-browser syntax, translate:

| agent-browser | Playwright |
|---|---|
| `open <url>` + `wait --load networkidle` | `page.goto(url, { waitUntil: 'networkidle' })` |
| `snapshot -i` → `@eN` refs | `page.locator(...)` / `page.evaluate` DOM harvest |
| `click @eN` | `locator.click()` |
| `fill @eN "text"` | `locator.fill('text')` |
| `screenshot --full x.png` | `page.screenshot({ path, fullPage: true })` |
| `diff snapshot` | capture `main.innerText` / DOM before & after, compare |
| `--session <name>` (parallel isolation) | one `browser.newContext()` per worker |

## Known limits

- Sandbox `bash` calls may have per-call timeouts (~45s). Chunk long crawls:
  run workers with a queue file, or split URL lists across calls.
- No WebKit/Firefox in restricted sandboxes without extra deps — chromium
  headless is the baseline; note the single-engine coverage in the report.
- `isMobile: true` is chromium-emulated touch, not a real device.

Executor credit: `scripts/run.js` and `scripts/helpers.js` adapted from
`playwright-skill` v4.1.0 by lackeyjb (MIT).
