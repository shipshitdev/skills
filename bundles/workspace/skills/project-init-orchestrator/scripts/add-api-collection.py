#!/usr/bin/env python3
"""
Add a new collection to the NestJS API.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from textwrap import dedent


def to_pascal_case(s: str) -> str:
    return "".join(word.capitalize() for word in s.replace("-", "_").split("_"))


def to_camel_case(s: str) -> str:
    pascal = to_pascal_case(s)
    return pascal[0].lower() + pascal[1:]


def create_module_ts(name: str) -> str:
    pascal = to_pascal_case(name)
    return dedent(f"""\
        import {{ Module }} from "@nestjs/common";
        import {{ {pascal}Controller }} from "./controllers/{name}.controller";
        import {{ {pascal}Service }} from "./services/{name}.service";

        // PrismaModule is global, so PrismaService is injectable without an import here.
        @Module({{
          controllers: [{pascal}Controller],
          providers: [{pascal}Service],
          exports: [{pascal}Service],
        }})
        export class {pascal}Module {{}}
    """)


def create_prisma_model(name: str) -> str:
    pascal = to_pascal_case(name)
    table = name.replace("-", "_")
    return (
        f"model {pascal} {{\n"
        f"  id             String   @id @default(cuid())\n"
        f"  organizationId String\n"
        f"  name           String\n"
        f"  isDeleted      Boolean  @default(false)\n"
        f"  createdAt      DateTime @default(now())\n"
        f"  updatedAt      DateTime @updatedAt\n"
        f"\n"
        f"  // Add the relation to Organization here once that model exists:\n"
        f"  // organization Organization @relation(fields: [organizationId], references: [id])\n"
        f"\n"
        f"  @@index([organizationId, isDeleted])\n"
        f'  @@map("{table}")\n'
        f"}}\n"
    )


def create_controller_ts(name: str) -> str:
    pascal = to_pascal_case(name)
    camel = to_camel_case(name)
    return dedent(f"""\
        import {{
          Controller,
          Get,
          Post,
          Patch,
          Delete,
          Body,
          Param,
          Query,
        }} from "@nestjs/common";
        import {{ ApiTags, ApiOperation, ApiBearerAuth }} from "@nestjs/swagger";
        import {{ {pascal}Service }} from "../services/{name}.service";
        import {{ Create{pascal}Dto }} from "../dto/create-{name}.dto";
        import {{ Update{pascal}Dto }} from "../dto/update-{name}.dto";

        @ApiTags("{name}")
        @ApiBearerAuth()
        @Controller("{name}")
        export class {pascal}Controller {{
          constructor(private readonly {camel}Service: {pascal}Service) {{}}

          @Post()
          @ApiOperation({{ summary: "Create {name}" }})
          create(@Body() dto: Create{pascal}Dto) {{
            return this.{camel}Service.create(dto);
          }}

          @Get()
          @ApiOperation({{ summary: "Get all {name}s" }})
          findAll(@Query("organizationId") organizationId: string) {{
            return this.{camel}Service.findAll(organizationId);
          }}

          @Get(":id")
          @ApiOperation({{ summary: "Get {name} by ID" }})
          findOne(
            @Param("id") id: string,
            @Query("organizationId") organizationId: string,
          ) {{
            return this.{camel}Service.findOne(id, organizationId);
          }}

          @Patch(":id")
          @ApiOperation({{ summary: "Update {name}" }})
          update(
            @Param("id") id: string,
            @Query("organizationId") organizationId: string,
            @Body() dto: Update{pascal}Dto,
          ) {{
            return this.{camel}Service.update(id, organizationId, dto);
          }}

          @Delete(":id")
          @ApiOperation({{ summary: "Soft delete {name}" }})
          remove(
            @Param("id") id: string,
            @Query("organizationId") organizationId: string,
          ) {{
            return this.{camel}Service.remove(id, organizationId);
          }}
        }}
    """)


def create_service_ts(name: str) -> str:
    pascal = to_pascal_case(name)
    camel = to_camel_case(name)
    return dedent(f"""\
        import {{ Injectable, NotFoundException }} from "@nestjs/common";
        import type {{ {pascal} }} from "../../../generated/prisma/client";
        import {{ PrismaService }} from "../../../prisma/prisma.service";
        import {{ Create{pascal}Dto }} from "../dto/create-{name}.dto";
        import {{ Update{pascal}Dto }} from "../dto/update-{name}.dto";

        @Injectable()
        export class {pascal}Service {{
          constructor(private readonly prisma: PrismaService) {{}}

          async create(dto: Create{pascal}Dto): Promise<{pascal}> {{
            return this.prisma.{camel}.create({{ data: dto }});
          }}

          async findAll(organizationId: string): Promise<{pascal}[]> {{
            return this.prisma.{camel}.findMany({{
              where: {{ organizationId, isDeleted: false }},
              orderBy: {{ createdAt: "desc" }},
            }});
          }}

          async findOne(id: string, organizationId: string): Promise<{pascal}> {{
            const row = await this.prisma.{camel}.findFirst({{
              where: {{ id, organizationId, isDeleted: false }},
            }});

            if (!row) {{
              throw new NotFoundException("{pascal} not found");
            }}

            return row;
          }}

          async update(
            id: string,
            organizationId: string,
            dto: Update{pascal}Dto,
          ): Promise<{pascal}> {{
            await this.findOne(id, organizationId);
            // Never let the caller move a row to another organization
            const {{ organizationId: _ignored, ...data }} = dto;
            return this.prisma.{camel}.update({{ where: {{ id }}, data }});
          }}

          async remove(id: string, organizationId: string): Promise<{pascal}> {{
            await this.findOne(id, organizationId);
            return this.prisma.{camel}.update({{
              where: {{ id }},
              data: {{ isDeleted: true }},
            }});
          }}
        }}
    """)


def create_create_dto_ts(name: str) -> str:
    pascal = to_pascal_case(name)
    return dedent(f"""\
        import {{ ApiProperty }} from "@nestjs/swagger";
        import {{ IsString, IsNotEmpty }} from "class-validator";

        export class Create{pascal}Dto {{
          @ApiProperty()
          @IsString()
          @IsNotEmpty()
          organizationId: string;

          @ApiProperty()
          @IsString()
          @IsNotEmpty()
          name: string;
        }}
    """)


def create_update_dto_ts(name: str) -> str:
    pascal = to_pascal_case(name)
    return dedent(f"""\
        import {{ PartialType }} from "@nestjs/swagger";
        import {{ Create{pascal}Dto }} from "./create-{name}.dto";

        export class Update{pascal}Dto extends PartialType(Create{pascal}Dto) {{}}
    """)


def create_http_file(name: str) -> str:
    return dedent(f"""\
        @baseUrl = http://localhost:3001
        @organizationId = YOUR_ORG_ID

        ### Get all {name}s
        GET {{{{baseUrl}}}}/{name}?organizationId={{{{organizationId}}}}

        ### Get {name} by ID
        GET {{{{baseUrl}}}}/{name}/ITEM_ID?organizationId={{{{organizationId}}}}

        ### Create {name}
        POST {{{{baseUrl}}}}/{name}
        Content-Type: application/json

        {{
          "organizationId": "{{{{organizationId}}}}",
          "name": "Test {name}"
        }}

        ### Update {name}
        PATCH {{{{baseUrl}}}}/{name}/ITEM_ID?organizationId={{{{organizationId}}}}
        Content-Type: application/json

        {{
          "name": "Updated name"
        }}

        ### Delete {name}
        DELETE {{{{baseUrl}}}}/{name}/ITEM_ID?organizationId={{{{organizationId}}}}
    """)


def add_api_collection(root: Path, name: str) -> None:
    """Add a new collection to the API."""

    collections_dir = root / "apps" / "api" / "src" / "collections"
    if not collections_dir.exists():
        print(f"Error: {collections_dir} does not exist. Is this an API project?")
        sys.exit(1)

    collection_dir = collections_dir / name
    if collection_dir.exists():
        print(f"Error: {collection_dir} already exists.")
        sys.exit(1)

    # Create directories
    dirs = [
        collection_dir / "controllers",
        collection_dir / "services",
        collection_dir / "dto",
    ]

    for d in dirs:
        d.mkdir(parents=True)

    # Create files
    files = {
        collection_dir / f"{name}.module.ts": create_module_ts(name),
        collection_dir / "controllers" / f"{name}.controller.ts": create_controller_ts(name),
        collection_dir / "services" / f"{name}.service.ts": create_service_ts(name),
        collection_dir / "dto" / f"create-{name}.dto.ts": create_create_dto_ts(name),
        collection_dir / "dto" / f"update-{name}.dto.ts": create_update_dto_ts(name),
        collection_dir / f"{name}.http": create_http_file(name),
    }

    # Prisma models live in the multi-file schema folder at the API project root
    prisma_schema_dir = root / "prisma" / "schema"
    prisma_schema_dir.mkdir(parents=True, exist_ok=True)
    files[prisma_schema_dir / f"{name}.prisma"] = create_prisma_model(name)

    for filepath, content in files.items():
        filepath.write_text(content)
        print(f"Created: {filepath}")

    pascal = to_pascal_case(name)
    print(f"\n✅ Collection '{name}' created at: {collection_dir}")
    print(f"\nDon't forget to:")
    print(f"1. Import {pascal}Module in app.module.ts")
    print(f"2. Run `bun run prisma:migrate` to create the migration for prisma/schema/{name}.prisma")
    print(f"3. Create serializer in packages/common/serializers/")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add a new collection to the NestJS API."
    )
    parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Path to the API project root",
    )
    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Collection name (e.g., 'users', 'posts')",
    )

    args = parser.parse_args()

    add_api_collection(
        root=args.root.resolve(),
        name=args.name.lower().replace(" ", "-"),
    )


if __name__ == "__main__":
    main()
