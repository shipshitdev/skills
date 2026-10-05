#!/usr/bin/env python3
"""
Scaffold a full-stack monorepo workspace with entity generation.

This script creates a complete, working full-stack application with:
- NestJS backend with Clerk authentication
- NextJS frontend with protected routes
- Vitest testing with 80% coverage thresholds
- GitHub Actions CI/CD pipeline
- Biome linting and Husky pre-commit hooks

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
    return json.dumps({
        "name": name.lower().replace(" ", "-"),
        "version": "0.0.1",
        "private": True,
        "workspaces": [
            "api",
            "frontend",
            "mobile",
            "packages"
        ],
        "scripts": {
            "dev:api": "cd api && bun run start:dev",
            "dev:frontend": "cd frontend && bun run dev",
            "dev:mobile": "cd mobile && bun run start"
        }
    }, indent=2)


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

        # Misc
        .vercel
        .turbo
    """)


def create_readme(name: str) -> str:
    return dedent(f"""\
        # {name}

        Full-stack monorepo workspace.

        ## Structure

        - `api/` - NestJS backend
        - `frontend/` - NextJS apps
        - `mobile/` - React Native + Expo
        - `packages/` - Shared packages

        ## Getting Started

        ```bash
        bun install
        ```

        ## Development

        ```bash
        # Backend
        cd api && bun run start:dev

        # Frontend
        cd frontend && bun run dev

        # Mobile
        cd mobile && bun run start
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
    return json.dumps({
        "name": f"@{org}/api",
        "version": "0.0.1",
        "private": True,
        "scripts": {
            "build": "nest build",
            "start": "nest start",
            "start:dev": "nest start --watch",
            "start:debug": "nest start --debug --watch",
            "start:prod": "node dist/main",
            "lint": "biome check .",
            "lint:fix": "biome check --write .",
            "test": "vitest run",
            "test:watch": "vitest",
            "test:coverage": "vitest run --coverage"
        },
        "dependencies": {
            "@nestjs/common": "11.1.11",
            "@nestjs/core": "11.1.11",
            "@nestjs/config": "4.1.1",
            "@nestjs/mongoose": "11.0.4",
            "@nestjs/platform-express": "11.1.11",
            "@nestjs/swagger": "11.2.3",
            "@clerk/clerk-sdk-node": "6.6.0",
            "mongoose": "9.1.1",
            "reflect-metadata": "0.2.2",
            "rxjs": "7.8.2",
            "class-validator": "0.14.3",
            "class-transformer": "0.5.1"
        },
        "devDependencies": {
            "@nestjs/cli": "11.0.14",
            "@nestjs/schematics": "11.0.9",
            "@nestjs/testing": "11.1.11",
            "@types/express": "5.0.6",
            "@types/node": "25.0.3",
            "typescript": "5.9.3",
            "@biomejs/biome": "2.3.11",
            "vitest": "3.0.7",
            "@vitest/coverage-v8": "3.0.7"
        }
    }, indent=2)


def create_nest_cli_json() -> str:
    return json.dumps({
        "$schema": "https://json.schemastore.org/nest-cli",
        "collection": "@nestjs/schematics",
        "sourceRoot": "apps/api/src",
        "monorepo": True,
        "root": "apps/api",
        "compilerOptions": {
            "webpack": False,
            "tsConfigPath": "tsconfig.json"
        },
        "projects": {
            "api": {
                "type": "application",
                "root": "apps/api",
                "entryFile": "main",
                "sourceRoot": "apps/api/src"
            }
        }
    }, indent=2)


def create_api_tsconfig() -> str:
    return json.dumps({
        "compilerOptions": {
            "module": "commonjs",
            "declaration": True,
            "removeComments": True,
            "emitDecoratorMetadata": True,
            "experimentalDecorators": True,
            "allowSyntheticDefaultImports": True,
            "target": "ES2021",
            "sourceMap": True,
            "outDir": "./dist",
            "baseUrl": "./",
            "incremental": True,
            "skipLibCheck": True,
            "strictNullChecks": True,
            "noImplicitAny": True,
            "strictBindCallApply": True,
            "forceConsistentCasingInFileNames": True,
            "noFallthroughCasesInSwitch": True,
            "paths": {
                "@collections/*": ["apps/api/src/collections/*"],
                "@services/*": ["apps/api/src/services/*"],
                "@guards/*": ["apps/api/src/guards/*"],
                "@helpers/*": ["apps/api/src/helpers/*"]
            }
        }
    }, indent=2)


def create_api_main_ts() -> str:
    return dedent("""\
        import { NestFactory } from "@nestjs/core";
        import { ValidationPipe } from "@nestjs/common";
        import { SwaggerModule, DocumentBuilder } from "@nestjs/swagger";
        import { AppModule } from "./app.module";

        async function bootstrap() {
          const app = await NestFactory.create(AppModule);

          // Validation
          app.useGlobalPipes(
            new ValidationPipe({
              whitelist: true,
              transform: true,
            })
          );

          // CORS
          app.enableCors();

          // Swagger
          const config = new DocumentBuilder()
            .setTitle("API")
            .setDescription("API Documentation")
            .setVersion("1.0")
            .addBearerAuth()
            .build();
          const document = SwaggerModule.createDocument(app, config);
          SwaggerModule.setup("api/docs", app, document);

          const port = process.env.PORT || 3001;
          await app.listen(port);
          console.log(`API running on http://localhost:${port}`);
        }
        bootstrap();
    """)


def create_api_app_module_ts() -> str:
    return dedent("""\
        import { Module } from "@nestjs/common";
        import { ConfigModule } from "@nestjs/config";
        import { MongooseModule } from "@nestjs/mongoose";

        @Module({
          imports: [
            ConfigModule.forRoot({
              isGlobal: true,
            }),
            MongooseModule.forRoot(process.env.MONGODB_URI || "mongodb://localhost/api"),
          ],
          controllers: [],
          providers: [],
        })
        export class AppModule {}
    """)


def create_api_dockerfile() -> str:
    return dedent("""\
        FROM oven/bun:1 AS base
        WORKDIR /app

        # Install dependencies
        FROM base AS deps
        COPY package.json bun.lockb ./
        RUN bun install --frozen-lockfile

        # Build
        FROM base AS builder
        COPY --from=deps /app/node_modules ./node_modules
        COPY . .
        RUN bun run build

        # Production
        FROM base AS runner
        ENV NODE_ENV=production
        COPY --from=builder /app/dist ./dist
        COPY --from=builder /app/node_modules ./node_modules
        EXPOSE 3001
        CMD ["bun", "run", "start:prod"]
    """)


# Frontend Templates
def create_frontend_package_json(org: str) -> str:
    return json.dumps({
        "name": f"@{org}/frontend",
        "version": "0.0.1",
        "private": True,
        "scripts": {
            "dev": "next dev --turbo",
            "build": "next build",
            "start": "next start",
            "lint": "biome check .",
            "lint:fix": "biome check --write .",
            "test": "vitest run",
            "test:watch": "vitest",
            "test:coverage": "vitest run --coverage"
        },
        "dependencies": {
            "next": "16.1.1",
            "react": "19.2.3",
            "react-dom": "19.2.3",
            "@clerk/nextjs": "6.20.0",
            "axios": "1.13.2",
            "zustand": "5.0.9",
            "react-hook-form": "7.69.0",
            "zod": "4.3.2",
            "@hookform/resolvers": "5.2.2",
            "@agenticindiedev/ui": "0.3.8",
            "lucide-react": "0.562.0"
        },
        "devDependencies": {
            "@types/node": "25.0.3",
            "@types/react": "19.2.7",
            "@types/react-dom": "19.2.3",
            "typescript": "5.9.3",
            "tailwindcss": "4.1.18",
            "@tailwindcss/postcss": "4.1.18",
            "@biomejs/biome": "2.3.11",
            "sass": "1.97.1",
            "vitest": "3.0.7",
            "@vitest/coverage-v8": "3.0.7",
            "@testing-library/react": "16.3.0",
            "jsdom": "26.1.0"
        }
    }, indent=2)


def create_frontend_next_config() -> str:
    return dedent("""\
        import type { NextConfig } from "next";
        import path from "path";

        const nextConfig: NextConfig = {
          reactStrictMode: true,
          transpilePackages: ["@agenticindiedev/ui"],
          sassOptions: {
            includePaths: [path.join(__dirname, "node_modules")],
          },
          // Empty turbopack config to acknowledge we have webpack config but want Turbopack
          turbopack: {},
          webpack: (config) => {
            // Configure sass-loader to resolve @agenticindiedev/ui package imports
            const rules = config.module.rules;
            const scssRule = rules.find(
              (rule: unknown) =>
                rule &&
                typeof rule === "object" &&
                rule !== null &&
                "test" in rule &&
                rule.test &&
                typeof rule.test === "object" &&
                "toString" in rule.test &&
                rule.test.toString().includes("scss"),
            );

            if (
              scssRule &&
              typeof scssRule === "object" &&
              scssRule !== null &&
              "oneOf" in scssRule &&
              Array.isArray(scssRule.oneOf)
            ) {
              scssRule.oneOf.forEach((oneOf: unknown) => {
                if (
                  oneOf &&
                  typeof oneOf === "object" &&
                  oneOf !== null &&
                  "use" in oneOf &&
                  Array.isArray(oneOf.use)
                ) {
                  oneOf.use.forEach((loader: unknown) => {
                    if (
                      loader &&
                      typeof loader === "object" &&
                      loader !== null &&
                      "loader" in loader &&
                      typeof loader.loader === "string" &&
                      loader.loader.includes("sass-loader")
                    ) {
                      const loaderWithOptions = loader as {
                        options?: {
                          api?: string;
                          sassOptions?: Record<string, unknown>;
                        };
                      };
                      loaderWithOptions.options = {
                        ...loaderWithOptions.options,
                        api: "modern-compiler",
                        sassOptions: {
                          ...loaderWithOptions.options?.sassOptions,
                          includePaths: [path.join(__dirname, "node_modules")],
                        },
                      };
                    }
                  });
                }
              });
            }

            return config;
          },
        };

        export default nextConfig;
    """)


def create_frontend_tailwind_config() -> str:
    return dedent("""\
        import type { Config } from "tailwindcss";

        const config: Config = {
          content: [
            "./apps/**/*.{js,ts,jsx,tsx,mdx}",
            "./packages/**/*.{js,ts,jsx,tsx,mdx}",
            "./node_modules/@agenticindiedev/ui/**/*.{js,ts,jsx,tsx}",
          ],
          theme: {
            extend: {},
          },
          plugins: [],
        };

        export default config;
    """)


def create_frontend_tsconfig() -> str:
    return json.dumps({
        "compilerOptions": {
            "target": "ES2017",
            "lib": ["dom", "dom.iterable", "esnext"],
            "allowJs": True,
            "skipLibCheck": True,
            "strict": True,
            "noEmit": True,
            "esModuleInterop": True,
            "module": "esnext",
            "moduleResolution": "bundler",
            "resolveJsonModule": True,
            "isolatedModules": True,
            "jsx": "preserve",
            "incremental": True,
            "plugins": [{"name": "next"}],
            "paths": {
                "@components/*": ["packages/components/*"],
                "@services/*": ["packages/services/*"],
                "@hooks/*": ["packages/hooks/*"],
                "@interfaces/*": ["packages/interfaces/*"],
                "@props/*": ["packages/props/*"],
                "@/*": ["./*"]
            }
        },
        "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
        "exclude": ["node_modules"]
    }, indent=2)


def create_frontend_layout_tsx() -> str:
    return dedent("""\
        import type { Metadata } from "next";
        import "./globals.scss";

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
            <html lang="en" data-theme="dark">
              <body>{children}</body>
            </html>
          );
        }
    """)


def create_frontend_page_tsx() -> str:
    return dedent("""\
        export default function Home() {
          return (
            <main className="min-h-screen p-8">
              <h1 className="text-4xl font-bold">Dashboard</h1>
              <p className="mt-4 text-gray-500">Welcome to your dashboard.</p>
            </main>
          );
        }
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


