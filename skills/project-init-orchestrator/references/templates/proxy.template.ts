/**
 * Next.js proxy.ts Template for Better Auth (Next.js 16)
 *
 * Place this at: frontend/apps/dashboard/proxy.ts
 *
 * Next.js 16 renamed middleware.ts to proxy.ts. The check is optimistic: it only looks for
 * the Better Auth session cookie. The API's AuthGuard is what actually enforces access.
 */

import { getSessionCookie } from "better-auth/cookies";
import { type NextRequest, NextResponse } from "next/server";

// Routes that do not require a session
const PUBLIC_PATHS = ["/", "/sign-in", "/sign-up"];

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (PUBLIC_PATHS.includes(pathname) || getSessionCookie(request)) {
    return NextResponse.next();
  }

  const signIn = new URL("/sign-in", request.url);
  signIn.searchParams.set("next", pathname);
  return NextResponse.redirect(signIn);
}

export const config = {
  // Skip Next.js internals, API routes and files with an extension
  matcher: ["/((?!_next|api|.*\\..*).*)"],
};
