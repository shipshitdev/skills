---
name: typescript-expert
description: "Solves TypeScript/JS problems: type-level programming, deep-instantiation errors, strict tsconfig, module resolution, JS-to-TS migration, Biome/ESLint/Nx tooling choices."
metadata:
  portable_source: "https://github.com/ericlitman/open-pstack"
  portable_commit: "56bfd14418fa733e34d98f714f357d28788470e3"
  category: framework
  risk: critical
  date_added: '2026-02-27'
  version: "2.2.2"
  tags: "typescript, javascript, tooling"
when_to_use: "type performance, monorepo config"
---

# TypeScript Expert

## When invoked

1. Analyze project setup comprehensively:

   **Prefer built-in file-reading and search capabilities for performance. Shell commands are fallbacks.**

   ```bash
   # Core versions and configuration
   bunx tsc --version
   node -v
   # Detect tooling ecosystem (prefer parsing package.json)
   node -e "const p=require('./package.json');console.log(Object.keys({...p.devDependencies,...p.dependencies}||{}).join('\n'))" 2>/dev/null | grep -E 'biome|eslint|prettier|vitest|jest|turborepo|nx' || echo "No tooling detected"
   # Check for monorepo (fixed precedence)
   (test -f pnpm-workspace.yaml || test -f lerna.json || test -f nx.json || test -f turbo.json) && echo "Monorepo detected"
   ```

   **After detection, adapt approach:**
   - Match import style (absolute vs relative)
   - Respect existing baseUrl/paths configuration
   - Prefer existing project scripts over raw tools
   - In monorepos, consider project references before broad tsconfig changes

2. Identify the specific problem category and complexity level

3. Apply the appropriate solution strategy from the expertise below

4. Validate thoroughly:

   ```bash
   # Fast fail approach (avoid long-lived processes)
   bun run typecheck || bunx tsc --noEmit
   bun run test || bunx vitest run --reporter=basic --no-watch
   # Only if needed and build affects outputs/config
   bun run build
   ```

   **Safety note:** Avoid watch/serve processes in validation. Use one-shot diagnostics only.

## Advanced Type System Expertise

### Type-Level Programming Patterns

**Branded Types for Domain Modeling** — nominal types (`type UserId = Brand<string, 'UserId'>`) prevent accidentally mixing domain primitives that share a base type. Use for critical domain primitives, API boundaries, currency/units. See `references/typescript-cheatsheet.md` (§ Branded Types) for the full pattern. Resource: https://egghead.io/blog/using-branded-types-in-typescript

**Advanced Conditional Types** — recursive type manipulation (e.g. `DeepReadonly<T>`) and template-literal event-source APIs. Use for library APIs, type-safe event systems, compile-time validation. Watch for type instantiation depth errors (limit recursion to 10 levels). See `references/typescript-cheatsheet.md` (§ Conditional Types, § Mapped Types, § Template Literal Types).

**Type Inference Techniques** — use `satisfies` (TS 5.0+) for constraint validation while preserving literal types; use `as const` assertions for maximum inference on literal arrays/objects. See `references/typescript-cheatsheet.md` (§ Best Practices).

### Performance Optimization Strategies

**Type Checking Performance**

```bash
bunx tsc --extendedDiagnostics --incremental false | grep -E "Check time|Files:|Lines:|Nodes:"
```

Common fixes for "Type instantiation is excessively deep": replace type intersections with interfaces, split large union types (>100 members), avoid circular generic constraints, use type aliases to break recursion.

**Build Performance Patterns**

- Enable `skipLibCheck: true` for library type checking only (often significantly improves performance on large projects, but avoid masking app typing issues)
- Use `incremental: true` with `.tsbuildinfo` cache
- Configure `include`/`exclude` precisely
- For monorepos: Use project references with `composite: true`

## Real-World Problem Resolution

### Complex Error Patterns

**"The inferred type of X cannot be named"**

- Cause: Missing type export or circular dependency
- Fix priority: export the required type explicitly; use `ReturnType<typeof function>` helper; break circular dependencies with type-only imports
- Resource: https://github.com/microsoft/TypeScript/issues/47663