def create_frontend_globals_scss() -> str:
    return dedent("""\
        @use "tailwindcss";
        @use "@agenticindiedev/ui/themes/dark";

        @source "../../node_modules/@agenticindiedev/ui/dist/**/*.{js,cjs}";
    """)


def create_biome_config() -> str:
    return json.dumps({
        "$schema": "https://biomejs.dev/schemas/2.3.12/schema.json",
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
            "ignoreUnknown": False,
            "ignore": ["node_modules", "dist", ".next", "build"]
        },
        "formatter": {
            "enabled": True,
            "indentStyle": "space",
            "indentWidth": 2,
            "lineWidth": 100
        },
        "linter": {
            "enabled": True,
            "rules": {
                "recommended": True
            }
        },
        "javascript": {
            "formatter": {
                "quoteStyle": "double",
                "semicolons": "always",
                "trailingCommas": "es5"
            }
        }
    }, indent=2)


# Mobile Templates
def create_mobile_package_json(org: str) -> str:
    return json.dumps({
        "name": f"@{org}/mobile",
        "version": "0.0.1",
        "private": True,
        "main": "expo-router/entry",
        "scripts": {
            "start": "expo start",
            "android": "expo start --android",
            "ios": "expo start --ios",
            "web": "expo start --web"
        },
        "dependencies": {
            "expo": "54.0.30",
            "expo-router": "6.0.21",
            "expo-status-bar": "3.0.9",
            "react": "19.2.3",
            "react-native": "0.83.1",
            "react-native-safe-area-context": "5.6.2",
            "react-native-screens": "4.19.0"
        },
        "devDependencies": {
            "@types/react": "19.2.7",
            "typescript": "5.9.3"
        }
    }, indent=2)


