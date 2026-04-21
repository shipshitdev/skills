---
name: nextjs-best-practices
description: "Next.js App Router principles: Server Components, data fetching, routing patterns, metadata, caching, and Server Actions. Use when building or reviewing Next.js App Router applications."
license: MIT
metadata:
  version: "1.0.0"
  tags: "nextjs, react, app-router, server-components, typescript"
  author: "antigravity-awesome-skills"
---

# Next.js Best Practices

> Principles for Next.js App Router development.

---

## 1. Server vs Client Components

### Decision Tree

```
Does it need...?
│
├── useState, useEffect, event handlers
│   └── Client Component ('use client')
│
├── Direct data fetching, no interactivity
│   └── Server Component (default)
│
└── Both?
    └── Split: Server parent + Client child
```

### By Default

| Type | Use |
|------|-----|
| **Server** | Data fetching, layout, static content |
| **Client** | Forms, buttons, interactive UI |

---

## 2. Data Fetching Patterns

| Pattern | Use |
|---------|-----|
| **Default** | Static (cached at build) |
| **Revalidate** | ISR (time-based refresh) |
| **No-store** | Dynamic (every request) |

| Source | Pattern |
|--------|---------|
| Database | Server Component fetch |
| API | fetch with caching |
| User input | Client state + server action |

---

## 3. Routing Principles

| File | Purpose |
|------|---------|
| `page.tsx` | Route UI |
| `layout.tsx` | Shared layout |
| `loading.tsx` | Loading state |
| `error.tsx` | Error boundary |
| `not-found.tsx` | 404 page |

| Pattern | Use |
|---------|-----|
| Route groups `(name)` | Organize without URL |
| Parallel routes `@slot` | Multiple same-level pages |
| Intercepting `(.)` | Modal overlays |

---

## 4. API Routes

- Validate input with Zod
- Return proper status codes
- Handle errors gracefully
- Use Edge runtime when possible

---

## 5. Performance Principles

- Use `next/image` with priority for above-fold, blur placeholder, responsive sizes
- Dynamic imports for heavy components
- Route-based code splitting (automatic)

---

## 6. Metadata

| Type | Use |
|------|-----|
| Static export | Fixed metadata |
| generateMetadata | Dynamic per-route |

Essential tags: title (50-60 chars), description (150-160 chars), Open Graph images, canonical URL.

---

## 7. Caching Strategy

| Layer | Control |
|-------|---------|
| Request | fetch options |
| Data | revalidate/tags |
| Full route | route config |

| Method | Use |
|--------|-----|
| Time-based | `revalidate: 60` |
| On-demand | `revalidatePath/Tag` |
| No cache | `no-store` |

---

## 8. Server Actions

- Mark with `'use server'`
- Validate all inputs
- Return typed responses
- Handle errors

---

## 9. Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| `'use client'` everywhere | Server by default |
| Fetch in client components | Fetch in server |
| Skip loading states | Use `loading.tsx` |
| Ignore error boundaries | Use `error.tsx` |
| Large client bundles | Dynamic imports |

---

## 10. Project Structure

```
app/
├── (marketing)/     # Route group
│   └── page.tsx
├── (dashboard)/
│   ├── layout.tsx   # Dashboard layout
│   └── page.tsx
├── api/
│   └── [resource]/
│       └── route.ts
└── components/
    └── ui/
```

> **Remember:** Server Components are the default. Start there, add `'use client'` only when needed.

## Limitations

- Use only when the task clearly matches Next.js App Router scope.
- Do not treat output as a substitute for environment-specific validation, testing, or expert review.
