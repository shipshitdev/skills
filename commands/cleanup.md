# Cleanup - Prune Merged Branches, Stale Worktrees, and Finished Work

Clean up what's already done. Default target is git hygiene: verify branches are
provably merged into the trunk (squash-merge aware), then prune the merged
local/remote branches and stale worktrees they leave behind. Explicit targets
extend the sweep to completed GitHub issues and old session files.

## Usage

```bash
/cleanup              # branches + worktrees: verify merged, print the prune plan (dry-run, default)
/cleanup branches     # scope to merged local + remote branches only
/cleanup worktrees    # scope to stale git worktrees only
/cleanup verify       # verification gate only — classify branches, no plan, no deletion
/cleanup prune        # execute the prune plan after you confirm it
/cleanup tasks        # close GitHub issues whose work already shipped
/cleanup sessions     # consolidate daily session files into monthly/yearly
/cleanup all          # git cleanup + tasks + sessions, sequentially
```

`prune` combines with a scope, e.g. `/cleanup prune branches`.

## Git Cleanup (default / `branches` / `worktrees` / `verify` / `prune`)

Use the `git-cleanup` skill. Fetch origin trunk first and classify by **file
content on trunk**, not unique commit SHAs. Squash-merge rewrites every commit;
`git patch-id` against master is not a landing signal. GitHub merged-PR metadata
is one oracle; path blobs that already exist on trunk at the same path are the
squash oracle.

1. Fetch origin trunk and fast-forward local trunk when it is behind. Never
   classify worktrees against a stale local master.
2. Verify every candidate's files are on trunk; report in-flight and genuinely
   stranded branches (unique blobs at a path) loudly.
3. Print the prune plan — local branches, remote branches, worktrees — plus a
   skipped list with reasons. Dry-run is the default; nothing is deleted.
4. In `prune` mode, delete only after you confirm the printed plan.

## Tasks (`tasks`)

Close completed work tracked in GitHub Issues so the open backlog stays accurate.

1. Find issues that are done (all checklist items `[x]`, or work shipped/merged)
   but still open (`gh issue list --state open`).
2. Confirm the list with the user before closing anything.
3. Close each with a short, self-contained completion comment that points at
   something a reader on GitHub can actually open — the shipped PR or commit:
   `gh issue close <number> --comment "Completed in <pr-or-commit-url>."`
   Never cite a local session file; `.agents/sessions/` is gitignored in most
   repos, so it is invisible to anyone reading the issue.
4. Log the closed issues to today's session file.

## Sessions (`sessions`)

Merge daily sessions into monthly, monthly into yearly.

1. Back up the contents of `.agents/sessions/` to a **sibling** directory first —
   `.agents/session-backups/<timestamp>/`. Never nest the backup inside the
   directory being consolidated, or a rerun sweeps earlier backups into itself.
2. Consolidate `YYYY-MM-DD.md` files for past months into `YYYY-MM.md`.
3. Consolidate `YYYY-MM.md` files for past years into `YYYY-yearly-review.md`.
4. Preserve `README.md`; report what was consolidated.

## Gates

- Git cleanup never deletes anything not proven merged into the trunk, never
  touches dirty worktrees, and always shows the dry-run plan before pruning.
- `tasks` closes issues only after you confirm the list.
- `sessions` backs up before modifying and supports a preview without changes.

## Related

- `/merge` lands open PRs and then hands off to `git-cleanup` for the prune.
- `/release` cuts tags and patch notes; it no longer owns branch cleanup.
- The `worktree` skill creates worktrees; `/cleanup` is how they get removed.
