---
name: ai-dev-loop
description: Orchestrate autonomous AI development with task-based workflow and QA gates
---

# AI Development Loop

Autonomous task execution with QA gates across multiple AI platforms.

## Overview

The AI Development Loop enables fully autonomous feature development where:

- AI agents pick up and implement tasks from a queue
- You do QA only (approve or reject in Testing column)
- Multiple platforms (Claude CLI, Cursor, Codex) can work in parallel
- Rate limits are maximized by switching between platforms

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   BACKLOG   │────▶│   TO DO     │────▶│  TESTING    │────▶│    DONE     │
│             │     │             │     │             │     │             │
│  PRDs ready │     │ Agent picks │     │ YOU review  │     │  Shipped    │
│             │     │ & builds    │     │ & approve   │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                          │                   │
                    ┌─────┴─────┐       ┌─────┴─────┐
                    │  Claude   │       │  Reject   │
                    │  Cursor   │       │  → To Do  │
                    │  Codex    │       └───────────┘
                    └───────────┘
```

## Task Lifecycle

### 1. Task Creation

Tasks live in `.agents/TASKS/[task-name].md` with structured metadata:

```markdown
## Task: [Feature Name]

**ID:** feature-name-slug
**Status:** Backlog | To Do | Testing | Done
**Priority:** High | Medium | Low
**PRD:** [Link](../PRDS/prd-file.md)

### Agent Metadata

**Claimed-By:** [platform-session-id]
**Claimed-At:** [timestamp]
**Completed-At:** [timestamp]

### Progress

**Agent-Notes:** [real-time updates]
**QA-Checklist:**

- [ ] Code compiles/lints
- [ ] Tests pass (CI)
- [ ] User acceptance
- [ ] Visual review

### Rejection History

**Rejection-Count:** 0
**Rejections:** [list of rejection notes]
```

### 2. Task Claiming

When an agent runs `/loop`:

1. Scans `.agents/TASKS/` for `Status: To Do`
2. Sorts by priority (High > Medium > Low)
3. Skips tasks with active claims (< 30 min old)
4. Updates task with `Claimed-By` and `Claimed-At`

### 3. Implementation

Agent works on the task:

1. Reads task file and linked PRD
2. Checks `.agents/SESSIONS/` for related past work
3. Implements the feature/fix
4. Updates `Agent-Notes` with progress
5. Creates branch and commits

### 4. Quality Check

Before moving to Testing:

1. Runs qa-reviewer skill
2. Updates QA-Checklist items
3. Ensures code compiles/lints

### 5. Completion

Agent finalizes:

1. Sets `Status: Testing`
2. Sets `Completed-At` timestamp
3. Adds final summary to `Agent-Notes`
4. Prompts for next action

### 6. QA Gate (Your Turn)

In Kaiban.md:

1. Review Testing column
2. Click task to see PRD preview
3. Check linked PR
4. **Approve**: Drag to Done
5. **Reject**: Click reject, add note → returns to To Do

### 7. Rejection Handling

When rejected:

1. Status returns to To Do
2. Rejection-Count increments
3. Rejection note added to history
4. Next `/loop` picks up with full context

## Multi-Platform Strategy

### Platform Strengths

| Platform   | Best For                             |
| ---------- | ------------------------------------ |
| Claude CLI | Complex logic, backend, architecture |
| Cursor     | UI components, styling, visual work  |
| Codex      | Bulk refactoring, migrations, docs   |

### Parallel Execution

Multiple platforms can work simultaneously:

- Each claims different tasks
- Claims prevent conflicts (30-min lock)
- Shared state via task files

### Rate Limit Handling

When rate limited:

1. Agent saves progress to `Agent-Notes`
2. Releases claim (clears `Claimed-By`)
3. Suggests switching platform
4. User continues with different platform

## Daily Workflow

### Morning QA Session

1. Open Kaiban.md extension in VS Code
2. Review Testing column
3. Approve good work → Done
4. Reject with notes → To Do

### Throughout Day

```bash
# Claude CLI
claude
> /loop   # Process task
> /loop   # Next task
# Rate limited? Switch to Cursor
```

### Rate Limit Strategy

```
Claude limit? → Switch to Cursor
Cursor limit? → Switch to Codex
All limited? → QA time (review Testing)
```

## Integration Points

### Kaiban.md Extension

- Visual Kanban board for `.agents/TASKS/`
- Drag & drop status changes
- PRD preview panel
- Reject button with note input
- Agent claim status badges

### Existing Skills

- **qa-reviewer**: 6-phase quality verification
- **session-documenter**: Auto-document completed work
- **rules-capture**: Learn from rejection feedback

### Git Workflow

- Branch per task: `feature/[task-id]`
- Commits with clear messages
- PR linked in task file

## Not a Daemon

Important: `/loop` is NOT a background process.

- Each invocation handles ONE task
- Returns control to user
- User decides to continue or stop
- Respects "never run background processes" rule

## Claim Expiration

Claims expire after 30 minutes:

- Handles agent crashes
- Handles rate limit interruptions
- Previous `Agent-Notes` provide context for pickup
- Enables multi-platform handoff

## Best Practices

### For Task Creation

- Write clear, actionable task descriptions
- Link to PRD for requirements
- Set appropriate priority
- Include testing criteria

### For Agents

- Read task and PRD thoroughly before starting
- Update `Agent-Notes` regularly
- Run qa-reviewer before completing
- Create clean, focused commits

### For QA (You)

- Review PRD alongside implementation
- Provide specific rejection feedback
- Approve incrementally (don't batch)
- Keep Testing column short
