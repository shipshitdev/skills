---
name: task-prd-creator
description: 'Create a well-written PRD, task, or GitHub issue/sub-issue for a feature, bug, or enhancement. Use when planning work, writing GitHub issues, breaking down epics into sub-issues, or creating local task files. Common prompts: create a task, write a PRD, open a GitHub issue, create a sub-issue, plan this feature, write up this bug, break this down into issues, I want to add X, implement Y.'
disable-model-invocation: true
allowed-tools: Bash(gh *)
---

# Task & PRD Creator

Write a clear, actionable PRD or task. Output depends on where the user tracks work.

## Step 1: Detect workflow preference

Check in order:

1. User explicitly says "GitHub issue", "local file", or both
2. Check if `gh auth status` succeeds and a GitHub remote exists → GitHub available
3. Check if `.agents/TASKS/` or `.agents/PRDS/` exist → local available
4. If ambiguous, ask: "GitHub issue, local file, or both?"

## Step 2: Understand the request

Ask only what's missing — don't interrogate if context is clear:

- What problem does this solve?
- Who's affected? (user-facing, internal, infra)
- Any hard constraints or dependencies?
- Is this part of a larger epic? (→ sub-issue)
- Priority: critical / high / medium / low

## Step 3: Research before writing

- Read relevant architecture docs if available (`.agents/SYSTEM/ARCHITECTURE.md`)
- Search codebase for related patterns
- Check for existing issues on same topic: `gh issue list --search "[keyword]"`

## Step 4: Write the PRD

See `references/full-guide.md` for the full PRD structure.

A good PRD has:

- **Problem** — why this exists, what breaks without it
- **Goal** — one sentence, measurable outcome
- **Scope** — what's in, what's explicitly out
- **Acceptance criteria** — testable, not vague
- **Technical notes** — approach, risks, dependencies

Keep it tight. No filler. Acceptance criteria must be checkable by a human.

## Step 5: Output to correct destination

### GitHub (primary if available)

**New issue:**

```bash
gh issue create \
  --title "[type]: clear title" \
  --body "$(cat <<'BODY'
[PRD content here]
BODY
)" \
  --label "feature" \
  --assignee "@me"
```

**Sub-issue** (linked to parent):

```bash
# Create sub-issue
gh issue create --title "..." --body "..." 

# Link as sub-issue to parent #N
gh issue develop N --checkout  # only if needed
# Use: gh api repos/{owner}/{repo}/issues/{parent}/sub_issues --method POST -f sub_issue_id={child_id}
```

**Draft PR from issue:**

```bash
gh issue develop [issue-number] --branch "feature/[name]"
```

### Local files (optional, or when no GitHub)

- Task: `.agents/TASKS/[kebab-name].md`
- PRD: `.agents/PRDS/[kebab-name].md`

See `references/full-guide.md` for local file templates.

## Step 6: Get approval before creating

Show the draft PRD. Wait for "looks good" or edits. Then create.

## Rules

- `disable-model-invocation: true` → only runs when user explicitly invokes
- Never create files or GitHub issues without user seeing the draft first
- Sub-issues should be small enough to ship in one PR
- If requirements are unclear, write the problem statement first — not the solution

## Related

- `spec-first` — spec-driven development before writing code
- `gh-fix-ci` — fix CI on existing PRs
- `strategy-expert` — broader roadmap and content planning
