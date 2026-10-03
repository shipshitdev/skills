---
name: structural-review
description: >-
  Perform a structural and maintainability review of a PR or codebase diff —
  covering file-size blockers, abstraction quality, layer violations, type
  structural discipline, spaghetti branching, non-atomic mutations,
  stack-specific hygiene (Bun, Tailwind v4, Next.js 16, shadcn/ui), design
  purity (code-judo), and directness over magic (no speculative generality). Use when
  asked to review code quality, maintainability, structural health, or
  architecture of a change. Orthogonal to /code-review (which owns correctness
  bugs and repo rule compliance) — run after correctness passes or in parallel
  when a thorough PR review is requested.
metadata:
  version: "2.2.2"
  tags: "code-quality, maintainability, architecture, refactoring, structural"
  author: Ship Shit Dev
when_to_use: "structural review, maintainability review, code quality review, architecture review, thermo-nuclear review, code judo, simplify this PR, is this code clean, before merge review"
user-invocable: false
---

# Structural Review

Opinionated structural and maintainability review rubric. Report-only — this skill produces findings; it does not mutate files or open PRs.

## Core Principle

**Every structural finding must answer: "What exactly should the author delete, collapse, or rename — and which specific file/line is the canonical landing zone?"** Vague nits ("this could be cleaner") are noise. High-conviction, actionable findings only.

This rubric is explicitly complementary to `/code-review`. Do not re-flag correctness bugs or repo instruction-file rule violations already covered there. Own the orthogonal structural/maintainability/devex dimensions. Use `codebase-design` vocabulary (**module**, **interface**, **depth**, **seam**) when judging whether a change made a module deeper or shallower.

## Primary Review Questions

Ask these first, before scanning for individual issues:

1. **Does this PR make the codebase smaller or larger?** If larger: is each new abstraction earning its keep, or is it complexity added on faith?
2. **Where is the decision logic?** Is it in the canonical layer (server action, domain service, hook) or scattered across render trees and event handlers?
3. **Can a reader understand this module in isolation?** Or does understanding it require tracking state/logic across 4+ files?
4. **Is every new type structurally placed?** Or are bare `unknown`, and `as X` casts hiding future breakage, and are interfaces inlined where they should be in `*.types.ts`?
5. **Does the PR leave the stack cleaner than it found it?** Tailwind v3 debris, `npm` invocations, raw HTML in a shadcn project, `middleware.ts` in a Next.js 16 app — these are regressions, not style notes.

## Axes

### 1. File Size — The ~1000-Line Rule

A file crossing ~1000 lines is a **presumptive blocker**. It is not a hard numeric law but a strong prior that the module has taken on too many responsibilities.

**Flag when:**

- Any file touched by this PR is now >1000 lines.
- The PR itself adds enough lines to push a previously-marginal file over the threshold.

**Preferred remedy:** Split into colocated slices — `*.service.ts`, `*.queries.ts`, `*.types.ts`, `*.hooks.ts` — before the PR lands. Not after.

**Phrase:** "File is now 1 180 lines. Split the query layer into `*.queries.ts` before this ships — the 1 000-line rule exists exactly for PRs like this one."

**Severity:** Blocker.

### 2. Abstraction Earns Its Keep

Every new function, hook, class, or file must justify its existence. Thin wrappers, identity helpers, and passthrough re-exports fail this test unconditionally.

**Flag when:**

- A new helper is a one-liner rename or a call-through with no added invariants.
- A new file re-exports a symbol from another file without transformation.
- A hook wraps a single `useState` with no co-located logic.
- An interface is defined once and used once at the call site — inline it.

**Preferred remedy:** Delete the abstraction; inline the real symbol at the call site. Bun + TS path aliases make the original easy to reach.

**Phrase:** "This helper is an identity function over `formatDate` — inline it and delete the file. Code-judo."

**Severity:** Request Changes.

### 3. Spaghetti Branching

Ad-hoc forks bolted onto existing flows are the primary mechanism by which a clean codebase becomes unmaintainable.

**Flag when:**

