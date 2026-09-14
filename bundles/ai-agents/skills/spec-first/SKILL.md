---
name: spec-first
description: "Coordinates preparation, prescribed implementation, independent review and verification using one shared issue contract. Use for nontrivial implementation that needs decisions settled before coding."
metadata:
  version: "2.0.0"
  tags: "specification, planning, execution, ears"
---

# Spec-First Development

Use the shared preparation contract before nontrivial implementation. Keep
requirements, decisions and steps on one issue, so the executor and independent
reviewer inspect the same source of truth.

## Contract

Inputs:

- User request, repository, existing issue/plan, and authorized delivery scope.

Outputs:

- Execution-ready issue or concrete planning blockers.
- When implementation is authorized, implementation evidence and delivery-gate state.

Creates/Modifies:

- Requested preparation packet, implementation, and delivery artifacts through
  delegated engines within the caller's scope.

External Side Effects:

- Authorized tracker/repository operations only; inherit all access and host limits.

Confirmation Required:

- Existing implementation authorization covers preparation and execution within
  the same scope. Ask only for missing consequential intent or expanded authority.
  A preparation-only request stops after preparation. Repository merge/deployment
  permissions and required review/CI gates still apply.

Delegates To:

- `feature-intake` for requirements plus resolved implementation planning.
- `prd-quality-gate` for blocking execution readiness and freshness validation.
- `executing-plans` for prescribed implementation and delivery evidence.

## Workflow

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

## Scope Proportionality

Use a compact packet for bounded work; avoid a full PRD for a typo or mechanical
edit. Preserve the same decision and verification boundary. A complete feature
includes all necessary API, UI, wiring, migrations, tests, docs and operational
handoff in its issue; any split follows the shared independent-outcome rule.
