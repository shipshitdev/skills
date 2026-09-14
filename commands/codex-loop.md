# Codex Loop — Execute one prepared issue

Run the `executing-plans` skill for one explicitly authorized `dispatch:codex`
issue. This is the local Codex entry point; the selected harness owns model,
effort, account, checkout and approval configuration.

## Usage

```text
/codex-loop            Execute one eligible prepared issue
/codex-loop --status   Show current ownership and delivery state; read-only
/codex-loop --list     List eligible queue candidates and blockers; read-only
```

## Contract

Resolve `executing-plans` through the active skill catalog and read its installed
`references/delivery-gate.md`. Resolve `prd-quality-gate` and its installed
`references/execution-readiness.md` the same way. If the repository has the
provisioned `.github/agent-dispatch.md`, read that shared dispatch contract too.
Missing required resources block execution; never reconstruct a weaker contract
from this command or assume the consumer contains this source repository.

- For `--status` or `--list`, inspect only. Do not claim, comment, edit or dispatch.
- Otherwise, process exactly one candidate with the selected gate and verified
  Backlog state, satisfied dependencies and a current prepared plan. Run the
  blocking semantic execution-readiness check before editing. A label or an old
  READY marker alone is insufficient.
- Serialize ownership across provider lanes. Confirm the run ended before explicit
  claim recovery; elapsed time never authorizes takeover. If ownership cannot be
  verified, stop intake. An already claimed push-workflow run owns its own claim.
- Implement the selected issue revision without making product or engineering
  decisions. Return missing or contradictory decisions to the planner.
- Publish the PR with `Refs #<issue>` and the current plan link/revision. Record
  acceptance evidence and the actual implementation provider, then hand off as
  `review_pending`. Self-QA and reviewer assignment do not satisfy independent review.
- Done requires independent review by a different model provider/lab from every
  implementation contributor, green required CI at the reviewed final head,
  verified merge, and required deployment/migration/smoke evidence. Keep the epic
  open until every required child outcome and the integrated feature are complete.
- Follow the engine's ownership and delivery receipt rules; release only this
  run's claim after a resumable handoff. This command grants no additional merge,
  deployment or provider-switching authority.

Preparation belongs to `/prd prepare` or the authorized `dispatch:plan` OpenAI
planner workflow. Preparation does not apply an execution gate. Use the harness's
configured executor to run this contract; keep lifecycle procedures in the shared
engines instead of copying them into a CLI prompt.