- The same `if (isAdmin)` / `if (featureFlag)` / `if (isPremium)` fork appears in 2+ files changed by this PR.
- A new branch is added to an existing render function that already has 3+ conditional paths.
- Feature-flag forks are spread across component render paths instead of being resolved at a single decision point.

**Preferred remedy:** Collapse all branches into one canonical decision point — a hook for client state, a server action or domain service for mutations. Branches then disappear from the components.

**Phrase:** "Three `if (isAdmin)` forks scattered across the render tree. Collapse the decision into one hook or server action; the branches can then disappear from the component."

**Severity:** Request Changes.

### 4. Canonical Layer Discipline

In this stack, logic belongs in a specific layer. Violating the layer model is a structural defect, not a preference.

**Layer map:**

- **Mutations** → server actions or domain services. Not in raw `<form onSubmit>`, not in `useEffect`.
- **Derived client state** → hooks. Not recomputed inline in JSX.
- **Interactive elements** → shadcn/ui primitives or `packages/ui` components. Not raw `<button>`, `<input>`, `<dialog>`.
- **Route middleware** → `proxy.ts`. Not `middleware.ts` (Next.js 16).

**Flag when:**

- A mutation is wired directly to a DOM event handler when a server action exists in the project.
- A computation that could be a hook is inlined in JSX and repeated in 2+ components.
- A raw HTML element appears in a file that already imports from `packages/ui` or shadcn.

**Phrase:** "`<button onClick={...}>` in a component that already imports `Button` from `packages/ui` — swap it; raw HTML is a regression in this codebase."

**Severity:** Request Changes; Blocker when the element is a raw interactive element in a shadcn/packages/ui project.

### 5. Type Structural Discipline

This axis covers structural placement and shape issues — not `any` existence, which is owned by the `/code-review` harness.

**Violations (flag all):**

- Bare `unknown` without an adjacent type guard — this is deferred `any`, structurally equivalent to leaving the shape unresolved.
- `as X` casts without a comment explaining why the type system cannot infer the narrowing.
- Inline interfaces defined inside a component or service file — place in colocated `*.types.ts` or `packages/types`.

**Preferred remedy:** Define the shape in `*.types.ts`. Add the type guard at the boundary where the `unknown` enters.

**Phrase:** "Bare `unknown` without a type guard is deferred `any`. Define the shape in `*.types.ts` or add the guard here."

**Severity:** Bare `unknown` without guard → Blocker. Inline interface → Request Changes. `as X` without comment → Minor.

### 6. Non-Atomic Mutations

Sequential `await` calls that each write to the database are a correctness-adjacent structural defect. A crash between writes leaves the system in a half-written state.

**Flag when:**

- Two or more `await db.update()` / `await db.insert()` calls appear in the same function without a wrapping transaction.
- A function performs a write, then calls an external service, then does a second write — with no compensation/rollback path.

**Preferred remedy:** Wrap in a DB transaction or model as a single atomic write. If the external call cannot be inside a transaction, add explicit compensation logic.

**Phrase:** "These two `await db.update()` calls are non-atomic. A failure between them leaves the row in an invalid state — wrap in a transaction or model as a single atomic write."

**Severity:** Blocker.

### 7. Sequential Orchestration Smell

Functions that orchestrate 5+ sequential steps with no intermediate abstraction are a future maintenance hazard. They are hard to test, hard to reuse, and hard to understand in isolation.

**Flag when:**

- A new function has 5+ sequential `await` calls with no intermediate named steps or helper functions.
- A route handler or server action reads, transforms, validates, writes, and notifies — all inline.

**Preferred remedy:** Extract named phases. Each phase is testable in isolation. The orchestrator becomes a readable list of intents.

**Severity:** Request Changes.

### 8. Stack Hygiene (Hard Regressions)

These are not style notes — they are regressions introduced by the PR that must be fixed before merge.

