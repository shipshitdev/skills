---
name: session-end
description: Document session context before clearing. Use when user says 'end session', 'end', 'wrap up', or before running /clear.
version: 1.0.0
tags:
  - session
  - workflow
  - documentation
  - productivity
---

# Session End

Document your session before clearing context. This is a TWO-STEP process: `/session-end` documents, then user manually runs `/clear`.

## Workflow

### Step 1: Document Session

When invoked, immediately:

1. Run the `session-documenter` skill to save all session context
2. Let it complete — it will document tasks, decisions, files changed, patterns, and mistakes
3. Confirm documentation saved

> **Cross-platform note**: If your agent platform doesn't support skill invocation, follow the session-documenter workflow manually by reading the `session-documenter` skill definition.

### Step 2: Remind User to Clear

After documentation is complete, tell the user:

```
Session documented to .agents/SESSIONS/YYYY-MM-DD.md

NEXT STEP: Run /clear to clear the conversation context.
Your session is safely preserved and will be loaded on next /session-start.
```

## Why This Matters

- WITHOUT documentation: all context is lost forever, next session has no idea what was done
- WITH documentation: context preserved, next `/session-start` reads the session file, continuity maintained

## Important Notes

- **ONE FILE PER DAY**: Session documenter appends to the same day's file
- **Multiple invocations**: Each one adds a new session entry
- **Does NOT clear context**: User must run `/clear` manually after

## Related Skills

- **session-start** — Loads preferences and today's session after clearing
- **session-documenter** — The underlying documentation skill
