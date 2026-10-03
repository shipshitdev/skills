---
description: "Review a PR and post one-click inline suggested changes after you confirm."
argument-hint: "[PR#|PR-URL] [scope]"
disable-model-invocation: true
---

# Suggest - Post Inline Suggested Changes on a PR

Review a pull request and post precise inline GitHub *suggested-change* blocks —
the one-click "Apply suggestion" kind — so the author can accept fixes directly.
Where `/review` reports findings back to you, `/suggest` writes applyable
suggestions onto the PR.

## Usage

```bash
/suggest              # review the current branch's PR and draft inline suggestions (default)
/suggest <PR#>        # target a specific PR by number
/suggest <PR-URL>     # target a PR by URL
```

`/suggest help` prints this Usage block and stops without running anything.

Optional scope: name files or a severity threshold, e.g. `/suggest 142 src/auth only`.

## Workflow

Use the `github-review-suggestions` skill.

1. Resolve the target PR and fetch its diff (read-only) before touching the branch.
2. Identify high-conviction, mechanically-applyable fixes and build exact
   suggestion blocks anchored to the right diff lines.
3. **Preview every suggestion and wait for confirmation.**
4. On approval: submit the review with the inline suggestions via `gh`.

## Gates

- Build and preview suggestions freely. **Never submit a review or post comments
  to GitHub without explicit confirmation** — this is public, outward-facing
  content on someone's PR.
- Only suggest changes you are confident apply cleanly; a wrong suggestion block
  is worse than a prose comment.

## Related

- `/review` reviews for *you*; `/suggest` posts suggestions *to the PR*.
  `/address` resolves comments others left on your PR.
