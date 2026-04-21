# Inbox - Quick Task Capture

Fast task capture into project-scoped inbox. Backlog only — no status tracking.

## Usage

```bash
/inbox                    # View inbox
/inbox [task description] # Quick add
/inbox expand             # Expand task to GitHub issue
```

## File Location

Each project has its own inbox at `.agents/inbox.md` in the project root.

If the file doesn't exist, create it with:

```markdown
# Inbox

## Backlog

<!-- Quick-captured tasks. Expand to GitHub issues when ready. -->
```

## Mode 1: View Inbox

Read `.agents/inbox.md` and display backlog items.

## Mode 2: Quick Capture

1. Extract task title from arguments
2. Ask: "Brief context? (1-2 sentences)" (skip if user already provided)
3. Append to Backlog section:

```markdown
- [ ] **[TASK_TITLE]** ([TODAY_DATE])
  [USER_CONTEXT]
```

1. Confirm added.

## Mode 3: Expand

1. Show numbered list of backlog items
2. Ask which to expand
3. Gather enough detail for a GitHub issue (problem, approach, acceptance criteria)
4. Create GitHub issue via `gh issue create`
5. Remove from inbox, note issue number

## Task Format

```markdown
- [ ] **Task Title** (YYYY-MM-DD)
  Brief context. Priority: HIGH/MEDIUM/LOW (optional)
```

Keep simple. Once expanded to issue, remove from inbox.
