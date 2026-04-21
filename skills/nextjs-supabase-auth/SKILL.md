---
name: nextjs-supabase-auth
description: "Expert integration of Supabase Auth with Next.js App Router. Covers browser/server client setup, auth middleware, OAuth callback routes, Server Actions for login/logout, and common validation checks. Use when implementing auth in a Next.js + Supabase project."
license: Apache-2.0
metadata:
  version: "1.0.0"
  tags: "nextjs, supabase, auth, middleware, oauth, server-actions"
  author: "antigravity-awesome-skills"
---

# Next.js + Supabase Auth

Expert integration of Supabase Auth with Next.js App Router.

## Prerequisites

- Next.js App Router project
- Supabase project with auth enabled
- `@supabase/ssr` package installed

## Patterns

### Supabase Client Setup

**Browser client** (`lib/supabase/client.ts`):

```typescript
'use client'
import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

**Server client** (`lib/supabase/server.ts`):

```typescript
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createClient() {
  const cookieStore = await cookies()
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() { return cookieStore.getAll() },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => {
            cookieStore.set(name, value, options)
          })
        },
      },
    }
  )
}
```

### Auth Middleware

Protect routes and refresh sessions (`middleware.ts`):

```typescript
import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({ request })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() { return request.cookies.getAll() },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => {
            response.cookies.set(name, value, options)
          })
        },
      },
    }
  )

  const { data: { user } } = await supabase.auth.getUser()

  if (request.nextUrl.pathname.startsWith('/dashboard') && !user) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return response
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
```

### Auth Callback Route

Handle OAuth redirects (`app/auth/callback/route.ts`):

```typescript
import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')
  const next = searchParams.get('next') ?? '/'

  if (code) {
    const supabase = await createClient()
    const { error } = await supabase.auth.exchangeCodeForSession(code)
    if (!error) {
      return NextResponse.redirect(`${origin}${next}`)
    }
  }

  return NextResponse.redirect(`${origin}/auth/error`)
}
```

### Server Action Auth

```typescript
'use server'
import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import { revalidatePath } from 'next/cache'

export async function signIn(formData: FormData) {
  const supabase = await createClient()
  const { error } = await supabase.auth.signInWithPassword({
    email: formData.get('email') as string,
    password: formData.get('password') as string,
  })

  if (error) return { error: error.message }

  revalidatePath('/', 'layout')
  redirect('/dashboard')
}

export async function signOut() {
  const supabase = await createClient()
  await supabase.auth.signOut()
  revalidatePath('/', 'layout')
  redirect('/')
}
```

### Get User in Server Component

```typescript
import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) redirect('/login')

  return <div><h1>Welcome, {user.email}</h1></div>
}
```

## Validation Checks

- **Never** use `getSession()` for auth checks — use `getUser()` (JWT verification)
- OAuth requires `app/auth/callback/route.ts` to handle code exchange
- Never use browser client in server context
- Add `revalidatePath('/', 'layout')` after auth mutations to clear stale cache
- Use `origin` not hardcoded `localhost` for redirect URLs

## When to Use

- Setting up Supabase Auth in a Next.js App Router project
- Implementing login, logout, or OAuth social sign-in
- Protecting routes with middleware
- Rendering user-specific content in Server Components

## Limitations

- Use only when task matches Next.js + Supabase auth scope.
- Do not treat output as a substitute for environment-specific validation or expert review.
