---
name: production-audit
description: Audits an app's production readiness from code, CI, config, migrations, observability, and deploy paths, returning a ship/block verdict. Use before launch or after risky merges.
metadata:
  version: "2.2.4"
  tags: "production, audit, launch, deployment, reliability"
when_to_use: "is this ready to ship, launch readiness, go-live check"
---

# Production Audit

Assess whether an application is safe to ship by inspecting the release surface and naming production risks.

## Contract

Inputs:

- Repository, branch, PR, release candidate, or deployed URL
- Optional launch-critical flows, test account, environment notes, or CI run

Outputs:

- Ship/block recommendation with score and evidence
- Blockers, high-value fixes, missing evidence, and next action
- Concrete file, command, CI, or URL references

Creates/Modifies:

- None in audit mode
- Follow-up fixes only when explicitly requested

External Side Effects:

- Read-only local commands and authorized HTTP/browser checks
- No source upload, destructive migration, production write, or scanner run by default

Confirmation Required:

- Before credentialed production actions, remote scanner use, deploys, migrations, data changes, or user-impacting tests

Delegates To:

- `security-audit` for application security findings
- `deploy-app` or `deployment-composer` for release mechanics
- `release` for gating the trunk SHA and cutting the release
- `playwright-e2e-init` for missing launch-critical browser coverage; `test-runner` for existing tests

## When to Use

- User asks "is this production ready?", "what breaks in prod?", "ready to
  ship?", "audit this release", or "what did we miss?"
- A launch, demo, customer rollout, or investor walkthrough is close.
- CI is green but production risk still needs review.
- A risky PR merged or a dependency upgrade landed.
- A deployed staging or preview URL needs a readiness pass.

Not a compliance, legal, financial, medical, or security certification — engineering release triage only.

## Evidence Order

Start with cheap local evidence:

```bash
git status --short --branch
git log --oneline --decorate -20
git diff --stat origin/main...HEAD
```

Then inspect the surfaces that actually exist:

- package scripts, build commands, CI workflows, and release scripts
- API routes, auth middleware, webhooks, workers, cron jobs, and queues
- migrations, seeds, backfills, rollback notes, and data access policies
- environment variable documentation and startup validation
- payment, email, storage, AI, and external-provider boundaries
- observability, logging, health checks, dashboards, and alert ownership
- E2E or smoke coverage for launch-critical user paths
- deployed URL checks when a URL is in scope

Do not call a release healthy just because CI is green.

## Risk Lenses

### Security and Auth

- Are sensitive routes protected server-side?
- Are authorization checks tenant-aware and applied near data access?
- Are secrets absent from client bundles, logs, examples, and committed files?
- Are uploads, CORS, CSRF, rate limits, and input validation appropriate?
- Do agent or AI surfaces isolate untrusted content from privileged tools?

### Data Integrity

- Can migrations run forward safely?
- Is there a rollback, recovery, or backup path for high-impact changes?
- Are destructive backfills staged and idempotent?
- Are retries safe for writes, jobs, and webhooks?
- Do sandbox, staging, and production schemas match the code assumptions?

### Payments and Webhooks

- Are webhook signatures verified before trusting payload fields?
- Are fulfillment handlers idempotent for duplicate delivery?
- Are out-of-order and replayed events handled?
- Are test and live credentials separated?
- Is customer-visible billing state recoverable after provider failure?

### Operations

- Can the app start from a clean checkout with documented commands?
- Are required environment variables named and validated at startup?
- Is there a health check that proves dependencies are reachable?
- Are logs useful without leaking secrets or personal data?
- Is there a clear deploy, rollback, and incident-owner path?

### User Experience

- Are launch-critical paths covered on desktop and mobile?
- Are loading, empty, error, and permission-denied states usable?
- Do forms handle invalid input, slow requests, and double submits?
- Is there a recovery or support path when a critical operation fails?

## Scoring

Use scores to force prioritization:

| Score | Verdict |
| --- | --- |
| 0-49 | Blocked: do not ship until blockers are fixed |
| 50-69 | Risky: internal beta or small rollout only |
| 70-84 | Launchable with caveats: ship if owners accept named risks |
| 85-100 | Strong: no obvious launch blockers from available evidence |

Cap at `69` if any are true:

- auth or authorization is missing for sensitive data
- payment or fulfillment webhooks are not idempotent
- required migrations cannot run safely
- secrets are exposed in client bundles, logs, or committed files
- no rollback or recovery path exists for a high-impact release

Cap at `84` if CI is not green or the launch-critical path was not tested end
to end.

## Output Format

Lead with one sentence:

```text
Production audit: 76/100, launchable with caveats, with webhook idempotency and rollback docs as the two risks to fix before public launch.
```

Then list:

- `Blockers`: must-fix items before deploy
- `High-value fixes`: next improvements by impact
- `Evidence checked`: files, commands, CI, URLs, or PRs inspected
- `Evidence missing`: what would change confidence
- `Next action`: one concrete fix or verification step

If no blockers are found, still state the evidence boundary.

## Anti-Patterns

- Running unpinned remote scanners as the default audit path.
- Uploading private source, secrets, customer data, or topology externally
  without explicit approval.
- Giving a score without naming evidence.
- Treating staging smoke tests as proof that data migrations are safe.
- Ending with a generic summary instead of the next concrete release action.
