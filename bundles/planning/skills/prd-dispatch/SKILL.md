---
name: prd-dispatch
description: "Routes /prd prepare to complete issue preparation and retains focused requirements, planning, draft lint, intake, and discovery modes."
metadata:
  version: "2.2.2"
  tags: "prd, planning, dispatcher, requirements, spec, specification, ears, orchestration"
  author: Ship Shit Dev
when_to_use: "/prd, prepare a feature issue, write a PRD, plan a feature, validate a PRD, discovery interview"
user-invocable: false
---

# PRD Dispatch

Route the requested mode to a shared engine. Keep requirements templates,
implementation contracts and readiness logic in their owning engines.

## Contract

Inputs:

- Mode, rough request or issue reference, repository context, and authorized scope.

Outputs:

- Selected engine output; empty input returns usage without mutations. `spec` adds
  implementation evidence and delivery-gate state when implementation is authorized.

Creates/Modifies:

- Nothing directly; pass requested writes to the selected engine.

External Side Effects:

- Read-only context resolution. Delegated writes stay within existing authority.

Confirmation Required:

- None for routing. Preserve existing authorization, draft/report-only restrictions,
  and host/provider limits. Ask only when an engine identifies missing authority;
  do not introduce repeated approval between preparation stages.

Delegates To:

- `feature-intake` for `prepare` and `intake` (complete preparation pipeline).
- `prd-task-creator` for `new` (publish an issue or prepare a rough request first).
- `prd-writer` for `write` (requirements only).
- `writing-plans` for `plan` (resolve the implementation plan).
- `prd-quality-gate` for `gate` (blocking execution readiness) or `lint` (draft warnings).
- `feature-intake`, `prd-quality-gate`, and `executing-plans` for `spec` (prepare, gate,
  then execute within authorized scope; see Spec mode).
- Recommend `interview` for `interview` (explicit discovery workflow).

## Route

Parse the first argument as the mode and forward remaining context and constraints.
Run only that selected workflow. Empty input shows usage; unknown modes show an
error and usage without mutation.

For `prepare`, run the `feature-intake` skill through the whole pipeline: researched
requirements, settled implementation decisions, blocking readiness, publication
within scope, and saved-packet verification. The user supplies one rough request;
do not stop after requirements and ask them to invoke planning separately.

For `gate`, pass `execution-readiness`; for `lint`, pass `draft-lint`. A successful
lint result is never execution readiness. `write` intentionally stops at
requirements; `plan` intentionally stops at the current implementation plan.
`new` may file an explicitly requested draft, but a rough request intended for
execution receives full preparation through the shared coordinator.

## Spec mode

`spec` coordinates preparation, implementation, independent review and
verification on one shared issue contract. Use it before nontrivial implementation.
Keep requirements, decisions and steps on one issue, so the executor and
independent reviewer inspect the same source of truth. Existing implementation
authorization covers preparation and execution within the same scope; ask only for
missing consequential intent or expanded authority. A preparation-only request
stops after preparation. Repository merge/deployment permissions and required
review/CI gates still apply.

1. Read the live issue and current plan when supplied. Run the `feature-intake`
   skill if the packet is missing or needs preparation. That coordinator uses the
   canonical requirements and plan templates; do not create separate spec, todo
   and decisions files or force the user through three alternative approaches.
2. Run the `prd-quality-gate` skill in `execution-readiness` mode against current
   source and requirements. The planner repairs gaps and stale assumptions; the
   executor never receives authority to choose missing behavior or architecture.
3. If implementation is authorized and READY, run the `executing-plans` skill with
   the exact issue/current plan, scope, host restrictions, and required delivery
   gates. Follow the harness-selected executor; do not choose model or effort here.
4. Require implementation checks, full acceptance evidence, independent review by
   the other lab selected in harness policy, and required CI for the final PR
   commit. A plan review or self-review cannot substitute for implementation review.
   Missing review capacity remains visible and blocks completion.
5. Return unresolved decisions to the planner, code defects to prescribed repair,
   and unavailable access/checks to explicit blocked state. After code changes,
   refresh affected checks/review for the actual final revision.
6. Report the real delivery state. A feature is complete only when its entire
   acceptance contract and project delivery gates are fulfilled. Child/backend
   PR merges and a green subset of CI cannot close an incomplete feature or epic.

Scope proportionality: use a compact packet for bounded work; avoid a full PRD for
a typo or mechanical edit. Preserve the same decision and verification boundary. A
complete feature includes all necessary API, UI, wiring, migrations, tests, docs and
operational handoff in its issue; any split follows the shared independent-outcome
rule.

## Usage

```text
/prd                     Show usage
/prd prepare <request>   Prepare one complete execution-ready issue
/prd intake <request>    Same preparation pipeline, with requested board placement
/prd new <request>       Publish prepared work or prepare a rough execution request
/prd write <request>     Draft requirements only
/prd plan <issue>        Resolve implementation decisions on the same issue
/prd gate <issue>        Check blocking execution readiness and freshness
/prd lint <issue>        Warn about incomplete draft requirements
/prd spec <request>      Prepare and implement within authorized scope
/prd interview <topic>   Recommend the explicit discovery entry point
```
