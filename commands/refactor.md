---
description: "Improve existing code: strip slop, safe refactor, tech-debt register, perf, structure review, or stack modernization."
argument-hint: "[deslop|code|debt|perf|structure|stack] [target]"
disable-model-invocation: true
---

# Refactor - One Front Door for Improving Existing Code

Point it at what you want improved and it routes to the right engine: strip AI slop,
safely refactor, pay down debt, optimize, review structure, or modernize the stack —
frontend and backend.

## Usage

```bash
/refactor deslop [--changed|all|dry-run]  # strip AI slop — code + product (copy/UI/UX)
/refactor code [target]                   # safe, behavior-preserving refactor (test-locked)
/refactor debt                            # inventory + prioritize tech debt into a register
/refactor perf [target]                   # optimize: a component, an API, or the whole monorepo
/refactor structure [target]              # read-only structural/maintainability review
/refactor stack                           # modernize deps + framework-pattern drift
/refactor                                 # show what this repo most needs, then Usage
```

`/refactor help` prints this Usage block and stops without running anything.

## Modes

- **`deslop`** → the `deslop` skill. Removes AI artifacts (console logs, `any`, dead
  code, over-nesting), product slop (marketing-filler copy, default-shadcn UI,
  half-wired flows), and prose tells. Edits code. Default scope is the current
  package; `--changed` keeps it to the branch diff.
- **`code`** → the `refactor-code` skill — behavior-preserving refactor with tests
  locked first, drawing on `typescript-refactor` / `react-refactor` for language
  specifics.
- **`debt`** → the `tech-debt` skill — quantifies and ranks debt into a register, and
  files it as issues on request.
- **`perf`** → `performance-expert`, or `react-component-performance` for one slow
  component, or `workspace-performance-audit` for a whole monorepo. Diagnoses; you
  apply via `code`. This is the sole performance front door — the retired
  `/performance` command folded in here.
- **`structure`** → the `structural-review` skill — read-only structural lens (also
  reachable as `/review --structural`).
- **`stack`** → the `stack-modernization` skill — outdated dependencies, dead
  packages, and framework-pattern drift (v3 patterns in a v4 repo, and the like).

## Gates

- `deslop`, `code`, and `stack` edit source — prefer `--changed` on a branch so the
  change stays reviewable; whole-tree edits are confirmed first.
- `debt`, `perf`, and `structure` report only; they never touch source. `debt` files
  issues only after confirmation.
- To find bugs (not improve structure), use `/review` — this command improves code,
  it does not gate correctness.