def create_mobile_app_json(name: str) -> str:
    slug = name.lower().replace(" ", "-")
    return json.dumps({
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
    }, indent=2)


def create_mobile_tsconfig() -> str:
    return json.dumps({
        "extends": "expo/tsconfig.base",
        "compilerOptions": {
            "strict": True,
            "paths": {
                "@/*": ["./*"]
            }
        },
        "include": ["**/*.ts", "**/*.tsx", ".expo/types/**/*.ts", "expo-env.d.ts"]
    }, indent=2)


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
    return json.dumps({
        "name": f"@{org}/packages",
        "version": "0.0.1",
        "private": True,
        "workspaces": [
            "packages/*"
        ]
    }, indent=2)


def create_packages_tsconfig() -> str:
    return json.dumps({
        "compilerOptions": {
            "target": "ES2020",
            "module": "ESNext",
            "moduleResolution": "bundler",
            "declaration": True,
            "strict": True,
            "skipLibCheck": True,
            "esModuleInterop": True
        }
    }, indent=2)


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
        import {{ ApiTags, ApiOperation, ApiBearerAuth }} from "@nestjs/swagger";
        import {{ {E}sService }} from "./{es}.service";
        import {{ Create{E}Dto }} from "./dto/create-{e}.dto";
        import {{ Update{E}Dto }} from "./dto/update-{e}.dto";
        import {{ ClerkAuthGuard }} from "../../auth/guards/clerk-auth.guard";
        import {{ CurrentUser }} from "../../auth/decorators/current-user.decorator";

        @ApiTags("{es}")
        @ApiBearerAuth()
        @UseGuards(ClerkAuthGuard)
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
    """Generate NestJS service for an entity."""
    E = entity.pascal_case
    e = entity.camel_case
    es = entity.plural

    return dedent(f"""\
        import {{ Injectable, NotFoundException }} from "@nestjs/common";
        import {{ InjectModel }} from "@nestjs/mongoose";
        import {{ Model }} from "mongoose";
        import {{ {E}, {E}Document }} from "./schemas/{e}.schema";
        import {{ Create{E}Dto }} from "./dto/create-{e}.dto";
        import {{ Update{E}Dto }} from "./dto/update-{e}.dto";

        @Injectable()
        export class {E}sService {{
          constructor(
            @InjectModel({E}.name) private {e}Model: Model<{E}Document>,
          ) {{}}

          async create(create{E}Dto: Create{E}Dto, userId: string): Promise<{E}> {{
            const {e} = new this.{e}Model({{
              ...create{E}Dto,
              userId,
            }});
            return {e}.save();
          }}

          async findAll(userId: string): Promise<{E}[]> {{
            const query = this.{e}Model.find({{ userId }}).sort({{ createdAt: -1 }});
            return query.then((docs) => docs);
          }}

          async findOne(id: string, userId: string): Promise<{E}> {{
            const query = this.{e}Model.findOne({{ _id: id, userId }});
            const {e} = await query.then((doc) => doc);

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
            const query = this.{e}Model.findOneAndUpdate(
              {{ _id: id, userId }},
              update{E}Dto,
              {{ new: true }},
            );
            const {e} = await query.then((doc) => doc);

            if (!{e}) {{
              throw new NotFoundException(`{E} with ID ${{id}} not found`);
            }}

            return {e};
          }}

          async remove(id: string, userId: string): Promise<void> {{
            const query = this.{e}Model.deleteOne({{ _id: id, userId }});
            const result = await query.then((res) => res);

            if (result.deletedCount === 0) {{
              throw new NotFoundException(`{E} with ID ${{id}} not found`);
            }}
          }}
        }}
    """)


