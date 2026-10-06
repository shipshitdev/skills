---
title: Mock Modules at Module Level
impact: MEDIUM
impactDescription: prevents intermittent mock timing failures
tags: setup, mock, vitest, modules
---

## Mock Modules at Module Level

Call `vi.mock()` at the top level of your test file, not inside tests. Vitest hoists `vi.mock` calls to the top of the file, but placing them inside tests is misleading and can cause timing issues. The factory must return the module shape (for example `{ fetchUser: vi.fn() }`); use `vi.importActual` to keep the real exports you do not mock.

**Incorrect (mock inside test):**

```tsx
test('fetches user data', async () => {
  vi.mock('./api', () => ({
    fetchUser: vi.fn().mockResolvedValue({ name: 'John' })
  }))

  render(<UserProfile />)
  // Mock may not be applied correctly
})
```

**Correct (mock at module level):**

```tsx
import { beforeEach, expect, test, vi } from 'vitest'
import { fetchUser } from './api'

vi.mock('./api', () => ({
  fetchUser: vi.fn(),
}))

const mockFetchUser = vi.mocked(fetchUser)

test('fetches user data', async () => {
  mockFetchUser.mockResolvedValue({ name: 'John' })

  render(<UserProfile />)
  expect(await screen.findByText('John')).toBeInTheDocument()
})

test('handles error', async () => {
  mockFetchUser.mockRejectedValue(new Error('Network error'))

  render(<UserProfile />)
  expect(await screen.findByRole('alert')).toHaveTextContent('Network error')
})
```

**Reset mocks between tests:**

```tsx
beforeEach(() => {
  vi.clearAllMocks()
})
```

Reference: [Vitest - Mocking](https://vitest.dev/guide/mocking)
