# Prepared Issues and Verified Delivery

Give the preparation agent a rough request once. It researches the repository,
settles the requirements and engineering decisions, and creates a complete GitHub
issue that an execution agent can implement without choosing the design.

## One Preparation Entry Point

Use `/prd prepare <request>` or `/feature <request>`. `feature-intake` orchestrates
`prd-writer`, `writing-plans`, `prd-quality-gate`, and `prd-task-creator`. The engines
own different stages; intake no longer maintains its own templates or slice rules.

`prd-quality-gate/references/execution-readiness.md` is the shared preparation
contract. `executing-plans/references/delivery-gate.md` owns completion evidence.
Resolve both from installed skills, not a guessed consumer `skills/` directory.

Requirements live in the issue body. The current implementation plan lives in a
same-issue comment, bound to a plan revision, requirements fingerprint, and inspected
repository revision. The executor checks that those assumptions still hold.

The planner specifies affected files and interfaces, existing patterns, data shapes,
algorithms where consequential, error behavior, dependencies, ordered work, and
acceptance-linked verification. It does not write the implementation in Markdown.
Small contract examples are useful; complete proposed implementation files are not
a prerequisite for preparation.

## Complete Features

An issue promising saved searches includes the API, persistence, UI, wiring, and
verification needed to save and reopen a search. A PR containing only the API cannot
close that feature issue. Backend/frontend/E2E may be internal checklist items.

Use one issue and one delivery PR by default. Split a large epic only when each
child promises an independently complete outcome. Keep the parent open until all
its acceptance criteria work together. Required migrations, deployment, feature
flag enablement, and smoke checks stay part of delivery, not hidden follow-up work.

## Execution Authority

The executor translates settled decisions into code. It has no authority to choose
missing behavior, architecture, libraries, interfaces, or scope. A gap produces a
specific planning escalation with evidence and affected acceptance IDs. The planner
updates the issue and reruns readiness before execution resumes.

This controls decision authority; it does not promise that a model can never make
an error. Checks and independent review catch deviations. If planning repeatedly
fails to eliminate decisions, improve the preparation contract or use a stronger
implementation lane explicitly rather than letting the cheaper agent improvise.

## Models and Capacity

Configure preparation, implementation, and review roles in the harness. Public
skills do not hard-code model names or effort. Select the capable planning role for
decisions and an approved economical executor for settled work. Reserve a frontier
reviewer from a different implementation lab. Another model from the same lab does
not satisfy independent review.

Use actual available capacity when exposed; never infer subscription usage or
relative costs from a model name. No automatic account probing or silent fallback.
A missing reviewer blocks delivery even when implementation and PR publication
succeed. See `.github/agent-dispatch.md` for the optional repository dispatch setup.

For a tiny task, planning and implementing in one capable session may use less total
work than a handoff. For substantial repeatable work, measure the split: preparation
usage, implementation usage, review/repair usage, first-pass acceptance, and planning
escalations. Compare representative completed tasks against direct implementation.
A static skills audit cannot prove cost savings or perfect execution.

## Delivery States

A PR can be published while review or CI is pending. Merge-ready requires current
acceptance evidence, a different-lab independent review PASS on the current head,
resolved findings, green required CI, and passing forge protections. A new code
commit invalidates old review and CI evidence.

Done additionally requires a verified merge and all planned post-merge delivery
steps. The receipt evaluator shipped with `executing-plans` checks these states
without changing GitHub. Its input must come from trusted live observations; it
does not authenticate a self-reported PASS.

## Provenance

`feature-intake` was introduced as a Shipshit orchestration skill in commit
`c2ec4a1`. The repository separately adopted selected Matt Pocock patterns; that
does not make intake a copy of a Pocock skill. `writing-plans` is attributed to
obra/superpowers and adapted here. Pstack is a separate orchestration integration
that now honors the same prepared-issue and delivery contracts.
