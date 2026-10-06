---
name: nestjs-expert
description: Guides NestJS 12 APIs with Prisma and Postgres — modules, DI, guards, interceptors, pipes, DTOs, auth, errors. Use when building NestJS APIs or debugging Nest-specific issues.
license: MIT
metadata:
  version: "2.2.2"
  tags: "nestjs, typescript, backend, api, prisma, postgres, rest"
when_to_use: "nest controller, nest service, dependency injection"
---

# NestJS Expert

Stack: NestJS 12 + Prisma 7 + Postgres + TypeScript strict mode.

NestJS 12 and Better Auth ship ESM-only packages. A CommonJS build (`module: commonjs` with `moduleResolution: bundler`) still works because Node 22.12+ loads ESM through `require(esm)`, so run the API on Node >= 22.12; older Node fails at startup with `ERR_REQUIRE_ESM`. Version 11 is the legacy line (`legacy` dist-tag): do not mix 11 and 12 packages.

## Module architecture

Every feature is a self-contained module. No cross-module direct imports — use exported providers.

```
src/
├── app.module.ts           # Root — imports feature modules only
├── common/                 # Shared guards, pipes, filters, interceptors
│   ├── filters/
│   ├── guards/
│   ├── interceptors/
│   └── pipes/
├── config/                 # ConfigModule setup
├── prisma/                 # PrismaModule + PrismaService (global, one client)
└── {feature}/
    ├── {feature}.module.ts
    ├── {feature}.controller.ts
    ├── {feature}.service.ts
    ├── dto/
    │   ├── create-{feature}.dto.ts
    │   └── update-{feature}.dto.ts
    └── {feature}.types.ts
```

## Dependency injection rules

- Inject interfaces, not concrete classes where possible
- Use `@Injectable({ scope: Scope.DEFAULT })` (singleton) unless you need request-scoped
- Circular deps = architectural problem — fix with `forwardRef` only as last resort
- Test with `Test.createTestingModule` — always mock external services

## Controllers

```typescript
@Controller('resources')
@UseGuards(JwtAuthGuard)
@UseInterceptors(ResponseTransformInterceptor)
export class ResourceController {
  constructor(private readonly resourceService: ResourceService) {}

  @Get()
  async findAll(@Query() query: PaginationQueryDto) {
    return this.resourceService.findAll(query);
  }

  @Post()
  @HttpCode(HttpStatus.CREATED)
  async create(@Body() dto: CreateResourceDto, @CurrentUser() user: AuthUser) {
    return this.resourceService.create(dto, user.id);
  }
}
```

Rules:

- Controllers are thin — no business logic, no DB calls
- Always type `@Body()`, `@Query()`, `@Param()` with DTOs
- Use `@CurrentUser()` custom decorator, never `@Req()`

## DTOs + validation

```typescript
import { IsString, IsEnum, IsOptional, MinLength, MaxLength } from 'class-validator';
import { Transform } from 'class-transformer';

export class CreateResourceDto {
  @IsString()
  @MinLength(1)
  @MaxLength(255)
  name: string;

  @IsEnum(ResourceStatus)
  status: ResourceStatus;

  @IsOptional()
  @IsString()
  @Transform(({ value }) => value?.trim())
  description?: string;
}
```

Global validation pipe in `main.ts`:

```typescript
app.useGlobalPipes(new ValidationPipe({
  whitelist: true,        // strip unknown props
  forbidNonWhitelisted: true,
  transform: true,        // auto-transform primitives
  transformOptions: { enableImplicitConversion: true },
}));
```

## Prisma / Postgres

Schema lives in `prisma/schema.prisma`; one global `PrismaService` wraps the client. Feature services depend on `PrismaService` — controllers never touch it.

Prisma 7: the `prisma-client` generator needs an explicit `output` (import `PrismaClient` from that path, not `@prisma/client`), the client needs a driver adapter (`@prisma/adapter-pg`), and the connection URL lives in `prisma.config.ts`. A CommonJS Nest build sets `moduleFormat = "cjs"` in the generator block. `output` is resolved relative to the schema file, so `prisma/schema.prisma` with `../src/generated/prisma` writes the client to `src/generated/prisma`, which the service below imports from `src/prisma/`. Keep that folder git-ignored and regenerate it in CI and Docker builds.

Set `datasource: { url: process.env.DATABASE_URL }` in `prisma.config.ts` rather than `env("DATABASE_URL")`: `env()` throws when the variable is missing, which breaks `prisma generate` in clean CI and Docker builds that have no `.env`. `migrate` commands still fail with a clear error when the URL is absent.

```typescript
// src/prisma/prisma.service.ts
import { PrismaPg } from '@prisma/adapter-pg';
import { PrismaClient } from '../generated/prisma/client';

@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit, OnModuleDestroy {
  constructor() {
    super({ adapter: new PrismaPg({ connectionString: process.env.DATABASE_URL }) });
  }

  async onModuleInit() {
    await this.$connect();
  }

  async onModuleDestroy() {
    await this.$disconnect();
  }
}
```

