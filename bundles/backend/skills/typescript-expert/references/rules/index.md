
# TypeScript refactoring rules

43 rules across 8 categories for TypeScript refactoring and modernization, prioritized by impact to guide automated refactoring, code review, and code generation. Read the individual rule files for explanations and code examples; [_sections.md](_sections.md) defines the categories and impact levels, and [_template.md](_template.md) is the template for new rules.

Loaded from `typescript-expert` (formerly the separate `typescript-refactor` skill).

## When to Apply

- Refactoring TypeScript code for type safety and maintainability
- Designing type architectures (discriminated unions, branded types, generics)
- Narrowing types to eliminate unsafe `as` casts
- Adopting modern TypeScript 4.x-5.x features (`satisfies`, `using`, const type parameters)
- Optimizing compiler performance in large codebases
- Implementing type-safe error handling patterns
- Reviewing code for TypeScript quirks and pitfalls

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Type Architecture | CRITICAL | `arch-` |
| 2 | Type Narrowing & Guards | CRITICAL | `narrow-` |
| 3 | Modern TypeScript | HIGH | `modern-` |
| 4 | Generic Patterns | HIGH | `generic-` |
| 5 | Compiler Performance | MEDIUM-HIGH | `compile-` |
| 6 | Error Safety | MEDIUM | `error-` |
| 7 | Runtime Patterns | MEDIUM | `perf-` |
| 8 | Quirks & Pitfalls | LOW-MEDIUM | `quirk-` |

## Quick Reference

### 1. Type Architecture (CRITICAL)

- [`arch-discriminated-unions`](arch-discriminated-unions.md) — Use discriminated unions over string enums for exhaustive pattern matching
- [`arch-branded-types`](arch-branded-types.md) — Use branded types for domain identifiers to prevent value mix-ups
- [`arch-satisfies-over-annotation`](arch-satisfies-over-annotation.md) — Use `satisfies` for config objects to preserve literal types
- [`arch-interfaces-over-intersections`](arch-interfaces-over-intersections.md) — Extend interfaces instead of intersecting types for better error messages
- [`arch-const-assertion`](arch-const-assertion.md) — Use `as const` for immutable literal inference
- [`arch-readonly-by-default`](arch-readonly-by-default.md) — Default to readonly types for function parameters and return values
- [`arch-avoid-partial-abuse`](arch-avoid-partial-abuse.md) — Avoid `Partial<T>` abuse for builder patterns

### 2. Type Narrowing & Guards (CRITICAL)

- [`narrow-custom-type-guards`](narrow-custom-type-guards.md) — Write custom type guards instead of type assertions
- [`narrow-assertion-functions`](narrow-assertion-functions.md) — Use assertion functions for precondition checks
- [`narrow-exhaustive-switch`](narrow-exhaustive-switch.md) — Enforce exhaustive switch with `never`
- [`narrow-in-operator`](narrow-in-operator.md) — Narrow with the `in` operator for interface unions
- [`narrow-eliminate-as-casts`](narrow-eliminate-as-casts.md) — Eliminate `as` casts with proper narrowing chains
- [`narrow-typeof-chains`](narrow-typeof-chains.md) — Use `typeof` narrowing before property access

### 3. Modern TypeScript (HIGH)

- [`modern-using-keyword`](modern-using-keyword.md) — Use the `using` keyword for resource cleanup
- [`modern-const-type-parameters`](modern-const-type-parameters.md) — Use const type parameters for literal inference
- [`modern-template-literal-types`](modern-template-literal-types.md) — Use template literal types for string patterns
- [`modern-noinfer-utility`](modern-noinfer-utility.md) — Use `NoInfer` to control type parameter inference
- [`modern-accessor-keyword`](modern-accessor-keyword.md) — Use `accessor` for auto-generated getters and setters
- [`modern-verbatim-module-syntax`](modern-verbatim-module-syntax.md) — Enable `verbatimModuleSyntax` for explicit import types

### 4. Generic Patterns (HIGH)

- [`generic-infer-over-annotate`](generic-infer-over-annotate.md) — Let TypeScript infer instead of explicit annotation
- [`generic-constrain-dont-overconstrain`](generic-constrain-dont-overconstrain.md) — Constrain generics minimally
- [`generic-avoid-distributive-surprises`](generic-avoid-distributive-surprises.md) — Control distributive conditional types
- [`generic-mapped-type-utilities`](generic-mapped-type-utilities.md) — Build custom mapped types for repeated transformations
- [`generic-return-type-inference`](generic-return-type-inference.md) — Preserve return type inference in generic functions

### 5. Compiler Performance (MEDIUM-HIGH)

- [`compile-explicit-return-types`](compile-explicit-return-types.md) — Add explicit return types to exported functions
- [`compile-avoid-deep-recursion`](compile-avoid-deep-recursion.md) — Avoid deeply recursive type definitions
- [`compile-project-references`](compile-project-references.md) — Use project references for monorepo builds
- [`compile-base-types-over-unions`](compile-base-types-over-unions.md) — Use base types instead of large union types

### 6. Error Safety (MEDIUM)

- [`error-result-type`](error-result-type.md) — Use Result types instead of thrown exceptions
- [`error-exhaustive-error-handling`](error-exhaustive-error-handling.md) — Use exhaustive checks for typed error variants
- [`error-typed-catch`](error-typed-catch.md) — Type catch clause variables as `unknown`
- [`error-never-for-unreachable`](error-never-for-unreachable.md) — Use `never` to mark unreachable code paths
- [`error-discriminated-error-unions`](error-discriminated-error-unions.md) — Model domain errors as discriminated unions

### 7. Runtime Patterns (MEDIUM)

- [`perf-union-literals-over-enums`](perf-union-literals-over-enums.md) — Use union literals instead of enums
- [`perf-avoid-delete-operator`](perf-avoid-delete-operator.md) — Avoid the `delete` operator on objects
- [`perf-object-freeze-const`](perf-object-freeze-const.md) — Use `Object.freeze` with `as const` for true immutability
- [`perf-object-keys-narrowing`](perf-object-keys-narrowing.md) — Avoid `Object.keys` type widening
- [`perf-map-set-over-object`](perf-map-set-over-object.md) — Use `Map` and `Set` over plain objects for dynamic collections

### 8. Quirks & Pitfalls (LOW-MEDIUM)

- [`quirk-excess-property-checks`](quirk-excess-property-checks.md) — Understand excess property checks on object literals
- [`quirk-empty-object-type`](quirk-empty-object-type.md) — Avoid the `{}` type — it means non-nullish
- [`quirk-type-widening-let`](quirk-type-widening-let.md) — Prevent type widening with `let` declarations
- [`quirk-variance-annotations`](quirk-variance-annotations.md) — Use variance annotations for generic interfaces
- [`quirk-structural-typing-escapes`](quirk-structural-typing-escapes.md) — Guard against structural typing escape hatches
