# Web Frontend Validation Strategy

## When This Applies
Project has `package.json` with React/Vue/Svelte/Next.js/Nuxt, or a
`playwright.config.*` file, or HTML/CSS/JS entry points.

## Build Verification

```bash
# Check for build script
cat package.json | jq '.scripts.build'

# Run build
npm run build 2>&1 | tail -20
# or
yarn build 2>&1 | tail -20
```

Zero errors required. Warnings are acceptable but should be reviewed.

## Dev Server

```bash
# Start dev server
npm run dev &
DEV_PID=$!
sleep 5  # Wait for server startup

# Verify it's running
curl -sf http://localhost:3000 > /dev/null && echo "Server up"
```

Note the port — it varies by framework (3000, 5173, 8080, etc.).
Check `package.json` scripts or framework config.

## Browser Automation

Two tools are available for web validation. Prefer `agent-browser` when
the skill is installed — it provides AI-guided browser interaction with
built-in evidence collection. Fall back to raw Playwright when `agent-browser`
is not available or when you need fine-grained scripted control.

| Tool | When to Use |
|------|-------------|
| **agent-browser** skill | Interactive validation, exploratory testing, complex form flows |
| **Playwright** (direct) | Scripted validation, CI pipelines, precise screenshot sequences |

### Using agent-browser

If the `agent-browser` skill is available, invoke it for browser-based
validation. It handles navigation, form filling, clicking, screenshotting,
and evidence collection with AI-guided interaction patterns. Screenshots
and page text are captured automatically.

### Using Playwright Directly

Playwright is the fallback validation tool for web frontends. If a
`playwright.config.*` exists, use the project's configuration. Otherwise,
set up a minimal Playwright script.

### Installation (if needed)
```bash
npm install -D @playwright/test
npx playwright install chromium
```

### Evidence Collection Script Pattern

```javascript
// validate.mjs — run with: node validate.mjs
import { chromium } from 'playwright';

const browser = await chromium.launch();
const page = await browser.newPage();
const evidenceDir = './evidence';

// Navigate
await page.goto('http://localhost:3000');
await page.waitForLoadState('networkidle');
await page.screenshot({ path: `${evidenceDir}/01-home.png`, fullPage: true });

// Interact
await page.click('button:has-text("Login")');
await page.waitForLoadState('networkidle');
await page.screenshot({ path: `${evidenceDir}/02-login-form.png` });

// Fill form
await page.fill('input[name="email"]', 'test@example.com');
await page.fill('input[name="password"]', 'password');
await page.click('button[type="submit"]');
await page.waitForLoadState('networkidle');
await page.screenshot({ path: `${evidenceDir}/03-after-login.png` });

// Verify content
const heading = await page.textContent('h1');
console.log(`Heading: ${heading}`);
const isVisible = await page.isVisible('[data-testid="dashboard"]');
console.log(`Dashboard visible: ${isVisible}`);

await browser.close();
```

### Key Playwright Patterns

| Action | Code | Notes |
|--------|------|-------|
| Navigate | `page.goto(url)` | Always `waitForLoadState` after |
| Click | `page.click('selector')` | Use text selectors for buttons |
| Fill input | `page.fill('selector', 'value')` | Clears first, then types |
| Screenshot | `page.screenshot({ path, fullPage })` | `fullPage: true` for scrollable pages |
| Wait for element | `page.waitForSelector('selector')` | Use before interacting |
| Check visibility | `page.isVisible('selector')` | Returns boolean |
| Get text | `page.textContent('selector')` | Returns string |
| Console errors | `page.on('console', msg => ...)` | Capture before navigation |

### Selector Priority
1. `data-testid` attributes (most stable)
2. Role selectors: `page.getByRole('button', { name: 'Submit' })`
3. Text selectors: `button:has-text("Submit")`
4. CSS selectors: `.class-name`, `#id` (least stable)

## Evidence Standards

### Screenshots
- Number sequentially: `01-home.png`, `02-login.png`
- Use `fullPage: true` for pages with scroll
- **Always read screenshots** — file existence means nothing
- Capture console errors alongside screenshots

### Console Monitoring
```javascript
const errors = [];
page.on('console', msg => {
  if (msg.type() === 'error') errors.push(msg.text());
});
// ... perform actions ...
console.log(`Console errors: ${errors.length}`);
errors.forEach(e => console.log(`  - ${e}`));
```

### Network Monitoring
```javascript
const failedRequests = [];
page.on('response', response => {
  if (response.status() >= 400) {
    failedRequests.push(`${response.status()} ${response.url()}`);
  }
});
```

## Responsive Testing

Test at multiple viewport sizes:
```javascript
// Mobile
await page.setViewportSize({ width: 375, height: 812 });
await page.screenshot({ path: 'mobile.png' });

// Tablet
await page.setViewportSize({ width: 768, height: 1024 });
await page.screenshot({ path: 'tablet.png' });

// Desktop
await page.setViewportSize({ width: 1440, height: 900 });
await page.screenshot({ path: 'desktop.png' });
```

## Backend Integration

If the frontend connects to a backend API:
```bash
# Verify backend is healthy
curl -sf http://localhost:<API_PORT>/health
```

Start the backend before testing the frontend. A frontend with no backend
shows error states or empty screens — not the features you're validating.

## Web-Specific Gotchas

| Gotcha | Impact | Solution |
|--------|--------|----------|
| Dev server not ready | Page loads fail | Wait for server + health check |
| SPA routing | Direct URL navigation may 404 | Navigate from root, click through |
| Auth tokens | Protected pages redirect to login | Log in first, or inject cookies |
| Lazy loading | Screenshots show placeholders | Scroll to trigger loads, wait |
| Animations | Screenshots capture mid-transition | Wait for animation completion |
| CORS | API calls fail from browser | Backend must allow frontend origin |
