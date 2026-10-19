---
name: deploy-app
description: Runs deployment workflows for web apps to staging or production. Use when the user says deploy, push to staging, ship it, or go live. Version or tag cuts are release.
metadata:
  version: "2.2.4"
  tags: "deployment, devops, ci-cd, production, staging"
---

# Deploy

Deploy a web app from the trunk to staging or production with gates, verification and a rollback path.

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

## Local quality gates (mandatory)

Before every deployment, run the repository's own format, lint and type-check scripts (plus tests and build when configured). Resolve the real script names from `package.json`; never guess or chain package managers (use the repo's own, Bun by default). Fix failures before pushing or deploying. Prefer CI-driven deploys over running provider CLIs locally.

## Process

### Staging

1. Ensure trunk CI is green.
2. Trigger the staging deploy from the trunk (no staging branch).
3. Wait for CI and staging health checks to pass.

### Production

1. Ensure staging is healthy.
2. **Require explicit confirmation.** Production is critical.
3. Deploy to production from the trunk.
4. Monitor the deployment; watch health endpoints and error tracking for 15 minutes.

### Hotfix

Branch `hotfix/xxx` off the trunk (default branch), fix, PR to trunk, merge, deploy to production.

## Post-deploy verification

1. Check health endpoints.
2. Check error tracking (Sentry or similar).
3. Verify critical user flows.
4. Check deployment logs.

## Rollback

If the deployment fails, revert the merge commit and redeploy.

## References

`references/workflow.md` has platform-specific deployment details, AWS patterns, CI/CD integration and rollback procedures. Its command examples are generic placeholders; substitute the repo's own package manager and scripts.
