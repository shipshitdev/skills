# Cleanup - Prune Merged Branches, Stale Worktrees, and Finished Work

Clean up what's already done. Default target is git hygiene: audit actual code
and intent on current trunk despite rewritten commit IDs, then prune proven-safe
local/remote branches and stale worktrees they leave behind. Explicit targets
extend the sweep to completed GitHub issues and old session files.

## Usage

```bash
/cleanup              # branches + worktrees: verify merged, print the prune plan (dry-run, default)
/cleanup branches     # scope to merged local + remote branches only
/cleanup worktrees    # scope to stale git worktrees only
/cleanup verify       # read-only alias: print the same code/intent audit plan, no deletion
/cleanup prune        # execute the reviewed plan within existing cleanup authorization
/cleanup tasks        # close GitHub issues whose work already shipped
/cleanup sessions     # consolidate daily session files into monthly/yearly
/cleanup all          # git cleanup + tasks + sessions, sequentially
```

`prune` combines with a scope, e.g. `/cleanup prune branches`.

## Git Cleanup (default / `branches` / `worktrees` / `verify` / `prune`)

Use the `git-cleanup` skill and its packaged helper. Fetch origin trunk first and
audit **current code and intended behavior**, independently of commit IDs or the
original PR. A merged PR, ancestry or historical blob alone cannot prove the work
is present on current master.

1. Fetch origin trunk and fast-forward local trunk when it is behind. Never
   classify worktrees against a stale local master.
2. Inspect per-path current-content evidence and the intended behavior. Record
   verified `intent_reviews` bound to candidate/base/trunk IDs with supporting
   evidence. Keep uncertain, partial or reverted work; report why it remains.
3. Print the prune plan — local branches, remote branches, worktrees — plus a
   skipped list with reasons. Dry-run is the default; nothing is deleted.
4. In `prune` mode, use the reviewed plan within existing authorization. Ask only
   when deletion or its scope is not authorized. Revalidate code and intent;
   create and verify a recovery ref before removal. Preserve ignored files.

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

- Git cleanup requires current-code proof and a verified intent receipt, preserves
  tracked history under a recovery ref, keeps dirty or ignored files, and shows
  the exact plan before pruning.
- `tasks` closes issues only after you confirm the list.
- `sessions` backs up before modifying and supports a preview without changes.

## Related

- `/merge` lands open PRs and then hands off to `git-cleanup` for the prune.
- `/release` cuts tags and patch notes; it no longer owns branch cleanup.
- The `worktree` skill creates worktrees; `/cleanup` is how they get removed.
