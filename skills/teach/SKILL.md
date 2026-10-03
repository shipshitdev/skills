---
name: teach
description: Explain a body of work so a person actually understands it. Runs how and why and weaves what they find into one plain explanation, built up diagram by diagram. Use for teach me this, help me really understand X, or explain this change or subsystem.
license: MIT
metadata:
  portable_source: "https://github.com/ericlitman/open-pstack"
  portable_commit: "56bfd14418fa733e34d98f714f357d28788470e3"
  version: "2.2.2"
  tags: "teaching, explanation, onboarding"
  author: Ship Shit Dev
  source: https://github.com/cursor/plugins/blob/main/pstack/skills/teach/SKILL.md
  upstream_repo: cursor/plugins
  upstream_ref: main
  upstream_commit: bdf7aa355337
  last_synced: "2026-09-05"
  license: MIT
when_to_use: "teach me this, help me really understand, explain this subsystem"
---

# Teach

Explain what a thing is, how it works, and why it is built that way,
in one plain account at the person's pace. Change nothing.

## Authorized Scope

Apply this engine only within the user's requested task and existing explicit
authorization. Loading or delegating to it grants no additional authority.
Preserve report-only restrictions and the caller's target, host, provider, and
cost limits. Existing approval satisfies a gate only for the same actions and
scope; obtain approval before expanding them. Forward these limits to delegates.

## Contract

Inputs:

- A change, subsystem, or concept the person wants to understand

Outputs:

- The explanation itself, never a report about what you delivered

Creates/Modifies:

- None

External Side Effects:

- None beyond the read-only work `how` and `why` do

Confirmation Required:

- None

Delegates To:

- `how` and `why` for investigation. Do not redo their digging.

## Steps

1. Decide the few things they should walk away understanding, from why
   they are asking and what they already know. Do not quiz them.
2. Let `how` and `why` do the work. Run them in parallel when both
   matter. Keep `why` narrow by default. Keep `why`'s confidence
   language intact.
3. Start with a plain definition. Then tie it to the case in front of
   you. Give the smallest complete answer first, a sentence or two,
   then stop. Add layers when they ask.
4. Keep it a conversation. No quizzes. No pacing theater. No
   "the key insight" labels.
5. Show, don't only tell. For three or more moving parts, draw a short
   series of diagrams that each add one part. Mermaid for flows. Skip
   a figure that only decorates.

Apply `references/prose-slop.md` from the selected `deslop` skill directory. Give each concept one
name and keep it.

**Reply:** the explanation. Lead with the main point, then what it is,
how it works, and why.

## Teach procedure

Read [teach procedure](references/teach-procedure.md) when running this workflow.
Apply the authorized scope and mode of this entry point to every step.
Resolve other skills through this distribution’s active catalog; resolve
resources relative to the installed skill directory.