**Missing type declarations** — add an ambient `.d.ts` module declaration for untyped packages. See `references/typescript-cheatsheet.md` (§ Module Declarations). For more detail: [Declaration Files Guide](https://www.typescriptlang.org/docs/handbook/declaration-files/introduction.html)

**"Excessive stack depth comparing types"**

- Cause: Circular or deeply recursive types
- Fix priority: limit recursion depth with conditional types; use `interface` extends instead of type intersection; simplify generic constraints

```typescript
// Bad: Infinite recursion
type InfiniteArray<T> = T | InfiniteArray<T>[];

// Good: Limited recursion
type NestedArray<T, D extends number = 5> =
  D extends 0 ? T : T | NestedArray<T, [-1, 0, 1, 2, 3, 4][D]>[];
```

**Module Resolution Mysteries** — "Cannot find module" despite the file existing:

1. Check `moduleResolution` matches your bundler
2. Verify `baseUrl` and `paths` alignment
3. For monorepos: Ensure workspace protocol (`workspace:*`)
4. Try clearing cache: `rm -rf node_modules/.cache .tsbuildinfo`

**Path Mapping at Runtime** — TypeScript paths only work at compile time, not runtime:

- ts-node: use `ts-node -r tsconfig-paths/register`
- Node ESM: use loader alternatives or avoid TS paths at runtime
- Production: pre-compile with resolved paths

### Migration Expertise

**JavaScript to TypeScript Migration** — incremental strategy: enable `allowJs`/`checkJs` in the existing tsconfig, rename files gradually (`.js` → `.ts`), add types file by file, enable strict mode features one by one. See `references/full-guide.md` (§ Migration Playbook) for the full command sequence and optional automated helpers (`ts-migrate`, `typesync`).

**Tool Migration Decisions**

| From | To | When | Migration Effort |
|------|-----|------|-----------------|
| ESLint + Prettier | Biome | Need much faster speed, okay with fewer rules | Low (1 day) |
| TSC for linting | Type-check only | Have 100+ files, need faster feedback | Medium (2-3 days) |
| Lerna | Nx/Turborepo | Need caching, parallel builds | High (1 week) |
| CJS | ESM | Node 18+, modern tooling | High (varies) |

### Monorepo Management

**Nx vs Turborepo Decision Matrix**

- Choose **Turborepo** if: Simple structure, need speed, <20 packages
- Choose **Nx** if: Complex dependencies, need visualization, plugins required
- Performance: Nx often performs better on large monorepos (>50 packages)

**TypeScript Monorepo Configuration** — root tsconfig `references` array plus `composite`/`declaration`/`declarationMap` per package. See `references/full-guide.md` (§ Monorepo TypeScript Configuration) for the full config.

## Modern Tooling Expertise

### Biome vs ESLint

**Use Biome when:** speed is critical, want a single tool for lint + format, TypeScript-first project, okay with 64 TS rules vs 100+ in typescript-eslint.

**Stay with ESLint when:** need specific rules/plugins, have complex custom rules, working with Vue/Angular (limited Biome support), need type-aware linting (Biome doesn't have this yet).

### Type Testing Strategies

**Vitest Type Testing (Recommended)** — write `.test-d.ts` files using `expectTypeOf` to assert on prop/return types at compile time. See `references/full-guide.md` (§ Vitest Type Testing) for a full example.

**When to Test Types:** publishing libraries, complex generic functions, type-level utilities, API contracts.

## Debugging Mastery

**CLI Debugging Tools** — trace module resolution (`tsc --traceResolution`), profile type-check performance (`tsc --generateTrace`), debug files directly with `tsx`/`ts-node --inspect-brk`. See `references/full-guide.md` (§ CLI Debugging Tools) for the full command set.

**Custom Error Classes** — extend `Error`, set `this.name`, and call `Error.captureStackTrace` to preserve the stack. See `references/full-guide.md` (§ Custom Error Classes) for the full pattern.

## Current Best Practices

### Strict by Default

Use `strict: true` plus `noUncheckedIndexedAccess`, `noImplicitOverride`, `exactOptionalPropertyTypes`, `noPropertyAccessFromIndexSignature`. See `references/tsconfig-strict.json` for a full production-ready strict config.

### ESM-First Approach

- Set `"type": "module"` in package.json
- Use `.mts` for TypeScript ESM files if needed
- Configure `"moduleResolution": "bundler"` for modern tools
- Use dynamic imports for CJS: `const pkg = await import('cjs-package')`
  - Note: `await import()` requires async function or top-level await in ESM
  - For CJS packages in ESM: may need `(await import('pkg')).default` depending on the package's export structure and compiler settings

### AI-Assisted Development

- AI coding assistants excel at TypeScript generics and boilerplate type definitions
- Validate AI-generated types with type tests
- Document complex types for AI context

## Code Review Checklist

### Type Safety

- [ ] No implicit `any` types (use `unknown` or proper types)
- [ ] Strict null checks enabled and properly handled
- [ ] Type assertions (`as`) justified and minimal
- [ ] Generic constraints properly defined
- [ ] Discriminated unions for error handling
- [ ] Return types explicitly declared for public APIs

### TypeScript Best Practices

- [ ] Prefer `interface` over `type` for object shapes (better error messages)
- [ ] Use const assertions for literal types
- [ ] Leverage type guards and predicates
- [ ] Avoid type gymnastics when simpler solution exists
- [ ] Template literal types used appropriately
- [ ] Branded types for domain primitives

### Performance Considerations

- [ ] Type complexity doesn't cause slow compilation
- [ ] No excessive type instantiation depth
- [ ] Avoid complex mapped types in hot paths
- [ ] Use `skipLibCheck: true` in tsconfig
- [ ] Project references configured for monorepos

### Module System

- [ ] Consistent import/export patterns, no circular dependencies
- [ ] Proper use of barrel exports (avoid over-bundling)
- [ ] ESM/CJS compatibility handled correctly, dynamic imports for code splitting

### Error Handling Patterns

- [ ] Result types or discriminated unions for errors
- [ ] Custom error classes with proper inheritance, type-safe error boundaries
- [ ] Exhaustive switch cases with `never` type

### Code Organization

- [ ] Types co-located with implementation
- [ ] Shared types in dedicated modules
- [ ] Avoid global type augmentation when possible
- [ ] Proper use of declaration files (.d.ts)

## Quick Decision Trees

```
"Which tool should I use?"
Type checking only? → tsc
Type checking + linting speed critical? → Biome
Type checking + comprehensive linting? → ESLint + typescript-eslint
Type testing? → Vitest expectTypeOf
Build tool? → Project size <10 packages? Turborepo. Else? Nx

"How do I fix this performance issue?"
Slow type checking? → skipLibCheck, incremental, project references
Slow builds? → Check bundler config, enable caching
Slow tests? → Vitest with threads, avoid type checking in tests
Slow language server? → Exclude node_modules, limit files in tsconfig
```

## Expert Resources

- Performance: [TypeScript Wiki Performance](https://github.com/microsoft/TypeScript/wiki/Performance), [Type instantiation tracking](https://github.com/microsoft/TypeScript/pull/48077)
- Advanced patterns: [Type Challenges](https://github.com/type-challenges/type-challenges), [Type-Level TypeScript Course](https://type-level-typescript.com)
- Tools: [Biome](https://biomejs.dev) (linter/formatter), [TypeStat](https://github.com/JoshuaKGoldberg/TypeStat) (auto-fix types), [ts-migrate](https://github.com/airbnb/ts-migrate) (migration toolkit)
- Testing: [Vitest Type Testing](https://vitest.dev/guide/testing-types), [tsd](https://github.com/tsdjs/tsd) (standalone type testing)

Always validate changes don't break existing functionality before considering the issue resolved.

## Typescript Best Practices procedure

Read [typescript-best-practices procedure](references/typescript-best-practices-procedure.md) when running this workflow.
Apply the authorized scope and mode of this entry point to every step.
Resolve other skills through this distribution’s active catalog; resolve
resources relative to the installed skill directory.
