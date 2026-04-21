---
name: nestjs-expert
description: NestJS architecture, modules, DI, guards, interceptors, pipes, MongoDB/Mongoose integration, auth, and production patterns. Use when building NestJS APIs, designing module structure, implementing auth, handling errors, writing DTOs, or debugging NestJS-specific issues.
when_to_use: "nestjs, nest module, nest controller, nest service, nest guard, nest interceptor, nest pipe, dependency injection, NestJS auth, NestJS MongoDB, NestJS error handling, NestJS performance"
license: MIT
metadata:
  version: "1.0.0"
  tags: "nestjs, typescript, backend, api, mongodb, rest"
---

# NestJS Expert

Production NestJS patterns for TypeScript APIs. Stack: NestJS + MongoDB/Mongoose + TypeScript strict mode.

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
└── {feature}/
    ├── {feature}.module.ts
    ├── {feature}.controller.ts
    ├── {feature}.service.ts
    ├── {feature}.repository.ts  # optional, wraps Mongoose model
    ├── dto/
    │   ├── create-{feature}.dto.ts
    │   └── update-{feature}.dto.ts
    ├── schemas/
    │   └── {feature}.schema.ts
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
  async create(@Body() dto: CreateResourceDto, @CurrentUser() user: UserDocument) {
    return this.resourceService.create(dto, user._id);
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

## MongoDB / Mongoose

```typescript
// schema
@Schema({ timestamps: true, versionKey: false })
export class Resource {
  @Prop({ required: true, index: true })
  name: string;

  @Prop({ type: Types.ObjectId, ref: 'User', required: true, index: true })
  userId: Types.ObjectId;

  @Prop({ enum: ResourceStatus, default: ResourceStatus.ACTIVE })
  status: ResourceStatus;
}

export const ResourceSchema = SchemaFactory.createForClass(Resource);
export type ResourceDocument = Resource & Document;
```

```typescript
// service
@Injectable()
export class ResourceService {
  constructor(
    @InjectModel(Resource.name) private readonly model: Model<ResourceDocument>,
  ) {}

  async findAll(userId: Types.ObjectId, query: PaginationQueryDto) {
    const { page = 1, limit = 20 } = query;
    return this.model
      .find({ userId, deletedAt: null })
      .sort({ createdAt: -1 })
      .skip((page - 1) * limit)
      .limit(limit)
      .lean()
      .exec();
  }
}
```

Rules:

- Always `.lean()` for read queries (plain objects, ~30% faster)
- Always `.exec()` to get a real Promise
- Use `Types.ObjectId` not `string` for references in service layer
- Soft delete: `deletedAt: Date | null`, never hard delete user data

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

  async validate(payload: JwtPayload): Promise<UserDocument> {
    // return value is injected as req.user
    return { _id: payload.sub, email: payload.email };
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
    return resource?.userId.equals(user._id) ?? false;
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
  mongoUri: process.env.MONGO_URI,
}));

// access in service
constructor(private config: ConfigService) {}
const port = this.config.get<number>('app.port');
```

Never use `process.env` directly outside config files.

## Performance rules

- `lean()` on all read queries
- Add indexes for every field used in `find()` filter or `sort()`
- Compound indexes for multi-field queries: `{ userId: 1, createdAt: -1 }`
- Use `select()` to project only needed fields on large documents
- Cache with `@nestjs/cache-manager` for expensive reads

## Common mistakes

| Wrong | Right |
|-------|-------|
| Business logic in controller | Move to service |
| `any` type anywhere | Define interface/DTO |
| `console.log` | `new Logger(ClassName.name)` |
| `req.user` directly | `@CurrentUser()` decorator |
| Hard-coding env vars | `ConfigService` |
| `.find()` without `.lean()` on reads | Always `.lean().exec()` |
| `string` for ObjectId refs | `Types.ObjectId` |

## Related skills

- `nestjs-queue-architect` — BullMQ async job patterns
- `nestjs-testing-expert` — Jest unit + integration testing
- `mongodb-migration-expert` — schema migrations
- `error-handling-expert` — global error strategy
