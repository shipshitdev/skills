# Triage Labels

Seed `docs/agents/triage-labels.md` with the repository's verified label strings and
board vocabulary. Preserve roles when labels are renamed; update local references
consistently without changing shared skill implementations.

## Shared Contracts

Resolve `executing-plans` and `prd-quality-gate` through the active skill catalog.
Read `references/delivery-gate.md` and `references/execution-readiness.md` relative
to their respective installed directories. For provisioned workflows, read
`.github/agent-dispatch.md` and use its pinned resources. Missing required contracts
block execution. These label descriptions do not replace those contracts.

## Label Vocabulary

| Label | Role |
| --- | --- |
| `claim:active` | One run owns the issue across all provider lanes; actual run state controls recovery. |
| `loop:planning`, `loop:executing`, `loop:testing`, `loop:shipping` | Activity within In Progress; not acceptance or completion evidence. |
| `priority:high`, `priority:medium`, `priority:low` | Queue ordering where these labels are the configured priority source. |
| `rejection:N` | Recorded review kickbacks; does not independently authorize retries. |
| `dispatch:plan` | Authorized OpenAI planner workflow; publish requirements/current plan and readiness, then stop without applying an execution gate. |
| `dispatch:claude` | Authorized Claude execution lane for a current READY issue. |
| `dispatch:codex` | Authorized Codex execution lane for a current READY issue. |
| `dispatch:openrouter` | Authorized OpenRouter transport lane; record the actual model lab for review independence. |
| `type:feature` | One complete feature outcome by default; technical layers are internal steps. |
| `wontfix` | Explicitly rejected work; preserve durable rationale where the repository tracks it. |

The harness owns model, effort, account and capacity routing. No implicit provider
fallback follows a quota error. At most one dispatch gate applies to an issue;
preparation does not grant implementation authority.

## Eligibility and Ownership

Intersect the execution gate with the verified Backlog item and satisfied
dependencies. Require the current prepared issue to pass metadata and semantic
execution-readiness checks. `AFK` means a passing contract with no outstanding
decisions or access blockers. Human-only (`HITL`) and planner-owned blockers stay
off execution gates; an explicitly authorized planning run may resolve planning
gaps but must stop at unresolved human intent.

Serialize claims across lanes. Confirm the run ended before explicit claim
recovery; an old timestamp never permits takeover. If ownership cannot be checked,
stop intake. Release only the current run's claim after a resumable handoff;
push-workflow agents leave workflow-owned finalization to that workflow.

## Handoff and Done

Status remains a native board field, commonly Backlog, In Progress, Human Review,
Done and Deferred. Keep delivery receipts separate from visual columns. Publishing
a PR with `Refs #<issue>` hands off as `review_pending`, commonly in Human Review.
A reviewer assignment or self-QA does not satisfy independent implementation review.

Done requires independent review of the actual implementation from a different
model provider/lab from every implementation contributor, green required CI at the
reviewed final head, verified merge and required deployment/migration/smoke evidence.
A new commit invalidates prior review and CI receipts. Unavailable review remains
blocked. Keep the epic open until every required child outcome and the integrated
feature satisfy the same acceptance and delivery gate. A partial or dependency PR
cannot close the complete feature.

Re-arm execution only within existing retry authorization, after resolving blockers,
verifying the previous run ended and explicitly recovering ownership. For paused
work, leave execution gates off and use the repository's Deferred state.
