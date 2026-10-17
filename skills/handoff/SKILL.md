---
name: handoff
description: Writes a handoff document so a fresh agent session can continue the current work. User-invoked.
disable-model-invocation: true
license: MIT
metadata:
  version: "2.2.5"
  tags: "handoff, context, session, continuity"
  author: Ship Shit Dev
  source: https://github.com/mattpocock/skills/blob/main/skills/productivity/handoff/SKILL.md
  upstream_repo: mattpocock/skills
  upstream_ref: main
  upstream_commit: 4588b32ecab9
  last_synced: "2026-10-05"
  license: MIT
when_to_use: "handoff, hand this off, new session, continue in a fresh agent"
argument-hint: "[what the next session is for]"
---

# Handoff

Compact the current conversation into one file a fresh agent can pick up cold.
Use it at a phase boundary where `/clear` would lose too much; `ask-dev-loop`
holds the tree that decides when.

## Contract

Inputs:

- The current conversation and working state
- Optional argument: what the next session is for

Outputs:

- One Markdown handoff file and its absolute path

Creates/Modifies:

- `${CODEX_HOME:-$HOME/.codex}/artifacts/handoffs/<date>-<slug>.md`, or a path
  the user names. Never the repository and never the machine temp directory

External Side Effects:

- None

Confirmation Required:

- None for the file. Starting the next session stays with the user

Delegates To:

- Recommend `recall` or the `pstack` Session pickup as the receiving side

## Write the document

Tailor everything to the argument when one is given. Sections, in order:

1. **Goal**: what the next session is for, one sentence.
2. **State**: done, in progress, not started. Mark each claim *verified* (with the
   command or file that proved it) or *unverified*.
3. **Decisions**: each with the reason, so the next agent does not reopen it.
4. **Open**: blockers and unanswered questions, with who can answer.
5. **Pointers**: specs, plans, ADRs, issues, PRs, commits and diffs as paths or
   URLs. Reference; never restate.
6. **Suggested skills**: the skills the next agent should run first, resolved
   through the active skill catalog.
7. **First move**: the single next action.

Redact secrets, tokens and personal data as `<REDACTED>`.

Done when the file exists, every pointer resolves, and the absolute path is
reported.
