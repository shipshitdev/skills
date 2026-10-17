---
name: playwright-e2e-init
description: "Initializes Playwright end-to-end testing for Next.js/React projects: config, example tests, Bun scripts, CI integration. Use when adding E2E tests to a frontend project."
metadata:
  version: "2.2.5"
  tags: "playwright, e2e, testing"
when_to_use: "playwright.config, e2e folder, browser tests"
---

# Playwright E2E Testing Initialization

Sets up Playwright for end-to-end testing in Next.js and React applications.

## When to Use

- Adding E2E tests to a Next.js project
- Setting up browser automation testing
- Creating user flow tests for critical paths
- Integrating E2E tests with CI/CD pipeline

## What It Does

1. **Installs Playwright** and browsers
2. **Creates configuration** (playwright.config.ts)
3. **Sets up test directory** (e2e/)
4. **Creates example tests** for common flows
5. **Adds Bun scripts** for running tests
6. **Updates CI/CD** to run E2E tests

## Quick Start

Example prompt:

```
Add Playwright E2E tests to this project
```

Or be specific:

```
Set up E2E tests for the authentication flow
```

## Installation

```bash
bun add -D @playwright/test
bunx playwright install chromium
```

## Configuration

### playwright.config.ts

```typescript
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [["html", { open: "never" }], ["list"]],
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
  ],
  webServer: {
    command: "bun run dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
```

## Test Structure

```
e2e/
├── home.spec.ts          # Homepage tests
├── auth.spec.ts          # Authentication flow
├── navigation.spec.ts    # Navigation tests
└── fixtures/
    └── test-data.ts      # Shared test data
```

## Example Tests

Generate project-specific tests for the actual routes in the codebase. Standard Playwright test patterns (navigation, auth flows, form submission, fixtures) are well-documented at https://playwright.dev/docs/writing-tests — focus inline tests on the project's concrete pages and critical user flows rather than generic examples.

## Bun Scripts

Add to package.json:

```json
{
  "scripts": {
    "e2e": "playwright test",
    "e2e:ui": "playwright test --ui",
    "e2e:headed": "playwright test --headed",
    "e2e:debug": "playwright test --debug",
    "e2e:report": "playwright show-report"
  }
}
```

## CI/CD Integration

### GitHub Actions

Add to your CI workflow:

```yaml
- name: Install Playwright Browsers
  run: bunx playwright install --with-deps chromium

- name: Run E2E tests
  run: bun run e2e
  env:
    CI: true

- name: Upload Playwright Report
  uses: actions/upload-artifact@v4
  if: always()
  with:
    name: playwright-report
    path: playwright-report/
    retention-days: 7
```

## Best Practices

- Focus E2E tests on critical user flows: auth, core features, payment/checkout, error handling.
- Use `data-testid` attributes for selectors — do not rely on CSS classes or text content.
- Use Page Object Model for reusable page interactions (`e2e/pages/`).
- Keep tests independent: each test sets up and cleans up its own state.
- Use `test.extend` fixtures for shared setup (authenticated sessions, seeded data).

## Troubleshooting

### Tests timing out

Increase timeout in config:

```typescript
timeout: 60000, // 60 seconds
```

### Elements not found

Use `waitFor`:

```typescript
await page.waitForSelector('[data-testid="element"]');
```

### Flaky tests

Add retries and use `toPass`:

```typescript
await expect(async () => {
  await expect(page.locator("text=Success")).toBeVisible();
}).toPass({ timeout: 10000 });
```

## Integration with Other Skills

| Skill | Integration |
|-------|-------------|
| `testing-cicd-init` | Sets up unit tests first |
| `testing-expert` | Provides testing patterns |
| `debug` | Investigates flaky tests and failing browser flows |
