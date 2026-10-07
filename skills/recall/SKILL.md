---
name: recall
description: Rebuilds recent working context from chat history, live state, and the shared record into a tight current-state brief. Use to resume or catch up on past work.
license: MIT
metadata:
  portable_source: "https://github.com/ericlitman/open-pstack"
  portable_commit: "1b03678171f6f400ae2cc9dc4e7a4a6a13e4bb43"
  version: "2.2.4"
  tags: "context, resume, briefing"
  author: Ship Shit Dev
  source: https://github.com/cursor/plugins/blob/main/pstack/skills/recall/SKILL.md
  upstream_repo: cursor/plugins
  upstream_ref: main
  upstream_commit: bdf7aa355337
  last_synced: "2026-09-05"
  license: MIT
when_to_use: "catch me up, where did I leave off, recall my work"
---

# Recall

Before you start or resume work, rebuild the user's recent working
context and hand back a tight capsule.

Companion to `pstack` Session pickup (one specific prior chat) and
`memory-systems` (designing persistent agent memory). This skill loads
working context across recent chats and the shared record.

## Authorized Scope

Act only within the user's request and existing approval; loading this skill
grants no new authority. Keep report-only requests report-only, honor the
caller's target, host, provider, and cost limits, ask before expanding scope,
and forward these limits to delegates.

## Contract

Inputs:

- An optional topic and time window (default last 7 days)
- The active workspace only

Outputs:

- A brief: capsule, tagged threads, recurring problems, next move

Creates/Modifies:

- None

External Side Effects:

- Read-only git / `gh` and whatever evidence connectors `why` uses

Confirmation Required:

- None

Delegates To:

- `why` investigators for the shared record
- Recommend `pstack` Session pickup when the ask is one specific prior chat

## Steps

1. Classify. One specific prior chat is Session pickup. A full state
   capsule already in the message skips mining.
2. Lock the scope. Pin the window, the topic, and the workspace. State
   the scope back. Never quietly turn "all" into "recent N". Never
   read another project's transcripts without being asked.
3. Fan out across chat history. Spawn parallel subagents on the fast
   cheap tier. Order candidates by real modification time. Each
   returns topic, goal, decisions, open threads, struggles, and
   artifacts, citing the chat id the harness uses.
4. Sweep the shared record whenever the topic names a feature, file,
   subsystem, or bug. Hand it to `why` investigators, steered to
   current state, what was tried, and what users still report.
5. Verify against live state with `git` and `gh`.
6. Write the brief to the contract below.

## Output contract

- **Capsule.** At most 5 bullets.
- **Threads.** One line each, prefixed with exactly one status tag:
  `[merged #N]`, `[open PR #N]`, `[in flight <branch>]`,
  `[verified, uncommitted]`, `[reverted #N]`, or
  `[planned, not started]`.
- **Problems.** At most 5 recurring ones.
- **Next move.** The single most useful next action.

Apply `references/prose-slop.md` from the selected `deslop` skill directory. Sanitize private
context before any public output.

## Recall procedure

Read [recall procedure](references/recall-procedure.md) when running this workflow.
Apply the authorized scope and mode of this entry point to every step.
Resolve other skills through this distribution’s active catalog; resolve
resources relative to the installed skill directory.