def generate_entity_schema(entity: EntityConfig) -> str:
    """Generate Mongoose schema for an entity."""
    E = entity.pascal_case

    # Generate field definitions
    field_defs = []
    for field in entity.fields:
        decorator = "@Prop("
        options = []
        if field.required:
            options.append("required: true")
        if field.default:
            options.append(f'default: "{field.default}"')
        if field.enum_values:
            enum_str = ", ".join(f'"{v}"' for v in field.enum_values)
            options.append(f"enum: [{enum_str}]")

        if options:
            decorator += "{ " + ", ".join(options) + " }"
        decorator += ")"

        optional = "" if field.required else "?"
        field_defs.append(f"  {decorator}\n  {field.name}{optional}: string;")

    fields_str = "\n\n".join(field_defs)

    return dedent(f"""\
        import {{ Prop, Schema, SchemaFactory }} from "@nestjs/mongoose";
        import {{ Document }} from "mongoose";

        export type {E}Document = {E} & Document;

        @Schema({{ timestamps: true }})
        export class {E} {{
{fields_str}

          @Prop({{ required: true }})
          userId: string;
        }}

        export const {E}Schema = SchemaFactory.createForClass({E});

        {E}Schema.index({{ userId: 1 }});
        {E}Schema.index({{ userId: 1, createdAt: -1 }});
    """)


