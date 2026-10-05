---
description: "Prepare work for agents: turn a request into an execution-ready issue with requirements, plan, and readiness gate."
argument-hint: "[prepare|intake|write|new|plan|lint|gate|spec|interview] <request|issue>"
disable-model-invocation: true
---

# Prd - Prepare Work for Agents

Use `/prd prepare <request>` to turn a rough request into an execution-ready issue
with settled requirements, an implementation plan, and a blocking readiness check.
Preparation finishes before implementation begins.

## Usage

```text
/prd prepare <request>  # prepare the complete issue and implementation contract
/prd intake <request>   # the same preparation with stakeholder/board context
/prd write <request>    # requirements only; not execution-ready
/prd new <request>      # file settled work through the task-creation engine
/prd plan <issue>       # resolve implementation decisions on the same issue
/prd lint <issue>       # warning-only draft requirements lint
/prd gate <issue>       # check readiness; draft lint never authorizes execution
/prd spec <request>     # apply the shared specification and planning contract
/prd interview <topic>  # discover missing product requirements
/prd                   # read-only status and usage
```

`/prd help` prints this Usage block and stops without running anything.

## Workflow

Parse the first argument as the mode, forward the remaining context and constraints,
and run only that workflow. Pass the existing authorization, draft/report-only
restrictions, and host/provider limits to the engine. Ask only when an engine
identifies missing authority; do not add approval steps between preparation stages.
Empty input shows usage; an unknown mode shows an error and usage without mutation.

| Mode | Engine |
|---|---|
| `prepare`, `intake` | Run the `feature-intake` skill through the whole pipeline: researched requirements, settled implementation decisions, blocking readiness, publication within scope, and saved-packet verification. The user supplies one rough request; do not stop after requirements and ask them to invoke planning. `intake` adds the requested board placement. |
| `new` | Run the `prd-task-creator` skill to publish prepared work, or an explicitly requested draft. A rough request meant for execution first gets full preparation through `feature-intake`. |
| `write` | Run the `prd-writer` skill; it stops at requirements. |
| `plan` | Run the `writing-plans` skill; it stops at the current implementation plan. |
| `gate` | Run the `prd-quality-gate` skill in `execution-readiness` mode. |
| `lint` | Run the `prd-quality-gate` skill in `draft-lint` mode. A successful lint is never execution readiness. |
| `spec` | Prepare, gate, then implement within authorized scope (see below). |
| `interview` | Recommend the `interview` skill, the explicit discovery entry point. |

### Spec mode

Use before nontrivial implementation. Keep requirements, decisions, and steps on one
issue so the executor and the independent reviewer inspect the same source of truth.
Existing implementation authorization covers preparation and execution within the
same scope; a preparation-only request stops after step 2.

1. Read the live issue and current plan when supplied. Run the `feature-intake` skill
   if the packet is missing or needs preparation. Do not create separate spec, todo,
   and decisions files.
2. Run the `prd-quality-gate` skill in `execution-readiness` mode against current
   source and requirements. The planner repairs gaps; the executor never chooses
   missing behavior or architecture.
3. If implementation is authorized and the gate says READY, run the `executing-plans`
   skill with the exact issue and plan, scope, host restrictions, and delivery gates.
4. Require implementation checks, full acceptance evidence, independent review by the
   other lab chosen by harness policy, and required CI for the final PR commit.
   Missing review capacity stays visible and blocks completion.
5. Return unresolved decisions to the planner, code defects to prescribed repair, and
   unavailable access to an explicit blocked state; refresh affected checks for the
   actual final revision.
6. Report the real delivery state. A feature is complete only when its whole
   acceptance contract and project delivery gates are met.

Use a compact packet for bounded work; a typo or mechanical edit does not need a full
PRD.

Complete the feature end to end in one issue/PR by default. Internal API, UI, and
verification tasks do not count as finished features. Preparation settles all
product and engineering decisions. Executors escalate gaps to the planner instead
of inventing answers. Model and effort selection belong to the harness.
