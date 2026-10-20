---
name: board
description: "Project board workflows behind one command: audit and configure a GitHub or Jira board's fields, columns, and scope, or reconcile the board with current work and delivery evidence."
argument-hint: "<configure|sync> [board] [args]"
compatibility: Requires access to the selected board provider. GitHub includes Node.js or Bun helper scripts; Jira uses an existing authenticated provider connection or browser.
metadata:
  tags: "boards, configuration, workflow, reconciliation, github, jira"
  author: Ship Shit Dev
when_to_use: "/board configure, /board sync"
disable-model-invocation: true
---

# Board

One entry point for project boards. The first word of the arguments picks the
action; everything after it goes to that action unchanged. Both actions read
first and change fields only within an explicit, approved scope.

| Action | Playbook | What it does |
|---|---|---|
| `configure` | [references/configure.md](references/configure.md) | Audits a board's fields, columns, and scope, and applies requested setup, copy, or normalization. |
| `sync` | [references/sync.md](references/sync.md) | Reconciles a board with current work and delivery evidence and reports gaps; applies only approved field changes. |

## Dispatch

1. Read the first word of the arguments. Accept only the two actions above.
2. Bare `/board`, or an unknown first word: print the table above and stop. Do
   not guess an action and do not run any command.
3. Otherwise read the action's playbook in full and follow it as if it were the
   skill, passing the remaining arguments as its arguments. Each playbook keeps
   its own scope, confirmation gates, and final report.

Examples:

```text
/board configure <board URL>        # audit fields, views, and workflows
/board sync <board URL>             # report drift against PR and deploy state
/board sync <board URL> --apply     # prepare approved field corrections
```

## Scope

Loading this router authorizes nothing by itself. Only the selected playbook's
contract applies, and its confirmation gates stay in force. Never chain to a
second action unless the user asks for it or the selected playbook names that
step as part of its own workflow; recommend it instead.
