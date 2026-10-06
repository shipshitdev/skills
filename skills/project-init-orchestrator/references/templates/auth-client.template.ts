/**
 * Better Auth Browser Client Template
 *
 * Place this at: frontend/apps/dashboard/lib/auth-client.ts
 *
 * Better Auth runs inside the API (default base path: /api/auth). The session lives in an
 * HTTP-only cookie, so serve the dashboard and the API from the same parent domain in
 * production (or proxy /api/auth through the dashboard).
 */

import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3001",
});

export const { signIn, signOut, signUp, useSession } = authClient;
