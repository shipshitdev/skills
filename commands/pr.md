---
description: "Pull request lifecycle: create or update the PR, review it, digest comments, tidy, address, fix CI, or suggest."
argument-hint: "[review|comments|tidy|address|fix-ci|suggest]"
disable-model-invocation: true
---

# PR - Pull Request Lifecycle

One entry point for the pull-request lifecycle: open or update a PR, review it,
digest its comments, tidy it for reviewers, apply review fixes, repair failing
CI, or post inline suggestions.

## Usage

```bash
/pr                 # create or update the PR for the current branch (default)
/pr review          # full multi-dimension review of the PR/branch
/pr comments        # read-only digest of the PR's review feedback
/pr tidy            # rewrite the PR description to be easy to review
/pr address         # apply review-comment fixes + draft replies
/pr fix-ci          # diagnose and fix failing CI checks on the PR
/pr suggest         # post inline suggested changes on the PR
```

`/pr help` prints this Usage block and stops without running anything.

`/pr comments` accepts the same arguments as the `pr-comments` skill, e.g.
`/pr comments <number>`, `/pr comments unresolved`, `/pr comments from <reviewer>`.

## Workflow

Route by subcommand:

1. **`/pr` (default)** — use the `github-pr-publish` skill to create or update the PR
   from local changes: branch hygiene, a durable title/body, validation notes, and
   safe push/PR gates.
2. **`/pr review`** — use the `full-code-review` skill (structural + security +
   devex dimensions, adversarially verified) against the PR diff. For a fast
   correctness-only pass, use `code-review` instead.
3. **`/pr comments`** — use the `pr-comments` skill to fetch and prioritize review
   feedback as a read-only action list. To then act on it, hand off to
   `github-address-comments`.
4. **`/pr tidy`** — use the `github-pr-publish` skill's reviewability pass to rewrite an
   existing PR's description into the standard body template (Summary with a
   visual, Evidence, Merge danger, and a Review guide for large diffs). It rewrites
   the description only — it does not reorder commits or force-push.
5. **`/pr address`** — use the `github-address-comments` skill to fetch review threads,
   map them to code, propose fixes, and draft replies for approval.
6. **`/pr fix-ci`** — use the `github-fix-ci` skill to diagnose failing GitHub Actions
   checks on the PR and apply targeted fixes (optionally looping until green).
7. **`/pr suggest`** — use the `github-review-suggestions` skill to post precise inline
   suggested changes as GitHub suggestion blocks on the PR.

## Gates

- Honor every `github-pr-publish` push/PR gate: confirm before staging broad files,
  committing, pushing, or marking a draft ready.
- `/pr review` and `/pr comments` are read-only — they never edit code or post
  changes.
- `/pr tidy` edits the PR description text only; it never rewrites git history.
- `/pr address`, `/pr fix-ci`, and `/pr suggest` mutate (code fixes or posted
  comments) — honor each skill's own confirmation gate before applying or posting.
