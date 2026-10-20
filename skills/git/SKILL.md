---
name: git
description: "Git and GitHub workflows behind one command: create isolated worktrees, guard secrets, resolve conflicts, open or update PRs, fix failing CI, review and merge open PRs, and prune merged branches and worktrees."
argument-hint: "<worktree|safety|conflicts|pr|ci|merge|cleanup> [args]"
compatibility: Requires git 2.5+ and an authenticated GitHub CLI gh; merge also needs jq; cleanup also needs Python 3.9+ and git patch-id --verbatim.
metadata:
  tags: "git, github, pull-requests, ci, merge, cleanup, worktrees, secrets, conflicts, branches"
  author: Ship Shit Dev
allowed-tools: Bash(git *) Bash(gh *) Bash(jq *) Bash(bun *) Bash(bunx *)
when_to_use: "/git worktree, /git safety, /git conflicts, /git pr, /git ci, /git merge, /git cleanup"
disable-model-invocation: true
---

# Git

One entry point for git and GitHub work. The first word of the arguments picks
the action; everything after it goes to that action unchanged.

| Action | Playbook | What it does |
|---|---|---|
| `worktree` | [references/worktree.md](references/worktree.md) | Creates an isolated worktree outside the repository, in the agent's worktree home, off the right base. |
| `safety` | [references/safety.md](references/safety.md) | Blocks staged secrets, gates destructive git commands, installs pre-commit hooks, drives leak response. |
| `conflicts` | [references/conflicts.md](references/conflicts.md) | Resolves merge, rebase, cherry-pick, or stash-pop conflicts correctness-first, then proves the tree builds. |
| `pr` | [references/pr.md](references/pr.md) | Creates, updates, and publishes pull requests with clean titles, durable bodies, branch hygiene, and safe push gates. |
| `ci` | [references/ci.md](references/ci.md) | Diagnoses failing or stuck GitHub Actions checks on a PR, fixes the root cause, and optionally loops until green. |
| `merge` | [references/merge.md](references/merge.md) | Reviews and lands open PRs into trunk behind one confirmation; `force` drains the queue non-serially. |
| `cleanup` | [references/cleanup.md](references/cleanup.md) | Proves each candidate is on current trunk, then plans or removes only proven-merged branches and worktrees. Read-only plan by default. |

## Dispatch

1. Read the first word of the arguments. Accept only the seven actions above.
2. Bare `/git`, or an unknown first word: print the table above and stop. Do
   not guess an action and do not run any command.
3. Otherwise read the action's playbook in full and follow it as if it were the
   skill, passing the remaining arguments as its arguments. Each playbook keeps
   its own scope, confirmation gates, and final report.

Examples:

```text
/git worktree fix-auth from develop
/git safety                   # staged-secret check before a commit
/git conflicts                # resolve the current merge or rebase
/git pr                       # push and open or update the PR
/git ci                       # diagnose and fix red checks on the PR
/git ci loop until green      # keep fixing and rechecking until it passes
/git merge                    # review, confirm, merge green PRs
/git merge review             # review only, merge nothing
/git merge force              # drain the queue without serial waits
/git cleanup                  # read-only cleanup plan
/git cleanup prune            # remove the proven-merged set from that plan
```

## Scope

Loading this router authorizes nothing by itself. Only the selected playbook's
contract applies, and its confirmation gates stay in force. Never chain to a
second action unless the user asks for it or the selected playbook names that
step as part of its own workflow; recommend it instead.
