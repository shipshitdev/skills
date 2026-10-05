# Clerk validator reference

Checks, deprecated patterns, and examples for the `clerk` stack of `scripts/validate.py --stack clerk`.

Validates Clerk authentication configuration and enforces modern Clerk patterns with Next.js 16.

## What Gets Checked

### 1. Package Version

```json
// GOOD: Latest Clerk
"@clerk/nextjs": "^6.0.0"

// BAD: Old version
"@clerk/nextjs": "^4.0.0"
```

### 2. Proxy vs Middleware (Next.js 16)

**GOOD - Next.js 16:**

```typescript
// proxy.ts
import { clerkMiddleware } from "@clerk/nextjs/server";
export default clerkMiddleware();
```

**BAD - Deprecated:**

```typescript
// middleware.ts (deprecated in Next.js 16)
import { authMiddleware } from "@clerk/nextjs";  // DEPRECATED
export default authMiddleware();
```

### 3. ClerkProvider Setup

**GOOD:** wrap the entire app in `<ClerkProvider>` inside `app/layout.tsx`.
**BAD:** placing it in `_app.tsx` (Pages Router, deprecated) or forgetting to
wrap the whole tree.

See the Full guide section below (§ Root Layout with Clerk Components) for the
full layout example.

### 4. Auth Import Patterns

**GOOD - Server-side:**

```typescript
import { auth } from "@clerk/nextjs/server";

export default async function Page() {
  const { userId } = await auth();
  // ...
}
```

**BAD - Old patterns:**

```typescript
// Don't use
import { getAuth } from "@clerk/nextjs/server";  // OLD
import { currentUser } from "@clerk/nextjs";     // Check version
```

### 5. Environment Variables

**Required:**

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
```

**Optional but recommended:**

```env
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/onboarding
```

## Deprecated Patterns

| Deprecated | Replacement |
|------------|-------------|
| `authMiddleware()` | `clerkMiddleware()` |
| `middleware.ts` | `proxy.ts` (Next.js 16) |
| `getAuth()` | `auth()` |
| `@clerk/nextjs` < v5 | `@clerk/nextjs@latest` |
| `_app.tsx` provider | `app/layout.tsx` provider |
| `withClerkMiddleware` | `clerkMiddleware()` |

## Validation Output

```
=== Clerk Validation Report ===
Package Version: @clerk/nextjs@6.0.0 ✓
Configuration: ✓ ClerkProvider  ✓ proxy.ts  ✗ middleware.ts found (deprecated)
Auth Patterns:  ✓ auth()  ✗ authMiddleware() in 1 file (deprecated)
Summary: 2 issues found
```

## Modern Clerk Patterns

### Protected Routes (Server Component)

Call `await auth()`, redirect to `/sign-in` when `userId` is missing, and
render only after that check.

See the Full guide section below (§ Protected Route Example) for the full page.

### Protected Routes (Client Component)

Mark the component `"use client"`, read `{ isLoaded, userId }` from
`useAuth()`, and render a loading/redirect state until both are resolved.

See the Full guide section below (§ Use Auth Hook) for the full component.

### API Routes

Call `await auth()` inside the route handler and return `401` before doing
any work when `userId` is missing.

See the Full guide section below (§ Protected API Route) for the full handler.

### NestJS Guard

Extract the bearer token, verify it with `clerkClient.verifyToken`, and
attach `userId` to the request; return `false`/throw on any failure.

See the Full guide section below (§ Authentication Guard) for the full guard.

## Webhook Configuration

Verify the `svix-id` / `svix-timestamp` / `svix-signature` headers with the
`svix` package against `CLERK_WEBHOOK_SECRET` before trusting the payload;
never process an unverified webhook body.

See the Full guide section below (§ Webhooks (Next.js App Router)) for the full
route handler, and (§ Webhook Handler) for the NestJS controller equivalent.

## Full guide

### Setup and Configuration

#### 1. Install Clerk SDK

**Next.js:**

```bash
bun add @clerk/nextjs@latest
```

**NestJS:**

```bash
bun add @clerk/clerk-sdk-node
```

#### 2. Environment Variables

Create `.env.local` (Next.js) or `.env` (NestJS):

```env
# .env.local
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=YOUR_PUBLISHABLE_KEY
CLERK_SECRET_KEY=YOUR_SECRET_KEY

# Optional: Webhook secret (if using webhooks)
CLERK_WEBHOOK_SECRET=YOUR_WEBHOOK_SECRET

