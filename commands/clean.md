# Clean - Unified Cleanup Command

Clean up completed tasks and consolidate session files.

## Usage

```bash
/clean tasks      # Clean completed task files
/clean sessions   # Merge and consolidate session files
/clean all        # Run all cleanup operations
```

## Option 1: Clean Tasks

Empty completed task files — keep filenames (shows what was done), remove content (no bloat).

### Process

1. Find task files where all checkboxes `[x]` or `Status: Complete`
2. Replace content with minimal marker:

```markdown
# [Original Task Name]

**Status:** Completed
**Completed:** [Date]

See `.agents/SESSIONS/[date].md` for details.
```

1. Log cleaned files to today's session file

### Checklist

- [ ] Search `.agents/TASKS/` for completed tasks
- [ ] List found tasks for user confirmation
- [ ] Replace content with completion marker
- [ ] Update session file with cleanup log

## Option 2: Clean Sessions

Merge daily sessions into monthly, monthly into yearly.

### Process

1. **Daily -> Monthly:** Consolidate `YYYY-MM-DD.md` files into `YYYY-MM.md`
2. **Monthly -> Yearly:** Consolidate `YYYY-MM.md` files into `YYYY-yearly-review.md`

### Safety

- Create backup before modifying: `.agents/SESSIONS/backups/`
- Preserve `README.md` and `TEMPLATE.md`
- Dry-run mode available — preview without changes

### Checklist

- [ ] Back up existing sessions
- [ ] Merge daily files for past months
- [ ] Merge monthly files for past years
- [ ] Report what was consolidated

## Option 3: Clean All

Run task cleanup then session cleanup sequentially. Report summary of both.
