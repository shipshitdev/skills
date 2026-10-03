---
name: deployment-composer
description: Compose deployment workflows from smaller skills and repo signals, including trunk-based releases, CI quality gates, provider deployment, post-deploy verification, rollback, and failed-check diagnosis. Use when the user asks for a deployment plan, release workflow, ship-to-staging/production environments, or a smart deploy process across GitHub, Vercel, EC2, Docker, or custom CI.
compatibility: Requires local repository access. GitHub release flows require gh and git access.
metadata:
  version: "2.2.2"
  tags: "deployment, orchestration, release, ci-cd, github, staging, production"
allowed-tools: Bash(git *) Bash(gh *) Bash(ls *) Bash(find *) Bash(rg *) Bash(cat *)
---

# Deployment Composer

Compose the smallest safe deployment workflow from the repository's actual branching model, CI setup, deploy provider, and release risk. Routes work to focused skills instead of treating every deploy as the same checklist.

## Authorized Scope

Apply this engine only within the user's requested task and existing explicit
authorization. Loading or delegating to it grants no additional authority.
Preserve report-only restrictions and the caller's target, host, provider, and
cost limits. Existing approval satisfies a gate only for the same actions and
scope; obtain approval before expanding them. Forward these limits to delegates.

## Contract

Inputs:

- Repository root
- Desired release/deploy goal
- Optional target environment, source branch, target branch, PR number, or provider

Outputs:

- Deployment route: release PR, provider deploy, CI setup, or repair
- Selected delegated skills
- Quality gate state
- Confirmation gates still required

Creates/Modifies:

- Nothing during discovery
- May create local release notes or PR body files
- May create GitHub PRs only through `release-pr-gates` after confirmation rules are satisfied

External Side Effects:

- Reads git/GitHub metadata and workflow status
- May trigger provider deployment commands through delegated skills

Confirmation Required:

- Before production deploys or merges
- Before creating GitHub PRs when the user did not explicitly request PR creation
- Before running provider commands with production flags

Delegates To:

- `release-pr-gates`
- `deploy`
- `github-fix-ci`
- `ec2-backend-deployer`
- `testing-cicd-init`
- `changelog-generator`

## Composed Skills

| Stage | Use |
|-------|-----|
| `release-pr-gates` | GitHub release PRs, branch discovery, gate + cut releases on the trunk, waiting for checks |
| `deploy` | General staging/production deploy checklist, local quality gates, post-deploy monitoring |
| `github-fix-ci` | Failed GitHub Actions checks on release or deploy PRs |
| `ec2-backend-deployer` | Docker + GitHub Actions + EC2 backend deployment setup |
| `testing-cicd-init` | Missing or weak GitHub Actions/test infrastructure |
| `changelog-generator` | Release notes from commit history |
| Provider-specific skills | Vercel, Docker, Turborepo, monitoring, or app-specific deployment when present |

## Discovery Phase

Always inspect before choosing a path:

```bash
git status -sb
git remote -v
git branch -r
find . -maxdepth 3 -type f \( -name 'package.json' -o -name 'vercel.json' -o -name 'Dockerfile' -o -name 'docker-compose.yml' -o -name 'docker-compose.yaml' -o -name 'turbo.json' \)
find .github/workflows -maxdepth 1 -type f 2>/dev/null
```

For GitHub repos:

```bash
gh repo view --json nameWithOwner,defaultBranchRef
gh workflow list
```

Capture:

- Current branch and dirty worktree state
- Default (trunk) branch and remote branch list
- CI provider and required checks
- Deploy provider: Vercel, EC2/Docker, GitHub Actions, custom scripts, or unknown
- Package manager and quality commands
- Environment targets: preview, staging, production

## Routing Rules

### Release

If the user wants to cut a release:

1. Use `release-pr-gates` to gate the release on the trunk (default branch).
2. A short-lived feature or fix branch is merged into the trunk via PR; the release is then cut from the trunk as a semver tag + GitHub release.
3. `staging` and `production` are deployment environments driven by CI/tags — not git branches.
4. Wait for quality gates before calling the release ready.
5. Use `github-fix-ci` if checks fail.

### Direct Provider Deploy

If the user wants to deploy the current branch/app to an environment:

1. Use `deploy` for local pre-deploy checks and post-deploy verification.
2. Route provider setup or execution:
   - Vercel project: use Vercel-specific guidance or CLI.
   - EC2/Docker backend: use `ec2-backend-deployer`.
   - Turborepo: inspect `turbo.json` and use affected builds where appropriate.
   - Unknown provider: inspect scripts and workflow files before acting.
3. Do not deploy production without explicit confirmation.

### CI Setup or Repair

If the repo has no CI or weak gates:

1. Use `testing-cicd-init` to add baseline checks.
2. Use `deploy` after CI exists.
3. For failing existing checks, use `github-fix-ci`.

### Release Notes

If the release needs user-facing notes or a PR body:

1. Use `changelog-generator` for commit summaries.
2. Include migrations, env changes, and rollback notes when visible.

## Deployment Workflow

1. Discover repo topology and deployment provider.
2. Choose the narrowest route from the routing rules.
3. Run local gates before every release PR or deployment. Format, lint, and type-check are mandatory:

   ```bash
   bun run format || npm run format || npx biome check --write .
   bun run lint || npm run lint || bunx turbo lint
   bun run typecheck || bun run type-check || npm run typecheck || npm run type-check || npx tsc --noEmit
   bun run test || npm test
   bun run build || npm run build
   ```

   Fix format, lint, and type-check failures before pushing or deploying. Tests
   and build should run when configured; report absent scripts as coverage gaps.

4. Execute the selected release or deploy path.
5. Wait for remote checks or deployment status.
6. Verify the deployed environment:
   - health endpoint
   - critical page/API path
   - logs or monitoring when available
7. Report final status and blockers.

## Safety Rules

- Never hide a dirty worktree; identify whether local changes are part of the deploy.
- Never bypass branch protection or required checks.
- Never merge or deploy production without explicit confirmation.
- Never assume a `staging` environment is configured; verify CI/deployment settings.
- Never call skipped or absent checks green.
- Prefer existing repo scripts and workflows over inventing new deploy commands.
- If a provider cannot be identified, stop after discovery and report what is missing.

## Output Shape

Return a compact deployment state:

```markdown
Deployment route: [release PR / provider deploy / CI setup / repair]
Repository: [owner/repo]
Branches: [source] -> [target] or [current branch]
Provider: [Vercel/EC2/Docker/GitHub Actions/custom/unknown]
Checks: [passing/failing/pending/not configured]
Deployment: [not started/in progress/succeeded/failed]
Verification: [passed/failed/not available]
Needs confirmation: [production merge/deploy, if applicable]
```
