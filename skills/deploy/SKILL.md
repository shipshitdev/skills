---
name: deploy
description: Run deployment workflows for web applications (staging, production). Use when user says 'deploy', 'push to staging', 'release', 'ship it', or 'go live'.
metadata:
  version: "2.2.2"
  tags: "deployment, devops, ci-cd, production, staging"
---

# Deploy

## Contract

Inputs:

- Repository root
- Target environment: preview, staging, or production
- Optional branch, PR number, deployment provider, and health-check URL

Outputs:

- Pre-deploy gate results
- Deployment route and provider
- Verification status
- Rollback or follow-up instructions when needed

Creates/Modifies:

- Local changes only when fixing failed gates before deployment
- Release PRs only when delegated to `release-pr-gates`

External Side Effects:

- May trigger provider deployments
- May create or update GitHub PRs through delegated release skills
- May read logs and monitoring systems

Confirmation Required:

- Before production deploys
- Before merging release PRs
- Before rollback commands
- Before force-pushes or history rewriting

Delegates To:

- `deployment-composer` for route discovery across providers
- `release-pr-gates` for branch promotion PRs
- `github-fix-ci` for failed GitHub Actions checks
- `ec2-backend-deployer` for EC2/Docker deployment setup

## When to Use

- Deploying to staging or production
- Setting up deployment pipelines
- Managing environment-specific deployments

## Local Quality Gates (MANDATORY)

Always run format, lint, and type-check locally before every release PR or
deployment. These mirror the expected GitHub Actions gates and are cheap enough
to run before pushing.

Use the repository's package manager and scripts when present. Prefer existing
scripts in `package.json`; fall back only when a script is missing.

```bash
# 1. Format - required
bun run format || npm run format || npx biome check --write .

# 2. Lint - required
bun run lint || npm run lint || bunx turbo lint

# 3. Type-check - required
bun run typecheck || bun run type-check || npm run typecheck || npm run type-check || npx tsc --noEmit

# 4. Tests - run when configured
npm test || bun run test --filter=[changed-package]

# 5. Build - run when configured
npm run build
```

If format, lint, or type-check fails, fix it before pushing, opening a release
PR, or triggering deployment. Do not hand known local quality failures to GitHub
Actions.

## Deployment Process

### To Staging

1. Ensure trunk CI is green
2. Trigger deploy to staging environment from the trunk (no staging branch)
3. Wait for CI and staging health checks to pass

### To Production

1. Ensure staging environment is healthy
2. **Require explicit confirmation** — production is critical
3. Deploy to production environment from the trunk
4. Monitor deployment
5. Watch health endpoints and error tracking for 15 minutes

### Hotfix Flow

1. Branch `hotfix/xxx` off the trunk (default branch)
2. Fix -> PR to trunk -> merge -> deploy to production

## Post-Deployment Verification

1. Check health endpoints
2. Monitor error tracking (Sentry, etc.)
3. Verify critical user flows
4. Check deployment logs

## Rollback

If deployment fails, revert the merge commit and re-deploy.

## References

See `references/workflow.md` for platform-specific deployment details, AWS patterns, CI/CD integration, and rollback procedures.
