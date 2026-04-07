---
name: commit-summary
description: Generate meaningful commit messages from staged changes using conventional commits. Use when user says 'commit', 'commit summary', 'generate commit message', or before committing.
version: 1.0.0
tags:
  - git
  - workflow
  - commits
  - productivity
---

# Commit Summary

Generate meaningful commit messages based on staged changes.

## Workflow

### Step 1: Review Changes

```bash
git status
git diff --staged
git log --oneline -5
```

### Step 2: Analyze Changes

Categorize:

- `feat:` New feature
- `fix:` Bug fix
- `refactor:` Code restructuring
- `docs:` Documentation only
- `test:` Adding/updating tests
- `chore:` Maintenance tasks

### Step 3: Generate Message

Format: `type(scope): short description`

- What changed
- Why it changed (if not obvious)

### Step 4: Review

Ensure message:

- Accurately describes changes
- Follows project conventions
- Is concise but complete

## Guidelines

- Start with type (feat, fix, refactor, etc.)
- Include scope if applicable
- Use imperative mood ("Add" not "Added")
- Keep first line under 72 chars
- Explain why, not just what

## Examples

- `feat(auth): add password reset flow`
- `fix(api): handle null response from external service`
- `refactor(utils): extract date formatting to shared helper`
- `docs: update API endpoint documentation`

## What NOT to Do

- Vague messages ("fix stuff", "update code")
- Too long first lines
- Missing context for non-obvious changes
- Committing unrelated changes together
