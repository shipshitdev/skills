# QA Reviewer - Full Guide

## QA Review Workflow

### Phase 1: Context Gathering

**1.1 Understand Original Task**

Review the conversation to identify:

- Primary objective stated by user
- All explicit requirements mentioned
- Implicit constraints or preferences
- Success criteria (if stated)
- Any "don't do this" warnings

**Questions to answer:**

- What was the user trying to achieve?
- What were the exact requirements?
- Were there any constraints mentioned?
- What files/systems were involved?

**1.2 Identify Deliverables**

List all changes made:

- Files created
- Files modified
- Files deleted
- Commands run
- Patterns introduced

**1.3 Check Critical Rules**

For projects, ALWAYS verify against:

```bash
cat .agents/SYSTEM/critical/CRITICAL-NEVER-DO.md
cat .agents/SYSTEM/critical/CROSS-PROJECT-RULES.md
```

### Phase 2: Requirement Verification

**2.1 Completeness Check**

Create a checklist of all requirements:

```
Original Requirements:
[ ] Requirement 1: <description>
[ ] Requirement 2: <description>
[ ] Requirement 3: <description>

Verification:
[ ] All requirements addressed?
[ ] Any requirements missed?
[ ] Any out-of-scope work done?
```

**2.2 Solution Alignment**

Ask:

- Does the solution actually solve the stated problem?
- Are there edge cases not handled?
- Does it work for all mentioned scenarios?
- Any assumptions made that could be wrong?

### Phase 3: Accuracy Verification

**3.1 Fact Checking**

Verify all factual claims:

- File paths actually exist
- Directory structures are accurate
- Referenced files contain what you claim
- Patterns match actual codebase
- Version numbers are correct
- Commands actually work

**How to verify:**

```bash
# Verify file exists
ls -la <file-path>

# Verify directory structure
find <dir> -type f | head -20

# Verify pattern in file
grep -n "<pattern>" <file>

# Test command syntax
<command> --help
```

**3.2 Cross-Reference Validation**

When citing documentation:

- Read the actual file
- Verify line numbers if cited
- Confirm context matches claim
- Check for recent updates

### Phase 4: Bug Detection

**4.1 Syntax Errors**

Check for:

- Markdown syntax (balanced code blocks, proper headers)
- Code syntax (if code written)
- File path syntax (proper slashes, no typos)
- Command syntax (proper flags, quotes)

**Verification commands:**

```bash
# Check balanced code blocks
python3 -c "
content = open('file.md').read()
blocks = content.count('```')
print(f'Blocks: {blocks}, Balanced: {blocks % 2 == 0}')
"

# Check file paths
ls <path> || echo "Path doesn't exist!"
```

**4.2 Logic Errors**

Look for:

- Contradictory instructions
- Circular references
- Incorrect conditionals
- Missing error handling
- Race conditions

**4.3 Project-Specific Violations**

Check against CRITICAL-NEVER-DO.md:

```
Violations to check:
[ ] No console.log (use logger)
[ ] No `any` types
[ ] No inline interfaces
[ ] No deletedAt (use isDeleted)
[ ] No serializers in API repo
[ ] No test execution locally
[ ] Multi-tenancy enforced
[ ] AGENTS.md/CLAUDE.md/CODEX.md not deleted
[ ] .agents/ folders not deleted
```

### Phase 5: Completeness Audit

**5.1 Todo List Reconciliation**

If TodoWrite was used:

- Were all todos completed?
- Any todos abandoned without explanation?
- Were todos accurate to what was done?

**5.2 File Coverage**

Verify all mentioned files:

```bash
# For each file mentioned in work summary
# Verify it was actually changed
git status | grep <file>
git diff <file>
```

**5.3 Side Effects**

Check for unintended consequences:

- Breaking changes introduced?
- Dependencies affected?
- Related files need updates?
- Documentation out of sync?

### Phase 6: Optimization Review

**6.1 Solution Quality**

Ask:

- Is this the optimal approach?
- Are there simpler solutions?
- Is it over-engineered?
- Is it under-engineered?
- Performance concerns?

**6.2 Pattern Consistency**

Check:

- Follows existing codebase patterns?
- Consistent with other similar implementations?
- Uses established conventions?
- Matches team style?

## Output Format

```markdown
# QA Review Report

## Context

**Task:** <original user request>
**Deliverables:** <what was changed>
**Scope:** <how many files, lines, etc.>

## Requirements Verification

Requirement Coverage:

