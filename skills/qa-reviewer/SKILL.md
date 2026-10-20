---
name: qa-reviewer
description: Runs a multi-phase verification pass on finished AI agent work to catch bugs, missed requirements, and bad assumptions. Use after long multi-step tasks or on check your work.
metadata:
  tags: "quality-assurance, verification, code-review, accuracy, completeness"
when_to_use: "check your work, verify before commit"
disable-model-invocation: true
---

# QA Reviewer: Systematic Work Verification

## Purpose

Structured framework for reviewing AI agent work before finalizing changes. Catches bugs, verifies accuracy, ensures completeness, validates solutions match requirements.

## When to Use

- User says "check your work" or "review this"
- After completing complex multi-step implementations
- Before committing major refactors
- When modifying commands or skills
- After implementing new features
- Proactively after any task >5 steps

## QA Workflow Phases

### 1. Context Gathering

- Review original task and requirements
- List all deliverables (files created/modified/deleted)
- Check critical rules in the repository's instruction files (`AGENTS.md`,
  `AGENTS.override.md`, `CLAUDE.md`, or configured fallbacks)

### 2. Requirement Verification

- Create checklist of all requirements
- Verify solution alignment
- Check for edge cases

### 3. Accuracy Verification

- Verify file paths exist
- Confirm patterns match codebase
- Cross-reference citations

### 4. Bug Detection

- Check syntax (markdown, code, paths)
- Look for logic errors
- Verify project-specific rules

### 5. Completeness Audit

- Reconcile todo list
- Verify all mentioned files changed
- Check for side effects

### 6. Optimization Review

- Evaluate solution quality
- Check pattern consistency
- Consider alternatives

## Quick Verification Commands

```bash
# Verify file exists
ls -la <file-path>

# Check balanced code blocks
grep -c '```' file.md

# Find violations
grep -r "console\.log" <files>
grep -r ": any" <files>
```

## Project Rules Check

Example checklist. Replace it with the rules in the repository's own instruction files.

- [ ] No console.log (use logger)
- [ ] No `any` types
- [ ] No inline interfaces
- [ ] Repository instruction files intact and scoped overrides intentional
- [ ] Configured fallback instruction files exist and are nonempty
- [ ] Agent configuration folders untouched unless the task required changes
- [ ] Project invariants preserved (for example multi-tenancy, if the project has it)

## Final Assessment Categories

- **Approve** - Ready to commit
- **Conditional** - Fix issues first
- **Reject** - Significant problems

---

For complete workflow phases, output format template, common issue patterns, and advanced techniques, load `${CLAUDE_SKILL_DIR}/references/full-guide.md` when performing a comprehensive QA pass or when the task has more than three deliverables.
