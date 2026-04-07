---
name: session-documenter
description: Document session work to .agents/SESSIONS/YYYY-MM-DD.md. Use when user says 'document session', 'save session', 'what did we do', or when invoked by session-start/session-end skills.
version: 1.0.0
tags:
  - session
  - documentation
  - workflow
  - productivity
---

# Session Documenter Skill

Document work, decisions, and context with explicit commands.

## Commands

| Command | Action |
|---------|--------|
| `/start` | Begin new session - creates/appends to today's file, loads context |
| `/end` | Finalize session - writes entry with all tracked work, updates related files |

## How It Works

1. **`/start`** - Creates `.agents/SESSIONS/YYYY-MM-DD.md` if missing, or loads existing context
2. **During session** - You tell me what to track: decisions, files changed, mistakes
3. **`/end`** - I write the full session entry with flowcharts, decisions, next steps

## Critical Rules

### Session File Naming (ONE FILE PER DAY)

```
✅ CORRECT: .agents/SESSIONS/2025-11-15.md
❌ WRONG:   .agents/SESSIONS/2025-11-15-feature-name.md
```

Multiple sessions same day → Same file, Session 1, Session 2, etc.

### Flowcharts (MANDATORY for features)

Include flowchart for:

- New features
- Feature modifications
- Multi-component bug fixes

## Session Entry Structure

1. **Session number and title**
2. **System flow diagram** (mermaid or text)
3. **Affected components** (frontend, backend, data, external)
4. **What was done** (task checklist)
5. **Key decisions** (with rationale)
6. **Files changed**
7. **Mistakes and fixes**
8. **Next steps**

## Related Files to Update

- `.agents/SESSIONS/README.md`
- `.agents/SYSTEM/SUMMARY.md`
- `.agents/TASKS/*/TODO.md`
- `.agents/SYSTEM/ARCHITECTURE.md` (if architectural decisions)

## References

- [Full guide: Phases, automation, validation, examples](references/full-guide.md)
