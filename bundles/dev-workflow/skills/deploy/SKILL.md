---
name: deploy
description: Run deployment workflows for web applications (staging, production). Use when user says 'deploy', 'push to staging', 'ship it', or 'go live'. Cutting a version or tag is `release`.
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
- Release PRs or tags only through the `release` skill

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
- `release` for gating the trunk SHA and cutting the release
- `github-fix-ci` for failed GitHub Actions checks
- `ec2-backend-deployer` for EC2/Docker deployment setup

## When to Use

- Deploying to staging or production
- Setting up deployment pipelines
- Managing environment-specific deployments

## Local Quality Gates (MANDATORY)

Before every deployment, run the repository's own format, lint, and type-check
scripts (and tests and build when configured), on the host the repo designates
for them. Resolve the real script names from `package.json`; never guess or
chain package managers. Fix failures before pushing or deploying.

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