```prisma
// prisma/schema.prisma
generator client {
  provider     = "prisma-client"
  output       = "../src/generated/prisma"
  moduleFormat = "cjs"
}

datasource db {
  provider = "postgresql"
}

model Resource {
  id        String         @id @default(uuid()) @db.Uuid
  name      String
  status    ResourceStatus @default(ACTIVE)
  userId    String         @db.Uuid
  user      User           @relation(fields: [userId], references: [id])
  createdAt DateTime       @default(now())
  updatedAt DateTime       @updatedAt
  deletedAt DateTime?

  @@index([userId, createdAt(sort: Desc)])
}

enum ResourceStatus {
  ACTIVE
  ARCHIVED
}
```

```typescript
// service
@Injectable()
export class ResourceService {
  constructor(private readonly prisma: PrismaService) {}

  async findAll(userId: string, query: PaginationQueryDto) {
    const { page = 1, limit = 20 } = query;
    return this.prisma.resource.findMany({
      where: { userId, deletedAt: null },
      orderBy: { createdAt: 'desc' },
      skip: (page - 1) * limit,
      take: limit,
      select: { id: true, name: true, status: true, createdAt: true },
    });
  }
}
```

Rules:

- Ids are `String` (uuid or cuid) and relations are explicit `@relation` fields — never hand-rolled id strings with no foreign key
- Type ids as `string` in the service layer; the Prisma-generated types are the source of truth (no hand-written model interfaces)
- Use `select` to return only needed fields; never return the raw row when it holds secrets
- Multi-step writes use `prisma.$transaction`; never chain dependent writes without it
- Prefer the typed client; for `$queryRaw` use the tagged template (`Prisma.sql`) so values stay parameterized — never `$queryRawUnsafe` with user input
- Soft delete: `deletedAt DateTime?`, never hard delete user data; filter `deletedAt: null` in reads
- Schema changes go through `prisma migrate dev` / `prisma migrate deploy`, never edited by hand in the database

## Auth pattern

```typescript
// JWT strategy
@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor(configService: ConfigService) {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      secretOrKey: configService.get<string>('JWT_SECRET'),
      ignoreExpiration: false,
    });
  }

  async validate(payload: JwtPayload): Promise<AuthUser> {
    // return value is injected as req.user
    return { id: payload.sub, email: payload.email };
  }
}

// custom decorator
export const CurrentUser = createParamDecorator(
  (data: unknown, ctx: ExecutionContext) => ctx.switchToHttp().getRequest().user,
);
```

## Guards

```typescript
@Injectable()
export class ResourceOwnerGuard implements CanActivate {
  constructor(private readonly resourceService: ResourceService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const { user, params } = context.switchToHttp().getRequest();
    const resource = await this.resourceService.findById(params.id);
    return resource?.userId === user.id;
  }
}
```

## Exception filter

```typescript
@Catch()
export class GlobalExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(GlobalExceptionFilter.name);

  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();

    if (exception instanceof HttpException) {
      return response.status(exception.getStatus()).json({
        statusCode: exception.getStatus(),
        message: exception.message,
      });
    }

    this.logger.error('Unhandled exception', exception instanceof Error ? exception.stack : exception);
    return response.status(500).json({ statusCode: 500, message: 'Internal server error' });
  }
}
```

## Config

```typescript
// config/app.config.ts
export default registerAs('app', () => ({
  port: parseInt(process.env.PORT ?? '3000', 10),
  jwtSecret: process.env.JWT_SECRET,
  databaseUrl: process.env.DATABASE_URL,
}));

// access in service
constructor(private config: ConfigService) {}
const port = this.config.get<number>('app.port');
```

Never use `process.env` directly outside config files.

## Performance rules

- `select` only needed columns on read queries
- Add `@@index` for every field used in a `where` filter or `orderBy`
- Compound indexes for multi-field queries: `@@index([userId, createdAt(sort: Desc)])`
- Avoid N+1: use `include`/`select` relations or batch with `findMany({ where: { id: { in: ids } } })`
- Paginate with `skip`/`take`, or cursor pagination for large tables
- Cache with `@nestjs/cache-manager` (Redis) for expensive reads

## Common mistakes

| Wrong | Right |
|-------|-------|
| Business logic in controller | Move to service |
| `any` type anywhere | Define interface/DTO |
| `console.log` | `new Logger(ClassName.name)` |
| `req.user` directly | `@CurrentUser()` decorator |
| Hard-coding env vars | `ConfigService` |
| `findMany()` returning every column | `select` only what the caller needs |
| `$queryRawUnsafe` with user input | Typed client or tagged `$queryRaw` |
| Dependent writes without a transaction | `prisma.$transaction` |

## Related skills

- `nestjs-queue-architect` — BullMQ async job patterns
- `postgres-ops` — migrations, indexes, query plans
- `error-handling-expert` — global error strategy
