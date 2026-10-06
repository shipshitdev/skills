#!/usr/bin/env python3
"""
Scaffold a full-stack monorepo workspace with entity generation.

This script creates a complete, working full-stack application with:
- NestJS backend with Prisma/Postgres and Better Auth (email + password)
- Next.js 16 frontend (Tailwind v4 CSS-first) with proxy.ts route protection
- Vitest testing with 80% coverage thresholds
- GitHub Actions CI/CD pipeline
- Biome linting

Usage:
  python3 init-workspace.py --root /path/to/project --name "My App" --org myorg
  python3 init-workspace.py --root /path/to/project --name "TaskFlow" --entities "task,project"
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import re
from pathlib import Path
from textwrap import dedent
from dataclasses import dataclass
from typing import Optional

# Every pinned dependency version lives here so the scaffold stays easy to refresh.
# Looked up with `npm view <pkg> version` on 2026-10-06. Deliberate deviations from the
# newest release are noted inline.
V = {
    # NestJS 12 (same line as the house repos; 11 is now the `legacy` dist-tag)
    "nestjs": "12.1.2",
    "nestjs-config": "12.0.1",
    "nestjs-swagger": "12.0.2",
    "nestjs-cli": "12.0.8",
    "nestjs-schematics": "12.0.6",
    # Prisma 7.10 is the newest stable; `prisma@latest` currently points at an 8.0 release candidate
    "prisma": "7.10.0",
    "better-auth": "1.7.7",
    "reflect-metadata": "0.2.2",
    "rxjs": "7.8.2",
    "class-validator": "0.15.1",
    "class-transformer": "0.5.1",
    "types-express": "5.0.6",
    "types-node": "26.6.4",
    # TypeScript 6.0: @nestjs/swagger 12 and the Next.js type checker do not support 7.x yet
    "typescript": "6.0.3",
    "biome": "2.5.15",
    "dotenv": "18.0.5",
    "unplugin-swc": "2.0.0",
    "swc-core": "1.16.13",
    "vitest": "5.0.3",
    "vite": "8.3.3",
    "next": "16.3.8",
    "react": "19.3.0",
    "types-react": "19.3.0",
    "axios": "1.20.0",
    "zustand": "5.0.15",
    "react-hook-form": "7.89.0",
    "zod": "4.6.5",
    "hookform-resolvers": "5.9.1",
    "lucide-react": "1.52.0",
    "tailwindcss": "4.3.3",
    "testing-library-react": "16.3.3",
    "testing-library-dom": "10.4.2",
    "testing-library-jest-dom": "7.0.1",
    "testing-library-user-event": "14.6.7",
    "jsdom": "30.1.2",
    "plugin-react": "6.1.2",
    # Mobile follows Expo SDK 57 (bundledNativeModules.json), not the newest react-native
    "expo": "57.0.26",
    "expo-router": "57.0.24",
    "expo-status-bar": "57.0.1",
    "expo-linking": "57.0.11",
    "expo-constants": "57.0.20",
    "react-native": "0.86.3",
    "expo-react": "19.2.3",
    "expo-types-react": "19.2.18",
    "react-native-safe-area-context": "5.7.0",
    "react-native-screens": "4.26.2",
}

# Better Auth owns these Prisma models, so entities cannot reuse the names.
RESERVED_ENTITY_NAMES = {"user", "session", "account", "verification"}


def dump_json(value: object, indent: int = 0, prefix_len: int = 0) -> str:
    """Serialize JSON the way Biome formats it: 2-space indent, short scalar arrays inline."""
    pad = " " * indent
    inner = " " * (indent + 2)
    if isinstance(value, dict):
        if not value:
            return "{}"
        lines = []
        for key, item in value.items():
            head = f"{json.dumps(key)}: "
            lines.append(f"{inner}{head}{dump_json(item, indent + 2, indent + 2 + len(head))}")
        return "{\n" + ",\n".join(lines) + f"\n{pad}}}"
    if isinstance(value, list):
        if not value:
            return "[]"
        if all(not isinstance(item, (dict, list)) for item in value):
            inline = "[" + ", ".join(json.dumps(item) for item in value) + "]"
            if prefix_len + len(inline) + 1 <= 100:
                return inline
        items = [f"{inner}{dump_json(item, indent + 2, indent + 2)}" for item in value]
        return "[\n" + ",\n".join(items) + f"\n{pad}]"
    return json.dumps(value)


@dataclass
class EntityField:
    """Represents a field in an entity schema."""
    name: str
    type: str  # string, number, boolean, date, enum, array
    required: bool = True
    default: Optional[str] = None
    enum_values: Optional[list[str]] = None


@dataclass
class EntityConfig:
    """Configuration for an entity to be generated."""
    name: str  # e.g., "Task"
    fields: list[EntityField]

    @property
    def pascal_case(self) -> str:
        """TaskProject -> TaskProject"""
        return self.name[0].upper() + self.name[1:]

    @property
    def camel_case(self) -> str:
        """TaskProject -> taskProject"""
        return self.name[0].lower() + self.name[1:]

    @property
    def plural(self) -> str:
        """Task -> tasks"""
        name = self.camel_case
        if name.endswith('y'):
            return name[:-1] + 'ies'
        elif name.endswith('s'):
            return name + 'es'
        return name + 's'

    @property
    def plural_pascal(self) -> str:
        """Task -> Tasks"""
        return self.plural[0].upper() + self.plural[1:]


def create_root_package_json(name: str) -> str:
    return dump_json({
        "name": name.lower().replace(" ", "-"),
        "version": "0.0.1",
        "private": True,
        "workspaces": [
            "api",
            "frontend/apps/*",
            "frontend/packages",
            "mobile",
            "packages"
        ],
        "engines": {
            "node": ">=22.12.0"
        },
        "scripts": {
            "dev:api": "cd api && bun run start:dev",
            "dev:frontend": "cd frontend && bun run dev",
            "dev:mobile": "cd mobile && bun run start",
            "prisma:generate": "cd api && bun run prisma:generate",
            "lint": "biome check .",
            "lint:fix": "biome check --write .",
            "test": "bun run test:api && bun run test:frontend",
            "test:api": "cd api && bun run test",
            "test:frontend": "cd frontend && bun run test",
            "typecheck": "cd api && bun run typecheck && cd ../frontend && bun run typecheck && cd ../mobile && bun run typecheck"
        },
        "devDependencies": {
            "@biomejs/biome": V["biome"]
        }
    })


def create_npmrc() -> str:
    return "engine-strict=true\n"


def create_gitignore() -> str:
    return dedent("""\
        # Dependencies
        node_modules/
        .pnp
        .pnp.js

        # Build
        dist/
        build/
        .next/
        out/
        *.tsbuildinfo
        next-env.d.ts

        # Environment
        .env
        .env.local
        .env.*.local

        # Logs
        logs/
        *.log
        npm-debug.log*

        # OS
        .DS_Store
        Thumbs.db

        # IDE
        .idea/
        .vscode/
        *.swp
        *.swo

        # Test
        coverage/

        # Generated Prisma client
        api/apps/api/src/generated/

        # Expo
        .expo/

        # Misc
        .vercel
        .turbo
    """)


def create_readme(name: str) -> str:
    return dedent(f"""\
        # {name}

        Full-stack monorepo workspace.

        ## Structure

        - `api/` - NestJS backend (Prisma + Postgres, Better Auth)
        - `frontend/` - Next.js apps (`frontend/apps/dashboard`) and shared packages
        - `mobile/` - React Native + Expo
        - `packages/` - Shared packages

        ## Getting Started

        ```bash
        bun install
        cp .env.example api/.env        # set DATABASE_URL and BETTER_AUTH_SECRET
        cp .env.example frontend/apps/dashboard/.env.local
        cd api && bun run prisma:migrate  # creates the first migration (auth tables + entities)
        bun run prisma:generate           # builds the Prisma client; migrate no longer does (Prisma 7)
        cd .. && bun run lint:fix         # formats the generated files once; commit the result
        ```

        Re-run `bun run prisma:generate` after every schema change (also from the workspace root).

        ## Development

        ```bash
        # Backend (http://localhost:3001, Swagger at /api/docs)
        bun run dev:api

        # Frontend (http://localhost:3000)
        bun run dev:frontend

        # Mobile
        bun run dev:mobile
        ```

        ## Authentication

        Better Auth runs inside the API at `/api/auth/*` (email + password, sessions in Postgres).
        The dashboard signs in through `better-auth/react` and `frontend/apps/dashboard/proxy.ts`
        redirects visitors without a session cookie to `/sign-in`. That check is optimistic; the
        API's `AuthGuard` is what enforces access. When the dashboard and API sit on sibling
        subdomains in production (`example.com` and `api.example.com`), set `COOKIE_DOMAIN`
        (for example `.example.com`) on the API so the session cookie is shared.

        ## Quality

        ```bash
        bun run lint
        bun run typecheck
        bun run test
        ```

        ## Documentation

        See `.agents/README.md` for AI documentation.
    """)


def create_agents_md(name: str) -> str:
    return dedent(f"""\
        # {name}

        Shared project instructions for AI agents, including Codex. Documentation in `.agents/`.

        ## Projects

        - `api/` - NestJS backend → `api/.agents/`
        - `frontend/` - NextJS apps → `frontend/.agents/`
        - `mobile/` - React Native → `mobile/.agents/`
        - `packages/` - Shared → `packages/.agents/`

        ## Context

        Durable project facts live in `.agents/memory/`. Session logs are in `.agents/sessions/`.
    """)


def create_claude_md(name: str) -> str:
    return dedent(f"""\
        # {name}

        Claude-specific additions. Read `AGENTS.md` first for shared project instructions.

        ## Commands

        ```bash
        bun run dev:api      # Start backend
        bun run dev:frontend # Start frontend
        bun run dev:mobile   # Start mobile
        ```

        ## Project Context

        Durable project facts live in `.agents/memory/`. Session logs are in `.agents/sessions/`.
    """)


# API Templates
def create_api_package_json(org: str) -> str:
    return dump_json({
        "name": f"@{org}/api",
        "version": "0.0.1",
        "private": True,
        "engines": {
            "node": ">=22.12.0"
        },
        "scripts": {
            "build": "bunx --bun prisma generate && nest build",
            "start": "nest start",
            "start:dev": "nest start --watch",
            "start:debug": "nest start --debug --watch",
            "start:prod": "node dist/main.js",
            "prisma:generate": "bunx --bun prisma generate",
            "prisma:migrate": "bunx --bun prisma migrate dev",
            "prisma:deploy": "bunx --bun prisma migrate deploy",
            "lint": "biome check .",
            "lint:fix": "biome check --write .",
            "typecheck": "tsc --noEmit",
            "test": "vitest run",
            "test:watch": "vitest",
            "test:coverage": "vitest run --coverage"
        },
        "dependencies": {
            "@nestjs/common": V["nestjs"],
            "@nestjs/core": V["nestjs"],
            "@nestjs/config": V["nestjs-config"],
            "@nestjs/platform-express": V["nestjs"],
            "@nestjs/swagger": V["nestjs-swagger"],
            "@prisma/client": V["prisma"],
            "@prisma/adapter-pg": V["prisma"],
            "better-auth": V["better-auth"],
            "reflect-metadata": V["reflect-metadata"],
            "rxjs": V["rxjs"],
            "class-validator": V["class-validator"],
            "class-transformer": V["class-transformer"]
        },
        "devDependencies": {
            "@nestjs/cli": V["nestjs-cli"],
            "@nestjs/schematics": V["nestjs-schematics"],
            "@nestjs/testing": V["nestjs"],
            "@types/express": V["types-express"],
            "@types/node": V["types-node"],
            "typescript": V["typescript"],
            "prisma": V["prisma"],
            "dotenv": V["dotenv"],
            "unplugin-swc": V["unplugin-swc"],
            "@swc/core": V["swc-core"],
            "vitest": V["vitest"],
            "@vitest/coverage-v8": V["vitest"]
        }
    })


def create_nest_cli_json() -> str:
    return dump_json({
        "$schema": "https://json.schemastore.org/nest-cli",
        "collection": "@nestjs/schematics",
        "sourceRoot": "apps/api/src",
        "entryFile": "main",
        "compilerOptions": {
            "deleteOutDir": True,
            "tsConfigPath": "tsconfig.build.json"
        }
    })


def create_api_tsconfig() -> str:
    # TypeScript 6 no longer auto-includes @types/*, so list the ambient types explicitly.
    # moduleResolution "bundler" lets the CommonJS output import ESM-only packages
    # (NestJS 12, Better Auth), which Node 22.12+ loads through require(esm).
    return dump_json({
        "compilerOptions": {
            "module": "commonjs",
            "moduleResolution": "bundler",
            "target": "ES2022",
            "lib": ["ES2022"],
            "types": ["node"],
            "strict": True,
            "strictPropertyInitialization": False,
            "emitDecoratorMetadata": True,
            "experimentalDecorators": True,
            "esModuleInterop": True,
            "resolveJsonModule": True,
            "skipLibCheck": True,
            "sourceMap": True,
            "incremental": True,
            "noEmit": True,
            "forceConsistentCasingInFileNames": True,
            "noFallthroughCasesInSwitch": True
        },
        "include": ["apps/**/*.ts", "prisma.config.ts", "vitest.config.mts"],
        "exclude": ["node_modules", "dist"]
    })


def create_api_tsconfig_build() -> str:
    return dump_json({
        "extends": "./tsconfig.json",
        "compilerOptions": {
            "noEmit": False,
            "outDir": "./dist",
            "rootDir": "./apps/api/src",
            "tsBuildInfoFile": "./dist/.tsbuildinfo"
        },
        "include": ["apps/api/src/**/*.ts"],
        "exclude": ["node_modules", "dist", "**/*.spec.ts"]
    })


def create_api_main_ts() -> str:
    return dedent("""\
        import { ValidationPipe } from "@nestjs/common";
        import { NestFactory } from "@nestjs/core";
        import type { NestExpressApplication } from "@nestjs/platform-express";
        import { DocumentBuilder, SwaggerModule } from "@nestjs/swagger";
        import { toNodeHandler } from "better-auth/node";
        import { AppModule } from "./app.module";
        import { AuthService } from "./auth/auth.service";
        import { allowedOrigins } from "./config/origins";

        async function bootstrap() {
          // Better Auth parses its own request bodies, so Nest's body parser is attached
          // after the auth handler is mounted.
          const app = await NestFactory.create<NestExpressApplication>(AppModule, {
            bodyParser: false,
          });

          // CORS with credentials so the apps in FRONTEND_URLS can send the session cookie
          app.enableCors({
            origin: allowedOrigins(),
            credentials: true,
          });

          // Better Auth endpoints: /api/auth/*
          app
            .getHttpAdapter()
            .getInstance()
            .all("/api/auth/*splat", toNodeHandler(app.get(AuthService).auth));

          app.useBodyParser("json");

          // Validation
          app.useGlobalPipes(
            new ValidationPipe({
              whitelist: true,
              transform: true,
            }),
          );

          // Swagger
          const config = new DocumentBuilder()
            .setTitle("API")
            .setDescription("API Documentation")
            .setVersion("1.0")
            .addCookieAuth("better-auth.session_token")
            .build();
          const document = SwaggerModule.createDocument(app, config);
          SwaggerModule.setup("api/docs", app, document);

          const port = process.env.PORT || 3001;
          await app.listen(port);
          console.log(`API running on http://localhost:${port}`);
        }
        bootstrap();
    """)


def create_api_origins_ts() -> str:
    return dedent("""\
        const DEFAULT_ORIGIN = "http://localhost:3000";

        /**
         * Origins of the frontend apps allowed to call the API. Used for both CORS and Better
         * Auth trustedOrigins. FRONTEND_URLS is a comma-separated list; FRONTEND_URL (a single
         * origin) is still accepted as a fallback.
         */
        export function allowedOrigins(env: NodeJS.ProcessEnv = process.env): string[] {
          const raw = env.FRONTEND_URLS || env.FRONTEND_URL || DEFAULT_ORIGIN;
          const origins = raw
            .split(",")
            .map((origin) => origin.trim().replace(/\\/+$/, ""))
            .filter(Boolean);

          return origins.length > 0 ? origins : [DEFAULT_ORIGIN];
        }
    """)


def create_api_origins_spec() -> str:
    return dedent("""\
        import { describe, expect, it } from "vitest";
        import { allowedOrigins } from "./origins";

        describe("allowedOrigins", () => {
          it("defaults to the local dashboard", () => {
            expect(allowedOrigins({})).toEqual(["http://localhost:3000"]);
          });

          it("splits a comma-separated FRONTEND_URLS and trims entries", () => {
            expect(
              allowedOrigins({ FRONTEND_URLS: "http://localhost:3000, http://localhost:3002/ ," }),
            ).toEqual(["http://localhost:3000", "http://localhost:3002"]);
          });

          it("falls back to the single FRONTEND_URL", () => {
            expect(allowedOrigins({ FRONTEND_URL: "https://app.example.com" })).toEqual([
              "https://app.example.com",
            ]);
          });

          it("prefers FRONTEND_URLS over FRONTEND_URL", () => {
            expect(
              allowedOrigins({ FRONTEND_URLS: "https://a.example.com", FRONTEND_URL: "https://b.example.com" }),
            ).toEqual(["https://a.example.com"]);
          });

          it("ignores an empty FRONTEND_URLS", () => {
            expect(allowedOrigins({ FRONTEND_URLS: " , ", FRONTEND_URL: "" })).toEqual([
              "http://localhost:3000",
            ]);
          });
        });
    """)


def create_api_app_module_ts() -> str:
    return dedent("""\
        import { Module } from "@nestjs/common";
        import { ConfigModule } from "@nestjs/config";
        import { AuthModule } from "./auth/auth.module";
        import { PrismaModule } from "./prisma/prisma.module";

        @Module({
          imports: [
            ConfigModule.forRoot({
              isGlobal: true,
            }),
            PrismaModule,
            AuthModule,
          ],
          controllers: [],
          providers: [],
        })
        export class AppModule {}
    """)


def create_api_dockerignore() -> str:
    """Docker context filter: secrets and local artifacts never enter an image layer."""
    return dedent("""\
        # The Docker context is the workspace root. Never send secrets or local build output.
        .git
        .env*
        !.env.example
        **/.env*
        !**/.env.example
        **/node_modules
        **/dist
        **/build
        **/coverage
        **/.next
        **/.turbo
        **/.expo
        **/*.tsbuildinfo
        **/*.log
    """)


def create_api_dockerfile(org: str) -> str:
    return dedent(f"""\
        # Build from the workspace root so Bun can resolve the workspace lockfile:
        #   docker build -f api/Dockerfile -t api .
        # The root .dockerignore keeps every .env file out of the build context.
        FROM oven/bun:1 AS base
        WORKDIR /app

        # Workspace manifests only, so dependency layers cache until a manifest changes
        FROM base AS manifests
        COPY package.json bun.lock ./
        COPY api/package.json api/package.json
        COPY frontend/apps/dashboard/package.json frontend/apps/dashboard/package.json
        COPY frontend/packages/package.json frontend/packages/package.json
        COPY mobile/package.json mobile/package.json
        COPY packages/package.json packages/package.json

        # All dependencies of the API workspace, for the build
        FROM manifests AS deps
        RUN bun install --frozen-lockfile --filter "@{org}/api"

        # Production dependencies only, for the runtime image
        FROM manifests AS prod-deps
        RUN bun install --frozen-lockfile --production --filter "@{org}/api"

        # Build. prisma generate needs no DATABASE_URL, so nothing secret is required here.
        FROM base AS builder
        COPY --from=deps /app/ ./
        COPY api ./api
        WORKDIR /app/api
        RUN bun run build

        # Production: only the compiled output and production dependencies.
        # The generated Prisma client is compiled into dist/generated, so it ships inside dist.
        FROM node:24-slim AS runner
        ENV NODE_ENV=production
        WORKDIR /app/api
        # Bun's isolated installs keep the packages in /app/node_modules and symlink the API's own
        # dependencies from /app/api/node_modules, so both folders are needed
        COPY --from=prod-deps /app/node_modules /app/node_modules
        COPY --from=prod-deps /app/api/node_modules ./node_modules
        COPY --from=builder /app/api/dist ./dist
        COPY --from=builder /app/api/package.json ./package.json
        EXPOSE 3001
        CMD ["node", "dist/main.js"]
    """)


# Frontend Templates
def create_frontend_package_json(org: str) -> str:
    """Thin package at frontend/ that delegates to the dashboard app."""
    return dump_json({
        "name": f"@{org}/frontend",
        "version": "0.0.1",
        "private": True,
        "scripts": {
            "dev": "cd apps/dashboard && bun run dev",
            "build": "cd apps/dashboard && bun run build",
            "start": "cd apps/dashboard && bun run start",
            "lint": "biome check .",
            "lint:fix": "biome check --write .",
            "typecheck": "cd apps/dashboard && bun run typecheck",
            "test": "cd apps/dashboard && bun run test",
            "test:watch": "cd apps/dashboard && bun run test:watch",
            "test:coverage": "cd apps/dashboard && bun run test:coverage"
        }
    })


def create_frontend_packages_package_json(org: str) -> str:
    """Workspace package for the code shared by every frontend app.

    Bun links dependencies per workspace, so shared code needs its own react entries to
    resolve imports (they point at the same installed copy the apps use).
    """
    return dump_json({
        "name": f"@{org}/frontend-packages",
        "version": "0.0.1",
        "private": True,
        "peerDependencies": {
            "react": V["react"],
            "react-dom": V["react"]
        },
        "devDependencies": {
            "react": V["react"],
            "react-dom": V["react"],
            "@types/react": V["types-react"],
            "@types/react-dom": V["types-react"]
        }
    })


def create_dashboard_package_json(org: str) -> str:
    return dump_json({
        "name": f"@{org}/dashboard",
        "version": "0.0.1",
        "private": True,
        "scripts": {
            "dev": "next dev",
            "build": "next build",
            "start": "next start",
            "lint": "biome check .",
            "lint:fix": "biome check --write .",
            "typecheck": "tsc --noEmit",
            "test": "vitest run",
            "test:watch": "vitest",
            "test:coverage": "vitest run --coverage"
        },
        "dependencies": {
            "next": V["next"],
            "react": V["react"],
            "react-dom": V["react"],
            "better-auth": V["better-auth"],
            "axios": V["axios"],
            "zustand": V["zustand"],
            "react-hook-form": V["react-hook-form"],
            "zod": V["zod"],
            "@hookform/resolvers": V["hookform-resolvers"],
            "lucide-react": V["lucide-react"]
        },
        "devDependencies": {
            "@types/node": V["types-node"],
            "@types/react": V["types-react"],
            "@types/react-dom": V["types-react"],
            "typescript": V["typescript"],
            "tailwindcss": V["tailwindcss"],
            "@tailwindcss/postcss": V["tailwindcss"],
            "vite": V["vite"],
            "vitest": V["vitest"],
            "@vitest/coverage-v8": V["vitest"],
            "@vitejs/plugin-react": V["plugin-react"],
            "@testing-library/react": V["testing-library-react"],
            "@testing-library/dom": V["testing-library-dom"],
            "@testing-library/jest-dom": V["testing-library-jest-dom"],
            "@testing-library/user-event": V["testing-library-user-event"],
            "jsdom": V["jsdom"]
        }
    })


def create_frontend_next_config() -> str:
    return dedent("""\
        import path from "node:path";
        import type { NextConfig } from "next";

        // Shared code lives in ../../packages and Bun hoists node_modules to the workspace root.
        const workspaceRoot = path.join(__dirname, "../../..");

        const nextConfig: NextConfig = {
          reactStrictMode: true,
          turbopack: { root: workspaceRoot },
          outputFileTracingRoot: workspaceRoot,
        };

        export default nextConfig;
    """)


def create_frontend_tsconfig() -> str:
    return dump_json({
        "compilerOptions": {
            "target": "ES2022",
            "lib": ["dom", "dom.iterable", "esnext"],
            "types": ["node"],
            "allowJs": False,
            "skipLibCheck": True,
            "strict": True,
            "noEmit": True,
            "esModuleInterop": True,
            "module": "esnext",
            "moduleResolution": "bundler",
            "resolveJsonModule": True,
            "isolatedModules": True,
            "jsx": "react-jsx",
            "incremental": True,
            "plugins": [{"name": "next"}],
            "paths": {
                "@components/*": ["../../packages/components/*"],
                "@services/*": ["../../packages/services/*"],
                "@hooks/*": ["../../packages/hooks/*"],
                "@interfaces/*": ["../../packages/interfaces/*"],
                "@/*": ["./*"]
            }
        },
        "include": [
            "next-env.d.ts",
            "**/*.ts",
            "**/*.tsx",
            "../../packages/**/*.ts",
            "../../packages/**/*.tsx",
            ".next/types/**/*.ts",
            ".next/dev/types/**/*.ts"
        ],
        "exclude": ["node_modules"]
    })


def create_frontend_layout_tsx() -> str:
    return dedent("""\
        import type { Metadata } from "next";
        import "./globals.css";

        export const metadata: Metadata = {
          title: "Dashboard",
          description: "Application dashboard",
        };

        export default function RootLayout({
          children,
        }: Readonly<{
          children: React.ReactNode;
        }>) {
          return (
            <html lang="en">
              <body>{children}</body>
            </html>
          );
        }
    """)


def create_frontend_page_tsx() -> str:
    return dedent("""\
        import Link from "next/link";

        export default function Home() {
          return (
            <main className="min-h-screen p-8">
              <h1 className="text-4xl font-bold">Dashboard</h1>
              <p className="mt-4 text-muted">Welcome to your dashboard.</p>
              <div className="mt-6 flex gap-4">
                <Link className="underline" href="/sign-in">
                  Sign in
                </Link>
                <Link className="underline" href="/sign-up">
                  Create account
                </Link>
              </div>
            </main>
          );
        }
    """)


def create_frontend_page_spec() -> str:
    return dedent("""\
        import { render, screen } from "@testing-library/react";
        import { describe, expect, it } from "vitest";
        import Home from "./page";

        describe("Home", () => {
          it("renders the dashboard heading and auth links", () => {
            render(<Home />);

            expect(screen.getByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
            expect(screen.getByRole("link", { name: "Sign in" })).toHaveAttribute(
              "href",
              "/sign-in",
            );
            expect(screen.getByRole("link", { name: "Create account" })).toHaveAttribute(
              "href",
              "/sign-up",
            );
          });
        });
    """)


def create_frontend_postcss_config() -> str:
    return dedent("""\
        const config = {
          plugins: {
            "@tailwindcss/postcss": {},
          },
        };

        export default config;
    """)


def create_frontend_globals_css() -> str:
    """Tailwind v4 CSS-first entry: @import plus an @theme block, no tailwind.config.*."""
    return dedent("""\
        @import "tailwindcss";

        /* Tailwind v4 only scans this app by default; the shared workspace package has classes too */
        @source "../../../packages";

        :root {
          --background: oklch(0.99 0 0);
          --foreground: oklch(0.18 0.01 260);
          --muted: oklch(0.5 0.02 260);
          --border: oklch(0.9 0.005 260);
          --primary: oklch(0.55 0.2 260);
          --primary-foreground: oklch(0.99 0 0);
          --danger: oklch(0.55 0.22 27);
        }

        @media (prefers-color-scheme: dark) {
          :root {
            --background: oklch(0.17 0.01 260);
            --foreground: oklch(0.96 0 0);
            --muted: oklch(0.7 0.02 260);
            --border: oklch(0.3 0.01 260);
            --primary: oklch(0.65 0.19 260);
            --primary-foreground: oklch(0.17 0.01 260);
            --danger: oklch(0.7 0.19 27);
          }
        }

        @theme inline {
          --color-background: var(--background);
          --color-foreground: var(--foreground);
          --color-muted: var(--muted);
          --color-border: var(--border);
          --color-primary: var(--primary);
          --color-primary-foreground: var(--primary-foreground);
          --color-danger: var(--danger);
          --font-sans: ui-sans-serif, system-ui, sans-serif;
        }

        @layer base {
          body {
            @apply bg-background font-sans text-foreground antialiased;
          }
        }
    """)


def create_dashboard_vitest_config() -> str:
    return dedent("""\
        import { fileURLToPath } from "node:url";
        import react from "@vitejs/plugin-react";
        import { defineConfig } from "vitest/config";

        const here = (path: string) => fileURLToPath(new URL(path, import.meta.url));

        export default defineConfig({
          plugins: [react()],
          resolve: {
            alias: [
              { find: /^@components\\//, replacement: here("../../packages/components/") },
              { find: /^@services\\//, replacement: here("../../packages/services/") },
              { find: /^@hooks\\//, replacement: here("../../packages/hooks/") },
              { find: /^@interfaces\\//, replacement: here("../../packages/interfaces/") },
              { find: /^@\\//, replacement: here("./") },
            ],
          },
          test: {
            globals: true,
            environment: "jsdom",
            setupFiles: ["./vitest.setup.ts"],
            include: ["**/*.spec.{ts,tsx}"],
            exclude: ["node_modules", ".next"],
            coverage: {
              provider: "v8",
              reporter: ["text", "json", "html", "lcov"],
              include: ["app/**/*.{ts,tsx}", "components/**/*.{ts,tsx}", "proxy.ts"],
              exclude: ["**/*.spec.{ts,tsx}", "**/*.d.ts", "app/layout.tsx"],
              thresholds: {
                lines: 80,
                functions: 80,
                branches: 75,
                statements: 80,
              },
            },
            mockReset: true,
            restoreMocks: true,
          },
        });
    """)


def create_dashboard_vitest_setup() -> str:
    return dedent("""\
        import "@testing-library/jest-dom/vitest";
    """)


def create_dashboard_proxy_ts() -> str:
    return dedent("""\
        import { getSessionCookie } from "better-auth/cookies";
        import { type NextRequest, NextResponse } from "next/server";

        const PUBLIC_PATHS = ["/", "/sign-in", "/sign-up"];

        // Optimistic check: only looks for the Better Auth session cookie. The API's AuthGuard
        // is what actually enforces access.
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
          matcher: ["/((?!_next|api|.*\\\\..*).*)"],
        };
    """)


def create_dashboard_proxy_spec() -> str:
    return dedent("""\
        // @vitest-environment node
        import { NextRequest } from "next/server";
        import { describe, expect, it } from "vitest";
        import { proxy } from "./proxy";

        function request(path: string, cookie?: string) {
          return new NextRequest(`http://localhost:3000${path}`, {
            headers: cookie ? { cookie } : {},
          });
        }

        describe("proxy", () => {
          it("lets public routes through without a session", () => {
            expect(proxy(request("/sign-in")).headers.get("location")).toBeNull();
            expect(proxy(request("/")).headers.get("location")).toBeNull();
          });

          it("redirects visitors without a session cookie to sign-in", () => {
            const response = proxy(request("/tasks"));

            expect(response.status).toBe(307);
            expect(response.headers.get("location")).toBe(
              "http://localhost:3000/sign-in?next=%2Ftasks",
            );
          });

          it("allows requests that carry the session cookie", () => {
            const response = proxy(request("/tasks", "better-auth.session_token=abc"));

            expect(response.headers.get("location")).toBeNull();
          });
        });
    """)


def create_dashboard_auth_client_ts() -> str:
    return dedent("""\
        import { createAuthClient } from "better-auth/react";

        // Better Auth runs inside the API (default base path: /api/auth)
        export const authClient = createAuthClient({
          baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3001",
        });

        export const { signIn, signOut, signUp, useSession } = authClient;
    """)


def create_dashboard_auth_form_tsx() -> str:
    return dedent("""\
        "use client";

        import Link from "next/link";
        import { useRouter } from "next/navigation";
        import { type FormEvent, useState } from "react";
        import { authClient } from "@/lib/auth-client";

        interface AuthFormProps {
          mode: "sign-in" | "sign-up";
          next?: string;
        }

        // Only follow same-site relative paths after signing in
        export function safeNext(next?: string): string {
          if (next?.startsWith("/") && !next.startsWith("//") && !next.includes("\\\\")) {
            return next;
          }
          return "/";
        }

        const inputClass = "w-full rounded-lg border border-border bg-background px-3 py-2";

        export function AuthForm({ mode, next }: AuthFormProps) {
          const router = useRouter();
          const [error, setError] = useState<string | null>(null);
          const [pending, setPending] = useState(false);
          const isSignUp = mode === "sign-up";

          async function handleSubmit(event: FormEvent<HTMLFormElement>) {
            event.preventDefault();
            const form = new FormData(event.currentTarget);
            const name = String(form.get("name") ?? "");
            const email = String(form.get("email") ?? "");
            const password = String(form.get("password") ?? "");

            setPending(true);
            setError(null);
            const { error: authError } = isSignUp
              ? await authClient.signUp.email({ name, email, password })
              : await authClient.signIn.email({ email, password });
            setPending(false);

            if (authError) {
              setError(authError.message ?? "Something went wrong");
              return;
            }

            router.push(safeNext(next));
            router.refresh();
          }

          return (
            <main className="mx-auto flex min-h-screen max-w-sm flex-col justify-center gap-6 p-8">
              <h1 className="text-3xl font-bold">{isSignUp ? "Create account" : "Sign in"}</h1>
              <form className="space-y-4" onSubmit={handleSubmit}>
                {isSignUp && (
                  <div className="space-y-1">
                    <label htmlFor="name" className="text-sm font-medium">
                      Name
                    </label>
                    <input id="name" name="name" required className={inputClass} />
                  </div>
                )}
                <div className="space-y-1">
                  <label htmlFor="email" className="text-sm font-medium">
                    Email
                  </label>
                  <input id="email" name="email" type="email" required className={inputClass} />
                </div>
                <div className="space-y-1">
                  <label htmlFor="password" className="text-sm font-medium">
                    Password
                  </label>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    minLength={8}
                    required
                    className={inputClass}
                  />
                </div>
                {error && (
                  <p role="alert" className="text-sm text-danger">
                    {error}
                  </p>
                )}
                <button
                  type="submit"
                  disabled={pending}
                  className="w-full rounded-lg bg-primary px-3 py-2 font-medium text-primary-foreground disabled:opacity-50"
                >
                  {isSignUp ? "Create account" : "Sign in"}
                </button>
              </form>
              <p className="text-sm text-muted">
                {isSignUp ? "Already have an account? " : "No account yet? "}
                <Link className="underline" href={isSignUp ? "/sign-in" : "/sign-up"}>
                  {isSignUp ? "Sign in" : "Create account"}
                </Link>
              </p>
            </main>
          );
        }
    """)


def create_dashboard_auth_form_spec() -> str:
    return dedent("""\
        import { fireEvent, render, screen, waitFor } from "@testing-library/react";
        import { describe, expect, it, vi } from "vitest";
        import { AuthForm, safeNext } from "./auth-form";

        const mocks = vi.hoisted(() => ({
          push: vi.fn(),
          refresh: vi.fn(),
          signIn: vi.fn(),
          signUp: vi.fn(),
        }));

        vi.mock("next/navigation", () => ({
          useRouter: () => ({ push: mocks.push, refresh: mocks.refresh }),
        }));

        vi.mock("@/lib/auth-client", () => ({
          authClient: {
            signIn: { email: mocks.signIn },
            signUp: { email: mocks.signUp },
          },
        }));

        function fill(label: string, value: string) {
          fireEvent.change(screen.getByLabelText(label), { target: { value } });
        }

        describe("safeNext", () => {
          it("only allows same-site relative paths", () => {
            expect(safeNext("/tasks")).toBe("/tasks");
            expect(safeNext("//evil.example")).toBe("/");
            expect(safeNext("/\\\\evil.example")).toBe("/");
            expect(safeNext("https://evil.example")).toBe("/");
            expect(safeNext(undefined)).toBe("/");
          });
        });

        describe("AuthForm", () => {
          it("signs in and navigates to the requested page", async () => {
            mocks.signIn.mockResolvedValue({ data: {}, error: null });
            render(<AuthForm mode="sign-in" next="/tasks" />);

            fill("Email", "ada@example.com");
            fill("Password", "correct-horse-battery");
            fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

            await waitFor(() => expect(mocks.push).toHaveBeenCalledWith("/tasks"));
            expect(mocks.signIn).toHaveBeenCalledWith({
              email: "ada@example.com",
              password: "correct-horse-battery",
            });
          });

          it("shows the error and stays on the page when sign-in fails", async () => {
            mocks.signIn.mockResolvedValue({ data: null, error: { message: "Invalid credentials" } });
            render(<AuthForm mode="sign-in" />);

            fill("Email", "ada@example.com");
            fill("Password", "wrong-password");
            fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

            expect(await screen.findByRole("alert")).toHaveTextContent("Invalid credentials");
            expect(mocks.push).not.toHaveBeenCalled();
          });

          it("creates an account with a name", async () => {
            mocks.signUp.mockResolvedValue({ data: {}, error: null });
            render(<AuthForm mode="sign-up" />);

            fill("Name", "Ada");
            fill("Email", "ada@example.com");
            fill("Password", "correct-horse-battery");
            fireEvent.click(screen.getByRole("button", { name: "Create account" }));

            await waitFor(() => expect(mocks.push).toHaveBeenCalledWith("/"));
            expect(mocks.signUp).toHaveBeenCalledWith({
              name: "Ada",
              email: "ada@example.com",
              password: "correct-horse-battery",
            });
          });
        });
    """)


def create_dashboard_auth_page_tsx(mode: str) -> str:
    comp = "SignInPage" if mode == "sign-in" else "SignUpPage"
    return dedent(f"""\
        import {{ AuthForm }} from "@/components/auth-form";

        export default async function {comp}({{
          searchParams,
        }}: {{
          searchParams: Promise<{{ next?: string }}>;
        }}) {{
          const {{ next }} = await searchParams;
          return <AuthForm mode="{mode}" next={{next}} />;
        }}
    """)


def create_dashboard_auth_pages_spec() -> str:
    return dedent("""\
        import { render, screen } from "@testing-library/react";
        import { describe, expect, it, vi } from "vitest";
        import SignInPage from "./sign-in/page";
        import SignUpPage from "./sign-up/page";

        vi.mock("@/components/auth-form", () => ({
          AuthForm: ({ mode, next }: { mode: string; next?: string }) => (
            <div data-testid="auth-form" data-mode={mode} data-next={next ?? ""} />
          ),
        }));

        describe("auth pages", () => {
          it("renders the sign-in form and forwards the next param", async () => {
            render(await SignInPage({ searchParams: Promise.resolve({ next: "/tasks" }) }));

            const form = screen.getByTestId("auth-form");
            expect(form).toHaveAttribute("data-mode", "sign-in");
            expect(form).toHaveAttribute("data-next", "/tasks");
          });

          it("renders the sign-up form", async () => {
            render(await SignUpPage({ searchParams: Promise.resolve({}) }));

            expect(screen.getByTestId("auth-form")).toHaveAttribute("data-mode", "sign-up");
          });
        });
    """)


def create_biome_config() -> str:
    """Single root Biome config; nested configs would each need `extends: "//"`."""
    return dump_json({
        "$schema": f"https://biomejs.dev/schemas/{V['biome']}/schema.json",
        "assist": {
            "actions": {
                "source": {
                    "organizeImports": "on"
                }
            }
        },
        "vcs": {
            "enabled": True,
            "clientKind": "git",
            "useIgnoreFile": True
        },
        "files": {
            "ignoreUnknown": True,
            "includes": [
                "**",
                "!**/node_modules",
                "!**/dist",
                "!**/.next",
                "!**/build",
                "!**/coverage",
                "!**/generated",
                "!**/.expo",
                "!**/.agents",
                "!**/next-env.d.ts",
                "!**/bun.lock"
            ]
        },
        "formatter": {
            "enabled": True,
            "indentStyle": "space",
            "indentWidth": 2,
            "lineWidth": 100
        },
        "css": {
            "parser": {
                "tailwindDirectives": True
            }
        },
        "linter": {
            "enabled": True,
            "rules": {
                "preset": "recommended"
            }
        },
        "javascript": {
            # NestJS controllers use parameter decorators (@Body(), @Param(), ...)
            "parser": {
                "unsafeParameterDecoratorsEnabled": True
            },
            "formatter": {
                "quoteStyle": "double",
                "semicolons": "always",
                "trailingCommas": "all"
            }
        },
        "overrides": [
            {
                # NestJS dependency injection reads constructor parameter types at runtime,
                # so those imports must stay value imports
                "includes": ["api/**"],
                "linter": {
                    "rules": {
                        "style": {
                            "useImportType": "off"
                        }
                    }
                }
            }
        ]
    })


# Mobile Templates
def create_mobile_package_json(org: str) -> str:
    # Versions follow Expo SDK 57's bundledNativeModules.json; re-check with `bunx expo install --check`
    return dump_json({
        "name": f"@{org}/mobile",
        "version": "0.0.1",
        "private": True,
        "main": "expo-router/entry",
        "scripts": {
            "start": "expo start",
            "android": "expo start --android",
            "ios": "expo start --ios",
            "web": "expo start --web",
            "typecheck": "tsc --noEmit"
        },
        "dependencies": {
            "expo": V["expo"],
            "expo-router": V["expo-router"],
            "expo-status-bar": V["expo-status-bar"],
            "expo-linking": V["expo-linking"],
            "expo-constants": V["expo-constants"],
            "react": V["expo-react"],
            "react-native": V["react-native"],
            "react-native-safe-area-context": V["react-native-safe-area-context"],
            "react-native-screens": V["react-native-screens"]
        },
        "devDependencies": {
            "@types/react": V["expo-types-react"],
            "typescript": V["typescript"]
        }
    })


def create_mobile_app_json(name: str) -> str:
    slug = name.lower().replace(" ", "-")
    return dump_json({
        "expo": {
            "name": name,
            "slug": slug,
            "version": "1.0.0",
            "scheme": slug,
            "platforms": ["ios", "android"],
            "ios": {
                "supportsTablet": True,
                "bundleIdentifier": f"com.{slug}.app"
            },
            "android": {
                "package": f"com.{slug}.app"
            },
            "experiments": {
                "typedRoutes": True
            }
        }
    })


def create_mobile_tsconfig() -> str:
    return dump_json({
        "extends": "expo/tsconfig.base",
        "compilerOptions": {
            "strict": True,
            "paths": {
                "@/*": ["./*"]
            }
        },
        "include": ["**/*.ts", "**/*.tsx", ".expo/types/**/*.ts", "expo-env.d.ts"]
    })


def create_mobile_layout_tsx() -> str:
    return dedent("""\
        import { Stack } from "expo-router";
        import { StatusBar } from "expo-status-bar";

        export default function RootLayout() {
          return (
            <>
              <Stack>
                <Stack.Screen name="index" options={{ title: "Home" }} />
              </Stack>
              <StatusBar style="auto" />
            </>
          );
        }
    """)


def create_mobile_index_tsx() -> str:
    return dedent("""\
        import { View, Text, StyleSheet } from "react-native";

        export default function Home() {
          return (
            <View style={styles.container}>
              <Text style={styles.title}>Welcome</Text>
              <Text style={styles.subtitle}>Your mobile app is ready.</Text>
            </View>
          );
        }

        const styles = StyleSheet.create({
          container: {
            flex: 1,
            alignItems: "center",
            justifyContent: "center",
            padding: 20,
          },
          title: {
            fontSize: 32,
            fontWeight: "bold",
          },
          subtitle: {
            fontSize: 16,
            color: "#666",
            marginTop: 8,
          },
        });
    """)


# Packages Templates
def create_packages_package_json(org: str) -> str:
    return dump_json({
        "name": f"@{org}/packages",
        "version": "0.0.1",
        "private": True
    })


def create_packages_tsconfig() -> str:
    return dump_json({
        "compilerOptions": {
            "target": "ES2020",
            "module": "ESNext",
            "moduleResolution": "bundler",
            "declaration": True,
            "strict": True,
            "skipLibCheck": True,
            "esModuleInterop": True
        }
    })


# =============================================================================
# ENTITY GENERATION FUNCTIONS
# =============================================================================

def create_default_entity(name: str) -> EntityConfig:
    """Create a default entity configuration with common fields."""
    return EntityConfig(
        name=name,
        fields=[
            EntityField(name="title", type="string", required=True),
            EntityField(name="description", type="string", required=False),
        ]
    )


def generate_entity_controller(entity: EntityConfig) -> str:
    """Generate NestJS controller for an entity."""
    E = entity.pascal_case
    e = entity.camel_case
    es = entity.plural

    return dedent(f"""\
        import {{
          Controller,
          Get,
          Post,
          Body,
          Patch,
          Param,
          Delete,
          UseGuards,
        }} from "@nestjs/common";
        import {{ ApiTags, ApiOperation, ApiCookieAuth }} from "@nestjs/swagger";
        import {{ {E}sService }} from "./{es}.service";
        import {{ Create{E}Dto }} from "./dto/create-{e}.dto";
        import {{ Update{E}Dto }} from "./dto/update-{e}.dto";
        import {{ AuthGuard }} from "../../auth/guards/auth.guard";
        import {{ CurrentUser }} from "../../auth/decorators/current-user.decorator";

        @ApiTags("{es}")
        @ApiCookieAuth()
        @UseGuards(AuthGuard)
        @Controller("{es}")
        export class {E}sController {{
          constructor(private readonly {es}Service: {E}sService) {{}}

          @Post()
          @ApiOperation({{ summary: "Create a new {e}" }})
          create(
            @Body() create{E}Dto: Create{E}Dto,
            @CurrentUser() user: {{ userId: string }},
          ) {{
            return this.{es}Service.create(create{E}Dto, user.userId);
          }}

          @Get()
          @ApiOperation({{ summary: "Get all {es}" }})
          findAll(@CurrentUser() user: {{ userId: string }}) {{
            return this.{es}Service.findAll(user.userId);
          }}

          @Get(":id")
          @ApiOperation({{ summary: "Get a {e} by ID" }})
          findOne(
            @Param("id") id: string,
            @CurrentUser() user: {{ userId: string }},
          ) {{
            return this.{es}Service.findOne(id, user.userId);
          }}

          @Patch(":id")
          @ApiOperation({{ summary: "Update a {e}" }})
          update(
            @Param("id") id: string,
            @Body() update{E}Dto: Update{E}Dto,
            @CurrentUser() user: {{ userId: string }},
          ) {{
            return this.{es}Service.update(id, update{E}Dto, user.userId);
          }}

          @Delete(":id")
          @ApiOperation({{ summary: "Delete a {e}" }})
          remove(
            @Param("id") id: string,
            @CurrentUser() user: {{ userId: string }},
          ) {{
            return this.{es}Service.remove(id, user.userId);
          }}
        }}
    """)


def generate_entity_service(entity: EntityConfig) -> str:
    """Generate NestJS service for an entity (Prisma)."""
    E = entity.pascal_case
    e = entity.camel_case
    es = entity.plural

    return dedent(f"""\
        import {{ Injectable, NotFoundException }} from "@nestjs/common";
        import type {{ {E} }} from "../../generated/prisma/client";
        import {{ PrismaService }} from "../../prisma/prisma.service";
        import {{ Create{E}Dto }} from "./dto/create-{e}.dto";
        import {{ Update{E}Dto }} from "./dto/update-{e}.dto";

        @Injectable()
        export class {E}sService {{
          constructor(private readonly prisma: PrismaService) {{}}

          async create(create{E}Dto: Create{E}Dto, userId: string): Promise<{E}> {{
            return this.prisma.{e}.create({{
              data: {{ ...create{E}Dto, userId }},
            }});
          }}

          async findAll(userId: string): Promise<{E}[]> {{
            return this.prisma.{e}.findMany({{
              where: {{ userId }},
              orderBy: {{ createdAt: "desc" }},
            }});
          }}

          async findOne(id: string, userId: string): Promise<{E}> {{
            const {e} = await this.prisma.{e}.findFirst({{
              where: {{ id, userId }},
            }});

            if (!{e}) {{
              throw new NotFoundException(`{E} with ID ${{id}} not found`);
            }}

            return {e};
          }}

          async update(
            id: string,
            update{E}Dto: Update{E}Dto,
            userId: string,
          ): Promise<{E}> {{
            // updateMany scopes the write to the owner in a single statement
            const result = await this.prisma.{e}.updateMany({{
              where: {{ id, userId }},
              data: update{E}Dto,
            }});

            if (result.count === 0) {{
              throw new NotFoundException(`{E} with ID ${{id}} not found`);
            }}

            return this.findOne(id, userId);
          }}

          async remove(id: string, userId: string): Promise<void> {{
            const result = await this.prisma.{e}.deleteMany({{
              where: {{ id, userId }},
            }});

            if (result.count === 0) {{
              throw new NotFoundException(`{E} with ID ${{id}} not found`);
            }}
          }}
        }}
    """)


def generate_entity_schema(entity: EntityConfig) -> str:
    """Generate the Prisma model file for an entity."""
    E = entity.pascal_case
    es = entity.plural

    prisma_types = {
        "string": "String",
        "number": "Float",
        "boolean": "Boolean",
        "date": "DateTime",
    }

    field_lines = []
    for field in entity.fields:
        prisma_type = prisma_types.get(field.type, "String")
        optional = "" if field.required else "?"
        attrs = ""
        if field.default:
            attrs = f' @default("{field.default}")'
        field_lines.append(f"  {field.name} {prisma_type}{optional}{attrs}")

    fields_str = "\n".join(field_lines)

    return (
        f"model {E} {{\n"
        f"  id        String   @id @default(cuid())\n"
        f"{fields_str}\n"
        f"  userId    String\n"
        f"  createdAt DateTime @default(now())\n"
        f"  updatedAt DateTime @updatedAt\n"
        f"\n"
        f"  @@index([userId, createdAt(sort: Desc)])\n"
        f'  @@map("{es}")\n'
        f"}}\n"
    )


def generate_entity_create_dto(entity: EntityConfig) -> str:
    """Generate Create DTO for an entity."""
    E = entity.pascal_case

    validators = {
        "string": ("IsString", "string"),
        "number": ("IsNumber", "number"),
        "boolean": ("IsBoolean", "boolean"),
        "date": ("IsDateString", "string"),  # ISO date string
    }

    used: set[str] = set()
    field_defs = []
    for field in entity.fields:
        validator, ts_type = validators.get(field.type, ("IsString", "string"))
        decorators = [f"@{validator}()"]
        used.add(validator)
        if not field.required:
            decorators.append("@IsOptional()")
            used.add("IsOptional")

        optional = "" if field.required else "?"
        lines = [f"  {decorator}" for decorator in decorators]
        lines.append(f"  {field.name}{optional}: {ts_type};")
        field_defs.append("\n".join(lines))

    imports = ", ".join(sorted(used))
    fields_str = "\n\n".join(field_defs)

    return (
        f'import {{ {imports} }} from "class-validator";\n'
        f"\n"
        f"export class Create{E}Dto {{\n"
        f"{fields_str}\n"
        f"}}\n"
    )


def generate_entity_update_dto(entity: EntityConfig) -> str:
    """Generate Update DTO for an entity."""
    E = entity.pascal_case
    e = entity.camel_case

    return dedent(f"""\
        import {{ PartialType }} from "@nestjs/swagger";
        import {{ Create{E}Dto }} from "./create-{e}.dto";

        export class Update{E}Dto extends PartialType(Create{E}Dto) {{}}
    """)


def generate_entity_module(entity: EntityConfig) -> str:
    """Generate NestJS module for an entity (PrismaModule is global)."""
    E = entity.pascal_case
    es = entity.plural

    return dedent(f"""\
        import {{ Module }} from "@nestjs/common";
        import {{ {E}sController }} from "./{es}.controller";
        import {{ {E}sService }} from "./{es}.service";

        @Module({{
          controllers: [{E}sController],
          providers: [{E}sService],
          exports: [{E}sService],
        }})
        export class {E}sModule {{}}
    """)


def generate_entity_service_spec(entity: EntityConfig) -> str:
    """Generate Vitest tests for the service."""
    E = entity.pascal_case
    e = entity.camel_case
    es = entity.plural

    return dedent(f"""\
        import {{ describe, it, expect, beforeEach, vi }} from "vitest";
        import {{ Test, TestingModule }} from "@nestjs/testing";
        import {{ NotFoundException }} from "@nestjs/common";
        import {{ PrismaService }} from "../../prisma/prisma.service";
        import {{ {E}sService }} from "./{es}.service";

        describe("{E}sService", () => {{
          let service: {E}sService;

          const prismaMock = {{
            {e}: {{
              create: vi.fn(),
              findMany: vi.fn(),
              findFirst: vi.fn(),
              updateMany: vi.fn(),
              deleteMany: vi.fn(),
            }},
          }};

          const mockUserId = "user-123";
          const mock{E} = {{
            id: "{e}-123",
            title: "Test {E}",
            description: null,
            userId: mockUserId,
            createdAt: new Date(),
            updatedAt: new Date(),
          }};

          beforeEach(async () => {{
            const module: TestingModule = await Test.createTestingModule({{
              providers: [
                {E}sService,
                {{ provide: PrismaService, useValue: prismaMock }},
              ],
            }}).compile();

            service = module.get<{E}sService>({E}sService);
          }});

          it("should be defined", () => {{
            expect(service).toBeDefined();
          }});

          describe("create", () => {{
            it("should create a {e} owned by the user", async () => {{
              prismaMock.{e}.create.mockResolvedValue(mock{E});

              const result = await service.create({{ title: "Test {E}" }}, mockUserId);

              expect(result).toEqual(mock{E});
              expect(prismaMock.{e}.create).toHaveBeenCalledWith({{
                data: {{ title: "Test {E}", userId: mockUserId }},
              }});
            }});
          }});

          describe("findAll", () => {{
            it("should return all {es} for a user", async () => {{
              prismaMock.{e}.findMany.mockResolvedValue([mock{E}]);

              const result = await service.findAll(mockUserId);

              expect(result).toEqual([mock{E}]);
              expect(prismaMock.{e}.findMany).toHaveBeenCalledWith({{
                where: {{ userId: mockUserId }},
                orderBy: {{ createdAt: "desc" }},
              }});
            }});
          }});

          describe("findOne", () => {{
            it("should return a {e} by id", async () => {{
              prismaMock.{e}.findFirst.mockResolvedValue(mock{E});

              const result = await service.findOne("{e}-123", mockUserId);

              expect(result).toEqual(mock{E});
            }});

            it("should throw NotFoundException if {e} not found", async () => {{
              prismaMock.{e}.findFirst.mockResolvedValue(null);

              await expect(
                service.findOne("nonexistent", mockUserId),
              ).rejects.toThrow(NotFoundException);
            }});
          }});

          describe("update", () => {{
            it("should update a {e}", async () => {{
              prismaMock.{e}.updateMany.mockResolvedValue({{ count: 1 }});
              prismaMock.{e}.findFirst.mockResolvedValue({{
                ...mock{E},
                title: "Updated",
              }});

              const result = await service.update(
                "{e}-123",
                {{ title: "Updated" }},
                mockUserId,
              );

              expect(result.title).toBe("Updated");
            }});

            it("should throw NotFoundException if {e} not found", async () => {{
              prismaMock.{e}.updateMany.mockResolvedValue({{ count: 0 }});

              await expect(
                service.update("nonexistent", {{ title: "Updated" }}, mockUserId),
              ).rejects.toThrow(NotFoundException);
            }});
          }});

          describe("remove", () => {{
            it("should delete a {e}", async () => {{
              prismaMock.{e}.deleteMany.mockResolvedValue({{ count: 1 }});

              await expect(
                service.remove("{e}-123", mockUserId),
              ).resolves.not.toThrow();
            }});

            it("should throw NotFoundException if {e} not found", async () => {{
              prismaMock.{e}.deleteMany.mockResolvedValue({{ count: 0 }});

              await expect(
                service.remove("nonexistent", mockUserId),
              ).rejects.toThrow(NotFoundException);
            }});
          }});
        }});
    """)


def generate_entity_controller_spec(entity: EntityConfig) -> str:
    """Generate Vitest tests for the controller (the auth guard is overridden)."""
    E = entity.pascal_case
    e = entity.camel_case
    es = entity.plural

    return dedent(f"""\
        import {{ describe, it, expect, beforeEach, vi }} from "vitest";
        import {{ Test, TestingModule }} from "@nestjs/testing";
        import {{ AuthGuard }} from "../../auth/guards/auth.guard";
        import {{ {E}sController }} from "./{es}.controller";
        import {{ {E}sService }} from "./{es}.service";

        describe("{E}sController", () => {{
          let controller: {E}sController;

          const serviceMock = {{
            create: vi.fn(),
            findAll: vi.fn(),
            findOne: vi.fn(),
            update: vi.fn(),
            remove: vi.fn(),
          }};

          const mockUser = {{ userId: "user-123" }};
          const mock{E} = {{
            id: "{e}-123",
            title: "Test {E}",
            description: null,
            userId: mockUser.userId,
            createdAt: new Date(),
            updatedAt: new Date(),
          }};

          beforeEach(async () => {{
            const module: TestingModule = await Test.createTestingModule({{
              controllers: [{E}sController],
              providers: [{{ provide: {E}sService, useValue: serviceMock }}],
            }})
              .overrideGuard(AuthGuard)
              .useValue({{ canActivate: () => true }})
              .compile();

            controller = module.get<{E}sController>({E}sController);
          }});

          it("creates a {e} for the signed-in user", async () => {{
            serviceMock.create.mockResolvedValue(mock{E});

            const result = await controller.create({{ title: "Test {E}" }}, mockUser);

            expect(result).toEqual(mock{E});
            expect(serviceMock.create).toHaveBeenCalledWith({{ title: "Test {E}" }}, mockUser.userId);
          }});

          it("lists the signed-in user's {es}", async () => {{
            serviceMock.findAll.mockResolvedValue([mock{E}]);

            await expect(controller.findAll(mockUser)).resolves.toEqual([mock{E}]);
            expect(serviceMock.findAll).toHaveBeenCalledWith(mockUser.userId);
          }});

          it("returns a single {e}", async () => {{
            serviceMock.findOne.mockResolvedValue(mock{E});

            await expect(controller.findOne("{e}-123", mockUser)).resolves.toEqual(mock{E});
            expect(serviceMock.findOne).toHaveBeenCalledWith("{e}-123", mockUser.userId);
          }});

          it("updates a {e}", async () => {{
            serviceMock.update.mockResolvedValue({{ ...mock{E}, title: "Updated" }});

            const result = await controller.update("{e}-123", {{ title: "Updated" }}, mockUser);

            expect(result.title).toBe("Updated");
            expect(serviceMock.update).toHaveBeenCalledWith(
              "{e}-123",
              {{ title: "Updated" }},
              mockUser.userId,
            );
          }});

          it("removes a {e}", async () => {{
            serviceMock.remove.mockResolvedValue(undefined);

            await controller.remove("{e}-123", mockUser);

            expect(serviceMock.remove).toHaveBeenCalledWith("{e}-123", mockUser.userId);
          }});
        }});
    """)


def generate_entity_interface(entity: EntityConfig) -> str:
    """Generate TypeScript interface for frontend."""
    E = entity.pascal_case

    ts_types = {
        "number": "number",
        "boolean": "boolean",
        "date": "string",  # ISO date string
    }

    lines = ["  id: string;"]
    for field in entity.fields:
        optional = "" if field.required else "?"
        lines.append(f"  {field.name}{optional}: {ts_types.get(field.type, 'string')};")
    lines += ["  userId: string;", "  createdAt: string;", "  updatedAt: string;"]

    return f"export interface {E} {{\n" + "\n".join(lines) + "\n}\n"


def generate_entity_service_client(entity: EntityConfig) -> str:
    """Generate frontend API service for an entity."""
    E = entity.pascal_case
    e = entity.camel_case
    es = entity.plural

    return dedent(f"""\
        import {{ {E} }} from "@interfaces/{e}.interface";

        const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001";

        interface RequestOptions {{
          signal?: AbortSignal;
        }}

        // Better Auth keeps the session in an HTTP-only cookie set by the API, so requests
        // only need to send credentials; no token handling lives in the browser.
        const jsonHeaders: HeadersInit = {{ "Content-Type": "application/json" }};

        async function handleResponse<T>(response: Response): Promise<T> {{
          if (!response.ok) {{
            const error = await response.json().catch(() => ({{ message: "Request failed" }}));
            throw new Error(error.message || `HTTP ${{response.status}}`);
          }}
          return response.json();
        }}

        export const {E}Service = {{
          async getAll(options?: RequestOptions): Promise<{E}[]> {{
            const response = await fetch(`${{API_URL}}/{es}`, {{
              headers: jsonHeaders,
              credentials: "include",
              signal: options?.signal,
            }});
            return handleResponse<{E}[]>(response);
          }},

          async getById(id: string, options?: RequestOptions): Promise<{E}> {{
            const response = await fetch(`${{API_URL}}/{es}/${{id}}`, {{
              headers: jsonHeaders,
              credentials: "include",
              signal: options?.signal,
            }});
            return handleResponse<{E}>(response);
          }},

          async create(data: Partial<{E}>): Promise<{E}> {{
            const response = await fetch(`${{API_URL}}/{es}`, {{
              method: "POST",
              headers: jsonHeaders,
              credentials: "include",
              body: JSON.stringify(data),
            }});
            return handleResponse<{E}>(response);
          }},

          async update(id: string, data: Partial<{E}>): Promise<{E}> {{
            const response = await fetch(`${{API_URL}}/{es}/${{id}}`, {{
              method: "PATCH",
              headers: jsonHeaders,
              credentials: "include",
              body: JSON.stringify(data),
            }});
            return handleResponse<{E}>(response);
          }},

          async delete(id: string): Promise<void> {{
            const response = await fetch(`${{API_URL}}/{es}/${{id}}`, {{
              method: "DELETE",
              credentials: "include",
            }});
            if (!response.ok) {{
              const error = await response.json().catch(() => ({{ message: "Delete failed" }}));
              throw new Error(error.message);
            }}
          }},
        }};
    """)


def generate_entity_list_component(entity: EntityConfig) -> str:
    """Generate React list component for an entity."""
    E = entity.pascal_case
    e = entity.camel_case
    es = entity.plural

    return dedent(f"""\
        "use client";

        import {{ useEffect, useState }} from "react";
        import {{ {E}Service }} from "@services/{e}.service";
        import {{ {E} }} from "@interfaces/{e}.interface";

        export function {E}List() {{
          const [{es}, set{E}s] = useState<{E}[]>([]);
          const [loading, setLoading] = useState(true);
          const [error, setError] = useState<string | null>(null);

          const fetch{E}s = async () => {{
            try {{
              setLoading(true);
              const controller = new AbortController();
              const data = await {E}Service.getAll({{ signal: controller.signal }});
              set{E}s(data);
              setError(null);
            }} catch (err) {{
              if (err instanceof Error && err.name !== "AbortError") {{
                setError(err.message);
              }}
            }} finally {{
              setLoading(false);
            }}
          }};

          useEffect(() => {{
            const controller = new AbortController();

            {E}Service.getAll({{ signal: controller.signal }})
              .then(set{E}s)
              .catch((err) => {{
                if (err.name !== "AbortError") {{
                  setError(err.message);
                }}
              }})
              .finally(() => setLoading(false));

            return () => controller.abort();
          }}, []);

          const handleDelete = async (id: string) => {{
            try {{
              await {E}Service.delete(id);
              fetch{E}s();
            }} catch (err) {{
              setError(err instanceof Error ? err.message : "Failed to delete");
            }}
          }};

          if (loading) {{
            return (
              <div className="flex items-center justify-center p-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
              </div>
            );
          }}

          if (error) {{
            return (
              <div className="rounded-lg border border-danger p-4 text-danger" role="alert">
                Error: {{error}}
              </div>
            );
          }}

          return (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold">{E}s</h2>
                <button
                  type="button"
                  className="rounded-lg bg-primary px-3 py-2 font-medium text-primary-foreground"
                  onClick={{() => {{
                    window.location.href = "/{es}/new";
                  }}}}
                >
                  Add {E}
                </button>
              </div>

              {{{es}.length === 0 ? (
                <div className="py-8 text-center text-muted">
                  No {es} yet. Create your first one!
                </div>
              ) : (
                <div className="space-y-2">
                  {{{es}.map(({e}) => (
                    <div key={{{e}.id}} className="p-4 border rounded-lg flex justify-between items-center">
                      <div>
                        <h3 className="font-medium">{{{e}.title}}</h3>
                        {{{e}.description && (
                          <p className="text-sm text-muted">{{{e}.description}}</p>
                        )}}
                      </div>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          className="rounded-lg px-3 py-1 hover:bg-border"
                          onClick={{() => {{
                            window.location.href = `/{es}/${{{e}.id}}`;
                          }}}}
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          className="rounded-lg px-3 py-1 hover:bg-border"
                          onClick={{() => handleDelete({e}.id)}}
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  ))}}
                </div>
              )}}
            </div>
          );
        }}
    """)


def generate_entity_page(entity: EntityConfig) -> str:
    """Generate NextJS page for entity list."""
    E = entity.pascal_case
    e = entity.camel_case
    es = entity.plural

    return dedent(f"""\
        import {{ {E}List }} from "@components/{es}/{e}-list";

        export default function {E}sPage() {{
          return (
            <main className="min-h-screen p-8">
              <{E}List />
            </main>
          );
        }}
    """)


def generate_entity_page_spec(entity: EntityConfig) -> str:
    """Generate the Vitest test for the entity list page."""
    E = entity.pascal_case
    e = entity.camel_case
    es = entity.plural

    return dedent(f"""\
        import {{ render, screen }} from "@testing-library/react";
        import {{ describe, expect, it, vi }} from "vitest";
        import {E}sPage from "./page";

        vi.mock("@components/{es}/{e}-list", () => ({{
          {E}List: () => <div data-testid="{e}-list" />,
        }}));

        describe("{E}sPage", () => {{
          it("renders the {e} list", () => {{
            render(<{E}sPage />);

            expect(screen.getByTestId("{e}-list")).toBeInTheDocument();
          }});
        }});
    """)


# =============================================================================
# AUTH GENERATION FUNCTIONS
# =============================================================================

def generate_auth_guard() -> str:
    """Generate the Better Auth session guard for NestJS."""
    return dedent("""\
        import type { IncomingHttpHeaders } from "node:http";
        import {
          CanActivate,
          ExecutionContext,
          Injectable,
          UnauthorizedException,
        } from "@nestjs/common";
        import { fromNodeHeaders } from "better-auth/node";
        import { AuthService } from "../auth.service";
        import type { CurrentUserPayload } from "../decorators/current-user.decorator";

        interface AuthenticatedRequest {
          headers: IncomingHttpHeaders;
          user?: CurrentUserPayload;
        }

        interface CookieResponse {
          append(name: string, value: string): unknown;
        }

        @Injectable()
        export class AuthGuard implements CanActivate {
          constructor(private readonly authService: AuthService) {}

          async canActivate(context: ExecutionContext): Promise<boolean> {
            const http = context.switchToHttp();
            const request = http.getRequest<AuthenticatedRequest>();
            const { headers, response: session } = await this.authService.auth.api.getSession({
              headers: fromNodeHeaders(request.headers),
              returnHeaders: true,
            });

            // Better Auth renews sessions close to expiry (and clears invalid cookies) through
            // Set-Cookie headers. Forward them or the browser keeps the stale cookie.
            const response = http.getResponse<CookieResponse>();
            for (const cookie of headers.getSetCookie()) {
              response.append("Set-Cookie", cookie);
            }

            if (!session) {
              throw new UnauthorizedException("Not signed in");
            }

            request.user = { userId: session.user.id, sessionId: session.session.id };
            return true;
          }
        }
    """)


def generate_auth_guard_spec() -> str:
    return dedent("""\
        import { ExecutionContext, UnauthorizedException } from "@nestjs/common";
        import { describe, expect, it, vi } from "vitest";
        import type { AuthService } from "../auth.service";
        import { AuthGuard } from "./auth.guard";

        const getSession = vi.fn();
        const append = vi.fn();
        const guard = new AuthGuard({ auth: { api: { getSession } } } as unknown as AuthService);

        function contextFor(request: object): ExecutionContext {
          return {
            switchToHttp: () => ({ getRequest: () => request, getResponse: () => ({ append }) }),
          } as unknown as ExecutionContext;
        }

        function sessionResult(response: unknown, cookies: string[] = []) {
          const headers = new Headers();
          for (const cookie of cookies) {
            headers.append("set-cookie", cookie);
          }
          return { headers, response };
        }

        describe("AuthGuard", () => {
          it("attaches the signed-in user to the request", async () => {
            getSession.mockResolvedValue(
              sessionResult({ user: { id: "user-1" }, session: { id: "session-1" } }),
            );
            const request: { headers: Record<string, string>; user?: unknown } = {
              headers: { cookie: "better-auth.session_token=abc" },
            };

            await expect(guard.canActivate(contextFor(request))).resolves.toBe(true);

            expect(request.user).toEqual({ userId: "user-1", sessionId: "session-1" });
          });

          it("asks Better Auth for the response headers", async () => {
            getSession.mockResolvedValue(sessionResult(null));

            await expect(guard.canActivate(contextFor({ headers: {} }))).rejects.toThrow();

            expect(getSession).toHaveBeenCalledWith(
              expect.objectContaining({ returnHeaders: true }),
            );
          });

          it("forwards refreshed session cookies to the client", async () => {
            append.mockClear();
            getSession.mockResolvedValue(
              sessionResult({ user: { id: "user-1" }, session: { id: "session-1" } }, [
                "better-auth.session_token=fresh; Path=/; HttpOnly",
                "better-auth.session_data=data; Path=/; HttpOnly",
              ]),
            );

            await guard.canActivate(contextFor({ headers: {} }));

            expect(append).toHaveBeenCalledTimes(2);
            expect(append).toHaveBeenCalledWith(
              "Set-Cookie",
              "better-auth.session_token=fresh; Path=/; HttpOnly",
            );
          });

          it("rejects requests without a session", async () => {
            getSession.mockResolvedValue(sessionResult(null));

            await expect(guard.canActivate(contextFor({ headers: {} }))).rejects.toThrow(
              UnauthorizedException,
            );
          });
        });
    """)


def generate_auth_service() -> str:
    """Generate the Nest provider that owns the Better Auth instance."""
    return dedent("""\
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
    """)


def generate_auth_service_spec() -> str:
    return dedent("""\
        import { describe, expect, it, vi } from "vitest";
        import type { PrismaService } from "../prisma/prisma.service";
        import { AuthService } from "./auth.service";

        describe("AuthService", () => {
          it("builds a Better Auth instance with an HTTP handler and server API", () => {
            const service = new AuthService({} as PrismaService);

            expect(service.auth.handler).toBeTypeOf("function");
            expect(service.auth.api.getSession).toBeTypeOf("function");
          });

          it("keeps cookies host-only unless COOKIE_DOMAIN is set", () => {
            vi.stubEnv("COOKIE_DOMAIN", "");
            const hostOnly = new AuthService({} as PrismaService);
            vi.stubEnv("COOKIE_DOMAIN", ".example.com");
            const shared = new AuthService({} as PrismaService);
            vi.unstubAllEnvs();

            expect(hostOnly.auth.options.advanced?.crossSubDomainCookies?.enabled).toBe(false);
            expect(shared.auth.options.advanced?.crossSubDomainCookies).toEqual({
              enabled: true,
              domain: ".example.com",
            });
          });
        });
    """)


def generate_auth_module() -> str:
    return dedent("""\
        import { Global, Module } from "@nestjs/common";
        import { AuthService } from "./auth.service";
        import { AuthGuard } from "./guards/auth.guard";

        // Global so feature modules can use @UseGuards(AuthGuard) without importing this module
        @Global()
        @Module({
          providers: [AuthService, AuthGuard],
          exports: [AuthService, AuthGuard],
        })
        export class AuthModule {}
    """)


def create_auth_prisma_models() -> str:
    """Prisma models Better Auth's Prisma adapter reads and writes."""
    return dedent("""\
        // Better Auth tables (email + password). Entities cannot reuse these model names.
        model User {
          id            String    @id
          name          String
          email         String    @unique
          emailVerified Boolean   @default(false)
          image         String?
          createdAt     DateTime  @default(now())
          updatedAt     DateTime  @default(now()) @updatedAt
          sessions      Session[]
          accounts      Account[]

          @@map("user")
        }

        model Session {
          id        String   @id
          expiresAt DateTime
          token     String   @unique
          createdAt DateTime @default(now())
          updatedAt DateTime @updatedAt
          ipAddress String?
          userAgent String?
          userId    String
          user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)

          @@index([userId])
          @@map("session")
        }

        model Account {
          id                    String    @id
          accountId             String
          providerId            String
          userId                String
          user                  User      @relation(fields: [userId], references: [id], onDelete: Cascade)
          accessToken           String?
          refreshToken          String?
          idToken               String?
          accessTokenExpiresAt  DateTime?
          refreshTokenExpiresAt DateTime?
          scope                 String?
          password              String?
          createdAt             DateTime  @default(now())
          updatedAt             DateTime  @updatedAt

          @@index([userId])
          @@map("account")
        }

        model Verification {
          id         String   @id
          identifier String
          value      String
          expiresAt  DateTime
          createdAt  DateTime @default(now())
          updatedAt  DateTime @default(now()) @updatedAt

          @@index([identifier])
          @@map("verification")
        }
    """)


def generate_current_user_decorator() -> str:
    """Generate CurrentUser decorator for NestJS."""
    return dedent("""\
        import { createParamDecorator, ExecutionContext } from "@nestjs/common";

        export interface CurrentUserPayload {
          userId: string;
          sessionId?: string;
        }

        export const CurrentUser = createParamDecorator(
          (_data: unknown, ctx: ExecutionContext): CurrentUserPayload => {
            const request = ctx.switchToHttp().getRequest();
            return request.user;
          },
        );
    """)


# =============================================================================
# QUALITY SETUP FUNCTIONS
# =============================================================================

def generate_api_vitest_config() -> str:
    """Vitest config for the NestJS API: unplugin-swc emits decorator metadata."""
    return dedent("""\
        import swc from "unplugin-swc";
        import { defineConfig } from "vitest/config";

        export default defineConfig({
          // esbuild does not emit decorator metadata, which NestJS DI needs
          plugins: [swc.vite({ module: { type: "es6" } })],
          test: {
            globals: true,
            environment: "node",
            include: ["**/*.spec.ts", "**/*.test.ts"],
            exclude: ["node_modules", "dist"],
            coverage: {
              provider: "v8",
              reporter: ["text", "json", "html", "lcov"],
              include: ["apps/**/src/**/*.ts"],
              exclude: [
                "**/*.spec.ts",
                "**/*.test.ts",
                "**/*.d.ts",
                "**/main.ts",
                "**/index.ts",
                "**/generated/**",
                "**/*.module.ts",
              ],
              thresholds: {
                lines: 80,
                functions: 80,
                branches: 75,
                statements: 80,
              },
            },
            mockReset: true,
            restoreMocks: true,
          },
        });
    """)


def create_prisma_config() -> str:
    return dedent("""\
        import "dotenv/config";
        import { defineConfig } from "prisma/config";

        // Prisma 7 does not load .env on its own; dotenv above does.
        // process.env is read directly instead of env("DATABASE_URL"): env() throws when the
        // variable is missing, which would break `prisma generate` in clean CI and Docker builds
        // that have no .env. Migrate commands still fail with a clear error without a URL.
        export default defineConfig({
          schema: "prisma/schema",
          migrations: { path: "prisma/migrations" },
          datasource: { url: process.env.DATABASE_URL },
        });
    """)


def create_prisma_base_schema() -> str:
    return dedent("""\
        // Multi-file schema: one <entity>.prisma file per model in this folder.
        generator client {
          provider = "prisma-client"
          output   = "../../apps/api/src/generated/prisma"
          // The NestJS API compiles to CommonJS (tsconfig module: commonjs)
          moduleFormat = "cjs"
        }

        datasource db {
          provider = "postgresql"
        }
    """)


def create_prisma_service_ts() -> str:
    return dedent("""\
        import { Injectable, OnModuleDestroy, OnModuleInit } from "@nestjs/common";
        import { PrismaPg } from "@prisma/adapter-pg";
        import { PrismaClient } from "../generated/prisma/client";

        @Injectable()
        export class PrismaService
          extends PrismaClient
          implements OnModuleInit, OnModuleDestroy
        {
          constructor() {
            super({
              adapter: new PrismaPg({ connectionString: process.env.DATABASE_URL }),
            });
          }

          async onModuleInit(): Promise<void> {
            await this.$connect();
          }

          async onModuleDestroy(): Promise<void> {
            await this.$disconnect();
          }
        }
    """)


def create_prisma_service_spec() -> str:
    return dedent("""\
        import { describe, expect, it, vi } from "vitest";
        import { PrismaService } from "./prisma.service";

        describe("PrismaService", () => {
          it("connects on module init and disconnects on destroy", async () => {
            const service = new PrismaService();
            const connect = vi.spyOn(service, "$connect").mockResolvedValue();
            const disconnect = vi.spyOn(service, "$disconnect").mockResolvedValue();

            await service.onModuleInit();
            await service.onModuleDestroy();

            expect(connect).toHaveBeenCalledOnce();
            expect(disconnect).toHaveBeenCalledOnce();
          });
        });
    """)


def create_prisma_module_ts() -> str:
    return dedent("""\
        import { Global, Module } from "@nestjs/common";
        import { PrismaService } from "./prisma.service";

        @Global()
        @Module({
          providers: [PrismaService],
          exports: [PrismaService],
        })
        export class PrismaModule {}
    """)



def generate_github_actions_ci() -> str:
    """Generate GitHub Actions CI workflow."""
    return dedent("""\
        name: CI

        on:
          push:
            branches: [main]
          pull_request:
            branches: [main]

        # prisma generate needs no DATABASE_URL (see api/prisma.config.ts) and unit tests
        # mock PrismaService, so no database is required in this workflow.

        jobs:
          lint:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
              - uses: oven-sh/setup-bun@v2
              - run: bun install --frozen-lockfile
              - run: bun run lint

          test-api:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
              - uses: oven-sh/setup-bun@v2
              - run: bun install --frozen-lockfile
              - run: cd api && bun run prisma:generate
              - run: cd api && bun run test:coverage
              - uses: codecov/codecov-action@v4
                with:
                  files: ./api/coverage/lcov.info
                  flags: api
                  fail_ci_if_error: false

          test-frontend:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
              - uses: oven-sh/setup-bun@v2
              - run: bun install --frozen-lockfile
              - run: cd frontend && bun run test:coverage
              - uses: codecov/codecov-action@v4
                with:
                  files: ./frontend/apps/dashboard/coverage/lcov.info
                  flags: frontend
                  fail_ci_if_error: false

          build:
            runs-on: ubuntu-latest
            needs: [lint, test-api, test-frontend]
            steps:
              - uses: actions/checkout@v4
              - uses: oven-sh/setup-bun@v2
              - run: bun install --frozen-lockfile
              - run: cd api && bun run build
              - run: cd frontend && bun run build

          typecheck:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
              - uses: oven-sh/setup-bun@v2
              - run: bun install --frozen-lockfile
              - run: cd api && bun run prisma:generate
              - run: bun run typecheck
    """)


def generate_env_example() -> str:
    """Generate .env.example file."""
    return dedent("""\
        # Database - Postgres (Prisma). Copy to api/.env
        # Format: postgresql://USER:PASSWORD@HOST:5432/DATABASE?schema=public
        DATABASE_URL=postgresql://postgres:postgres@localhost:5432/myapp?schema=public

        # Better Auth (runs inside the API at /api/auth)
        # Generate a secret with: openssl rand -base64 32
        BETTER_AUTH_SECRET=change-me-generate-with-openssl-rand-base64-32
        BETTER_AUTH_URL=http://localhost:3001

        # API
        PORT=3001
        # Comma-separated origins of every frontend app allowed to call the API (CORS and Better
        # Auth trustedOrigins). Add a new app's origin here, e.g.
        # FRONTEND_URLS=http://localhost:3000,http://localhost:3002
        # FRONTEND_URL is still accepted as a single-origin fallback.
        FRONTEND_URLS=http://localhost:3000
        # Production with api.example.com + example.com: share the session cookie with the
        # dashboard (leave unset locally)
        # COOKIE_DOMAIN=.example.com

        # Dashboard (copy to frontend/apps/dashboard/.env.local)
        NEXT_PUBLIC_API_URL=http://localhost:3001
    """)


def generate_entity_crud(
    root: Path,
    entity: EntityConfig,
) -> None:
    """Generate complete CRUD stack for an entity."""
    E = entity.pascal_case
    e = entity.camel_case
    es = entity.plural

    # Backend paths
    api_collections = root / "api" / "apps" / "api" / "src" / "collections" / es
    api_schemas = root / "api" / "prisma" / "schema"
    api_dto = api_collections / "dto"

    # Frontend paths
    frontend_components = root / "frontend" / "packages" / "components" / es
    frontend_services = root / "frontend" / "packages" / "services"
    frontend_interfaces = root / "frontend" / "packages" / "interfaces"
    frontend_pages = root / "frontend" / "apps" / "dashboard" / "app" / es

    # Create directories
    for d in [api_collections, api_schemas, api_dto, frontend_components,
              frontend_services, frontend_interfaces, frontend_pages]:
        d.mkdir(parents=True, exist_ok=True)

    # Generate backend files
    backend_files = {
        api_collections / f"{es}.controller.ts": generate_entity_controller(entity),
        api_collections / f"{es}.service.ts": generate_entity_service(entity),
        api_collections / f"{es}.module.ts": generate_entity_module(entity),
        api_collections / f"{es}.service.spec.ts": generate_entity_service_spec(entity),
        api_collections / f"{es}.controller.spec.ts": generate_entity_controller_spec(entity),
        api_schemas / f"{e}.prisma": generate_entity_schema(entity),
        api_dto / f"create-{e}.dto.ts": generate_entity_create_dto(entity),
        api_dto / f"update-{e}.dto.ts": generate_entity_update_dto(entity),
    }

    # Generate frontend files
    frontend_files = {
        frontend_interfaces / f"{e}.interface.ts": generate_entity_interface(entity),
        frontend_services / f"{e}.service.ts": generate_entity_service_client(entity),
        frontend_components / f"{e}-list.tsx": generate_entity_list_component(entity),
        frontend_pages / "page.tsx": generate_entity_page(entity),
        frontend_pages / "page.spec.tsx": generate_entity_page_spec(entity),
    }

    # Write all files
    for filepath, content in {**backend_files, **frontend_files}.items():
        filepath.write_text(content if content.endswith("\n") else content + "\n")
        print(f"  Created: {filepath.relative_to(root)}")


def generate_app_module_with_entities(entities: list[EntityConfig]) -> str:
    """Generate app.module.ts with entity module imports."""
    local_imports = {
        "./auth/auth.module": "AuthModule",
        "./prisma/prisma.module": "PrismaModule",
    }
    module_names = []
    for entity in entities:
        E = entity.pascal_case
        es = entity.plural
        local_imports[f"./collections/{es}/{es}.module"] = f"{E}sModule"
        module_names.append(f"{E}sModule")

    import_lines = [
        'import { Module } from "@nestjs/common";',
        'import { ConfigModule } from "@nestjs/config";',
    ] + [
        f'import {{ {name} }} from "{path}";'
        for path, name in sorted(local_imports.items())
    ]
    imports_str = "\n".join(import_lines)
    module_imports_str = "\n".join(
        f"    {name}," for name in ["PrismaModule", "AuthModule", *module_names]
    )

    return (
        f"{imports_str}\n"
        f"\n"
        f"@Module({{\n"
        f"  imports: [\n"
        f"    ConfigModule.forRoot({{\n"
        f"      isGlobal: true,\n"
        f"    }}),\n"
        f"{module_imports_str}\n"
        f"  ],\n"
        f"  controllers: [],\n"
        f"  providers: [],\n"
        f"}})\n"
        f"export class AppModule {{}}\n"
    )


def scaffold_workspace(
    root: Path,
    name: str,
    org: str,
    allow_outside: bool,
    entities: list[EntityConfig] | None = None,
) -> None:
    """Create the full workspace structure with optional entity generation."""

    cwd = Path.cwd()
    if not allow_outside and not root.is_relative_to(cwd):
        print(f"Error: Target path {root} is outside current directory.")
        print("Use --allow-outside to confirm this is intentional.")
        sys.exit(1)

    if root.exists():
        print(f"Error: {root} already exists.")
        sys.exit(1)

    entities = entities or []
    print(f"Creating workspace at {root}...")
    if entities:
        print(f"Entities to generate: {', '.join(e.name for e in entities)}")

    # Create directories
    dirs = [
        root,
        root / ".agents",
        root / ".github" / "workflows",
        root / "api" / "apps" / "api" / "src" / "collections",
        root / "api" / "apps" / "api" / "src" / "prisma",
        root / "api" / "prisma" / "schema",
        root / "api" / "apps" / "api" / "src" / "auth" / "guards",
        root / "api" / "apps" / "api" / "src" / "auth" / "decorators",
        root / "api" / "apps" / "api" / "src" / "config",
        root / "api" / "apps" / "api" / "src" / "helpers",
        root / "api" / ".agents",
        root / "frontend" / "apps" / "dashboard" / "app" / "sign-in",
        root / "frontend" / "apps" / "dashboard" / "app" / "sign-up",
        root / "frontend" / "apps" / "dashboard" / "components",
        root / "frontend" / "apps" / "dashboard" / "lib",
        root / "frontend" / "packages" / "components",
        root / "frontend" / "packages" / "services",
        root / "frontend" / "packages" / "hooks",
        root / "frontend" / "packages" / "interfaces",
        root / "frontend" / ".agents",
        root / "mobile" / "app",
        root / "mobile" / ".agents",
        root / "packages" / "packages" / "common" / "serializers",
        root / "packages" / "packages" / "common" / "interfaces",
        root / "packages" / "packages" / "common" / "enums",
        root / "packages" / "packages" / "helpers",
        root / "packages" / "packages" / "constants",
        root / "packages" / ".agents",
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Determine app.module.ts content based on entities
    app_module_content = (
        generate_app_module_with_entities(entities) if entities
        else create_api_app_module_ts()
    )

    # Root files
    files = {
        root / "package.json": create_root_package_json(name),
        root / ".npmrc": create_npmrc(),
        root / ".gitignore": create_gitignore(),
        root / ".env.example": generate_env_example(),
        root / "biome.json": create_biome_config(),
        root / "README.md": create_readme(name),
        root / "AGENTS.md": create_agents_md(name),
        root / "CLAUDE.md": create_claude_md(name),

        # GitHub Actions CI
        root / ".github" / "workflows" / "ci.yml": generate_github_actions_ci(),

        # API
        root / "api" / "package.json": create_api_package_json(org),
        root / "api" / "nest-cli.json": create_nest_cli_json(),
        root / "api" / "tsconfig.json": create_api_tsconfig(),
        root / "api" / "tsconfig.build.json": create_api_tsconfig_build(),
        root / "api" / "vitest.config.mts": generate_api_vitest_config(),
        root / "api" / "prisma.config.ts": create_prisma_config(),
        root / "api" / "prisma" / "schema" / "schema.prisma": create_prisma_base_schema(),
        root / "api" / "prisma" / "schema" / "auth.prisma": create_auth_prisma_models(),
        root / "api" / "apps" / "api" / "src" / "prisma" / "prisma.service.ts": create_prisma_service_ts(),
        root / "api" / "apps" / "api" / "src" / "prisma" / "prisma.service.spec.ts": create_prisma_service_spec(),
        root / "api" / "apps" / "api" / "src" / "prisma" / "prisma.module.ts": create_prisma_module_ts(),
        root / "api" / "Dockerfile": create_api_dockerfile(org),
        root / ".dockerignore": create_api_dockerignore(),
        root / "api" / "apps" / "api" / "src" / "main.ts": create_api_main_ts(),
        root / "api" / "apps" / "api" / "src" / "app.module.ts": app_module_content,
        root / "api" / "apps" / "api" / "src" / "config" / "origins.ts": create_api_origins_ts(),
        root / "api" / "apps" / "api" / "src" / "config" / "origins.spec.ts": create_api_origins_spec(),
        root / "api" / "AGENTS.md": create_agents_md(f"{name} API"),
        root / "api" / "CLAUDE.md": create_claude_md(f"{name} API"),

        # Auth (Better Auth, always generated)
        root / "api" / "apps" / "api" / "src" / "auth" / "auth.service.ts": generate_auth_service(),
        root / "api" / "apps" / "api" / "src" / "auth" / "auth.service.spec.ts": generate_auth_service_spec(),
        root / "api" / "apps" / "api" / "src" / "auth" / "auth.module.ts": generate_auth_module(),
        root / "api" / "apps" / "api" / "src" / "auth" / "guards" / "auth.guard.ts": generate_auth_guard(),
        root / "api" / "apps" / "api" / "src" / "auth" / "guards" / "auth.guard.spec.ts": generate_auth_guard_spec(),
        root / "api" / "apps" / "api" / "src" / "auth" / "decorators" / "current-user.decorator.ts": generate_current_user_decorator(),

        # Frontend (thin group package + the dashboard Next.js app)
        root / "frontend" / "package.json": create_frontend_package_json(org),
        root / "frontend" / "packages" / "package.json": create_frontend_packages_package_json(org),
        root / "frontend" / "apps" / "dashboard" / "package.json": create_dashboard_package_json(org),
        root / "frontend" / "apps" / "dashboard" / "next.config.ts": create_frontend_next_config(),
        root / "frontend" / "apps" / "dashboard" / "postcss.config.mjs": create_frontend_postcss_config(),
        root / "frontend" / "apps" / "dashboard" / "tsconfig.json": create_frontend_tsconfig(),
        root / "frontend" / "apps" / "dashboard" / "vitest.config.mts": create_dashboard_vitest_config(),
        root / "frontend" / "apps" / "dashboard" / "vitest.setup.ts": create_dashboard_vitest_setup(),
        root / "frontend" / "apps" / "dashboard" / "proxy.ts": create_dashboard_proxy_ts(),
        root / "frontend" / "apps" / "dashboard" / "proxy.spec.ts": create_dashboard_proxy_spec(),
        root / "frontend" / "apps" / "dashboard" / "lib" / "auth-client.ts": create_dashboard_auth_client_ts(),
        root / "frontend" / "apps" / "dashboard" / "components" / "auth-form.tsx": create_dashboard_auth_form_tsx(),
        root / "frontend" / "apps" / "dashboard" / "components" / "auth-form.spec.tsx": create_dashboard_auth_form_spec(),
        root / "frontend" / "apps" / "dashboard" / "app" / "layout.tsx": create_frontend_layout_tsx(),
        root / "frontend" / "apps" / "dashboard" / "app" / "page.tsx": create_frontend_page_tsx(),
        root / "frontend" / "apps" / "dashboard" / "app" / "page.spec.tsx": create_frontend_page_spec(),
        root / "frontend" / "apps" / "dashboard" / "app" / "globals.css": create_frontend_globals_css(),
        root / "frontend" / "apps" / "dashboard" / "app" / "sign-in" / "page.tsx": create_dashboard_auth_page_tsx("sign-in"),
        root / "frontend" / "apps" / "dashboard" / "app" / "sign-up" / "page.tsx": create_dashboard_auth_page_tsx("sign-up"),
        root / "frontend" / "apps" / "dashboard" / "app" / "auth-pages.spec.tsx": create_dashboard_auth_pages_spec(),
        root / "frontend" / "AGENTS.md": create_agents_md(f"{name} Frontend"),
        root / "frontend" / "CLAUDE.md": create_claude_md(f"{name} Frontend"),

        # Mobile
        root / "mobile" / "package.json": create_mobile_package_json(org),
        root / "mobile" / "app.json": create_mobile_app_json(name),
        root / "mobile" / "tsconfig.json": create_mobile_tsconfig(),
        root / "mobile" / "app" / "_layout.tsx": create_mobile_layout_tsx(),
        root / "mobile" / "app" / "index.tsx": create_mobile_index_tsx(),
        root / "mobile" / "AGENTS.md": create_agents_md(f"{name} Mobile"),
        root / "mobile" / "CLAUDE.md": create_claude_md(f"{name} Mobile"),

        # Packages
        root / "packages" / "package.json": create_packages_package_json(org),
        root / "packages" / "tsconfig.json": create_packages_tsconfig(),
        root / "packages" / "AGENTS.md": create_agents_md(f"{name} Packages"),
        root / "packages" / "CLAUDE.md": create_claude_md(f"{name} Packages"),
    }

    for filepath, content in files.items():
        filepath.write_text(content if content.endswith("\n") else content + "\n")
        print(f"Created: {filepath}")

    # Generate entity CRUD if entities provided
    if entities:
        print("\nGenerating entity CRUD stack...")
        for entity in entities:
            print(f"\n[{entity.pascal_case}]")
            generate_entity_crud(root, entity)

    # Run agent-folder-init for .agents folders
    agent_init_script = Path.home() / ".codex" / "skills" / "agent-folder-init" / "scripts" / "scaffold.py"
    if agent_init_script.exists():
        for project in [root, root / "api", root / "frontend", root / "mobile", root / "packages"]:
            project_name = project.name if project != root else name
            try:
                subprocess.run([
                    "python3", str(agent_init_script),
                    "--root", str(project),
                    "--name", project_name,
                    "--allow-outside"
                ], check=True, capture_output=True)
                print(f"Initialized .agents/ for {project}")
            except subprocess.CalledProcessError:
                print(f"Warning: Could not initialize .agents/ for {project}")

    print(f"\n✅ Workspace created at: {root}")
    print(f"\nNext steps:")
    print(f"1. cd {root}")
    print(f"2. bun install")
    print(f"3. cp .env.example api/.env  (set DATABASE_URL and BETTER_AUTH_SECRET)")
    print(f"4. cd api && bun run prisma:migrate")
    print(f"5. bun run prisma:generate  (Prisma 7 migrate no longer generates the client;")
    print(f"   repeat after every schema change)")
    print(f"6. cd .. && bun run lint:fix  (formats the generated files once)")
    print(f"7. Start developing!")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold a full-stack monorepo workspace with entity generation."
    )
    parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Directory to create the workspace in",
    )
    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Project name",
    )
    parser.add_argument(
        "--org",
        type=str,
        default="myorg",
        help="Organization name for package scoping (default: myorg)",
    )
    parser.add_argument(
        "--entities",
        type=str,
        default="",
        help="Comma-separated list of entity names (e.g., 'task,project,tag')",
    )
    parser.add_argument(
        "--allow-outside",
        action="store_true",
        help="Allow creating files outside current directory",
    )

    args = parser.parse_args()

    # Parse entities
    entity_configs = []
    if args.entities:
        entity_names = [e.strip() for e in args.entities.split(",") if e.strip()]
        for name in entity_names:
            # Convert to PascalCase
            pascal_name = "".join(word.capitalize() for word in name.replace("-", " ").replace("_", " ").split())
            entity_configs.append(create_default_entity(pascal_name))

    reserved = sorted(
        e.name for e in entity_configs if e.name.lower() in RESERVED_ENTITY_NAMES
    )
    if reserved:
        print(
            f"Error: {', '.join(reserved)} clash with the Better Auth models "
            f"({', '.join(sorted(RESERVED_ENTITY_NAMES))}). Pick a different entity name."
        )
        sys.exit(1)

    scaffold_workspace(
        root=args.root.resolve(),
        name=args.name,
        org=args.org,
        allow_outside=args.allow_outside,
        entities=entity_configs,
    )


if __name__ == "__main__":
    main()
