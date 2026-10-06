# Legacy Manual Route — NestJS + Next.js Workspace

Use this guide only when `npx @shipshitdev/v0` is not appropriate or the user
explicitly asks to bypass it for an existing workspace.

## Phase 1: PRD Brief Intake

Ask the user for a 1-2 paragraph product description, then extract and confirm:

```
I'll help you build [Project Name]. Based on your description, I understand:

**Entities:**
- [Entity1]: [fields]
- [Entity2]: [fields]

**Features:**
- [Feature 1]
- [Feature 2]

**Routes:**
- / - Home/Dashboard
- /[entity] - List view
- /[entity]/[id] - Detail view

**API Endpoints:**
- GET/POST /api/[entity]
- GET/PATCH/DELETE /api/[entity]/:id

Is this correct? Any adjustments?
```

## Phase 2: Auth Setup (Always Included)

Generate Better Auth (email + password, sessions in Postgres through Prisma). Better Auth
runs inside the API; the dashboard talks to it with `better-auth/react`. The scaffold
generates all of this, so the manual route only needs it when you assemble a workspace by hand.

**Backend:**

- `auth/auth.service.ts` - Owns the Better Auth instance (Prisma adapter)
- `auth/auth.module.ts` - Global module exporting `AuthService` and `AuthGuard`
- `auth/guards/auth.guard.ts` - Session guard (`auth.api.getSession`)
- `auth/decorators/current-user.decorator.ts` - User extraction decorator
- `main.ts` - Mounts `toNodeHandler(auth)` at `/api/auth/*` before Nest's body parser
- `prisma/schema/auth.prisma` - `User`, `Session`, `Account`, `Verification` models

**Frontend (`frontend/apps/dashboard`):**

- `lib/auth-client.ts` - `createAuthClient` pointed at the API
- `components/auth-form.tsx` - Shared sign-in / sign-up form
- `app/sign-in/page.tsx`, `app/sign-up/page.tsx` - Auth pages
- `proxy.ts` - Optimistic route protection (Next.js 16 renamed `middleware.ts` to `proxy.ts`)

**Environment:**

- `.env.example` with `DATABASE_URL`, `BETTER_AUTH_SECRET`, `BETTER_AUTH_URL`, `FRONTEND_URLS`
  and `NEXT_PUBLIC_API_URL`

## Phase 3: Entity Generation

For each extracted entity, generate complete CRUD **with tests**:

**Backend (NestJS):**

```
api/apps/api/src/collections/{entity}/
├── {entity}.module.ts
├── {entity}.controller.ts         # Full CRUD + Swagger + AuthGuard
├── {entity}.controller.spec.ts    # Controller unit tests
├── {entity}.service.ts            # Business logic
├── {entity}.service.spec.ts       # Service unit tests
└── dto/
    ├── create-{entity}.dto.ts     # class-validator decorators
    └── update-{entity}.dto.ts     # PartialType of create

api/apps/api/src/test/
└── {entity}.e2e.spec.ts           # E2E tests with supertest (needs a Postgres database)

api/prisma/schema/
└── {entity}.prisma                # Prisma model with userId
```

**Frontend (Next.js):**

```
frontend/apps/dashboard/
├── app/{entity}/
│   ├── page.tsx                   # List view (protected by proxy.ts)
│   ├── page.spec.tsx              # Page test
│   └── [id]/page.tsx              # Detail view (protected)
├── vitest.setup.ts                # jest-dom matchers
└── vitest.config.mts              # Frontend test config (jsdom)

frontend/packages/components/
├── {entity}-list.tsx
├── {entity}-list.spec.tsx         # Component tests
├── {entity}-form.tsx
├── {entity}-form.spec.tsx         # Component tests
└── {entity}-item.tsx

frontend/packages/hooks/
├── use-{entities}.ts              # React hook for state management
└── use-{entities}.spec.ts         # Hook tests

frontend/packages/services/
└── {entity}.service.ts            # API client with auth headers
```

## Phase 4: Quality Setup

**Vitest Configuration:**

- `api/vitest.config.mts` (with `unplugin-swc` for decorator metadata) and
  `frontend/apps/dashboard/vitest.config.mts` (jsdom)
- 80% coverage threshold for lines, functions, branches
- `@vitest/coverage-v8` provider

**GitHub Actions:**

- `.github/workflows/ci.yml`
- Runs on push to main and PRs
- Steps: install → lint → typecheck → test → build

**Husky Hooks:**

- Pre-commit: `lint-staged` (Biome check)
- Pre-push: `bun run typecheck`

**Biome:**

- One `biome.json` at the workspace root (nested configs would each need `extends: "//"`)
- 100 character line width
- Double quotes, semicolons
- Run `bun run lint:fix` once after generating so Biome formats the scaffold output

## Phase 5: Verification

```
✅ Generation complete!

Quality Report:
- bun install: ✓ succeeded
- bun run lint: ✓ 0 errors
- bun run test: ✓ 24 tests passed
- Coverage: 82% (threshold: 80%)

Ready to run:
  cd [project]
  bun dev
```

## Generated Structure