# Optional: Custom URLs (defaults to Clerk hosted)
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/
```

**Important:** Store real keys only in `.env.local` (never in app code, markdown, or other tracked files). Verify `.gitignore` excludes `.env*`.

#### 3. Clerk Dashboard Setup

1. Create account at [clerk.com](https://clerk.com)
2. Create a new application
3. Configure authentication methods (Email, OAuth, etc.)
4. Copy publishable key and secret key
5. Set up webhook endpoints (if needed)

### Next.js Implementation

#### 1. App Router Setup

**Create `proxy.ts` file:**

Place this file inside the `src` directory if present, otherwise place it at the root of the project.

```typescript
// proxy.ts (or src/proxy.ts if using src directory)
import { clerkMiddleware } from "@clerk/nextjs/server";

export default clerkMiddleware();

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    // Always run for API routes
    "/(api|trpc)(.*)",
  ],
};
```

**Root Layout with Clerk Components:**

```typescript
// app/layout.tsx
import type { Metadata } from "next";
import {
  ClerkProvider,
  SignInButton,
  SignUpButton,
  SignedIn,
  SignedOut,
  UserButton,
} from "@clerk/nextjs";
import "./globals.css";

export const metadata: Metadata = {
  title: "Clerk Next.js Quickstart",
  description: "Generated by create next app",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>
          <header>
            <SignedOut>
              <SignInButton />
              <SignUpButton />
            </SignedOut>
            <SignedIn>
              <UserButton />
            </SignedIn>
          </header>
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
```

**Protected Route Example:**

```typescript
// app/dashboard/page.tsx
import { auth } from "@clerk/nextjs/server";
import { currentUser } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";

export default async function DashboardPage() {
  const { userId } = await auth();

  if (!userId) {
    redirect('/sign-in');
  }

  const user = await currentUser();

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Welcome, {user?.firstName} {user?.lastName}</p>
      <p>Email: {user?.emailAddresses[0]?.emailAddress}</p>
    </div>
  );
}
```

#### 2. Client Components (User Interface)

**Sign In Component:**

```typescript
// components/sign-in.tsx
'use client';

import { SignIn } from '@clerk/nextjs';

export default function SignInPage() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <SignIn />
    </div>
  );
}
```

**Sign Up Component:**

```typescript
// components/sign-up.tsx
'use client';

import { SignUp } from '@clerk/nextjs';

export default function SignUpPage() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <SignUp />
    </div>
  );
}
```

**User Button (Profile Menu):**

```typescript
// components/user-button.tsx
'use client';

import { UserButton } from '@clerk/nextjs';

export default function UserButtonComponent() {
  return <UserButton afterSignOutUrl="/" />;
}
```

**Use Auth Hook:**

```typescript
// components/protected-content.tsx
'use client';

import { useAuth, useUser } from '@clerk/nextjs';

export default function ProtectedContent() {
  const { isSignedIn, userId } = useAuth();
  const { user } = useUser();

  if (!isSignedIn) {
    return <div>Please sign in</div>;
  }

  return (
    <div>
      <p>User ID: {userId}</p>
      <p>Email: {user?.emailAddresses[0]?.emailAddress}</p>
    </div>
  );
}
```

#### 3. API Routes (Server-side)

**Protected API Route:**

```typescript
// app/api/protected/route.ts
import { auth } from "@clerk/nextjs/server";
import { currentUser } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

export async function GET() {
  const { userId } = await auth();

  if (!userId) {
    return NextResponse.json(
      { error: "Unauthorized" },
      { status: 401 }
    );
  }

  const user = await currentUser();

  return NextResponse.json({
    message: "Protected data",
    userId,
    userEmail: user?.emailAddresses[0]?.emailAddress,
  });
}
```

**API Route with User Data:**

```typescript
// app/api/user/route.ts
import { currentUser } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

export async function GET() {
  const user = await currentUser();

  if (!user) {
    return NextResponse.json(
      { error: "Not authenticated" },
      { status: 401 }
    );
  }

  return NextResponse.json({
    id: user.id,
    firstName: user.firstName,
    lastName: user.lastName,
    email: user.emailAddresses[0]?.emailAddress,
    imageUrl: user.imageUrl,
  });
}
```

#### 4. Outdated Patterns to Avoid

**DO NOT use these deprecated patterns:**

```typescript
// DO NOT use authMiddleware() - it's replaced by clerkMiddleware()
import { authMiddleware } from "@clerk/nextjs"; // Outdated

// DO NOT place Clerk config in _app.tsx (Pages Router approach)
// This is for the old Pages Router, not App Router
function MyApp({ Component, pageProps }) {
  // ...
}