def generate_entity_create_dto(entity: EntityConfig) -> str:
    """Generate Create DTO for an entity."""
    E = entity.pascal_case

    # Generate field definitions
    field_defs = []
    for field in entity.fields:
        decorators = []
        if field.type == "string":
            decorators.append("@IsString()")
        elif field.type == "number":
            decorators.append("@IsNumber()")
        elif field.type == "boolean":
            decorators.append("@IsBoolean()")
        elif field.type == "date":
            decorators.append("@IsDateString()")

        if not field.required:
            decorators.append("@IsOptional()")

        optional = "" if field.required else "?"
        decorator_str = "\n  ".join(decorators)
        field_defs.append(f"  {decorator_str}\n  {field.name}{optional}: string;")

    fields_str = "\n\n".join(field_defs)

    return dedent(f"""\
        import {{
          IsString,
          IsOptional,
          IsBoolean,
          IsNumber,
          IsDateString,
        }} from "class-validator";

        export class Create{E}Dto {{
{fields_str}
        }}
    """)


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
    """Generate NestJS module for an entity."""
    E = entity.pascal_case
    e = entity.camel_case
    es = entity.plural

    return dedent(f"""\
        import {{ Module }} from "@nestjs/common";
        import {{ MongooseModule }} from "@nestjs/mongoose";
        import {{ {E}sController }} from "./{es}.controller";
        import {{ {E}sService }} from "./{es}.service";
        import {{ {E}, {E}Schema }} from "./schemas/{e}.schema";

        @Module({{
          imports: [
            MongooseModule.forFeature([
              {{ name: {E}.name, schema: {E}Schema }},
            ]),
          ],
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
        import {{ getModelToken }} from "@nestjs/mongoose";
        import {{ NotFoundException }} from "@nestjs/common";
        import {{ {E}sService }} from "./{es}.service";
        import {{ {E} }} from "./schemas/{e}.schema";

        describe("{E}sService", () => {{
          let service: {E}sService;
          let mockModel: any;

          const mockUserId = "user-123";
          const mock{E} = {{
            _id: "{e}-123",
            title: "Test {E}",
            userId: mockUserId,
            createdAt: new Date(),
            save: vi.fn().mockResolvedValue(this),
          }};

          beforeEach(async () => {{
            mockModel = {{
              find: vi.fn(),
              findOne: vi.fn(),
              findOneAndUpdate: vi.fn(),
              deleteOne: vi.fn(),
            }};

            const module: TestingModule = await Test.createTestingModule({{
              providers: [
                {E}sService,
                {{
                  provide: getModelToken({E}.name),
                  useValue: {{
                    ...mockModel,
                    new: vi.fn().mockImplementation((data) => ({{
                      ...data,
                      save: vi.fn().mockResolvedValue({{ ...data, _id: "new-id" }}),
                    }})),
                  }},
                }},
              ],
            }}).compile();

            service = module.get<{E}sService>({E}sService);
          }});

          it("should be defined", () => {{
            expect(service).toBeDefined();
          }});

          describe("findAll", () => {{
            it("should return all {es} for a user", async () => {{
              const mock{E}s = [mock{E}];
              mockModel.find.mockReturnValue({{
                sort: vi.fn().mockReturnValue({{
                  then: vi.fn().mockResolvedValue(mock{E}s),
                }}),
              }});

              const result = await service.findAll(mockUserId);

              expect(result).toEqual(mock{E}s);
              expect(mockModel.find).toHaveBeenCalledWith({{ userId: mockUserId }});
            }});
          }});

          describe("findOne", () => {{
            it("should return a {e} by id", async () => {{
              mockModel.findOne.mockReturnValue({{
                then: vi.fn().mockResolvedValue(mock{E}),
              }});

              const result = await service.findOne("{e}-123", mockUserId);

              expect(result).toEqual(mock{E});
            }});

            it("should throw NotFoundException if {e} not found", async () => {{
              mockModel.findOne.mockReturnValue({{
                then: vi.fn().mockResolvedValue(null),
              }});

              await expect(
                service.findOne("nonexistent", mockUserId),
              ).rejects.toThrow(NotFoundException);
            }});
          }});

          describe("update", () => {{
            it("should update a {e}", async () => {{
              const updated{E} = {{ ...mock{E}, title: "Updated" }};
              mockModel.findOneAndUpdate.mockReturnValue({{
                then: vi.fn().mockResolvedValue(updated{E}),
              }});

              const result = await service.update(
                "{e}-123",
                {{ title: "Updated" }},
                mockUserId,
              );

              expect(result.title).toBe("Updated");
            }});
          }});

          describe("remove", () => {{
            it("should delete a {e}", async () => {{
              mockModel.deleteOne.mockReturnValue({{
                then: vi.fn().mockResolvedValue({{ deletedCount: 1 }}),
              }});

              await expect(
                service.remove("{e}-123", mockUserId),
              ).resolves.not.toThrow();
            }});

            it("should throw NotFoundException if {e} not found", async () => {{
              mockModel.deleteOne.mockReturnValue({{
                then: vi.fn().mockResolvedValue({{ deletedCount: 0 }}),
              }});

              await expect(
                service.remove("nonexistent", mockUserId),
              ).rejects.toThrow(NotFoundException);
            }});
          }});
        }});
    """)