```
myproject/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI/CD
├── .husky/
│   ├── pre-commit              # Lint staged files
│   └── pre-push                # Type check
├── .agents/                     # AI documentation
├── package.json                # Workspace root (workspaces: api, frontend/apps/*, frontend/packages, mobile, packages)
├── biome.json                  # Lint and format config
│
├── api/                        # NestJS backend
│   ├── apps/api/src/
│   │   ├── main.ts
│   │   ├── app.module.ts
│   │   ├── auth/
│   │   │   ├── auth.service.ts                  # Better Auth instance
│   │   │   ├── auth.module.ts
│   │   │   ├── guards/auth.guard.ts
│   │   │   ├── guards/auth.guard.spec.ts        # Auth guard tests
│   │   │   └── decorators/current-user.decorator.ts
│   │   └── collections/
│   │       └── {entity}/
│   │           ├── {entity}.controller.ts
│   │           ├── {entity}.controller.spec.ts  # Controller tests
│   │           ├── {entity}.service.ts
│   │           └── {entity}.service.spec.ts     # Service tests
│   ├── apps/api/src/test/
│   │   └── {entity}.e2e.spec.ts                 # E2E tests (optional)
│   ├── prisma/schema/                           # schema.prisma, auth.prisma, {entity}.prisma
│   ├── prisma.config.ts
│   ├── tsconfig.json / tsconfig.build.json
│   ├── vitest.config.mts
│   └── package.json
│
├── frontend/                   # Next.js apps
│   ├── apps/dashboard/         # Own workspace: package.json, next.config.ts, postcss.config.mjs
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── globals.css     # Tailwind v4: @import "tailwindcss" + @theme
│   │   │   ├── sign-in/page.tsx
│   │   │   ├── sign-up/page.tsx
│   │   │   └── {entity}/       # Generated per entity
│   │   ├── components/auth-form.tsx
│   │   ├── lib/auth-client.ts
│   │   ├── proxy.ts            # Route protection (Next.js 16 name for middleware)
│   │   ├── vitest.config.mts   # Frontend test config (jsdom)
│   │   └── tsconfig.json
│   ├── packages/               # Shared workspace package
│   │   ├── components/
│   │   │   └── {entity}-list.tsx
│   │   ├── services/           # API clients (credentials: "include")
│   │   ├── hooks/
│   │   └── interfaces/
│   └── package.json            # Delegates scripts to apps/dashboard
│
├── mobile/                     # React Native + Expo (optional)
│   └── ...
│
└── packages/                   # Shared packages
    └── packages/
        ├── common/
        │   ├── interfaces/
        │   └── enums/
        └── helpers/
```

## Key Patterns

### Backend Controller Pattern

```typescript
@ApiTags('tasks')
@ApiCookieAuth()
@UseGuards(AuthGuard)
@Controller('tasks')
export class TasksController {
  constructor(private readonly tasksService: TasksService) {}

  @Post()
  @ApiOperation({ summary: 'Create a new task' })
  create(
    @Body() createTaskDto: CreateTaskDto,
    @CurrentUser() user: { userId: string },
  ) {
    return this.tasksService.create(createTaskDto, user.userId);
  }
  // ... full CRUD
}
```

### Backend Service Pattern

```typescript
@Injectable()
export class TasksService {
  constructor(private readonly prisma: PrismaService) {}

  async create(createTaskDto: CreateTaskDto, userId: string): Promise<Task> {
    return this.prisma.task.create({ data: { ...createTaskDto, userId } });
  }
  // ... full CRUD with userId filtering
}
```

### Frontend Component Pattern

```typescript
'use client';

import { useEffect, useState } from 'react';
import { TaskService } from '@services/task.service';
import { Task } from '@interfaces/task.interface';

export function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();
    TaskService.getAll({ signal: controller.signal })
      .then(setTasks)
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, []);

  // ... render
}
```

## Additional Scripts

```bash
# Add an organization-scoped collection to an existing API
python3 scripts/add-api-collection.py \
  --root ~/www/myproject/api \
  --name comments

# Add a new frontend app (its own workspace under frontend/apps)
python3 scripts/add-frontend-app.py \
  --root ~/www/myproject/frontend \
  --name admin
```

## Development Commands

After scaffolding:

```bash
cd myproject

# Install all dependencies
bun install

# Format the generated files once, then commit
bun run lint:fix

# Start all services (backend + frontend)
bun dev

# Or start individually
bun run dev:api      # Backend on :3001
bun run dev:frontend # Frontend on :3000
bun run dev:mobile   # Mobile via Expo

# Database (from api/)
bun run prisma:generate  # Generate the Prisma client
bun run prisma:migrate   # Create and apply a dev migration
bun run prisma:deploy    # Apply migrations (CI and production)

# Quality commands
bun run lint         # Check code style
bun run test         # Run API and frontend tests
bun run typecheck    # API, frontend and mobile
(cd api && bun run test:coverage)        # API coverage
(cd frontend && bun run test:coverage)   # Frontend coverage
```

## Environment Variables

Create `.env` files based on `.env.example`:

**API (`api/.env`):**

```
PORT=3001
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/myproject?schema=public
BETTER_AUTH_SECRET=<openssl rand -base64 32>
BETTER_AUTH_URL=http://localhost:3001
FRONTEND_URLS=http://localhost:3000   # comma-separated origins (CORS + trustedOrigins)
```

**Dashboard (`frontend/apps/dashboard/.env.local`):**

```
NEXT_PUBLIC_API_URL=http://localhost:3001
```

`prisma generate` and `bun run build` need no `DATABASE_URL`; `prisma migrate` and the running
API do.
