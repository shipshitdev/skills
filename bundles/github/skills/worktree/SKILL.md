---
name: worktree
description: Creates an isolated git worktree from the right base branch (current feature branch, else trunk), gitignored. Use for parallel or isolated workspaces and multi-agent runs.
compatibility: Requires git 2.5+ (worktree support).
metadata:
  version: "2.2.3"
  tags: "git, worktree, branch, isolation, parallel, workspace"
  author: Ship Shit Dev
allowed-tools: Bash(git *)
when_to_use: "branch off current work, sibling checkout"
---

# Worktree

Create a git worktree off the **right base branch**, in a clean gitignored
directory, with the safety checks that keep the main checkout and `.gitignore`
correct. This skill only **creates** and **lists** worktrees. Removing and
pruning merged worktrees is `git-cleanup`'s job (`/cleanup`) — do not delete here.

## Authorized Scope

Act only within the user's request and existing approval; loading this skill
grants no new authority. Keep report-only requests report-only, honor the
caller's target, host, provider, and cost limits, ask before expanding scope,
and forward these limits to delegates.

## Contract

Inputs:

- Repository root (must be inside a git work tree)
- Optional worktree/branch name (the new branch to create)
- Optional explicit base branch override (`from <base>` / `--base <base>`)
- Optional `--fetch` flag to refresh the base from origin before branching

Outputs:

- A new worktree directory at `.worktrees/<name>` checked out on a new branch
- The resolved base branch and why it was chosen
- A warning if the base is behind its remote (local mode does not auto-fetch)
- The path to `cd` into, ready for a parallel session

Creates/Modifies:

- Adds `.worktrees/` to `.gitignore` and commits that change if not already ignored
- Creates a new branch and a new worktree directory
- Never touches the current working tree's tracked files, never switches the current branch

External Side Effects:

- None by default (local tips only, no network)
- Only with `--fetch`: a single `git fetch origin <base>` to refresh the base ref

Confirmation Required:

- Before writing to `.gitignore` and committing it (one-time, only if `.worktrees/` is not yet ignored)
- Before reusing an existing branch instead of creating a new one
- Before overwriting or reusing a worktree path that already exists

Delegates To:

- Recommend `git-cleanup` to verify promotion and prune merged worktrees and branches
- `git-safety` if a branch about to live in a worktree may contain secrets

## Base Branch Selection (the core behavior)

The base is resolved in this order. **Local tips only — no automatic fetch.**

1. **Explicit override.** If the user named a base (`/worktree fix-auth from develop`
   or `--base release/1.4`), use it verbatim.
2. **On a feature branch → branch off the current branch.** If the current branch
   is not one of the protected/integration branches, the worktree forks from it.
   This is the default: you stay on your in-progress work and explore a sibling
   line without disturbing the current checkout.
3. **On a protected branch or detached HEAD → branch off the default/trunk branch.**
   If the current branch is `master` or `main`, or HEAD is detached, fork from
   the repository's default branch (auto-detected). Never use `develop` or
   `staging` as a long-lived integration base in a trunk-based workflow.

```text
current branch          ->  base the worktree forks from
----------------------      ----------------------------
feat/foo  (feature)     ->  feat/foo        (continue current work)
bugfix/x  (feature)     ->  bugfix/x        (continue current work)
master / main           ->  default branch  (trunk)
detached HEAD           ->  default branch  (trunk)
explicit "from <base>"  ->  <base>          (always wins)
```

Protected/trunk set (never used as a "feature" base in step 2):

```
master  main
```

## Phase 1: Verify Repo and Resolve Inputs

```bash
git rev-parse --is-inside-work-tree            # must be true; else STOP
TOPLEVEL="$(git rev-parse --show-toplevel)"
CURRENT="$(git symbolic-ref --quiet --short HEAD || echo DETACHED)"
git worktree list                              # show what already exists
```

Resolve the **new branch name**:

- If the user gave a name, use it as the new branch name and the directory name.
- If no name was given, ask for one. Do not invent a throwaway name.
- Sanitize the directory name from the branch name (a branch like `feat/foo`
  becomes directory `.worktrees/feat-foo` while the branch stays `feat/foo`).

## Phase 2: Resolve the Base Branch

