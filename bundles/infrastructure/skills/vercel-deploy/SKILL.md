---
name: vercel-deploy
description: Deploy a Next.js app to Vercel and manage its environment — preview and production deploys, environment variables per environment, promotion, and rollback to a previous deployment. Use when asked to deploy to Vercel, ship a preview, promote to production, roll back a bad deploy, or manage Vercel env vars. Confirms the project is linked before any deploy and never links unattended.
compatibility: Requires the Vercel CLI authenticated, and a linked project (.vercel/project.json).
disable-model-invocation: true
argument-hint: "[preview | prod | rollback | env]"
allowed-tools: Bash(vercel *)
metadata:
  version: "2.2.5"
  tags: "vercel, deploy, nextjs, rollback, environments, infrastructure"
  author: Ship Shit Dev
when_to_use: "deploy to Vercel, ship a preview, deploy to production, promote to production, roll back the deploy, revert deployment, manage Vercel env vars, /deploy vercel"
---

# Vercel Deploy

Ship a Next.js app to Vercel and control its environments safely: preview deploys for
review, production promotes behind confirmation, and a fast rollback when a deploy goes
bad. Deploying is publishing — every production action is gated.

## Contract

Inputs:

- A linked Vercel project; mode `preview` (default), `prod`, `rollback`, or `env`.

Outputs:

- A deployment URL (preview or production), or the restored deployment (rollback), or
  the env-var change summary.

Creates/Modifies:

- Vercel deployments and environment variables. Production deploys, promotions, env
  changes, and rollbacks happen only after confirmation.

External Side Effects:

- Publishes to Vercel. A production deploy is user-visible immediately. No git writes.

Confirmation Required:

- Before any production deploy or promotion.
- Before changing or removing an environment variable.
- Before a rollback (name the target deployment first).

Delegates To:

- `monitoring-setup` to confirm error tracking is live before a production deploy.
- `dependency-audit` / `security-audit` as a pre-production gate on risky releases.

## Step 0 — Verify the project is linked (safety gate)

Never deploy an unlinked project, and never link one unattended:

```bash
test -f .vercel/project.json || { echo "Not linked — .vercel/project.json missing."; exit 1; }
vercel whoami    # confirm the CLI is authenticated as the right account
```

If `.vercel/project.json` is absent, **stop and ask the user** to run `vercel link`
themselves — do not run it for them. Linking to the wrong project deploys to the wrong
place.

## Step 1 — Preview deploy (default)

A preview build for review — never production:

```bash
vercel                 # builds and deploys a preview; prints the preview URL
```

Report the preview URL. This is the safe default for any "deploy this" without an
explicit production ask.

## Step 2 — Production deploy (`prod`)

Confirm first, then promote. Prefer promoting an already-built preview over a fresh
`--prod` build so what ships is what was reviewed:

```bash
vercel --prod          # builds and deploys straight to production
# or promote a specific, already-reviewed deployment:
vercel promote <deployment-url>
```

Before running: state what will go live (branch/commit), confirm error tracking is on
(`monitoring-setup`), and get an explicit yes. Production is live to users the moment
this returns.

## Step 3 — Rollback (`rollback`)

When a production deploy is bad, roll back to the last known-good deployment:

```bash
vercel ls --prod                     # list recent production deployments
vercel rollback <good-deployment-url>   # or `vercel promote` the known-good one
```

Name the target deployment (URL + commit) and confirm before rolling back. Rollback is
itself a production change.

## Step 4 — Environment variables (`env`)

Manage vars per environment; production changes are gated:

```bash
vercel env ls                                  # what's set, per environment
vercel env add <NAME> production               # prompts for the value (not echoed)
vercel env rm <NAME> production                # after confirmation
```

Never print a secret value into the transcript. Set the same var across `development`,
`preview`, and `production` deliberately — a var present in preview but missing in
production is a classic "works in preview, 500s in prod" bug.

## Anti-Patterns

- **Deploying an unlinked project or running `vercel link` unattended** — stop and ask;
  linking to the wrong project ships to the wrong place.
- **`vercel --prod` without confirmation** — production is live immediately; preview is
  the default.
- **Fresh `--prod` build instead of promoting the reviewed preview** — promote what was
  reviewed so prod matches what was tested.
- **Echoing secret env values** into the transcript.
- **A rollback without naming the target** — confirm the exact known-good deployment
  first.