def generate_entity_interface(entity: EntityConfig) -> str:
    """Generate TypeScript interface for frontend."""
    E = entity.pascal_case

    # Generate field definitions
    field_defs = []
    for field in entity.fields:
        optional = "" if field.required else "?"
        ts_type = "string"
        if field.type == "number":
            ts_type = "number"
        elif field.type == "boolean":
            ts_type = "boolean"
        elif field.type == "date":
            ts_type = "string"  # ISO date string

        field_defs.append(f"  {field.name}{optional}: {ts_type};")

    fields_str = "\n".join(field_defs)

    return dedent(f"""\
        export interface {E} {{
          _id: string;
{fields_str}
          userId: string;
          createdAt: string;
          updatedAt: string;
        }}
    """)


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

        async function getAuthHeaders(): Promise<HeadersInit> {{
          const token = await window.Clerk?.session?.getToken();

          return {{
            "Content-Type": "application/json",
            ...(token ? {{ Authorization: `Bearer ${{token}}` }} : {{}}),
          }};
        }}

        async function handleResponse<T>(response: Response): Promise<T> {{
          if (!response.ok) {{
            const error = await response.json().catch(() => ({{ message: "Request failed" }}));
            throw new Error(error.message || `HTTP ${{response.status}}`);
          }}
          return response.json();
        }}

        export const {E}Service = {{
          async getAll(options?: RequestOptions): Promise<{E}[]> {{
            const headers = await getAuthHeaders();
            const response = await fetch(`${{API_URL}}/{es}`, {{
              headers,
              signal: options?.signal,
            }});
            return handleResponse<{E}[]>(response);
          }},

          async getById(id: string, options?: RequestOptions): Promise<{E}> {{
            const headers = await getAuthHeaders();
            const response = await fetch(`${{API_URL}}/{es}/${{id}}`, {{
              headers,
              signal: options?.signal,
            }});
            return handleResponse<{E}>(response);
          }},

          async create(data: Partial<{E}>): Promise<{E}> {{
            const headers = await getAuthHeaders();
            const response = await fetch(`${{API_URL}}/{es}`, {{
              method: "POST",
              headers,
              body: JSON.stringify(data),
            }});
            return handleResponse<{E}>(response);
          }},

          async update(id: string, data: Partial<{E}>): Promise<{E}> {{
            const headers = await getAuthHeaders();
            const response = await fetch(`${{API_URL}}/{es}/${{id}}`, {{
              method: "PATCH",
              headers,
              body: JSON.stringify(data),
            }});
            return handleResponse<{E}>(response);
          }},

          async delete(id: string): Promise<void> {{
            const headers = await getAuthHeaders();
            const response = await fetch(`${{API_URL}}/{es}/${{id}}`, {{
              method: "DELETE",
              headers,
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
        import {{ Button }} from "@agenticindiedev/ui";

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
              <div className="p-4 bg-red-50 text-red-600 rounded-lg">
                Error: {{error}}
              </div>
            );
          }}

          return (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold">{E}s</h2>
                <Button onClick={{() => window.location.href = "/{es}/new"}}>
                  Add {E}
                </Button>
              </div>

              {{{es}.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No {es} yet. Create your first one!
                </div>
              ) : (
                <div className="space-y-2">
                  {{{es}.map(({e}) => (
                    <div key={{{e}._id}} className="p-4 border rounded-lg flex justify-between items-center">
                      <div>
                        <h3 className="font-medium">{{{e}.title}}</h3>
                        {{{e}.description && (
                          <p className="text-sm text-gray-500">{{{e}.description}}</p>
                        )}}
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="ghost"
                          onClick={{() => window.location.href = `/{es}/${{{e}._id}}`}}
                        >
                          Edit
                        </Button>
                        <Button
                          variant="ghost"
                          onClick={{() => handleDelete({e}._id)}}
                        >
                          Delete
                        </Button>
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
    """.replace("{e}", entity.camel_case))


# =============================================================================
# AUTH GENERATION FUNCTIONS
# =============================================================================

def generate_clerk_auth_guard() -> str:
    """Generate Clerk auth guard for NestJS."""
    return dedent("""\
        import {
          Injectable,
          CanActivate,
          ExecutionContext,
          UnauthorizedException,
        } from "@nestjs/common";
        import { Clerk } from "@clerk/clerk-sdk-node";

        @Injectable()
        export class ClerkAuthGuard implements CanActivate {
          private clerk: Clerk;

          constructor() {
            this.clerk = new Clerk({
              secretKey: process.env.CLERK_SECRET_KEY || "",
            });
          }

          async canActivate(context: ExecutionContext): Promise<boolean> {
            const request = context.switchToHttp().getRequest();
            const authHeader = request.headers.authorization;

            if (!authHeader || !authHeader.startsWith("Bearer ")) {
              throw new UnauthorizedException("No authorization token provided");
            }

            const token = authHeader.replace("Bearer ", "");

            try {
              const session = await this.clerk.verifyToken(token);
              request.user = {
                userId: session.sub,
                sessionId: session.sid,
              };
              return true;
            } catch (error) {
              throw new UnauthorizedException("Invalid or expired token");
            }
          }
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
          (data: unknown, ctx: ExecutionContext): CurrentUserPayload => {
            const request = ctx.switchToHttp().getRequest();
            return request.user;
          },
        );
    """)


# =============================================================================
# QUALITY SETUP FUNCTIONS
# =============================================================================

def generate_vitest_config() -> str:
    """Generate Vitest configuration with coverage thresholds."""
    return dedent("""\
        import { defineConfig } from "vitest/config";

        export default defineConfig({
          test: {
            globals: true,
            environment: "node",
            include: ["**/*.spec.ts", "**/*.test.ts"],
            exclude: ["node_modules", "dist", ".next", "build"],
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


def generate_github_actions_ci() -> str:
    """Generate GitHub Actions CI workflow."""
    return dedent("""\
        name: CI

        on:
          push:
            branches: [main]
          pull_request:
            branches: [main]

        jobs:
          lint:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
              - uses: oven-sh/setup-bun@v2
              - run: bun install
              - run: bun run lint

          test-api:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
              - uses: oven-sh/setup-bun@v2
              - run: bun install
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
              - run: bun install
              - run: cd frontend && bun run test:coverage
              - uses: codecov/codecov-action@v4
                with:
                  files: ./frontend/coverage/lcov.info
                  flags: frontend
                  fail_ci_if_error: false

          build:
            runs-on: ubuntu-latest
            needs: [lint, test-api, test-frontend]
            steps:
              - uses: actions/checkout@v4
              - uses: oven-sh/setup-bun@v2
              - run: bun install
              - run: cd api && bun run build
              - run: cd frontend && bun run build

          typecheck:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
              - uses: oven-sh/setup-bun@v2
              - run: bun install
              - run: cd api && bunx tsc --noEmit
              - run: cd frontend && bunx tsc --noEmit
    """)


def generate_env_example() -> str:
    """Generate .env.example file."""
    return dedent("""\
        # Database - MongoDB Atlas (recommended for production)
        # Get your connection string from: https://cloud.mongodb.com
        # Format: mongodb+srv://USERNAME:PASSWORD@CLUSTER.mongodb.net/DATABASE?retryWrites=true&w=majority
        MONGODB_URI=mongodb+srv://USERNAME:PASSWORD@cluster.mongodb.net/myapp?retryWrites=true&w=majority

        # Clerk Authentication
        CLERK_SECRET_KEY=sk_test_xxxxx
        NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxx

        # API
        PORT=3001
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
    api_schemas = api_collections / "schemas"
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
        api_schemas / f"{e}.schema.ts": generate_entity_schema(entity),
        api_dto / f"create-{e}.dto.ts": generate_entity_create_dto(entity),
        api_dto / f"update-{e}.dto.ts": generate_entity_update_dto(entity),
    }

    # Generate frontend files
    frontend_files = {
        frontend_interfaces / f"{e}.interface.ts": generate_entity_interface(entity),
        frontend_services / f"{e}.service.ts": generate_entity_service_client(entity),
        frontend_components / f"{e}-list.tsx": generate_entity_list_component(entity),
        frontend_pages / "page.tsx": generate_entity_page(entity),
    }

    # Write all files
    for filepath, content in {**backend_files, **frontend_files}.items():
        filepath.write_text(content)
        print(f"  Created: {filepath.relative_to(root)}")


def generate_app_module_with_entities(entities: list[EntityConfig]) -> str:
    """Generate app.module.ts with entity module imports."""
    imports = []
    module_imports = []

    for entity in entities:
        E = entity.pascal_case
        es = entity.plural
        imports.append(f'import {{ {E}sModule }} from "./collections/{es}/{es}.module";')
        module_imports.append(f"    {E}sModule,")

    imports_str = "\n".join(imports)
    module_imports_str = "\n".join(module_imports)

    return dedent(f"""\
        import {{ Module }} from "@nestjs/common";
        import {{ ConfigModule }} from "@nestjs/config";
        import {{ MongooseModule }} from "@nestjs/mongoose";
{imports_str}

        @Module({{
          imports: [
            ConfigModule.forRoot({{
              isGlobal: true,
            }}),
            MongooseModule.forRoot(process.env.MONGODB_URI || "mongodb://localhost/api"),
{module_imports_str}
          ],
          controllers: [],
          providers: [],
        }})
        export class AppModule {{}}
    """)


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
        root / "api" / "apps" / "api" / "src" / "auth" / "guards",
        root / "api" / "apps" / "api" / "src" / "auth" / "decorators",
        root / "api" / "apps" / "api" / "src" / "config",
        root / "api" / "apps" / "api" / "src" / "helpers",
        root / "api" / ".agents",
        root / "frontend" / "apps" / "dashboard" / "app",
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
        root / "README.md": create_readme(name),
        root / "AGENTS.md": create_agents_md(name),
        root / "CLAUDE.md": create_claude_md(name),

        # GitHub Actions CI
        root / ".github" / "workflows" / "ci.yml": generate_github_actions_ci(),

        # API
        root / "api" / "package.json": create_api_package_json(org),
        root / "api" / "nest-cli.json": create_nest_cli_json(),
        root / "api" / "tsconfig.json": create_api_tsconfig(),
        root / "api" / "biome.json": create_biome_config(),
        root / "api" / "vitest.config.ts": generate_vitest_config(),
        root / "api" / "Dockerfile": create_api_dockerfile(),
        root / "api" / "apps" / "api" / "src" / "main.ts": create_api_main_ts(),
        root / "api" / "apps" / "api" / "src" / "app.module.ts": app_module_content,
        root / "api" / "AGENTS.md": create_agents_md(f"{name} API"),
        root / "api" / "CLAUDE.md": create_claude_md(f"{name} API"),

        # Auth files (always generated)
        root / "api" / "apps" / "api" / "src" / "auth" / "guards" / "clerk-auth.guard.ts": generate_clerk_auth_guard(),
        root / "api" / "apps" / "api" / "src" / "auth" / "decorators" / "current-user.decorator.ts": generate_current_user_decorator(),

        # Frontend
        root / "frontend" / "package.json": create_frontend_package_json(org),
        root / "frontend" / "next.config.ts": create_frontend_next_config(),
        root / "frontend" / "postcss.config.mjs": create_frontend_postcss_config(),
        root / "frontend" / "tailwind.config.ts": create_frontend_tailwind_config(),
        root / "frontend" / "tsconfig.json": create_frontend_tsconfig(),
        root / "frontend" / "biome.json": create_biome_config(),
        root / "frontend" / "vitest.config.ts": generate_vitest_config(),
        root / "frontend" / "apps" / "dashboard" / "app" / "layout.tsx": create_frontend_layout_tsx(),
        root / "frontend" / "apps" / "dashboard" / "app" / "page.tsx": create_frontend_page_tsx(),
        root / "frontend" / "apps" / "dashboard" / "app" / "globals.scss": create_frontend_globals_scss(),
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
        filepath.write_text(content)
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
    print(f"3. Start developing!")


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

    scaffold_workspace(
        root=args.root.resolve(),
        name=args.name,
        org=args.org,
        allow_outside=args.allow_outside,
        entities=entity_configs,
    )


if __name__ == "__main__":
    main()
