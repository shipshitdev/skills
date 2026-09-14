# The Prepared AI Dev Loop

last_verified: 2026-09-14

Prepare one complete feature issue, implement its settled decisions, and track
actual delivery. The issue body holds requirements; its `Current plan:` pointer
selects one authoritative `## Implementation Plan` comment bound to requirements
and source revision. A PR is an implementation handoff, not feature completion.

## Canonical Contracts

- `.github/agent-dispatch.md` owns the provisioned planning/execution workflow prompt.
- `executing-plans` owns execution and its `references/delivery-gate.md` owns delivery.
- `prd-quality-gate` owns `references/execution-readiness.md`, including templates,
  fingerprint/revision rules and the blocking semantic readiness check.

Resolve skills through the active catalog and references relative to their installed
directories. In provisioned workflows, use the setup-pinned `.github/agent-skills/`
copy verified by preflight; this source repository exposes them under `skills/`.
Do not assume a consumer checkout has the source repository layout. Missing required
resources block the run. This page is an operator map, not another execution script.

## Roles and Entry Points

| Stage | Entry point | Responsibility |
| --- | --- | --- |
| Prepare | `/prd prepare`, `feature-intake` | Research requirements, resolve every implementation decision, validate and publish the complete issue. |
| Queued planning | `dispatch:plan`, `plan-dispatch.yml` | OpenAI planner; publish the current plan and readiness verdict, then stop at the existing execution-authorization boundary. |
| Implement | `/loop`, `/codex-loop`, or an authorized execution gate | Run `executing-plans` against the current prepared issue; escalate missing decisions. |
| Review | Separately configured independent reviewer | Review actual implementation and acceptance evidence from another model provider/lab. |
| Deliver | Repository delivery gate | Verify acceptance, independent review, required CI, merge and deployment evidence. |

The harness owns model, effort, account and capacity routing. `dispatch:plan` uses
the OpenAI planning workflow; it has no implicit usage-based provider fallback.
The execution gates are `dispatch:claude`, `dispatch:codex` and
`dispatch:openrouter`; the last identifies transport, so record the actual model
lab for review independence. At most one dispatch gate applies to an issue.
Preparation and execution authorization are separate; do not auto-apply an execution
gate merely because preparation passed.

## Intake and Ownership

For one authorized invocation, intersect the selected execution gate with the
verified Backlog item in the target repository. Inspect current requirements,
selected plan, dependencies and claims. Metadata preflight and semantic readiness
must both pass; no missing plan or open decision is delegated to the executor.
Read-only status/list requests perform no mutations.

Serialize claims across all lanes and inspect actual run ownership. Confirm the run
ended before explicit claim recovery. Elapsed time, an old timestamp, or a rate-limit
error alone does not prove another owner has stopped. If ownership or board state
cannot be verified, leave the issue unclaimed. Preserve interrupted work and record
a resumable handoff. A push workflow owns its claim/finalization; the dispatched
agent does not claim again or clear the workflow's labels.

## Delivery State

Board Status is the human-facing location: Backlog, In Progress, Human Review,
Done or Deferred. `loop:*` labels show activity; neither labels nor column placement
prove delivery. Record the exact implementation head and delivery receipt.

| State | Required evidence or next action |
| --- | --- |
| `blocked` | Missing intent, stale plan, access, ownership or required review capacity; identify the owner and remedy. |
| `review_pending` | Implementation PR published with `Refs #<issue>` and current plan revision; independent review still required. |
| `ci_pending` | Review and acceptance evidence recorded; required checks still pending or failing. |
| `merge_ready` | Complete acceptance, different-lab review PASS at the final head, findings resolved, green required CI and repository protection gates satisfied. |
| `delivery_pending` | Merge verified; required deployment, migration, enablement or smoke evidence remains. |
| `done` | Merge and all planned delivery obligations verified, including complete integrated feature/epic acceptance. |

Independent review must come from a different model provider/lab from every
implementation contributor and examine the actual diff. Self-QA, another model
from the same lab, a plan review, reviewer assignment or a review request is not
that evidence. New commits invalidate prior review/CI receipts; refresh them for
the actual final head. Unavailable review stays blocked, never an invented PASS.

Done requires green required CI plus independent implementation review, verified
merge and required deployment/migration/smoke evidence (or an explicit prepared
N/A decision). Keep an epic open until every required child outcome and integrated
feature passes the same gate. Use references in implementation PRs to avoid closing
work before post-merge delivery. Merge-ready is evidence, not authority to merge.

## Setup and Recovery

Run the repository's `setup-dev-loop.sh` under existing setup authorization to
provision its board, labels, pinned workflow contracts and resources. Use
`setup-agent-routing` to generate the consumer tracker/domain documentation.
Inspect the resulting configuration and separately provision the independent
review route and protected-branch checks. The dispatch workflows prepare and
implement; they do not themselves supply independent review or branch protection.

After a failed or interrupted run, inspect its actual state and preserve evidence.
Resolve planning gaps through the planner; revalidate changed plans before a new
execution. Re-arm a gate only within existing retry authorization, after the prior
run has ended and claim recovery is explicit. Do not probe accounts or silently
change providers to bypass missing capacity.
