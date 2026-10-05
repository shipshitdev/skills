---
name: tdd
description: Drives feature work and bug fixes test-first with red-green-refactor and vertical slices. Use for TDD, test-first implementation, or regression-first fixes.
license: MIT
metadata:
  portable_source: "https://github.com/ericlitman/open-pstack"
  portable_commit: "1b03678171f6f400ae2cc9dc4e7a4a6a13e4bb43"
  version: "2.2.2"
  tags: "testing, tdd, red-green-refactor, quality, verification"
  author: Ship Shit Dev
  source: https://github.com/mattpocock/skills/blob/main/skills/engineering/tdd/SKILL.md
  upstream_repo: mattpocock/skills
  upstream_ref: main
  upstream_commit: 8b78b531ab96
  last_synced: "2026-09-05"
  license: MIT
when_to_use: "failing test first"
---

# Test-Driven Development

Build or fix behavior one verified slice at a time. A cheap local test path
writes the failing check first. An expensive or unclear path names why and uses
the closest executable proof instead.

## Contract

Inputs:

- Feature request, bug report, PRD, issue, or implementation plan
- Existing test commands and project conventions
- Public interface or user-facing behavior to protect

Outputs:

- Test-first implementation plan when a cheap path exists
- New or updated tests and code when implementation is requested
- Verification commands and the failing-before / passing-after evidence

Creates/Modifies:

- Test files and production code needed for the requested behavior
- No unrelated refactors or broad test-suite rewrites

External Side Effects:

- None by default
- Do not use production data or live external writes for tests

Confirmation Required:

- Before changing public APIs, schemas, migrations, or user-visible behavior beyond the request

Delegates To:

- `testing-expert` for broad test strategy or framework setup
- `testing-expert` (AI regression mode) for bug-specific regression coverage and path parity
- `debug` when the root cause is still unknown
- `codebase-design` when the test boundary is a module **seam** that still needs shaping
- `verification-before-completion` when about to claim the work is done

## Cheap-path gate

Write a new test only when the path is cheap and local:

- A focused unit, component, or existing integration check for that codepath
- Deterministic, fast enough to rerun, and free of production-only state
- Encodes intended behavior, not the current broken implementation

Skip a new test when it would need broad harness setup, brittle mocks, slow
end-to-end infrastructure, vague reproduction steps, or large unrelated fixture
churn. Prefer no new test over a bad one.

A bad test mostly tests mocks, encodes implementation details, depends on
timing or unrelated global state, needs expensive infrastructure for a small
fix, or would be deleted immediately after proving the fix.

Do not skip silently. Before changing production code, name why a failing test
is not worth the cost and name the closest executable check: a targeted script,
reproduction command, browser drive, snapshot comparison, log assertion, or
focused integration check.

## Core Rule

Write one failing behavior test, make it pass, then refactor. Repeat.

Tests should verify behavior through public interfaces. They should survive an
internal refactor. If a test fails because a private helper was renamed while
the behavior still works, the test is too coupled to implementation.

## Before Writing Tests

1. Find at least 3 existing tests or implementations that match the local pattern.
2. Identify the highest useful test boundary: user flow, route, service API, CLI, or pure function.
3. State the behavior in user or caller language.
4. Choose the narrowest command that runs the new test.
5. List only the first 1-3 behaviors needed for a useful vertical slice.

Ask only when the public behavior or interface is genuinely unclear. Otherwise
make a conservative assumption and proceed.

## Red-Green-Refactor Loop

### 1. Red

Add one test for one observable behavior.

The test must fail for the right reason:

- It exercises the public behavior, not a private detail.
- It fails because the behavior is missing or broken.
- It is deterministic and small enough to run repeatedly.

Run the new test before changing production code. If it passes or fails for an
unrelated reason, fix the test or the reproduction first.

### 2. Green

Write the smallest production change that makes the test pass.

Do not add speculative options, future branches, or unrelated cleanup while the
test is red.

### 3. Refactor

After the test passes:

- Remove duplication.
- Improve naming around the domain language already used in the repo.
- Move complexity behind clearer interfaces only when the current slice proves it is needed.
- Re-run the narrow test after each refactor step.

## Vertical Slices

Prefer thin end-to-end slices over horizontal batches.

Good:

- One behavior test
- One implementation path
- One verification command
- A demoable or inspectable outcome

Bad:

- All tests first, then all implementation
- Tests for imagined data structures before behavior exists
- Mocking internal collaborators just to fit a planned design
- Splitting work by layer when no slice is independently useful

## Bug Fixes

For bugs, reproduce first. If the cause is unknown, use `debug`.

When the cause is known and the cheap-path gate passes:

1. Convert the reproduction into a failing regression test.
2. Verify the test fails on the broken behavior.
3. Fix the behavior.
4. Verify the regression test passes.
5. Re-run the original reproduction or user flow.

Stage the failing repro before the fix in git history when committing. The
diff tells the story: red, then green.

If there is no good test boundary, state that as a design finding. Add the best
available verification and note the residual risk.

## Guardrails

- Do not change tests merely to match a wrong implementation.
- Do not weaken existing assertions unless the expected behavior has genuinely changed.
- Keep the regression test focused on the bug. Avoid broad fixture churn.
- If the bug is flaky, make the test deterministic where possible and document the locked signal.
- If the bug exposes a broader class of failures, land the focused path first, then consider sibling coverage.

## Mocking Rules

- Mock network, time, randomness, payment providers, email, storage, and other external systems.
- Avoid mocking code owned by the module under test.
- Prefer fakes or fixtures when they keep behavior realistic.
- Do not assert implementation calls unless the call itself is the public contract.

## Done Checklist

- [ ] New behavior is covered by at least one failing-then-passing test, or the skip is named with the closest check.
- [ ] Test name describes the behavior, not the implementation.
- [ ] Test uses the public interface available to callers or users.
- [ ] Narrow verification command passes.
- [ ] Relevant broader suite, typecheck, or lint command passes when practical.
- [ ] No unrelated refactor or broad rewrite was bundled into the slice.

## Final Response

Report the evidence, not just the outcome:

- Name the failing-before test or executable check and the failure it produced.
- Name the passing-after run and any nearby validation performed.
- If failing-before evidence could not be demonstrated, state why and describe the closest regression check used instead.

## Tdd procedure

Read [tdd procedure](references/tdd-procedure.md) when applying the cheap-path gate and vertical-slice contract above.
Apply the authorized scope and mode of this entry point to every step.
Resolve other skills through this distribution’s active catalog; resolve
resources relative to the installed skill directory.
