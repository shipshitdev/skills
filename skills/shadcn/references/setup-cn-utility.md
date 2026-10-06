---
title: Create the cn Utility Before Using Components
impact: CRITICAL
impactDescription: required by every shadcn/ui component for class merging
tags: setup, cn, clsx, tailwind-merge, utility, className
---

## Create the cn Utility Before Using Components

Every shadcn/ui component uses the `cn` utility to merge Tailwind classes. Missing this utility causes runtime errors in all components. `bunx shadcn@latest init` creates it for you.

**Incorrect (missing cn utility):**

```typescript
// components/ui/button.tsx
import { cn } from "@/lib/utils"
// Error: Cannot find module '@/lib/utils'

export function Button({ className, ...props }) {
  return (
    <button className={cn("px-4 py-2", className)} {...props} />
  )
}
```

**Correct (current shadcn: re-export from the cn package):**

```typescript
// lib/utils.ts
export { cn } from "cn"
```

```bash
bun add cn
```

The `cn` package merges conditional classes (clsx behavior) and resolves Tailwind v4 conflicts (tailwind-merge v3 behavior) in one call, so `cn("base", isActive && "active")` and `cn("px-2", "px-4")` returning `"px-4"` both work.

**Correct (existing projects still on clsx and tailwind-merge):**

```typescript
// lib/utils.ts
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

Move an existing project to the new utility with `bunx --bun shadcn@latest migrate cn`. Tailwind v3 projects must stay on `tailwind-merge` v2.

Reference: [shadcn/ui Manual Installation](https://ui.shadcn.com/docs/installation/manual) and [CLI migrate cn](https://ui.shadcn.com/docs/cli)
