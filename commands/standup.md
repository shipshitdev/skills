---
description: "Recap what you shipped over a time window from your git history."
argument-hint: "[7d|today|yesterday|since <ref>|from <date> to <date>] [--author <email>] [--all-repos <dir>]"
disable-model-invocation: true
---

# Standup - What Did I Get Done

Summarize what **you** shipped over a time window from git history — an engineer
standup or weekly recap, scoped to your git author identity. The inward-facing
twin of a changelog: it reads your commits and their diffs and writes a terse
status update, not customer release notes.

## Usage

```bash
/standup                      # last 24h, your commits, current repo (default)
/standup 7d                   # rolling week
/standup today | yesterday
/standup since <ref|date>     # e.g. since v1.4.0, since "3 days ago"
/standup from <date> to <date>
/standup --author <email>     # scope to a different identity
/standup --all-repos <dir>    # sweep sibling repos under <dir>, grouped by repo
```

`/standup help` prints this Usage block and stops without running anything.

## Workflow

Use the `standup` skill.

1. Resolve the author from `git config user.email` (or `--author`). Stop and ask if
   no identity can be resolved — never silently report everyone's commits.
2. Translate the window into `--since` / `--until`.
3. `git log --author=<you> --no-merges --since=<window>` and read the diffstat for
   substance.
4. Classify each meaningful change (feature / fix / refactor·tech-debt / docs·chore)
   from what the diff actually does, collapsing many small commits into one outcome.
5. Print a terse 2–6 bullet recap. Optionally enrich with merged PRs you authored.

## Gates

- Read-only: never commit, push, tag, or modify files.
- Require a resolvable author identity before reporting.
- For customer-facing release notes use the `release` or `changelog-generator`
  skills instead.
