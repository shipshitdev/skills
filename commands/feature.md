---
description: "Turn a rough requirement into one execution-ready feature issue with a plan and readiness verdict."
argument-hint: "<rough requirement>"
disable-model-invocation: true
---

# Feature - Prepare an End-to-End Feature

## Usage

```text
/feature <rough requirement>
```

`/feature help` prints this Usage block and stops without running anything.

Apply `feature-intake` with the request, target, existing authorization, and caller
restrictions. It composes requirements writing, implementation planning, readiness
validation, and issue creation. It owns no competing PRD template.

Default to one issue and one PR containing the complete feature, including every
required layer, integration, verification, migration, and delivery step. Split only
independently complete outcomes; keep the epic open until all promised behavior is
delivered. Ask only for consequential product information that existing context
cannot answer. Existing authorization covers the same tracker writes without a
repeated approval ceremony.

Return the issue, current plan, readiness verdict, and blockers. Preparation does
not silently start implementation or apply an execution dispatch gate.
