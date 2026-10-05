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
├── schemas/
│   └── users.schema.ts       # Mongoose schema
├── dto/
│   ├── create-user.dto.ts
│   └── update-user.dto.ts
└── users.http                # REST Client tests
```

### Database Patterns

**Soft Deletes:**

```typescript
@Prop({ default: false, index: true })
isDeleted: boolean;
```

**Multi-Tenancy:**

```typescript
// Always filter by organization
async findAll(organizationId: string) {
  return this.model.find({
    organization: organizationId,
    isDeleted: false,
  });
}
```

**Indexes:**

- Simple indexes: In schema via `@Prop({ index: true })`
- Compound indexes: In module's `useFactory`

```typescript
MongooseModule.forFeatureAsync([{
  name: User.name,
  useFactory: () => {
    const schema = UserSchema;
    schema.index({ organization: 1, isDeleted: 1 });
    return schema;
  },
}]),
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
export function serializeUser(user: UserDocument): IUser {
  return {
    id: user._id.toString(),
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
