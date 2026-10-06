---
title: Use DOM Matchers for DOM Assertions
impact: HIGH
impactDescription: 2-3× faster debugging with semantic error messages
tags: assert, dom-matchers, matchers, assertions
---

## Use DOM Matchers for DOM Assertions

Use `@testing-library/jest-dom` matchers instead of generic Vitest matchers. They provide clearer error messages and test semantic properties.

**Setup (Vitest):** register the matchers once in the setup file with the Vitest entry point, and list that file in `setupFiles`.

```ts
// vitest.setup.ts
import '@testing-library/jest-dom/vitest'
```

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
  },
})
```

**Incorrect (generic Vitest matchers):**

```tsx
render(<Button disabled>Submit</Button>)

const button = screen.getByRole('button')
expect(button.disabled).toBe(true)
expect(button.textContent).toBe('Submit')
expect(document.body.contains(button)).toBe(true)
// Unclear error messages, tests implementation
```

**Correct (DOM matchers):**

```tsx
render(<Button disabled>Submit</Button>)

const button = screen.getByRole('button')
expect(button).toBeDisabled()
expect(button).toHaveTextContent('Submit')
expect(button).toBeInTheDocument()
// Clear error: "Expected element to be disabled but it was enabled"
```

**Common DOM matchers:**

| Matcher | Use Case |
|---------|----------|
| `toBeInTheDocument()` | Element exists in DOM |
| `toBeDisabled()` | Form element is disabled |
| `toBeEnabled()` | Form element is enabled |
| `toBeVisible()` | Element is visible to user |
| `toHaveTextContent()` | Element contains text |
| `toHaveValue()` | Input has specific value |
| `toHaveClass()` | Element has CSS class |
| `toHaveFocus()` | Element has focus |

For TypeScript, include the setup file (or a `.d.ts` that imports `@testing-library/jest-dom/vitest`) in `tsconfig.json` so the matcher types resolve.

Reference: `@testing-library/jest-dom` [Custom Matchers](https://github.com/testing-library/jest-dom)
