---
name: qa
description: "QA behind one command: a localhost QA loop that fixes what you report, a verification pass over finished agent work, or post-release QA of a shipped release on production with a dedicated account. Bare /qa starts the loop."
argument-hint: "[run|review|prod] [focus|tag]"
compatibility: Requires git; run needs a locally runnable application and uses Portless when the project already configures it; prod needs gh, Node.js, and QA-account credentials in the environment.
metadata:
  tags: "qa, localhost, browser-testing, debugging, screenshots, verification, review, post-release, production"
  author: Ship Shit Dev
when_to_use: "/qa, /qa run, /qa review, /qa prod, post-release QA, QA the release, check your work"
disable-model-invocation: true
---

# QA

One entry point for checking work. The first word of the arguments picks the
action; everything after it goes to that action unchanged.

| Action | Playbook | What it does |
|---|---|---|
| `run` | [references/run.md](references/run.md) | Default. Creates today's `qa/YYYY-MM-DD` from freshly fetched `origin/<default>` in the current checkout (or resumes it), then reproduces, fixes, and re-verifies each issue you report, one local commit per fix. Never pushes, opens a PR, or deploys. |
| `review` | [references/review.md](references/review.md) | Multi-phase verification pass on finished agent work: bugs, missed requirements, and bad assumptions. |
| `prod` | [references/prod.md](references/prod.md) | Post-release QA: exercises every feature in a release, and the cards in the human-review column, on production with a dedicated QA account. Reports pass or fail with repro steps and evidence. Fixes nothing unless asked. Setup: [references/prod-setup.md](references/prod-setup.md). |

## Dispatch

1. Read the first word of the arguments.
2. If it is one of the actions above, read that playbook in full and follow it
   as if it were the skill, passing the remaining arguments as its arguments.
   Each playbook keeps its own scope, confirmation gates, and final report.
3. Bare `/qa`, or a first word that is not an action: run `run` with
   the full arguments unchanged.
4. If the first word looks like a mistyped action (for example `reveiw`), print
   the table above and stop instead of guessing.

Examples:

```text
/qa                               # start or resume today's QA loop
/qa the onboarding flow           # same, focused on one area
/qa review                        # check finished agent work against the ask
/qa prod v1.4.0                   # QA that release on production, report only
```

## Scope

Loading this router authorizes nothing by itself. Only the selected playbook's
contract applies, and its confirmation gates stay in force. Never chain to a
second action unless the user asks for it or the selected playbook names that
step as part of its own workflow; recommend it instead.
