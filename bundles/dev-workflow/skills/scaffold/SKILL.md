---
name: scaffold
description: Generates incremental code modules inside an existing repo following local patterns — endpoints, components, packages, database models. Not for new full-project scaffolds.
metadata:
  version: "2.2.5"
  tags: "scaffolding, code-generation, boilerplate, productivity"
when_to_use: "add a module, new endpoint, new component"
---

# Scaffold

Generate incremental code inside an existing repository, following local
codebase patterns.

## Contract

Inputs:

- Scaffold target type and name
- Repository root
- Existing examples to follow

Outputs:

- Files created or modified
- Patterns copied from existing code
- Manual follow-up steps and tests to run

Creates/Modifies:

- Local source, test, and export files for the requested module/component/package
- Does not create a full product repo

External Side Effects:

- None

Confirmation Required:

- Before overwriting existing files
- Before introducing a new pattern when fewer than 3 matching examples exist

Delegates To:

- `project-init-orchestrator` when the user needs a whole new project
- `project-init-orchestrator` (v0 route) / `npx @shipshitdev/v0` when the user needs a new Shipshit.dev product repo
- Framework-specific skills such as `nestjs-expert`, `react-patterns`, `shadcn`, or `typescript-expert`

## Steps

1. **Determine what to scaffold** from arguments:
   - `endpoint [name]` — New API endpoint (controller + service + module)
   - `module [name]` — New backend module with full structure
   - `component [name]` — New UI component with proper typing
   - `package [name]` — New shared package
   - `model [name]` — New database model (Prisma) with service

2. **Find 3+ existing examples**:
   - Search for similar implementations in the codebase
   - Identify the exact patterns used (imports, naming, file structure)
   - Note any module-specific conventions

3. **Scaffold based on type**:

   ### API Endpoint

   - Controller, Service, Module in appropriate directory
   - Follow: auth guards, tenant filtering, serializer response

   ### UI Component

   - Component file with proper typing
   - Props interface in dedicated props file
   - Export from barrel

   ### Shared Package

   - Directory with package.json
   - Barrel export: `src/index.ts`
   - TypeScript config

   ### Database Model

   - Prisma model file plus migration
   - Interface in shared interfaces package
   - Serializer in shared serializers package (if applicable)

4. **Apply critical rules**:
   - Interfaces in dedicated files, not inline
   - Path aliases, not relative imports
   - Tenant/organization filter in all queries (if applicable)

5. **Report**: List all files created and any manual steps needed

## Arguments

- Required: what to scaffold (e.g., "endpoint tasks", "component ImageGrid", "model workflows")
