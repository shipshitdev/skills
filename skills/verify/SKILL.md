---
name: verify
description: "Verification loop behind one command: check a target against evidence, debug each failure to its root cause, fix it test-first, and re-verify until green or a stop condition. Bare /verify runs the loop."
argument-hint: "[loop|check|debug|fix] <target: report path, issue or PR, command, or URL>"
compatibility: Requires git and the repository's own test commands; app-driven checks use the harness's browser tools or an HTTP client. Written to run unattended in Codex or Claude Code.
metadata:
  tags: "verification, debugging, fix-loop, regression, qa, codex, evidence"
  author: Ship Shit Dev
when_to_use: "/verify, verify and fix, loop until green, debug and fix the QA failures, re-verify"
disable-model-invocation: true
---

# Verify

One entry point for the loop that turns "this does not work" into "this works, and
here is the proof": verify, debug, fix, re-verify. The first word of the arguments
picks the action; everything after it goes to that action unchanged.

| Action | Playbook | What it does |
|---|---|---|
| `loop` | [references/loop.md](references/loop.md) | Default. Checks the target, then debugs and fixes each failure one at a time, re-verifying after every fix, until green or a stop condition. One local commit per fix. |
| `check` | [references/check.md](references/check.md) | One report-only verification pass. Produces findings with a deterministic repro and evidence. Changes nothing. |
| `debug` | [references/debug.md](references/debug.md) | Finds the root cause of one failing finding by building a fast, reproducible feedback loop first. Changes no source. |
| `fix` | [references/fix.md](references/fix.md) | Fixes one diagnosed finding test-first with the smallest change and verifies it. One local commit. |

## Dispatch

1. Read the first word of the arguments.
2. If it is one of the actions above, read that playbook in full and follow it as if
   it were the skill, passing the remaining arguments as its arguments. Each playbook
   keeps its own scope, confirmation gates, and final report.
3. Bare `/verify`, or a first word that is not an action: run `loop` with the full
   arguments unchanged.
4. If the first word looks like a mistyped action (for example `chek`), print the
   table above and stop instead of guessing.

Examples:

```text
/verify                                     # loop on the current branch's own checks
/verify .tmp/qa-prod/v1.4.0/report.md       # loop on a post-release QA report's failures (surface prod is inferred)
/verify check #231                          # verify an issue's acceptance criteria, report only
/verify debug "export button does nothing"  # root-cause one failure, change no source
```

In Codex the same commands start with `$` (`$verify loop <target>`). Nothing in these
playbooks depends on a harness-specific tool: browser work uses whatever browser or
page-automation tool the harness provides, and state lives in a ledger file so a run
that loses its context can resume from it.

## The loop in one paragraph

Verify produces findings. Each finding has a command or steps that fail the same way
every time, the expected result, the actual result, and evidence. Debug finds the first
place the system went wrong and proves it. Fix writes the failing check first, makes the
smallest change that turns it green, and commits it. Re-verify runs the finding again
and then the whole set, because a fix that breaks a neighbor is not a fix. The loop
stops only when everything is green, a budget is spent, progress stalls, or a decision
needs a human. It never makes a check pass by weakening it.

## Scope

Loading this router authorizes nothing by itself. Only the selected playbook's contract
applies, and its confirmation gates stay in force. Never chain to a second action unless
the user asks for it or the selected playbook names that step as part of its own workflow
(`loop` runs `check`, `debug`, and `fix`); recommend it instead.

## Credits

The "build a fast, red-capable feedback loop before forming theories" discipline in
`debug` follows the `diagnosing-bugs` skill in
[mattpocock/skills](https://github.com/mattpocock/skills) (MIT). The proof standards in
`check` (drive the real user path, verify side effects, never weaken a journey to make it
pass) and the finding-must-be-reproduced rule follow `create-verification-skill` and
`interrogate` in pstack by Lauren Tan ([cursor/plugins](https://github.com/cursor/plugins),
MIT). The text here is original. When upstream mattpocock `diagnosing-bugs` or `tdd` is
installed, prefer it for a stubborn bug or a deeper test-first session; these playbooks
stay self-contained so they run without it.
