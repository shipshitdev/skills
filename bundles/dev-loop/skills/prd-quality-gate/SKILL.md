---
name: prd-quality-gate
description: "Validates draft requirements and blocks execution until the same issue contains a complete, current implementation contract. Owns the shared preparation templates and readiness rules."
metadata:
  version: "2.0.0"
  tags: "prd, planning, validation, quality-gate, spec, requirements, ears"
---

# PRD Quality Gate

## Contract

Inputs:

- Requirements, implementation plan, target repository, and requested mode.
- Live issue body/comments and repository revision when execution is requested.

Outputs:

- `draft-lint`: warnings for incomplete requirements; never execution permission.
- `execution-readiness`: `READY` or `BLOCKED`, evidence for each check, and exact gaps.

Creates/Modifies:

- No implementation or tracker mutations; return findings to the calling engine.

External Side Effects:

- Read-only repository and tracker inspection.

Confirmation Required:

- None for read-only validation. Preserve the caller's access restrictions.

## One Shared Contract

Read [Execution readiness](references/execution-readiness.md) before validating or
supplying preparation templates. This reference owns the requirements template,
plan template, decomposition rule, decision boundary, and readiness checklist.
Resolve this skill through the active catalog; consumers load the reference
relative to this skill's installed directory. Do not maintain alternate copies.

Use `draft-lint` for an explicit requirements-only review. Check required headings,
nonempty scope and EARS acceptance criteria; report missing information as warnings.
Draft lint may help the planner continue research. It cannot mark an issue ready
for an executor, even if every heading is present.

Use blocking `execution-readiness` for `/prd prepare`, feature intake, execution
handoff, AFK classification, or any request to declare work ready for an agent.
An unspecified mode in one of those contexts means `execution-readiness`.
Otherwise default to `draft-lint` and label that limitation in the output.

## Validate Meaning and Evidence

Check actual behavior, complete decisions, repository evidence, verification
feasibility, and freshness. Headings and EARS grammar alone cannot establish
readiness. Read source files and command definitions; distinguish observed facts
from proposed changes. Fail unknowns that require an executor decision.

Accept numbered or checkbox acceptance bullets, removing their marker and optional
`AC-N:` prefix before checking EARS. Accept `WHEN`, `WHILE`, `WHERE`, `IF ... THEN`,
or `THE SYSTEM SHALL` forms with an observable response. Give each criterion a
stable ID for the plan-to-verification mapping. Reject subjective pass conditions
and criteria that merely repeat a heading.

Return the validation mode, verdict, issue/plan identity, inspected revision,
passed checks, and blockers with remediation owners. Missing or unavailable
checks are `BLOCKED`, never an inferred pass. A blocked draft may be saved within
authorized scope, but stays off the runnable path until the planner repairs it.
