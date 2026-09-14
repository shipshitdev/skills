# Execution Readiness Contract

Prepare one durable issue that an executor can implement without choosing product
behavior, architecture, contracts, scope, or verification policy. The planner owns
all decisions. The executor translates the settled contract into code and reports
gaps to the planner. Model, effort, account, and dispatch configuration belong to
the harness; this contract does not select them.

## Unit of Delivery

Default to one issue and one PR for one complete feature. Include every necessary
API, UI, integration, migration, test, configuration, documentation, and operational
change in that issue. Technical layers are ordered implementation steps, never
separate completion claims. A merged backend alone does not complete a feature
whose acceptance requires a working user flow.

Split only when each child delivers an independently useful, verifiable, complete
outcome and the split preserves the user's promised feature. Record why each child
can ship independently, cross-child dependencies, and parent acceptance coverage.
Keep the epic open until every parent criterion and integration obligation is
verified. An internal dependency PR may be needed for sequencing; label it as
partial delivery and keep feature completion blocked. Do not close the feature
from that PR's merge.

## Authority and Unknowns

Use repository evidence and existing authorization to resolve decisions during
preparation. Ask the user only for consequential intent, constraints, or authority
that cannot be inferred; ask the smallest necessary question and continue research
that does not depend on it. Never turn an uncertainty into an unstated assumption.

The planner chooses the approach, concrete interfaces, persistence, dependencies,
algorithms where behavior depends on them, error handling, UI states, compatibility,
migrations, and verification. Record alternatives only when they explain the
chosen decision. Do not hand options to the executor.

The executor has zero delegated product or engineering decision authority. Follow
the prescribed steps and named repository patterns for mechanical coding. If a
missing choice, incompatible pattern, unexpected dependency, failed assumption, or
scope expansion appears, stop the affected work and return the exact evidence and
question to the planner. Continue independent prescribed steps only when their
contracts remain valid. Never silently repair the plan, select a different library,
change acceptance criteria, or weaken a check.

## Canonical Storage and Identity

Keep requirements in the issue body and the current plan in a comment starting
with `## Implementation Plan` on that same issue. Link the current plan comment
from the body after publication. The body contains exactly one `Current plan: <comment URL>` line under its
Implementation Plan heading. Use one current plan revision; explicitly mark
prior revisions superseded. Read the body and all relevant comments, but never
combine contradictory historical plans. A local-only workflow uses one authorized
canonical document with both sections, not parallel copies in memory and docs.

Each plan records:

- Repository identity and inspected base commit SHA; include relevant dirty-state
  details when planning against uncommitted input. A dirty snapshot without a
  reproducible patch or commit is blocked for another executor.
- Plan revision, preparation date, and the requirements SHA256 defined below.
- Exact relevant existing paths and symbols plus evidence for at least three nearby
  patterns, or a documented inventory showing fewer exist. Label new paths/symbols
  as proposed; they must fit the observed architecture.
- Canonical plan link and readiness verdict once published.

For machine-readable dispatch, place these exact unbulleted lines immediately
after the `## Implementation Plan` heading (one occurrence of each):

```text
Plan revision: <positive integer>
Base commit: <40-character lowercase commit SHA>
Requirements SHA256: <64-character lowercase digest>
Readiness: READY
```

Use `Readiness: BLOCKED` while any readiness requirement fails. Compute the digest
from the current issue body: replace CRLF with LF, remove every whole line starting
with `Current plan:` followed by a space, join remaining lines with LF, trim leading/trailing whitespace,
then compute SHA256 of UTF-8 bytes. Adding the current-plan URL thus leaves the
digest unchanged. Recompute after any other requirements-body edit. Record the
date, repository identity, evidence and prior revision link below these fields.
The current-plan URL must select the exact plan comment, authored by an actor
trusted under the repository dispatch policy; older comments cannot override it.

Automated dispatch uses exact current default-branch HEAD matching for Base commit.
After branch drift, the planner revalidates and republishes with the current SHA,
even when the comparison found no relevant changes. For manual execution, compare
the actual target checkout and record equivalent freshness evidence.

Re-read the issue and compare the target checkout before dispatch. A changed
requirement, relevant source, dependency contract, or verification setup invalidates
readiness. The planner revalidates affected decisions and publishes an updated
revision. Unrelated repository changes may retain readiness only after a recorded
comparison shows the relevant evidence and assumptions still hold.

## Requirements Template

Use short sections for bounded work. Expand user stories, rollout detail, or
nonfunctional requirements only when they add information. A full PRD is optional;
the contract is mandatory for execution.