```bash
PROTECTED='master|main'

# Default/trunk branch fallback — resolved to a ref that actually exists locally.
# Auto-detect the repo's default branch; never hardcode develop or staging.
DEF="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')"
DEF="${DEF:-$(git symbolic-ref --quiet --short HEAD 2>/dev/null)}"
DEF="${DEF:-master}"
git show-ref --verify --quiet "refs/heads/$DEF" && FALLBACK="$DEF" || FALLBACK="origin/$DEF"

# Apply the precedence. BASE is the start-point ref passed to `git worktree add`.
if [ -n "$EXPLICIT_BASE" ]; then
  BASE="$EXPLICIT_BASE"
elif printf '%s\n' "$CURRENT" | grep -qxE "$PROTECTED" || [ "$CURRENT" = DETACHED ]; then
  BASE="$FALLBACK"          # on trunk or detached HEAD -> default/trunk branch
else
  BASE="$CURRENT"           # on a feature branch -> continue current work
fi
echo "Base: $BASE  (current: $CURRENT)"
```

`BASE` is always a concrete start-point (a local branch like `master`, a
remote-tracking ref like `origin/main`, or the user's explicit base). Report
the resolved base and the reason before creating anything.

## Phase 3: Freshness Check (warn, do not fetch)

Local mode is the default: branch from the local tip of `$BASE`. If the base has
an upstream and is behind it, warn — do not silently fetch.

```bash
if git rev-parse --verify --quiet "$BASE@{upstream}" >/dev/null; then
  BEHIND="$(git rev-list --count "$BASE..$BASE@{upstream}" 2>/dev/null || echo 0)"
  [ "$BEHIND" -gt 0 ] && echo "WARNING: local $BASE is $BEHIND commit(s) behind its remote. Using local tip. Pass --fetch to update first."
fi
```

Only if the user passed `--fetch`:

```bash
git fetch origin "$BASE"
git update-ref "refs/heads/$BASE" "origin/$BASE"   # only when safe / fast-forward
```

Do not fetch by default. Do not rewrite a base branch that has local commits not
on the remote — warn and use the local tip instead.

## Phase 4: Ensure `.worktrees/` Is Gitignored

The worktree directory must never be tracked. Verify, and fix once if needed.

```bash
if ! git -C "$TOPLEVEL" check-ignore -q .worktrees; then
  # .worktrees/ is not ignored yet — confirm, then add and commit
  printf '\n# Local git worktrees (created by the worktree skill)\n.worktrees/\n' >> "$TOPLEVEL/.gitignore"
  git -C "$TOPLEVEL" add .gitignore
  git -C "$TOPLEVEL" commit -m "chore: ignore .worktrees/ directory"
fi
```

This is the only commit the skill makes, and only the first time in a repo.
Confirm before committing in a shared repo.

## Phase 5: Create the Worktree

```bash
NAME="<sanitized-name>"
BRANCH="<new-branch-name>"
DEST="$TOPLEVEL/.worktrees/$NAME"

# Guard: destination must not already exist
[ -e "$DEST" ] && { echo "Path exists: $DEST — choose another name or remove it first."; exit 1; }

if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  # Branch already exists: confirm, then attach it (no -b, no new branch)
  git worktree add "$DEST" "$BRANCH"
else
  # New branch off the resolved local base tip
  git worktree add -b "$BRANCH" "$DEST" "$BASE"
fi

git worktree list
```

Rules:

- Use `-b` only when creating a new branch. If the branch exists, attach it and
  say so — never silently reset an existing branch.
- A branch can be checked out in only one worktree at a time. If `$BRANCH` is
  already checked out elsewhere, report where and stop.
- Never pass `--force`. If git refuses, surface the reason and let the user decide.

## Phase 6: Report and Hand Off

Report:

- Worktree path: `.worktrees/<name>`
- New branch and the base it forked from (plus why that base)
- Any freshness warning from Phase 3
- How to start work there: `cd .worktrees/<name>` and open a parallel session in
  that directory. Each worktree is an independent checkout sharing one `.git`.
- If the project needs dependencies, install them inside the worktree before
  running anything (worktrees do not share `node_modules`).

## Modes

- `worktree <name>` — create a worktree named `<name>` on a new branch `<name>`,
  base resolved by the smart rules above. (Default.)
- `worktree <name> from <base>` / `worktree <name> --base <base>` — force the base.
- `worktree <name> --fetch` — refresh the base from origin before branching.
- `worktree list` — list existing worktrees and their branches; create nothing.

When the user scopes it differently ("off master", "use my current branch",
"don't touch gitignore"), honor the scope but keep the safety checks that prevent
tracking the worktree dir or clobbering an existing branch/path.

## Safety Model

1. Never switches the current branch or modifies the current working tree's
   tracked files. A worktree is additive.
2. Never tracks the worktree directory — `.worktrees/` is verified ignored first.
3. Local tips by default; network only on explicit `--fetch`.
4. Never `--force`, never reset an existing branch, never overwrite an existing
   path. On conflict, report and stop.
5. Removal and pruning are out of scope — hand off to `git-cleanup` (`/cleanup`).