| Issue | Rule | Phrase |
|---|---|---|
| `middleware.ts` created or left in place | Next.js 16 renamed the entry point to `proxy.ts`; the old name is silently ignored | "This is `middleware.ts`. Rename to `proxy.ts` — Next.js 16 renamed the entry point." |
| `tailwind.config.ts` or `tailwind.config.js` added | v4 uses CSS-based config (`@theme` in CSS); JS config is v3 | "`tailwind.config.ts` created by this PR — that's v3. Delete it and move the theme tokens into the CSS `@theme` block per v4." |
| `@apply` directive or `bg-opacity-*` class added | v3 patterns; must migrate to v4 slash syntax | Cite the exact line and the v4 equivalent. |
| `npm run`, `npx`, `yarn add`, `pnpm exec` in scripts, CI YAML, or docs | Bun is the only package manager; replace with `bun run` / `bunx` / `bun add` | "`npx prisma migrate` two lines below must be `bunx prisma migrate`." |

**Severity:** All Blocker.

### 9. Design Purity — Same Behavior, Cleaner Shape

The sharpest structural question is not "is this correct?" but "could this same
behavior be expressed with materially less structure?" A change that ships the
right behavior on top of avoidable complexity is a missed simplification, and
missed simplifications compound.

**Flag when:**

- A new state machine, config object, or branch tree encodes a decision that a
  single derived value or default would express.
- A special case is added where collapsing it into the general path (a sensible
  default, an early return) would delete the branch entirely.
- A refactor reshuffles code without reducing the number of moving parts a
  reader must hold at once.

**Preferred remedy:** Reframe the state model. Collapse the special case into a
default. Deletion and collapse beat polishing — "code-judo" the complexity
category out of existence rather than tidying it.

**Phrase:** "This three-state flag collapses to one derived boolean — the same
behavior with a whole branch deleted. Reframe rather than polish."

**Severity:** Request Changes (Blocker when the simpler form also removes a
correctness footgun).

### 10. Directness vs Magic

Prefer the obvious mechanism over the clever one. Over-generic abstractions,
hidden assumptions, and indirection that hides control flow cost more to read
than they save to write.

**Flag when:**

- A generic/parameterized mechanism is introduced for a single concrete caller
  ("speculative generality").
- Behavior depends on a hidden assumption — implicit ordering, a global, a
  naming convention, reflection/metaprogramming — that a reader cannot see at
  the call site.
- Indirection (dynamic dispatch, event indirection, deep config) replaces a
  direct call without an invariant that earns it.

**Preferred remedy:** Inline to the direct form for the one real caller. Make
the assumption explicit at the boundary, or remove the magic.

**Phrase:** "Generic registry for a single handler — delete it, call the handler
directly. Add the abstraction back when the second caller actually arrives."

**Severity:** Request Changes.

## What to Ignore

- Style preferences not rooted in a structural defect (indentation, naming micro-variations).
- Correctness bugs and test coverage gaps — these belong in `/code-review`.
- Security issues — these belong in `/security-audit`.
- Repo instruction-file rule violations already covered by the correctness review harness.
- Documentation gaps (inline docs, README updates) — off unless explicitly requested.
- Coverage percentage floors — flag missing tests for new critical paths only, not a specific number.

## Output Format

Order findings by severity:

```text
## Structural Review

### Blockers (must fix before merge)
[File-size violations, non-atomic mutations, stack regressions (middleware.ts, tailwind config, npm/yarn usage), bare unknown without guard, design-purity simplifications that also remove a correctness footgun]

### Request Changes (significant structural debt)
[Abstraction-earns-keep failures, canonical-layer violations, spaghetti branching, sequential orchestration smells, inline interfaces, missed design-purity simplifications, speculative generality / magic indirection]

### Minor (low-debt, flag for awareness)
[as X casts without comments, small layer suggestions with obvious inlines]

### Approved Axes
[Axes with no findings — confirm clean]
```

Include for each finding:

- **File + line range** (exact, not approximate).
- **One sentence** stating the structural defect.
- **One sentence** stating the specific remedy.
- A **reviewer phrase** (use the examples above or adapt them to the specific code).

## Approval Bar

Blocker and request-changes criteria are embedded in each axis above. **When ambiguous, default to Request Changes** — the ambiguity tax is paid by the author, not the codebase.
