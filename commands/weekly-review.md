---
description: "Weekly repository health review over the last 7 days: shipped work, board drift, operational health, scoped cleanup."
argument-hint: "[7d|since <SHA>] [--report-only|--fix]"
disable-model-invocation: true
---

# Weekly Review

Coordinate the recurring repository maintenance review through `weekly-review`.

## Usage

```text
/weekly-review
/weekly-review 7d
/weekly-review since <SHA>
/weekly-review 14d --report-only
/weekly-review 7d --fix
```

`/weekly-review help` prints this Usage block and stops without running anything.

Pass the repository, board URL, optional package scope, window, and existing
authorization to the `weekly-review` skill. Default to seven days and report-only.
Preserve `--report-only` across every delegate; it wins when both flags are supplied. `--fix` authorizes scoped code
repairs; it does not authorize board writes, issue closure, merges, deployments,
or a recurring schedule. Preserve separately granted authority without reasking.

Report unknown arguments and show usage. Resolve ambiguous targets before
dependent work while continuing independent inspection.
