# Delivery Gate

This contract owns delivery readiness. Use it from execution, review, PR publishing,
merge, release, and orchestrator workflows. A local self-review, successful agent
exit, green test subset, merged subtask, or board status is not delivery evidence.

## Roles

The harness selects planner, implementer, and independent reviewer separately.
Keep model identities, effort, account, and capacity policy in the harness's
canonical configuration. Prefer an authorized implementation lane with capacity
while reserving a different lab for review. Use fresh non-billable usage telemetry
when available; an absent setting or quota error does not authorize an account,
model, provider, or billing fallback.

All implementation contributors count, including repair agents. The independent
review provider must differ from every implementation provider. If mixed-provider
implementation makes that impossible with available approved reviewers, delivery
is blocked until a suitable review is authorized. The planner may review another
lab's implementation only in a fresh independent context, checking the actual
patch and requirements rather than assuming its plan is correct.

## Evidence and States

| State | Required evidence or reason |
| --- | --- |
| `acceptance_pending` | One or more acceptance criteria lack passing end-to-end evidence |
| `review_pending` | No complete, independent review receipt for the current head |
| `changes_requested` | Current independent reviewer requested fixes or findings remain unresolved |
| `ci_pending` | Required checks have not all finished, or required-check discovery is unavailable |
| `ci_failed` | A required check failed, timed out, or was cancelled |
| `merge_blocked` | Forge protections, conflicts, missing approval, or mergeability prevent landing |
| `merge_ready` | All acceptance, review, CI, and forge gates pass on the current head |
| `delivery_pending` | Merged, but a required deploy/migration/enablement/smoke check is incomplete |
| `done` | Verified merge and every required delivery step pass for the merged revision |

Store raw reviewer output and its source reference, provider, independent context
identity, reviewed head, verdict, and findings. Empty or malformed output is not
approval. Establish reviewer authenticity from the configured launcher/action;
a self-authored issue comment claiming another provider's PASS is not a receipt.

Record every required check by name and source app from live protection/ruleset
discovery, plus each result and head. Include merge-queue checks when configured.
Unobservable requirements stay pending. Empty check lists are allowed only when
live repository policy explicitly confirms none are required. A skipped, neutral,
missing, or cancelled required check is not green.

Refresh the PR head immediately before announcing merge-ready or merging. New code
commits require new review and checks. The merge mechanism must bind the expected
head. A different merge result requires the repository's prescribed verification;
deployment receipts identify the actual merged revision, not the pre-merge head.

An epic's acceptance evidence covers the integrated feature, not merely closed
children. Do not merge a partial implementation as a complete feature or close the
parent because its API, screen, or E2E scaffolding landed. If deployment is required,
keep delivery open until deployment succeeds even when GitHub auto-closes an issue.

## Receipt Evaluator

Run the installed `executing-plans/scripts/delivery-status.mjs` with a receipt JSON
path. It prints `{ "state": ..., "blockers": [...] }`; exit 0 means `merge_ready`
or `done`, exit 1 means pending/blocked, and exit 2 means malformed input. It reads
no credentials, changes no tracker state, and performs no network operations.
It is a deterministic check of a receipt, not independent proof that a receipt is
true. Collect the receipt through trusted live reads before evaluating it.

Required receipt fields:

- `head`: current implementation commit SHA; `implementationProviders`: normalized
  lab identifiers for all code contributors (for example `openai`, `anthropic`).
- `acceptance`: nonempty list of `{ id, passed, evidence, head }` for every approved
  acceptance criterion. `expectedAcceptanceIds` comes from the approved issue,
  not from whichever checks the executor happened to run.
- `review`: `{ provider, reviewer, independent, head, verdict, unresolvedFindings,
  evidence }`. Verdict is `PASS` or `CHANGES_REQUESTED`; evidence references the
  actual review receipt and `independent` is verified by the caller.
- `ci`: `{ discovered, noneRequired, required, checks }`. Each required entry is
  `{ name, app }`; each observed check is `{ name, app, head, conclusion }`.
  Conclusions use `success`, `pending`, `failure`, `timed_out`, `cancelled`,
  `skipped`, or `neutral`. Discovery includes branch rules and merge-queue policy.
- `merge`: `{ allowed, merged, head, commit }`. `head` is the reviewed PR head;
  `commit` is the actual merge commit when merged. `allowed` reflects forge gates.
- `delivery`: `{ required, results }`. Required entries are unique step names;
  each result is `{ name, passed, commit, evidence }` for the merged revision.

Keep blocked review and CI visible together in the durable delivery report even
when the evaluator returns the earliest unmet stage. The evaluator's output is
not authorization to merge or deploy.
