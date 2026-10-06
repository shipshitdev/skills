# Architecture Guide

Architectural patterns for the full-stack workspace.

---

## Project Structure

```
workspace/
├── api/              # NestJS backend
├── frontend/         # NextJS apps
├── mobile/           # React Native + Expo
└── packages/         # Shared code
```

---

## Backend Architecture (NestJS)

### Collection Pattern

Each feature is a "collection" with consistent structure:

```
collections/projects/
├── projects.module.ts           # NestJS module
├── controllers/
│   └── projects.controller.ts   # HTTP endpoints
├── services/
│   └── projects.service.ts      # Business logic
├── dto/
│   ├── create-project.dto.ts
│   └── update-project.dto.ts
└── projects.http                # REST Client tests

# Models live in the multi-file Prisma schema folder, one file per model:
prisma/schema/projects.prisma
# auth.prisma holds the Better Auth models (User, Session, Account, Verification);
# do not reuse those model names for collections
```

### Database Patterns

**Soft Deletes:**

```prisma
isDeleted Boolean @default(false)

@@index([organizationId, isDeleted])
```

**Multi-Tenancy:**

```typescript
// Always filter by organization
async findAll(organizationId: string) {
  return this.prisma.project.findMany({
    where: { organizationId, isDeleted: false },
  });
}
```

**Indexes:**

- Single-column: `@@index([email])` or `@unique` in the model
- Compound: `@@index([organizationId, isDeleted])` in the model
- Every index change ships as a migration (`bun run prisma:migrate`)

```prisma
model Project {
  id             String  @id @default(cuid())
  organizationId String
  isDeleted      Boolean @default(false)

  @@index([organizationId, isDeleted])
}
```

---

## Frontend Architecture (NextJS)

### Package Structure

```
frontend/
├── apps/
│   ├── dashboard/        # Main app: own package.json, next.config.ts, tsconfig, proxy.ts
│   ├── admin/            # Admin app (python3 scripts/add-frontend-app.py)
│   └── settings/         # Settings app
└── packages/             # Workspace package shared by every app
    ├── components/       # Reusable UI
    ├── services/         # API clients
    ├── hooks/            # Custom hooks
    └── interfaces/       # TypeScript types
```

Every app is its own Bun workspace (`frontend/apps/*`), so `next dev` and `next build` run
inside the app folder. Styling is Tailwind v4 CSS-first: `app/globals.css` starts with
`@import "tailwindcss"` and an `@theme` block, PostCSS uses `@tailwindcss/postcss`, and
there is no `tailwind.config.*`.

### Path Aliases

```typescript
import { TaskList } from "@components/tasks/task-list";
import { TaskService } from "@services/task.service";
import type { Task } from "@interfaces/task.interface";
```

The aliases map to `frontend/packages/*` in each app's `tsconfig.json` and `vitest.config.mts`.

### Async Operations

Always use AbortController:

```typescript
useEffect(() => {
  const controller = new AbortController();

  const fetchData = async () => {
    try {
      const data = await service.getData({ signal: controller.signal });
      setData(data);
    } catch (error) {
      if (error.name === "AbortError") return;
      handleError(error);
    }
  };

  fetchData();
  return () => controller.abort();
}, []);
```

---

## Mobile Architecture (React Native + Expo)

### Expo Router

File-based routing:

```
mobile/app/
├── _layout.tsx       # Root layout
├── index.tsx         # Home screen
├── (tabs)/           # Tab group
│   ├── _layout.tsx
│   ├── home.tsx
│   └── profile.tsx
└── settings/
    └── index.tsx
```

---

## Shared Packages

### Location

All shared code goes in `packages/`:

```
packages/packages/
├── common/
│   ├── serializers/      # Data serializers
│   ├── interfaces/       # Shared types
│   └── enums/            # Shared enums
├── helpers/              # Utility functions
└── constants/            # Shared constants
```

### Serializers

Serializers live in packages, NOT in API:

```typescript
// packages/packages/common/serializers/user.serializer.ts
export function serializeUser(user: User): IUser {
  return {
    id: user.id,
    name: user.name,
    email: user.email,
    // Never expose isDeleted, internal fields, etc.
  };
}
```

---

## Data Flow

```
Frontend → API → Service → Database
    ↓
Mobile  →

           ←  Serializer ← Response
```

1. Frontend/Mobile makes API request
2. Controller receives request
3. Service handles business logic
4. Database query with organization + isDeleted filters
5. Serializer transforms response
6. Client receives clean data

---

## Authentication

- Better Auth runs inside the API at `/api/auth/*` (email + password; sessions and users in
  Postgres through the Prisma adapter)
- The session lives in an HTTP-only cookie; browsers call the API with `credentials: "include"`
- `AuthGuard` resolves the session with `auth.api.getSession` and attaches the user
- The dashboard's `proxy.ts` (Next.js 16's replacement for `middleware.ts`) redirects visitors
  without a session cookie to `/sign-in`; that check is optimistic, the guard enforces access

```typescript
@UseGuards(AuthGuard)
@Controller("protected")
export class ProtectedController {}
```

---

## Caching

- Redis for query caching
- BullMQ for job queues
- Cache invalidation on mutations

---

## Environment

Each project has its own `.env`:

```
api/.env
frontend/apps/dashboard/.env.local
mobile/.env
```

Never commit `.env` files.
