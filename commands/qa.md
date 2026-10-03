---
description: "Structured verification pass on your changes before commit: bugs, missed requirements, wrong assumptions."
argument-hint: "[scope]"
disable-model-invocation: true
---

# QA - Structured Verification Pass on Your Work

Run a multi-phase verification pass over completed work — checking for bugs,
missed requirements, and incorrect assumptions — before it gets committed. The
on-demand version of the QA gate that `/loop` runs automatically.

## Usage

```bash
/qa              # verify the current uncommitted/branch changes (default)
/qa <scope>      # focus the pass on a path, feature, or set of files
```

`/qa help` prints this Usage block and stops without running anything.

## Workflow

Use the `qa-reviewer` skill.

1. Establish what the change was supposed to do (the requirement / task intent).
2. Run the verification phases — requirements coverage, correctness, edge cases,
   assumptions, and the project's own rules check.
3. Run the quick verification commands (build, lint, scoped tests) the skill
   prescribes for this stack.
4. Report a final assessment bucketed by category, with concrete gaps to fix —
   read-only, it reports rather than edits.

## Gates

- Read-only and advisory. Surfaces what to fix; it does not apply changes or
  commit.

## Related

- `/qa` is the direct shortcut for `/test qa` — same `qa-reviewer` engine,
  kept as its own command because it is the most-used pre-commit gate.
- `/qa` verifies *your* work before commit; `/review` is the correctness +
  security gate on a diff/PR. Run `/qa` before `/pr`.
