/**
 * Better Auth Service Template
 *
 * Place this at: api/apps/api/src/auth/auth.service.ts
 *
 * Owns the Better Auth instance. main.ts mounts its handler at /api/auth/* with
 * toNodeHandler(app.get(AuthService).auth) before Nest's body parser (bodyParser: false
 * on NestFactory.create, then app.useBodyParser("json")).
 *
 * Better Auth stores users and sessions through Prisma, so the schema needs the User,
 * Session, Account and Verification models the scaffold writes to prisma/schema/auth.prisma.
 */

import { Injectable } from "@nestjs/common";
import { betterAuth } from "better-auth";
import { prismaAdapter } from "better-auth/adapters/prisma";
import { allowedOrigins } from "../config/origins";
import { PrismaService } from "../prisma/prisma.service";

function createAuth(prisma: PrismaService) {
  // Host-only cookies set by api.example.com never reach example.com. Set COOKIE_DOMAIN
  // (for example .example.com) in production so the dashboard's proxy.ts sees the session.
  // Leave it unset locally: localhost:3000 and localhost:3001 already share cookies.
  const cookieDomain = process.env.COOKIE_DOMAIN;

  return betterAuth({
    database: prismaAdapter(prisma, { provider: "postgresql" }),
    baseURL: process.env.BETTER_AUTH_URL ?? "http://localhost:3001",
    secret: process.env.BETTER_AUTH_SECRET,
    trustedOrigins: allowedOrigins(),
    emailAndPassword: { enabled: true },
    advanced: {
      crossSubDomainCookies: cookieDomain
        ? { enabled: true, domain: cookieDomain }
        : { enabled: false },
    },
  });
}

@Injectable()
export class AuthService {
  readonly auth: ReturnType<typeof createAuth>;

  constructor(prisma: PrismaService) {
    this.auth = createAuth(prisma);
  }
}
