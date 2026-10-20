---
name: issue
description: "Issue workflows behind one command: turn a rough request into one execution-ready GitHub issue, or run one step alone (requirements, implementation plan, readiness check, publish), or file a Bug issue. Bare /issue runs feature intake."
argument-hint: "[feature|prd|plan|check|publish|bug] <request or issue>"
compatibility: Requires git and an authenticated GitHub CLI gh for issue, sub-issue, and project board writes.
metadata:
  tags: "issues, prd, planning, requirements, ears, readiness, bug, github"
  author: Ship Shit Dev
allowed-tools: Bash(gh *) Bash(git *)
when_to_use: "/issue, /issue feature, /issue prd, /issue plan, /issue check, /issue publish, /issue bug"
disable-model-invocation: true
---

# Issue

One entry point for preparing work as GitHub issues. The first word of the
arguments picks the action; everything after it goes to that action unchanged.
`feature` runs `prd`, `plan`, `check`, and `publish` in order; call a step alone
when you need only that piece.

| Action | Playbook | What it does |
|---|---|---|
| `feature` | [references/feature.md](references/feature.md) | Default. Turns a rough request into one execution-ready issue through the four steps below. |
| `prd` | [references/prd.md](references/prd.md) | Writes repository-grounded requirements with full scope and observable EARS acceptance criteria, interviewing for open decisions. |
| `plan` | [references/plan.md](references/plan.md) | Resolves implementation decisions into an exact, current execution plan on the same issue. |
| `check` | [references/check.md](references/check.md) | Validates requirements and plan, and blocks execution until the issue holds a complete, current implementation contract. |
| `publish` | [references/publish.md](references/publish.md) | Publishes prepared requirements and plans as one GitHub feature issue, with child issues only when justified. |
| `bug` | [references/bug.md](references/bug.md) | Drafts a structured Bug issue, previews it, and files it on confirmation. `bug draft` previews only. |

## Dispatch

1. Read the first word of the arguments.
2. If it is one of the six actions above, read that playbook in full and follow it
   as if it were the skill, passing the remaining arguments as its arguments.
   Each playbook keeps its own scope, confirmation gates, and final report.
3. Bare `/issue`, or a first word that is not an action: run `feature` with
   the full arguments unchanged.
4. If the first word looks like a mistyped action (for example `prds`), print
   the table above and stop instead of guessing.

Examples:

```text
/issue add CSV export to the invoices page      # feature intake
/issue prd #123                                 # requirements only
/issue plan #123                                # implementation plan only
/issue check #123                               # is this issue ready to execute?
/issue publish                                  # file the prepared packet
/issue bug draft checkout ignores the discount  # preview only
/issue bug checkout ignores the discount        # preview, then file
```

## Scope

Loading this router authorizes nothing by itself. Only the selected playbook's
contract applies, and its confirmation gates stay in force. Never chain to a
second action unless the user asks for it or the selected playbook names that
step as part of its own workflow; recommend it instead.
