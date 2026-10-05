# Out-of-scope knowledge base

`.out-of-scope/` at the repo root records rejected enhancement requests: memory of
why, and a dedup check for the next request that arrives.

## Rules

- One file per **concept**, not per issue. Name it in kebab-case so the directory
  listing reads as the list of rejections (`dark-mode.md`, `plugin-system.md`).
- Write only for a rejected **enhancement** or enhancement PR. Never for a bug,
  and never for something closed because it already exists: that would poison
  later matches with false rejections.
- The reason is durable: project scope, a technical constraint, a strategic
  choice. "Too busy right now" is a deferral, not a rejection.
- Commit the file through the repo's normal branch and PR flow.

## File shape

```markdown
# <Concept>

<One sentence: this project does not do X.>

## Why this is out of scope

<The reasoning, as a short design note: constraints, what supporting it would
require, how it conflicts with scope. Code samples when they make it clear.>

## Prior requests

- <issue or PR link>: "<title>"
```

## On a match

Surface the entry with its reason and ask the maintainer. They can **confirm**
(append the new request under Prior requests, then close), **reconsider** (delete
or rewrite the file and triage normally), or say the requests are **distinct**
(triage normally). Deleting an entry does not reopen old issues.
