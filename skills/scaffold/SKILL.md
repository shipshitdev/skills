---
name: scaffold
description: Generates incremental code modules inside an existing repo following local patterns — endpoints, components, packages, database models. Not for new full-project scaffolds.
metadata:
  version: "2.2.4"
  tags: "scaffolding, code-generation, boilerplate, productivity"
when_to_use: "add a module, new endpoint, new component"
---

# Scaffold

Generate incremental code inside an existing repository, following local codebase patterns.

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

## Arguments

Required: what to scaffold, e.g. `endpoint tasks`, `component ImageGrid`, `model workflows`.

- `endpoint [name]`: new API endpoint (controller + service + module)
- `module [name]`: new backend module with full structure
- `component [name]`: new UI component with proper typing
- `package [name]`: new shared package
- `model [name]`: new database model (Prisma) with service

## Steps

1. **Determine what to scaffold** from the arguments above.
2. **Find 3+ existing examples.** Search for similar implementations, identify the exact patterns (imports, naming, file structure) and note module-specific conventions. With fewer than 3, ask before introducing a new pattern.
3. **Scaffold by type**, copying the examples' structure:
   - **API endpoint:** controller, service and module in the appropriate directory. Follow the examples' auth guards, tenant filtering and serializer response.
   - **UI component:** component file with proper typing; props interface in a dedicated props file; export from the barrel.
   - **Shared package:** directory with `package.json`, barrel export `src/index.ts`, TypeScript config.
   - **Database model:** Prisma model plus migration; interface in the shared interfaces package; serializer in the shared serializers package if applicable.
4. **Apply critical rules:**
   - Interfaces live in dedicated files, not inline.
   - Use path aliases, not relative imports.
   - Add the tenant/organization filter to all queries, if the codebase uses one.
5. **Report** every file created and any manual steps needed.
