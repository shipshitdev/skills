---
name: commit-summary
description: Writes Conventional Commit messages from git changes, splits unrelated changes, flags breaking changes, and commits after approval. Use when writing messages or committing work.
compatibility: Requires git.
allowed-tools: Bash(git *)
metadata:
  portable_source: "https://github.com/ericlitman/open-pstack"
  portable_commit: "1b03678171f6f400ae2cc9dc4e7a4a6a13e4bb43"
  version: "2.2.4"
  tags: "git, workflow, commits, productivity"
when_to_use: "staged changes, split commits"
---

# Commit Summary

Generate accurate Conventional Commits from real git diffs. Stay within what the user asked: message-only requests stay message-only, and committing requires the user's request or approval.

## Contract

Inputs:

- Repository root
- Staged changes, unstaged changes, or approved paths to stage
- Optional commit type, scope, and breaking-change context

Outputs:

- Commit message candidate
- Logical commit grouping when changes are mixed
- Created commit hash after approval, if requested

Creates/Modifies:

- No changes in message-only mode
- May stage files and create commits after approval

External Side Effects:

- None unless another workflow pushes the commit later

Confirmation Required:

- Before staging files
- Before creating a commit
- Before amending or squashing existing commits

Delegates To:

- `github-pr-publish` when the commit should be pushed and opened as a PR
- `git-safety` when secrets or sensitive files appear in the diff

## Workflow

1. Inspect repository state:

   ```bash
   git status -sb
   git log --oneline -5
   git diff --stat
   git diff --cached --stat
   ```

2. Decide what to describe:
   - If changes are staged, generate the message from `git diff --staged`.
   - If nothing is staged, inspect unstaged changes and propose logical groups.
   - If unrelated changes are mixed, recommend separate commits.

3. Guard against unsafe commits:
   - Do not stage secrets, `.env*`, credentials, private keys, local databases, build caches, or large generated artifacts. If sensitive files appear, stop and tell the user.
   - Do not include unrelated formatting churn in a feature/fix commit unless the change requires it.

4. Choose the type:
   - `feat`: user-visible feature or capability
   - `fix`: bug fix
   - `docs`: documentation only
   - `style`: formatting only, no behavior change
   - `refactor`: restructuring without behavior change
   - `perf`: performance improvement
   - `test`: tests only
   - `build`: build system, package manager, dependencies
   - `ci`: CI/CD workflow changes
   - `chore`: maintenance with no user-facing behavior
   - `revert`: revert a previous commit

5. Detect scope. Prefer package, app, domain, or subsystem names already used in history. Omit the scope if it would be vague (`misc`, `stuff`, `changes`).

6. Detect breaking changes:
   - Public API contract changes
   - CLI flag or output changes
   - Database/schema migrations requiring user action
   - Removed config keys, env vars, routes, events, or exported symbols

   Format as `type(scope)!: summary` and add a `BREAKING CHANGE:` footer.

7. Write the message:

   ```text
   type(scope): imperative summary

   Optional body explaining why and any non-obvious implementation detail.

   Optional footer such as:
   BREAKING CHANGE: migration required because ...
   Refs: #123
   ```

8. If the user asked to commit, show the exact message and proceed within that authorization. Ask for approval before staging or committing anything beyond the request, and before amending or squashing existing commits:

   ```bash
   git add <approved-paths>
   git diff --staged --stat
   git commit -m "<subject>" -m "<body-or-footer>"
   ```

## Quality bar

- Subject is imperative and under 72 characters.
- Body explains why when the diff alone is not enough.
- Message does not overstate behavior.
- Commit contains one logical change.
- Verification commands stay out of the message unless the repo convention asks for them.

## Gotchas

- **`git add .` can stage unintended files.** If `.gitignore` does not exclude `node_modules`, `.env*`, or build artifacts, prefer `git add <specific-paths>`. Verify with `git diff --staged --stat` before committing.
- **The breaking-change footer is case-sensitive.** Use exactly `BREAKING CHANGE:` (space, all caps) so tools like `semantic-release` and `conventional-changelog` detect it. `BREAKING-CHANGE:` is not equivalent.
- **Amending rewrites history.** Never amend a commit already pushed to a shared branch; create a new fix commit instead.
- **Co-authored-by trailers may be forbidden.** Check the repo's agent instructions (`AGENTS.md`, `CLAUDE.md`, or equivalent) and recent history for the convention before adding or omitting them.

## Examples

- `feat(auth): add password reset flow`
- `fix(api): handle null provider response`
- `ci(actions): restrict pull request token permissions`
- `refactor(utils): extract date formatting helper`
- `docs: update GitHub project board workflow`
