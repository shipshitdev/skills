---
name: github-actions-author
description: "Author, review, and harden GitHub Actions workflows using current official documentation, secure trigger patterns, least-privilege permissions, current action versions, and CI/CD validation. Use when creating, editing, debugging, or security-reviewing workflow YAML."
compatibility: Requires access to GitHub Actions documentation for version-sensitive guidance. Uses git and gh when validating repository workflows.
disable-model-invocation: true
allowed-tools: Bash(git *) Bash(gh *) Bash(bun *)
metadata:
  version: "2.2.3"
  tags: "github, actions, ci-cd, workflows, security"
---

# GitHub Actions Author

## Contract

Inputs:

- Repository root or target workflow file
- Desired workflow behavior, triggers, runtimes, and deployment target
- Optional secrets, environments, runner constraints, and matrix strategy

Outputs:

- Workflow YAML or patch summary
- Documentation-backed rationale for non-obvious choices
- Security and validation checklist

Creates/Modifies:

- May create or edit `.github/workflows/*.yml`
- Does not add secrets or deploy without approval

External Side Effects:

- Reads official GitHub documentation when syntax, permissions, or product
  behavior may have changed
- May query workflow metadata with GitHub CLI
- Does not dispatch, rerun, or cancel workflows without approval

Confirmation Required:

- Before writing workflow files when requirements are unclear
- Before adding deployment, release, publish, or secret-consuming behavior
- Before dispatching or rerunning workflows

Delegates To:

- `testing-cicd-init` for first-pass TypeScript test infrastructure
- `github-fix-ci` when a workflow is failing on a PR
- `git-safety` when workflows touch credentials, tokens, or publish steps

## Workflow

1. Discover existing CI shape:

   ```bash
   find .github/workflows -maxdepth 1 -type f 2>/dev/null
   gh workflow list
   git status -sb
   ```

2. Read relevant local context:
   - Existing workflow files
   - `package.json`, lockfiles, workspace config, test scripts
   - Deployment docs or release conventions

3. Ground version-sensitive choices in official GitHub docs:
   - Workflow syntax, triggers, contexts, expressions
   - `GITHUB_TOKEN` permissions
   - `pull_request` vs `pull_request_target`
   - OIDC, environments, deployment protection rules
   - Cache, artifacts, reusable workflows, matrices, concurrency

4. Check action versions before adding or bumping common actions:

   ```bash
   gh release view --repo actions/checkout --json tagName --jq '.tagName'
   gh release view --repo actions/setup-node --json tagName --jq '.tagName'
   gh release view --repo oven-sh/setup-bun --json tagName --jq '.tagName'
   ```

5. Author with safe defaults:
   - Pin permissions at workflow or job level; default to `contents: read`.
   - Use `pull_request` for untrusted code. Use `pull_request_target` only for
     metadata/comment workflows that do not check out or execute fork code.
   - Pass untrusted event data through environment variables before shell use.
   - Use `concurrency` for expensive or deploy workflows.
   - Use cache keys that include lockfile hashes.
   - Avoid printing secrets or full tokens.
   - Separate CI, release, and deployment workflows when permissions differ.

6. Validate locally when possible:

   ```bash
   git diff -- .github/workflows
   gh workflow view <workflow-name-or-id> --yaml
   ```

   Run `actionlint` if already installed. Do not install new global tools unless
   the user asks.

7. Final output:
   - Files changed
   - Trigger behavior
   - Permissions and secret boundaries
   - Validation performed
   - Remaining manual setup such as secrets or environments

## Security Review Checklist

- No hardcoded secrets, tokens, credentials, or private URLs.
- Job permissions are minimal and explicit.
- Fork PRs cannot access secrets or execute trusted-token publish paths.
- Shell steps quote variables and avoid direct interpolation of issue/PR text.
- Third-party actions are current and reputable; pin to SHA for sensitive
  workflows or untrusted supply-chain surfaces.
- Deployment jobs use environments when human approval or environment-scoped
  secrets are needed.
- Release/publish jobs run only on trusted refs or signed/manual dispatch paths.