// DO NOT create sign-in files under pages/ directory
// Use App Router with Clerk components instead
```

### Webhooks (Next.js App Router)

```typescript
// app/api/webhooks/clerk/route.ts
import { Webhook } from "svix";
import { headers } from "next/headers";
import { WebhookEvent } from "@clerk/nextjs/server";

export async function POST(req: Request) {
  const WEBHOOK_SECRET = process.env.CLERK_WEBHOOK_SECRET;
  if (!WEBHOOK_SECRET) throw new Error("Missing CLERK_WEBHOOK_SECRET");

  const headerPayload = headers();
  const svix_id = headerPayload.get("svix-id");
  const svix_timestamp = headerPayload.get("svix-timestamp");
  const svix_signature = headerPayload.get("svix-signature");

  const body = await req.text();
  const wh = new Webhook(WEBHOOK_SECRET);
  const evt = wh.verify(body, {
    "svix-id": svix_id!,
    "svix-timestamp": svix_timestamp!,
    "svix-signature": svix_signature!,
  }) as WebhookEvent;

  // Handle event
  switch (evt.type) {
    case "user.created":
      // Sync to database
      break;
  }

  return new Response("OK", { status: 200 });
}
```

### NestJS Implementation

#### 1. Module Setup

```typescript
// src/clerk/clerk.module.ts
import { Module, Global } from '@nestjs/common';
import { ClerkService } from './clerk.service';

@Global()
@Module({
  providers: [ClerkService],
  exports: [ClerkService],
})
export class ClerkModule {}
```

#### 2. Clerk Service

```typescript
// src/clerk/clerk.service.ts
import { Injectable } from '@nestjs/common';
import { clerkClient } from '@clerk/clerk-sdk-node';

@Injectable()
export class ClerkService {
  private clerk = clerkClient;

  getClerk() {
    return this.clerk;
  }

  async getUser(userId: string) {
    return await this.clerk.users.getUser(userId);
  }

  async updateUser(userId: string, data: any) {
    return await this.clerk.users.updateUser(userId, data);
  }

  async deleteUser(userId: string) {
    return await this.clerk.users.deleteUser(userId);
  }
}
```

#### 3. Authentication Guard

```typescript
// src/clerk/clerk.guard.ts
import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
} from '@nestjs/common';
import { clerkClient } from '@clerk/clerk-sdk-node';

@Injectable()
export class ClerkGuard implements CanActivate {
  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const token = this.extractTokenFromHeader(request);

    if (!token) {
      throw new UnauthorizedException('No token provided');
    }

    try {
      const { userId } = await clerkClient.verifyToken(token);
      request.userId = userId;

      // Optionally fetch full user object
      const user = await clerkClient.users.getUser(userId);
      request.user = user;

      return true;
    } catch (error) {
      throw new UnauthorizedException('Invalid token');
    }
  }

  private extractTokenFromHeader(request: any): string | undefined {
    const [type, token] = request.headers.authorization?.split(' ') ?? [];
    return type === 'Bearer' ? token : undefined;
  }
}
```

#### 4. Custom Decorator for User

```typescript
// src/clerk/current-user.decorator.ts
import { createParamDecorator, ExecutionContext } from '@nestjs/common';

export const CurrentUser = createParamDecorator(
  (data: unknown, ctx: ExecutionContext) => {
    const request = ctx.switchToHttp().getRequest();
    return request.user;
  },
);

export const CurrentUserId = createParamDecorator(
  (data: unknown, ctx: ExecutionContext) => {
    const request = ctx.switchToHttp().getRequest();
    return request.userId;
  },
);
```

#### 5. Controller with Authentication

```typescript
// src/users/users.controller.ts
import { Controller, Get, UseGuards } from '@nestjs/common';
import { ClerkGuard } from '../clerk/clerk.guard';
import { CurrentUser, CurrentUserId } from '../clerk/current-user.decorator';
import { ClerkService } from '../clerk/clerk.service';

@Controller('users')
@UseGuards(ClerkGuard)
export class UsersController {
  constructor(private clerkService: ClerkService) {}

  @Get('me')
  async getCurrentUser(@CurrentUserId() userId: string) {
    return await this.clerkService.getUser(userId);
  }

