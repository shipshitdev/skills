---
name: check
description: "Review behind one command: review a PR or diff for correctness, security, and spec fidelity; get a verified second opinion through the Grok CLI; or run the weekly engineering review. Bare /check reviews the current branch."
argument-hint: "[code|grok|week] [target]"
compatibility: Requires git; gh for PR targets; grok needs the grok CLI logged in; week needs access to the selected board.
metadata:
  tags: "review, code-review, correctness, security, second-opinion, grok, weekly"
  author: Ship Shit Dev
allowed-tools: Bash(git *) Bash(gh *) Bash(grok *) Bash(command -v *) Bash(mktemp *)
when_to_use: "/check, /check code, /check grok, /check week, review my code, is this safe to merge"
disable-model-invocation: true
---

# Check

One entry point for reviews. The first word of the arguments picks the action;
everything after it goes to that action unchanged. Every action reports; none
edits code without its playbook's explicit repair flag or confirmation.

| Action | Playbook | What it does |
|---|---|---|
| `code` | [references/code.md](references/code.md) | Default. Reviews a PR or diff for correctness, security, and spec fidelity. `adversarial` runs a multi-model panel when pstack `interrogate` is installed. |
| `grok` | [references/grok.md](references/grok.md) | Independent second-opinion review through the Grok CLI; verifies every finding against the code before reporting. |
| `week` | [references/week.md](references/week.md) | Weekly engineering review of board accuracy, recent changes, operational health, and scoped cleanup. Report-only unless `--fix`. |

## Dispatch

1. Read the first word of the arguments.
2. If it is one of the three actions above, read that playbook in full and follow it
   as if it were the skill, passing the remaining arguments as its arguments.
   Each playbook keeps its own scope, confirmation gates, and final report.
3. Bare `/check`, or a first word that is not an action: run `code` with
   the full arguments unchanged.
4. If the first word looks like a mistyped action (for example `grk`), print
   the table above and stop instead of guessing.

Examples:

```text
/check                          # current branch against its base
/check #42                      # a PR
/check adversarial #42          # multi-model panel
/check grok #42                 # second opinion from the Grok CLI
/check week                     # last 7 days, report only
/check week since <SHA> --fix   # also repair confirmed findings in scope
```

## Scope

Loading this router authorizes nothing by itself. Only the selected playbook's
contract applies, and its confirmation gates stay in force. Never chain to a
second action unless the user asks for it or the selected playbook names that
step as part of its own workflow; recommend it instead.
