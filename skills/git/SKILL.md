---
name: git
description: "Local git workflows behind one command: prune merged branches and worktrees, guard secrets and destructive commands, resolve merge conflicts, create isolated worktrees."
argument-hint: "<cleanup|safety|conflicts|worktree> [args]"
compatibility: Requires git 2.5+; cleanup also needs Python 3.9+, git patch-id --verbatim, and an authenticated GitHub CLI gh for PR-backed proofs.
metadata:
  tags: "git, cleanup, worktrees, secrets, pre-commit, merge, conflicts, branches"
  author: Ship Shit Dev
allowed-tools: Bash(git *) Bash(bun *) Bash(bunx *)
when_to_use: "/git cleanup, /git safety, /git conflicts, /git worktree"
disable-model-invocation: true
---

# Git

One entry point for local git work. The first word of the arguments picks the
action; everything after it goes to that action unchanged.

| Action | Playbook | What it does |
|---|---|---|
| `cleanup` | [references/cleanup.md](references/cleanup.md) | Proves each candidate is on current trunk, then plans or removes only proven-merged branches and worktrees. Read-only plan by default. |
| `safety` | [references/safety.md](references/safety.md) | Blocks staged secrets, gates destructive git commands, installs pre-commit hooks, drives leak response. |
| `conflicts` | [references/conflicts.md](references/conflicts.md) | Resolves merge, rebase, cherry-pick, or stash-pop conflicts correctness-first, then proves the tree builds. |
| `worktree` | [references/worktree.md](references/worktree.md) | Creates an isolated worktree outside the repository, in the agent's worktree home, off the right base. |

## Dispatch

1. Read the first word of the arguments. Accept only the four actions above.
2. Bare `/git`, or an unknown first word: print the table above and stop. Do not
   guess an action and do not run any git command.
3. Otherwise read the action's playbook in full and follow it as if it were the
   skill, passing the remaining arguments as its arguments. Each playbook keeps
   its own scope, confirmation gates, and final report.

Examples:

```text
/git cleanup                  # read-only cleanup plan
/git safety                   # staged-secret check before a commit
/git conflicts                # resolve the current merge or rebase
/git worktree fix-auth from develop
```

## Scope

Loading this router authorizes nothing by itself. Only the selected playbook's
contract applies, and its confirmation gates stay in force. Never chain to a
second action unless the user asks for it; recommend it instead (for example,
recommend `/git cleanup` after a worktree's PR merges).