- Requirement 1: <status>
- Requirement 2: <status>
- Requirement 3: <issue found>

Overall: X/Y requirements fully met

## Accuracy Check

Facts Verified:

- File paths: All exist and accurate
- Patterns: Verified against actual codebase
- References: Cross-checked with source files
- Issue: <describe any inaccuracy found>

## Bugs Found

Critical:

- Bug 1: <description>
  - Location: <file:line>
  - Impact: <what breaks>
  - Fix: <how to fix>

Minor:

- Bug 2: <description>
  - Impact: <minor issue>
  - Fix: <suggestion>

## Completeness

- All files mentioned were modified
- All todos completed
- Missing: <anything incomplete>
- Side effects: <unintended changes>

## Project Rules Compliance

CRITICAL-NEVER-DO.md:

- No console.log violations
- No `any` types added
- No inline interfaces
- No test execution locally
- Multi-tenancy preserved
- Mandatory files protected

## Optimization Suggestions

Improvements:

1. <suggestion 1 with reasoning>
2. <suggestion 2 with reasoning>

## Final Assessment

**Overall Quality:** Excellent | Good with issues | Needs revision

**Recommendation:**

- [ ] Approve - Ready to commit
- [ ] Conditional - Fix issues first
- [ ] Reject - Significant problems

**Critical Actions Required:**

1. <action if any>
2. <action if any>
```

## Common Issue Patterns

### Pattern 1: Inaccurate File Paths

**Symptom:** Referenced files don't exist at stated paths

**Detection:**

```bash
ls <claimed-path> || echo "NOT FOUND"
```

**Fix:** Verify actual structure before referencing

### Pattern 2: Unbalanced Markdown

**Symptom:** Code blocks not closed, broken formatting

**Detection:**

````python
code_blocks = content.count('```')
balanced = code_blocks % 2 == 0
````

**Fix:** Ensure all ``` markers are paired

### Pattern 3: Incomplete Requirements

**Symptom:** User asked for A, B, C but only A, B delivered

**Detection:** Create explicit checklist from requirements

**Fix:** Address all requirements or explain why not

### Pattern 4: Pattern Drift

**Symptom:** New code doesn't match existing patterns

**Detection:** Compare with similar existing implementations

**Fix:** Align with established patterns

### Pattern 5: Assumption Cascade

**Symptom:** One wrong assumption leads to multiple errors

**Detection:** Verify base assumptions first

**Fix:** Validate assumptions before building on them

## Advanced Techniques

### Differential Analysis

Compare before/after states:

```bash
# Create snapshot before work
git diff HEAD > before.diff

# After work, compare
git diff HEAD > after.diff
diff before.diff after.diff
```

### Pattern Matching

Use grep to find violations:

```bash
# Find console.log
grep -r "console\.log" <files>

# Find any types
grep -r ": any" <files>

# Find test execution
grep -r "npm test\|pnpm test\|vitest run" <files>
```

### Cross-Reference Validation

Verify claims against multiple sources:

```bash
# Claim: "Serializers in [packages-project]"
# Verify 1: Check packages
ls [packages-project]/packages/common/serializers/

# Verify 2: Check NOT in API
find [api-project] -name "*serializer*" -type f

# Verify 3: Check CRITICAL-NEVER-DO.md confirms
grep -i "serializer" .agents/SYSTEM/critical/CRITICAL-NEVER-DO.md
```

## Best Practices

### For Reviewers (AI Agents)

1. **Be Thorough**: Don't skip steps, even if work looks good
2. **Verify Facts**: Never assume, always check
3. **Read Actual Files**: Don't rely on memory or assumptions
4. **Test Commands**: Run them to ensure they work
5. **Check Edge Cases**: Think about what could go wrong
6. **Be Specific**: Point to exact lines, files, issues
7. **Suggest Fixes**: Don't just identify problems, propose solutions
8. **Be Balanced**: Acknowledge good work, not just issues

### For Developers (Users)

1. **Use Proactively**: Don't wait for bugs to appear
2. **Review Reports Carefully**: QA catches what humans miss
3. **Act on Findings**: Fix critical issues before committing
4. **Learn Patterns**: Recurring issues indicate systemic problems
5. **Provide Feedback**: Help improve the QA process

## Continuous Improvement

Track common issues over time:

- Which bugs appear repeatedly?
- Which patterns are often missed?
- Which checks catch the most issues?
- How can the QA process improve?

**Adapt the checklist based on:**

- Project evolution
- New patterns introduced
- Lessons learned
- Team feedback
