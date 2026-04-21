---
name: playwright-skill
description: "General-purpose browser automation with Playwright. Write and execute custom Playwright scripts for testing login flows, forms, responsive design, broken links, and any browser interaction. Use when automating browser tasks, testing UI flows, or capturing screenshots."
license: MIT
metadata:
  version: "1.0.0"
  tags: "playwright, browser-automation, testing, e2e, screenshots"
  author: "antigravity-awesome-skills"
---

# Playwright Browser Automation

General-purpose browser automation skill. Writes and executes custom Playwright code for any automation task.

## When to Use

- Testing UI flows (login, forms, navigation)
- Capturing screenshots across viewports
- Checking for broken links or console errors
- Automating repetitive browser interactions
- Visual regression testing

## Critical Workflow

Follow these steps in order:

1. **Auto-detect dev servers** for localhost testing:

   ```bash
   # Check which ports have active servers
   lsof -i :3000 -i :3001 -i :3002 -i :8080 2>/dev/null | grep LISTEN
   ```

   If multiple: ask user which to test. If none: ask for URL.

2. **Write scripts to `/tmp`** — never to the project or skill directory
   - File names: `/tmp/playwright-test-*.js`

3. **Use visible browser by default** — `headless: false` unless user requests headless

4. **Parameterize URLs** — define URL as a constant at the top of every script

## Common Patterns

### Basic Page Test

```javascript
// /tmp/playwright-test-page.js
const { chromium } = require('playwright')

const TARGET_URL = 'http://localhost:3000'

;(async () => {
  const browser = await chromium.launch({ headless: false })
  const page = await browser.newPage()

  await page.goto(TARGET_URL)
  console.log('Title:', await page.title())
  await page.screenshot({ path: '/tmp/screenshot.png', fullPage: true })
  console.log('Screenshot saved to /tmp/screenshot.png')

  await browser.close()
})()
```

### Responsive Design Test

```javascript
const { chromium } = require('playwright')
const TARGET_URL = 'http://localhost:3000'

;(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 100 })
  const page = await browser.newPage()

  await page.setViewportSize({ width: 1920, height: 1080 })
  await page.goto(TARGET_URL)
  await page.screenshot({ path: '/tmp/desktop.png', fullPage: true })

  await page.setViewportSize({ width: 375, height: 667 })
  await page.screenshot({ path: '/tmp/mobile.png', fullPage: true })

  await browser.close()
})()
```

### Login Flow Test

```javascript
const { chromium } = require('playwright')
const TARGET_URL = 'http://localhost:3000'

;(async () => {
  const browser = await chromium.launch({ headless: false })
  const page = await browser.newPage()

  await page.goto(`${TARGET_URL}/login`)
  await page.fill('input[name="email"]', 'test@example.com')
  await page.fill('input[name="password"]', 'password123')
  await page.click('button[type="submit"]')

  await page.waitForURL('**/dashboard')
  console.log('Login successful')

  await browser.close()
})()
```

### Form Submission Test

```javascript
const { chromium } = require('playwright')
const TARGET_URL = 'http://localhost:3000'

;(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 50 })
  const page = await browser.newPage()

  await page.goto(`${TARGET_URL}/contact`)
  await page.fill('input[name="name"]', 'Test User')
  await page.fill('input[name="email"]', 'test@example.com')
  await page.fill('textarea[name="message"]', 'Test message from Playwright')
  await page.click('button[type="submit"]')

  await page.waitForSelector('.success-message', { timeout: 5000 })
  console.log('Form submitted successfully')

  await browser.close()
})()
```

### Broken Link Checker

```javascript
const { chromium } = require('playwright')
const TARGET_URL = 'http://localhost:3000'

;(async () => {
  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage()

  await page.goto(TARGET_URL)
  const links = await page.locator('a[href^="http"]').all()
  const broken = []

  for (const link of links) {
    const href = await link.getAttribute('href')
    try {
      const response = await page.request.head(href)
      if (!response.ok()) broken.push({ href, status: response.status() })
    } catch {
      broken.push({ href, status: 'network error' })
    }
  }

  console.log(`Checked ${links.length} links. Broken: ${broken.length}`)
  if (broken.length) console.table(broken)

  await browser.close()
})()
```

## Execution

```bash
# Install Playwright if not already installed
npm install playwright

# Run script
node /tmp/playwright-test-page.js
```

## Key Selectors

```javascript
// By role (preferred)
page.getByRole('button', { name: 'Submit' })
page.getByLabel('Email')

// By text
page.getByText('Welcome back')

// By CSS
page.locator('input[name="email"]')
page.locator('.success-message')

// By test ID (most stable)
page.getByTestId('submit-button')
```

## Assertions

```javascript
import { expect } from '@playwright/test'

await expect(page).toHaveTitle(/Dashboard/)
await expect(page.getByRole('heading')).toContainText('Welcome')
await expect(page.getByRole('button')).toBeVisible()
await expect(page.getByRole('button')).toBeEnabled()
```

## Limitations

- Use only when task matches browser automation scope.
- Playwright requires Chromium/Firefox/WebKit binaries to be installed.
- Do not run against production without explicit user confirmation.