  @Get('profile')
  async getProfile(@CurrentUser() user: any) {
    return {
      id: user.id,
      firstName: user.firstName,
      lastName: user.lastName,
      email: user.emailAddresses[0]?.emailAddress,
    };
  }
}
```

#### 6. Webhook Handler

```typescript
// src/clerk/clerk.webhook.controller.ts
import { Controller, Post, Body, Headers, HttpCode, HttpStatus } from '@nestjs/common';
import { Webhook } from 'svix';
import { clerkClient } from '@clerk/clerk-sdk-node';

@Controller('webhooks/clerk')
export class ClerkWebhookController {
  @Post()
  @HttpCode(HttpStatus.OK)
  async handleWebhook(
    @Body() body: any,
    @Headers('svix-id') svixId: string,
    @Headers('svix-timestamp') svixTimestamp: string,
    @Headers('svix-signature') svixSignature: string,
  ) {
    const webhookSecret = process.env.CLERK_WEBHOOK_SECRET!;

    const wh = new Webhook(webhookSecret);

    let evt: any;

    try {
      evt = wh.verify(JSON.stringify(body), {
        'svix-id': svixId,
        'svix-timestamp': svixTimestamp,
        'svix-signature': svixSignature,
      });
    } catch (err) {
      throw new Error('Webhook verification failed');
    }

    const { id, ...attributes } = evt.data;
    const eventType = evt.type;

    switch (eventType) {
      case 'user.created':
        // Handle user creation
        console.log('User created:', id);
        break;

      case 'user.updated':
        // Handle user update
        console.log('User updated:', id);
        break;

      case 'user.deleted':
        // Handle user deletion
        console.log('User deleted:', id);
        break;

      default:
        console.log(`Unhandled event type: ${eventType}`);
    }

    return { received: true };
  }
}
```

### Organization/Team Features

#### 1. Create Organization (Next.js)

```typescript
// app/api/organizations/route.ts
import { auth } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";
import { clerkClient } from "@clerk/clerk-sdk-node";

export async function POST(request: Request) {
  const { userId } = await auth();

  if (!userId) {
    return NextResponse.json(
      { error: "Unauthorized" },
      { status: 401 }
    );
  }

  const { name } = await request.json();

  const organization = await clerkClient.organizations.createOrganization({
    name,
    createdBy: userId,
  });

  return NextResponse.json({ organizationId: organization.id });
}
```

#### 2. Organization Membership (Next.js)

```typescript
// components/organization-switcher.tsx
'use client';

import { OrganizationSwitcher } from '@clerk/nextjs';

export default function OrganizationSwitcherComponent() {
  return (
    <OrganizationSwitcher
      afterCreateOrganizationUrl="/dashboard"
      afterSelectOrganizationUrl="/dashboard"
    />
  );
}
```

#### 3. Organization Guard (NestJS)

```typescript
// src/clerk/organization.guard.ts
import {
  Injectable,
  CanActivate,
  ExecutionContext,
  ForbiddenException,
} from '@nestjs/common';
import { clerkClient } from '@clerk/clerk-sdk-node';

@Injectable()
export class OrganizationGuard implements CanActivate {
  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const userId = request.userId;
    const organizationId = request.params.organizationId || request.body.organizationId;

    if (!organizationId) {
      throw new ForbiddenException('Organization ID required');
    }

    const memberships = await clerkClient.users.getOrganizationMembershipList({
      userId,
    });

    const hasAccess = memberships.some(
      (m) => m.organization.id === organizationId
    );

    if (!hasAccess) {
      throw new ForbiddenException('Not a member of this organization');
    }

    request.organizationId = organizationId;
    return true;
  }
}
```

### Best Practices

#### Security

- Always verify tokens on the server side
- Use HTTPS for all authentication flows
- Store secrets in environment variables
- Implement proper error handling
- Validate user permissions before actions

#### Session Management

- Use Clerk's built-in session management
- Implement proper logout flows
- Handle token refresh automatically
- Use middleware for route protection

#### User Management

- Sync user data with your database when needed
- Handle webhooks for user lifecycle events
- Implement proper user data validation
- Respect user privacy and data protection

#### Organization Management

- Implement proper organization access controls
- Use organization guards for multi-tenant features
- Handle organization membership changes via webhooks
- Implement proper organization data isolation

#### Error Handling

- Provide clear error messages
- Handle authentication failures gracefully
- Implement proper logging for security events
- Handle edge cases (expired tokens, revoked access)

### Common Clerk Events

- `user.created` - New user signed up
- `user.updated` - User profile updated
- `user.deleted` - User account deleted
- `session.created` - New session started
- `session.ended` - Session ended
- `organization.created` - New organization created
- `organizationMembership.created` - User joined organization
- `organizationMembership.deleted` - User left organization
