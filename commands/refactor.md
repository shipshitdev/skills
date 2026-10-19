---
description: "Improve existing code: safe refactor, tech-debt register, perf, or stack modernization."
argument-hint: "[code|debt|perf|stack] [target]"
disable-model-invocation: true
---

# Refactor - One Front Door for Improving Existing Code

Point it at what you want improved and it routes to the right engine: strip AI slop,
safely refactor, pay down debt, optimize, or modernize the stack —
frontend and backend.

## Usage

```bash
/refactor code [target]                   # safe, behavior-preserving refactor (test-locked)
/refactor debt                            # inventory + prioritize tech debt into a register
/refactor perf [target]                   # optimize: a component, an API, or the whole monorepo
/refactor stack                           # modernize deps + framework-pattern drift
/refactor                                 # show what this repo most needs, then Usage
```

`/refactor help` prints this Usage block and stops without running anything.

## Modes

- **`code`** → the `refactor-code` skill — behavior-preserving refactor with tests
  locked first, drawing on `react-refactor` for language specifics.
- **`debt`** → the `tech-debt` skill — quantifies and ranks debt into a register, and
  files it as issues on request.
- **`perf`** → `performance-expert`, or `react-component-performance` for one slow
  component, or `workspace-performance-audit` for a whole monorepo. Diagnoses; you
  apply via `code`. This is the sole performance front door — the retired
  `/performance` command folded in here.
- **`stack`** → the `stack-modernization` skill — outdated dependencies, dead
  packages, and framework-pattern drift (v3 patterns in a v4 repo, and the like).

## Gates

- `code` and `stack` edit source — prefer a branch so the
  change stays reviewable; whole-tree edits are confirmed first.
- `debt` and `perf` report only; they never touch source. `debt` files
  issues only after confirmation.
- To find bugs (not improve structure), use `/review` — this command improves code,
  it does not gate correctness.
