---
description: "Inspect, audit, configure, or reconcile a GitHub or Jira project board."
argument-hint: "[audit|init|normalize|copy <source>|sync [--apply]|schedule [days]|review] [board-url]"
disable-model-invocation: true
---

# Board

Inspect, configure, and reconcile the selected board through one provider-aware
entry point. Preserve its existing workflow. The provider may be GitHub, Jira,
or another connected system with clearly stated capability limits.

## Usage

```text
/board                         # inspect current configuration
/board audit                   # audit existing configuration, read-only
/board init                    # prepare a requested new-board configuration
/board normalize               # propose explicit configuration changes
/board copy <source>            # prepare a copy to the specified destination
/board sync                    # reconcile work evidence, read-only
/board sync --apply             # prepare approved provider-supported field repairs
/board schedule [days]          # report upcoming work (default horizon 7 days)
/board review                  # report every item mapped to human review
```

`/board help` prints this Usage block and stops without running anything.

A board URL can identify the target. `--preset shipshit` selects the optional
house layout in configuration modes; it is a workflow option, not a flag to
forward unchanged to provider scripts. Without a selected preset or requested
change, audit the configuration as it exists.

## Routing

1. Parse the mode; unknown modes produce usage rather than an invented action.
2. Resolve the explicit board/provider through its URL or an unambiguous existing
   connection. A repository remote does not identify a Jira board. Ask for the
   missing target only when it remains ambiguous.
3. Route status/audit/init/normalize/copy to `project-board`. Status and audit are
   read-only. Creation, copying, and configuration writes require the skill's
   concrete change plan and approval.
4. Route sync/schedule/review to `board-sync`. Map existing statuses by meaning,
   retaining unknown meanings and reporting incomplete coverage. Never normalize
   a board just to make reconciliation run.
5. For schedule, show available planning units within the horizon and their
   unfinished work. GitHub milestones and Jira sprints are different provider
   concepts. Missing scheduling capabilities must be disclosed.
6. For review, list every item mapped to review; prioritize actionable evidence
   without dropping items whose checks or approvals are unavailable. A starvation
   finding bucket alone is not the complete review queue.

## Boundaries

Status, audit, schedule, review, and sync without apply are read-only. Apply
first produces a fresh report and approved per-category batches; it is not a
blanket mutation grant. Existing authorizations persist only for the same scope.

GitHub apply may set approved project Status and authoritative Priority values.
Jira apply may edit approved Priority where issue metadata permits it. Jira
status changes are issue-workflow transitions and require a separate, explicit
action; board sync never transitions or closes an issue. Neither provider route
merges PRs, deletes/archives items, posts comments, or changes planning units.

Use existing connections and provider references. Do not install integrations or
change credentials implicitly. GitHub includes packaged helpers; Jira has a
documented capability-driven procedure, without a bundled Jira runner or live
Jira validation in this change.
