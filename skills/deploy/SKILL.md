---
name: deploy
description: Run deployment workflows for web applications (staging, production). Use when user says 'deploy', 'push to staging', 'release', 'ship it', or 'go live'.
metadata:
  version: 1.0.0
  tags: deployment, devops, ci-cd, production, staging
---

# Deploy

Streamline deployment workflows for React, Next.js, NestJS applications to various environments.

## When to Use

- Deploying to staging or production
- Setting up deployment pipelines
- Managing environment-specific deployments

## Pre-Deployment Checklist (MANDATORY)

Run ALL of these locally before every push:

```bash
# 1. Format
npx biome check --write . || npm run format

# 2. Lint
npm run lint || bunx turbo lint

# 3. Type-check
npm run type-check || tsc --noEmit

# 4. Run tests for changed packages
npm test || bun run test --filter=[changed-package]

# 5. Verify build
npm run build
```

If ANY step fails, fix it before pushing.

## Deployment Process

### To Staging

1. Ensure develop/main CI is green
2. Create PR to staging branch (if applicable)
3. Wait for CI to pass
4. Merge when green

### To Production

1. Ensure staging CI is green
2. Create PR to production branch
3. **Require explicit confirmation** — production is critical
4. Merge and monitor deployment
5. Watch health endpoints and error tracking for 15 minutes

### Hotfix Flow

1. Branch `hotfix/xxx` off production branch
2. Fix -> PR to production -> deploy
3. Merge hotfix back into develop

## Post-Deployment Verification

1. Check health endpoints
2. Monitor error tracking (Sentry, etc.)
3. Verify critical user flows
4. Check deployment logs

## Rollback

If deployment fails, revert the merge commit and re-deploy.

## References

See `references/workflow.md` for platform-specific deployment details, AWS patterns, CI/CD integration, and rollback procedures.
