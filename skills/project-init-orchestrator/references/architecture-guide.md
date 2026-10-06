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
collections/users/
├── users.module.ts           # NestJS module
├── controllers/
│   └── users.controller.ts   # HTTP endpoints
├── services/
│   └── users.service.ts      # Business logic
├── dto/
│   ├── create-user.dto.ts
│   └── update-user.dto.ts
└── users.http                # REST Client tests

# Models live in the multi-file Prisma schema folder, one file per model:
prisma/schema/users.prisma
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
  return this.prisma.user.findMany({
    where: { organizationId, isDeleted: false },
  });
}
```

**Indexes:**

- Single-column: `@@index([email])` or `@unique` in the model
- Compound: `@@index([organizationId, isDeleted])` in the model
- Every index change ships as a migration (`bun run prisma:migrate`)

```prisma
model User {
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
│   ├── dashboard/        # Main app
│   ├── admin/            # Admin app
│   └── settings/         # Settings app
└── packages/
    ├── components/       # Reusable UI
    ├── services/         # API clients
    ├── hooks/            # Custom hooks
    ├── interfaces/       # TypeScript types
    └── props/            # Component props
```

### Path Aliases

```typescript
import { Button } from "@components/ui/Button";
import { UserService } from "@services/user";
import { useUser } from "@hooks/useUser";
import type { IUser } from "@interfaces/user";
```

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

- Use Clerk (or similar) for auth
- JWT tokens in Authorization header
- Guards validate tokens on protected routes

```typescript
@UseGuards(ClerkAuthGuard)
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
frontend/.env
mobile/.env
```

Never commit `.env` files.
