# Executor Brief

## Inputs

Save the live issue body and its one current plan comment to separate files.
Read those inputs and this brief before editing. The planner owns all product and
engineering decisions; return any gap to the planner.

## 1 Check

After `git fetch`, obtain the head with `git rev-parse origin/<default-branch>`.
Create the execution branch from that commit. From the installed skill directory,
run `node scripts/plan-header.mjs check <issue-body-file> <plan-comment-file> <head-sha>`.
Exit 0 permits the scan. Exit 1 means report every blocker and stop; return to the
planner. Exit 2 means fix the invocation before continuing.
Any base-commit mismatch returns to the planner. Never judge drift irrelevant;
the planner records its comparison by republishing with the new SHA.

## 2 Scan

Before editing, scan each step's text and fields case-insensitively for:
`TBD`, `TODO`, unfilled `<...>` placeholders, `choose`, `decide`, `as appropriate`,
`appropriately`, `if needed`, `or similar`, `best practice`, and `etc.`.
On a hit, leave that step unedited and return its step ID, quoted text, and
affected AC IDs to the planner. Continue only independent steps whose Touch paths
do not overlap the blocked step.

## 3 Implement

Implement steps in order using the named Pattern. Edit only the step's Touch
paths, including explicitly listed generated outputs. Do not fill missing
decisions. When a Stop if condition fires, stop that step and escalate; continue
only independent steps whose contracts remain valid.

## 4 Verify

Run each step's Check, then every command in the acceptance-to-verification mapping
on the permitted host. Record the command, result, and affected AC IDs. Never
report an unrun check as passed. Return failed or unavailable checks to the planner.

## 5 Escalate

Use these fixed report fields for each failure or gap:

- Step ID:
- AC IDs:
- Quoted evidence:
- Question:
- Completed steps:

## 6 Hand off

Continue with [SKILL.md](../SKILL.md) sections 4-6 for verification, authorized
publication, independent review, delivery gates, and the final status report.
