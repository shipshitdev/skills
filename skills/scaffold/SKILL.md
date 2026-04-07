---
name: scaffold
description: Generate new code modules following existing codebase patterns. Use when user says 'scaffold', 'generate', 'create new endpoint', 'new component', or 'new module'.
version: 1.0.0
tags:
  - scaffolding
  - code-generation
  - boilerplate
  - productivity
---

# Scaffold

Generate new code following existing codebase patterns.

## Steps

1. **Determine what to scaffold** from arguments:
   - `endpoint [name]` — New API endpoint (controller + service + module)
   - `module [name]` — New backend module with full structure
   - `component [name]` — New UI component with proper typing
   - `package [name]` — New shared package
   - `collection [name]` — New database collection with schema + service

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

   ### Database Collection

   - Schema/model file
   - Interface in shared interfaces package
   - Serializer in shared serializers package (if applicable)

4. **Apply critical rules**:
   - Interfaces in dedicated files, not inline
   - Path aliases, not relative imports
   - Tenant/organization filter in all queries (if applicable)

5. **Report**: List all files created and any manual steps needed

## Arguments

- Required: what to scaffold (e.g., "endpoint tasks", "component ImageGrid", "collection workflows")
