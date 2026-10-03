---
description: "Name the Dev Loop skill that fits your current situation, and why."
argument-hint: "[situation]"
disable-model-invocation: true
---

# Ask - Which Dev Loop skill to run

Name the flagship skill that fits the current situation. Hint only — do not fire
other user-invoked skills.

## Usage

```bash
/ask                 # route the current situation to a Dev Loop skill
/ask "I have an idea"
/ask "this bug keeps coming back"
```

`/ask help` prints this Usage block and stops without running anything.

## Workflow

Use the `ask-dev-loop` skill. Match the situation to the main flow, an on-ramp
(bug, intake, foggy large work), review, setup, or a standalone (`wait-what`,
`wizard`, `prototype`). Reply with the skill to type, why, and what happens next.
