---
name: prd-writer
description: "Authors repository-grounded requirements with complete feature scope and observable acceptance criteria. Reuses the canonical preparation contract; implementation planning is writing-plans."
metadata:
  version: "2.0.0"
  tags: "prd, planning, requirements, spec, scoping, ears"
when_to_use: "write a PRD for X, draft a PRD, scope this out, what should X do, formalize this feature, flesh out this issue before planning"
---

# PRD Writer

Write the requirements portion of the shared execution contract. Keep user intent
and observable behavior clear; implementation decisions belong in the plan on the
same issue. A bounded task needs a compact issue, not an inflated PRD.

## Contract

Inputs:

- Request, target repository/issue, available product context, and constraints.
- Draft versus publication mode and existing authorization.

Outputs:

- Requirements draft with current behavior, complete desired outcome, scope,
  EARS acceptance criteria, delivery coverage, dependencies, and verification needs.

Creates/Modifies:

- Requested canonical requirements document or authorized issue body.
- No implementation and no automatic decomposition.

External Side Effects:

- Read-only research; authorized requirements publication only.

Confirmation Required:

- Ask only for a missing destination, consequential intent, or write authority
  that cannot be resolved from the session. Existing same-scope authorization
  carries through. An orchestrator's draft mode produces a draft without writes.

Delegates To:

- `prd-quality-gate` for the canonical template and draft lint.
- `writing-plans` when invoked to plan settled requirements.
- Recommend `feature-intake` for complete preparation from a rough request.

## Workflow

1. Resolve the canonical destination from session/repository context. Prefer the
   existing tracker issue; use one local document only when that is the requested
   workflow. Search issues and PRs for duplicates before creating new work.
2. Read relevant product decisions, code, and existing behavior. Reuse established
   facts before asking questions. Distinguish observed requirements from inferred
   intent; resolve consequential uncertainties before claiming readiness.
3. Load the template from `prd-quality-gate` and its execution-readiness reference.
   Write a short imperative title. Fill each required section with concrete content;
   use stable acceptance IDs and EARS outcomes. Expand into a full PRD only when
   complexity warrants additional user stories or nonfunctional requirements.
4. Cover the entire feature, including required API, UI, wiring, migration, tests,
   docs and operational handoff. Record N/A reasons for absent surfaces. Do not
   convert technical layers into separate feature-completion issues.
5. State verification requirements based on repository practice. The planner will
   bind them to exact commands, files and expected results. Keep unresolved facts
   visible under Open Decisions; draft lint warnings do not grant readiness.
6. Run the `prd-quality-gate` skill in `draft-lint` mode. Return the requirements to
   the calling coordinator so planning continues without another user prompt.
   For a standalone requirements-only request, return/publish the draft within
   authorization and clearly say that execution readiness has not been checked.

## Updates and Planning

When asked to plan existing requirements, read the live issue body and relevant
comments, then run the `writing-plans` skill. A draft state does not prevent a
planner from resolving gaps; it prevents executor dispatch until READY.

When requirements change, invalidate the old plan/readiness and identify affected
acceptance criteria. Preserve settled decisions and unrelated user edits. Keep
native issue type, priority and board status in tracker fields; use the body for
content and the canonical current-plan link. Never silently mark a requirements
edit execution-ready because an older plan passed.
