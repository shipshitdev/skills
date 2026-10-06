---
title: Remove Manual cleanup Calls
impact: HIGH
impactDescription: eliminates 2-3 lines of boilerplate per test file
tags: anti, cleanup, afterEach, setup
---

## Remove Manual cleanup Calls

Testing Library automatically calls `cleanup` after each test when the test framework exposes a global `afterEach`. Vitest does so only with `test.globals: true`. With that setting, manual calls are unnecessary.

**Incorrect (manual cleanup):**

```tsx
import { render, cleanup } from '@testing-library/react'

afterEach(() => {
  cleanup()
})

test('renders dashboard', () => {
  render(<Dashboard />)
  // ...
})
// cleanup() is called twice - once manually, once automatically
```

**Correct (rely on automatic cleanup):**

```tsx
import { render } from '@testing-library/react'

test('renders dashboard', () => {
  render(<Dashboard />)
  // ...
})
// cleanup() runs automatically after test
```

**Vitest configuration:** enable globals so automatic cleanup registers.

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
  },
})
```

**When manual cleanup IS needed:**

- Vitest with `globals: false` (the default)
- Using a test framework without global `afterEach` (like AVA)
- Custom test runners without RTL integration

Register cleanup once in the setup file, not in every test file:

```ts
// vitest.setup.ts
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

afterEach(() => {
  cleanup()
})
```

Reference: [Testing Library - Cleanup](https://testing-library.com/docs/react-testing-library/api#cleanup)
