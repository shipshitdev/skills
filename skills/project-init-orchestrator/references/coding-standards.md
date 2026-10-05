# Coding Standards

Coding rules for the full-stack workspace.

---

## General Rules

### Do

- Follow existing patterns (search for 3+ examples)
- Use TypeScript strict mode
- Write meaningful variable names
- Keep functions small and focused
- Handle errors properly

### Don't

- Use `any` type
- Use `console.log` (use LoggerService)
- Create inline interfaces
- Skip error handling
- Commit without review

---

## TypeScript

### Types

```typescript
// ❌ Wrong
function process(data: any) {}

// ✅ Correct
function process(data: UserData): ProcessedResult {}
```

### Interfaces

```typescript
// ❌ Wrong - inline
function Component({ name }: { name: string }) {}

// ✅ Correct - in dedicated file
// packages/props/user.props.ts
export interface UserProps {
  name: string;
}

// component.tsx
import type { UserProps } from "@props/user";
function Component({ name }: UserProps) {}
```

---

## Imports

### Order

1. External packages
2. Internal aliases
3. Relative imports
4. Types

```typescript
// External
import { useState } from "react";
import { Controller } from "@nestjs/common";

// Internal aliases
import { Button } from "@components/ui";
import { UserService } from "@services/user";

// Relative
import { helpers } from "./utils";

// Types
import type { IUser } from "@interfaces/user";
```

### Path Aliases

```typescript
// ❌ Wrong
import { Button } from "../../../packages/components/ui/Button";

// ✅ Correct
import { Button } from "@components/ui/Button";
```

---

## Error Handling

### Backend

```typescript
try {
  const result = await operation();
  return result;
} catch (error) {
  this.logger.error("Operation failed", error, "ServiceName");
  throw new InternalServerErrorException("User-friendly message");
}
```

### Frontend

```typescript
try {
  const data = await service.getData({ signal: controller.signal });
  setData(data);
} catch (error) {
  if (error.name === "AbortError") return;
  LoggerService.getInstance().error("API failed", error);
  NotificationService.getInstance().error("Something went wrong");
}
```

---

## Database

### Soft Deletes

```typescript
// ❌ Wrong
@Prop({ type: Date })
deletedAt?: Date;

// ✅ Correct
@Prop({ default: false, index: true })
isDeleted: boolean;
```

### Queries

```typescript
// ❌ Wrong - missing filters
async findAll() {
  return this.model.find();
}

// ✅ Correct - always filter
async findAll(organizationId: string) {
  return this.model.find({
    organization: organizationId,
    isDeleted: false,
  });
}
```

### Indexes

```typescript
// Simple indexes - in schema
@Prop({ index: true })
email: string;

// Compound indexes - in module
schema.index({ organization: 1, isDeleted: 1 });
```

---

## API Endpoints

### Controllers

```typescript
@Get()
@ApiOperation({ summary: "Get all users" })
@ApiResponse({ status: 200, description: "Returns users" })
async findAll(@Query("organizationId") orgId: string) {
  const users = await this.userService.findAll(orgId);
  return users.map(serializeUser); // Always serialize
}
```

### DTOs

```typescript
export class CreateUserDto {
  @ApiProperty()
  @IsString()
  @IsNotEmpty()
  name: string;

  @ApiProperty()
  @IsEmail()
  email: string;
}
```

---

## React Components

### Structure

```typescript
// 1. Imports
import { useState } from "react";
import type { ComponentProps } from "@props/component";

// 2. Types (if local only)
interface LocalState {
  count: number;
}

// 3. Component
export function Component({ title }: ComponentProps) {
  // State
  const [state, setState] = useState<LocalState>({ count: 0 });

  // Effects
  useEffect(() => {
    // ...
  }, []);

  // Handlers
  const handleClick = () => {
    // ...
  };

  // Render
  return <div>{title}</div>;
}
```

### Async in useEffect

```typescript
useEffect(() => {
  const controller = new AbortController();

  const fetchData = async () => {
    try {
      const data = await api.get({ signal: controller.signal });
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

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Files | kebab-case | `user-service.ts` |
| Components | PascalCase | `UserProfile.tsx` |
| Variables | camelCase | `userName` |
| Constants | UPPER_SNAKE | `MAX_RETRIES` |
| Interfaces | PascalCase with I | `IUserProfile` |
| Types | PascalCase | `UserRole` |
| Enums | PascalCase | `UserStatus` |

---

## Git

### Commits

```
type(scope): description

feat(auth): add OAuth login
fix(api): handle null user
docs(readme): update setup
```

### Branches

```
feature/user-auth
fix/api-error
chore/update-deps
```

---

## Testing

- Tests run in CI/CD only
- Mock external dependencies
- Test business logic, not implementation
- Use descriptive test names
