---
name: prd-dispatch
description: "Routes /prd prepare to complete issue preparation and retains focused requirements, planning, draft lint, intake, and discovery modes."
metadata:
  version: "3.0.0"
  tags: "prd, planning, dispatcher, requirements, spec, orchestration"
  author: Ship Shit Dev
when_to_use: "/prd, create a PRD, plan a feature, write a spec, validate a PRD, feature intake, discovery interview, scope this out, write up this feature"
disable-model-invocation: true
---

# PRD Dispatch

Route the requested mode to a shared engine. Keep requirements templates,
implementation contracts and readiness logic in their owning engines.

## Contract

Inputs:

- Mode, rough request or issue reference, repository context, and authorized scope.

Outputs:

- Selected engine output; empty input returns usage without mutations.

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
- `spec-first` for `spec` (prepare and execute within authorized scope).
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
