---
name: codebase-design
description: Supplies shared deep-module vocabulary. Use when designing or improving a module interface, placing a seam, or making code more testable or AI-navigable.
license: MIT
metadata:
  version: "2.2.2"
  tags: "architecture, modules, seams, design, testability"
  author: Ship Shit Dev
  source: https://github.com/mattpocock/skills/blob/main/skills/engineering/codebase-design/SKILL.md
  upstream_repo: mattpocock/skills
  upstream_ref: main
  upstream_commit: 8b78b531ab96
  last_synced: "2026-08-14"
  license: MIT
when_to_use: "deepening opportunities"
---

# Codebase Design

Design **deep modules**: a lot of behaviour behind a small interface, placed at a
clean **seam**, testable through that interface. Use this language wherever code
is being designed or restructured. The aim is **leverage** for callers,
**locality** for maintainers, and testability for everyone.

This is the design language. `tech-debt` and `codebase-advisor` inventory;
`structural-review` judges a diff; this skill names the shape.

## Contract

Inputs:

- A module, interface, or cluster being designed or restructured

Outputs:

- Design decisions expressed in the glossary below
- Optional alternative interfaces via [references/DESIGN-IT-TWICE.md](references/DESIGN-IT-TWICE.md)

Creates/Modifies:

- None by default. Calling skills apply the design.

External Side Effects:

- None

Confirmation Required:

- None. Advisory vocabulary and design process.

Delegates To:

- None. `tdd`, `structural-review`, and `codebase-advisor` speak this vocabulary.

## Glossary

Use these terms exactly — do not substitute "component," "service," "API," or
"boundary." Consistent language is the whole point.

**Module** — anything with an interface and an implementation. Deliberately
scale-agnostic: a function, class, package, or tier-spanning slice.
_Avoid_: unit, component, service.

**Interface** — everything a caller must know to use the module correctly: the
type signature, plus invariants, ordering constraints, error modes, required
configuration, and performance characteristics.
_Avoid_: API, signature (too narrow — they refer only to the type-level surface).

**Implementation** — what's inside a module, its body of code. Distinct from
**Adapter**: a thing can be a small adapter with a large implementation (a
Postgres repo) or a large adapter with a small implementation (an in-memory
fake). Reach for "adapter" when the seam is the topic; "implementation" otherwise.

**Depth** — leverage at the interface: the amount of behaviour a caller (or test)
can exercise per unit of interface they have to learn. A module is **deep** when
a large amount of behaviour sits behind a small interface, **shallow** when the
interface is nearly as complex as the implementation.

**Seam** — a place where you can alter behaviour without editing in that place;
the _location_ at which a module's interface lives. Where to put the seam is its
own design decision, distinct from what goes behind it.
_Avoid_: boundary (overloaded with DDD's bounded context).

**Adapter** — a concrete thing that satisfies an interface at a seam. Describes
_role_ (what slot it fills), not substance (what's inside).

**Leverage** — what callers get from depth: more capability per unit of interface
they learn. One implementation pays back across N call sites and M tests.

**Locality** — what maintainers get from depth: change, bugs, knowledge, and
verification concentrate in one place rather than spreading across callers.

## Deep vs shallow

**Deep module** = small interface + lots of implementation.

**Shallow module** = large interface + little implementation.

When designing an interface, ask:

- Can I reduce the number of methods?
- Can I simplify the parameters?
- Can I hide more complexity inside?

## Principles

- **Depth is a property of the interface, not the implementation.** A deep module
  can be internally composed of small, mockable, swappable parts — they just
  aren't part of the interface. A module can have **internal seams** (private to
  its implementation) as well as the **external seam** at its interface.
- **The deletion test.** Imagine deleting the module. If complexity vanishes, it
  was a pass-through. If complexity reappears across N callers, it was earning
  its keep.
- **The interface is the test surface.** Callers and tests cross the same seam.
  If you want to test _past_ the interface, the module is probably the wrong shape.
- **One adapter means a hypothetical seam. Two adapters means a real one.**
  Introduce a seam when something actually varies across it.

## Designing for testability

Good interfaces make testing natural:

1. **Accept dependencies, don't create them.** Inject the payment gateway; skip
   constructing it inside the function.
2. **Return results, don't produce side effects.** Return a `Discount`; skip
   mutating `cart.total` in place.
3. **Small surface area.** Fewer methods = fewer tests needed. Fewer params =
   simpler test setup.

## Relationships

- A **Module** has exactly one **Interface** (the surface it presents to callers
  and tests).
- **Depth** is a property of a **Module**, measured against its **Interface**.
- A **Seam** is where a **Module**'s **Interface** lives.
- An **Adapter** sits at a **Seam** and satisfies the **Interface**.
- **Depth** produces **Leverage** for callers and **Locality** for maintainers.

## Rejected framings

- **Depth as ratio of implementation-lines to interface-lines** — rewards padding
  the implementation. Use depth-as-leverage instead.
- **"Interface" as the TypeScript `interface` keyword or a class's public
  methods** — too narrow.
- **"Boundary"** — overloaded with DDD's bounded context. Say **seam** or
  **interface**.

## Going deeper

- **Deepening a cluster given its dependencies** — [references/DEEPENING.md](references/DEEPENING.md)
- **Exploring alternative interfaces** — [references/DESIGN-IT-TWICE.md](references/DESIGN-IT-TWICE.md)