```markdown
# <Imperative feature title>

## Executive Summary
<Who needs what complete outcome and why.>

## Problem Statement
<Observed current behavior and evidence.>

## Goals
- <Observable desired outcome.>

## Scope
- In: <All work needed for that outcome.>
- Out: <Explicit exclusions.>

## Functional Requirements
- <Settled behavior, including relevant failure and edge conditions.>

## Acceptance Criteria
- AC-1: WHEN <trigger> THE SYSTEM SHALL <observable response>.
- AC-2: IF <failure condition> THEN THE SYSTEM SHALL <handled response>.

## Dependencies
<Named dependencies and their availability, or None.>

## Delivery Coverage
| Surface | Required change or evidenced N/A reason | Acceptance IDs |
| --- | --- | --- |
| API/data | <Change or N/A> | <IDs> |
| UI | <Change or N/A> | <IDs> |
| Integration | <Wiring and complete workflow or N/A> | <IDs> |
| Migration/configuration | <Compatibility, rollout and rollback or N/A> | <IDs> |
| Tests/docs/operations | <Required proof and user/operator handoff> | <IDs> |

## Verification Plan
<Required proof, current command sources, execution environment, and expected
results; detailed AC-to-step mapping lives in the implementation plan.>

## Open Decisions
<None when READY; otherwise exact question, evidence, owner, and blocked scope.>

## Implementation Plan
Current plan: <current plan comment URL after publication>
```

## Implementation Plan Template

```markdown
## Implementation Plan

Plan revision: <positive integer>
Base commit: <40-character lowercase commit SHA>
Requirements SHA256: <64-character lowercase digest>
Readiness: BLOCKED

### Identity
- Repository: <owner/repository>
- Prepared: <date and reproducible input state>
- Supersedes: <prior plan comment link, or None>

### Repository Evidence
| Path and symbol | Observed responsibility or pattern | Planned use |
| --- | --- | --- |
| <existing path::symbol> | <Observed evidence> | <Exact application> |

### Resolved Decisions and Contracts
- D-1: <Chosen behavior/approach, reason, exact contracts and constraints.>
- <Define relevant inputs/outputs, validation, failures, authorization, state,
  concurrency/idempotency, compatibility, and migration/rollback behavior.>

### Ordered Implementation Steps
- [ ] S-1: <Exact files/symbols to create or change, change to make, prescribed
  pattern, required prior steps, and observable completion condition.>
- [ ] S-2: <Next settled change, including complete cross-layer wiring.>

### Acceptance-to-Verification Mapping
| Acceptance ID | Decisions | Steps | Verification and command source | Expected result |
| --- | --- | --- | --- | --- |
| AC-1 | D-1 | S-1, S-2 | <Test/check, cwd, environment, exact command, source> | <Pass condition> |

### Blockers and Escalation
<None, or evidence + question + planner/user owner + blocked steps.>

### Delivery Gates
<Acceptance evidence, independent review route and result, required CI checks
at the final PR commit, merge/deployment requirements from project policy.>

### Readiness
<READY or BLOCKED; checked revision; evidence; remaining gaps.>
```

Specify implementation precisely without prewriting it. Include signatures, data
examples, decision tables, or concise pseudocode only where needed to remove
ambiguity. Do not include complete production code, complete test bodies, arbitrary
2–5 minute task limits, or a commit after every micro-step. The executor performs
coding work; the planner settles the decisions that govern it.

## Blocking Readiness Checklist

Every item must pass with evidence before declaring `READY`:

1. **Intent:** current behavior, complete desired outcome, exclusions, and stable,
   observable EARS acceptance criteria are stated without placeholders.
2. **Completion:** every required surface is covered; all acceptance criteria map to
   ordered steps and verification, including user/caller-facing integration.
3. **Decisions:** implementation choices and edge/failure behavior are settled.
   Open decisions are empty; external blockers are resolved or explicitly prevent
   dispatch. An accepted risk is not permission for an unspecified decision.
4. **Grounding:** inspected revision, paths, symbols, nearby patterns, dependencies,
   and new artifacts agree with the repository. Proposed artifacts are explicit.
5. **Execution:** each step names the change, inputs/dependencies, decision/pattern
   references, and finish condition. The executor need not research an approach.
6. **Verification:** commands come from inspected scripts, CI, or documented tooling;
   record working directory, required host/environment, fixtures, and observable
   pass conditions. Label new checks and specify how to add and invoke them using
   an existing runner. Never invent available scripts or claim an unrun check passed.
   Match test/coverage scope to the change and project policy; do not impose a
   universal percentage or require code tests for a pure documentation change.
7. **Freshness:** the selected plan matches current requirements and relevant source.
   Revalidate drift before dispatch; an old READY marker alone is insufficient.
8. **Delivery:** record required acceptance proof, independent implementation review
   by the other lab selected in harness policy, required CI at the final PR commit,
   and any project merge/deployment gates. Missing review capacity remains blocked;
   implementation, a plan review, or green CI alone is not delivery completion.

Publish draft work within authorized scope when useful. Keep blocked work in the
repository's non-runnable state. Set `AFK` only after READY; use `HITL` for human-only
blockers and identify planner-owned blockers separately. Tracker fields describe
state; they never replace evidence or authorize an executor to guess.
