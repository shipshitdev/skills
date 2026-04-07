---
name: session-start
description: Load critical preferences, session history, and inbox tasks at session start. Use when user says 'start', 'start session', 'load context', or after running /clear.
version: 1.0.0
tags:
  - session
  - workflow
  - context
  - productivity
---

# Session Start

Load all critical preferences and instructions at the start of each session or after `/clear`.

## Workflow

### 1. Read Session Quick Start

Read the primary entry point document:

Read `.agents/SYSTEM/ai/SESSION-QUICK-START.md`.

This document will guide you to any other necessary documentation.

### 2. Read User Preferences (CRITICAL)

Read the user's non-negotiable preferences at `.agents/SYSTEM/ai/USER-PREFERENCES.md`.

This file contains:

- Critical rules (NEVER build/test locally, check recent sessions, follow codebase patterns)
- Quality standards
- Communication preferences
- Past corrections and lessons learned

### 3. Read Today's Session File

Read today's session to understand what was already done before `/clear`:

Read today's session file at `.agents/SESSIONS/YYYY-MM-DD.md` (where YYYY-MM-DD is today's date).

If the file exists, this shows what tasks were completed, decisions made, files changed, and patterns used. If the file doesn't exist yet, this is a fresh session day.

### 4. Activate Session Documenter

Run the `session-documenter` skill to track all work throughout the session.

### 5. Display Inbox Tasks

Show the current inbox backlog from `.agents/TASKS/INBOX.md` in two categories:

1. **Human QA (Blocking Production)** — Tasks requiring manual testing
2. **Features to Prompt** — Tasks ready for AI implementation

### 6. Confirmation

After reading all files and displaying inbox, provide a brief confirmation (5-7 bullet points max):

- Critical rules understood
- Today's session context loaded (if exists)
- Ready to follow codebase-specific patterns
- Session documenter active
- Inbox tasks displayed

## Related Skills

- **session-end** — Document session before clearing context
- **session-documenter** — Tracks work throughout the session
