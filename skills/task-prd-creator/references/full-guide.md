# Task & PRD Creator — Full Guide

## Workflow detection

| Situation | Output |
|-----------|--------|
| `gh auth status` OK + git remote is GitHub | GitHub issue (default) |
| `.agents/TASKS/` exists | Local file (default) |
| Both available | Ask user which, or both |
| Neither | Create local files, suggest `gh auth login` |

---

## PRD structure

Every PRD — whether GitHub issue body or local file — uses this structure.
Skip sections that don't apply. Never leave placeholder text in.

```markdown
## Problem

[What breaks, what's missing, why this matters. 2-4 sentences max.]

## Goal

[One sentence. Measurable. "Users can X without Y friction."]

## Scope

**In:**
- [specific thing 1]
- [specific thing 2]

**Out:**
- [explicitly excluded thing — prevents scope creep]

## Acceptance criteria

- [ ] [Specific, testable condition — can a human verify this?]
- [ ] [Another condition]
- [ ] [Edge case handled]

## Technical notes

**Approach:** [Pattern to follow, key architectural decision]
**Risks:** [What could go wrong, unknowns]
**Dependencies:** [Other issues, external services, env vars needed]
**Files likely affected:** [rough list if known]

## Links

- Parent issue: #N (if sub-issue)
- Related: #N, #N
- Design: [Figma/Linear link if any]
```

---

## Issue types and titles

Format: `[type]: [clear imperative title]`

| Type | When to use | Example |
|------|-------------|---------|
| `feat` | New capability | `feat: add CSV export to reports` |
| `fix` | Bug, broken behavior | `fix: auth token not refreshing on 401` |
| `chore` | Infra, deps, config | `chore: upgrade NestJS to v11` |
| `refactor` | Same behavior, different code | `refactor: extract payment service` |
| `perf` | Performance improvement | `perf: lazy load dashboard charts` |
| `docs` | Documentation | `docs: add API authentication guide` |

---

## GitHub issue creation

### Standard issue

```bash
gh issue create \
  --title "feat: add CSV export to reports" \
  --body "$(cat <<'BODY'
## Problem
Users need to export report data for external analysis. Currently only PDF is supported, which isn't usable in spreadsheets.

## Goal
Users can download any report as CSV in one click.

## Scope
**In:**
- CSV export button on report detail page
- All visible columns included
- Filename: `report-[id]-[date].csv`

**Out:**
- Scheduled/automated exports
- Custom column selection

## Acceptance criteria
- [ ] Export button visible on report detail page
- [ ] Downloaded file is valid CSV with headers
- [ ] Large reports (10k+ rows) don't timeout
- [ ] Empty reports download as headers-only CSV

## Technical notes
**Approach:** Stream response, don't buffer full dataset in memory
**Dependencies:** None
BODY
)" \
  --label "feature" \
  --assignee "@me"
```

### Sub-issue (part of epic)

```bash
# 1. Create the sub-issue
CHILD_ID=$(gh issue create \
  --title "feat: CSV export — streaming backend endpoint" \
  --body "..." \
  --json number --jq '.number')

# 2. Link it to parent epic #42
gh api repos/{owner}/{repo}/issues/42/sub_issues \
  --method POST \
  -f sub_issue_id=$CHILD_ID
```

Get `{owner}/{repo}` from:

```bash
gh repo view --json nameWithOwner --jq '.nameWithOwner'
```

### Update existing issue

```bash
# Add comment with update
gh issue comment 42 --body "Scope change: removing X, adding Y. See updated description."

# Edit body
gh issue edit 42 --body "$(cat updated-prd.md)"

# Close with reason
gh issue close 42 --comment "Shipped in #87"
```

---

## Local file format (optional)

Use when: no GitHub access, or user explicitly wants local tracking.

**Task file:** `.agents/TASKS/[kebab-name].md`

```markdown
## Task: [Feature Name]

**ID:** kebab-name
**Type:** Feature | Bug | Enhancement | Refactor | Chore
**Status:** Backlog | In Progress | Testing | Done
**Priority:** Critical | High | Medium | Low
**Created:** YYYY-MM-DD
**Updated:** YYYY-MM-DD
**GitHub:** #N (link if issue exists)
**PRD:** [full-prd.md](../PRDS/kebab-name.md)
```

**PRD file:** `.agents/PRDS/[kebab-name].md`

Use the PRD structure from above. Add `# [Feature Name]` as h1.

**File naming rules:**

- kebab-case only: `video-generation-with-captions.md`
- Full words, no abbreviations: not `vid-gen.md`
- No dates in filename (use metadata)

---

## Sub-issue sizing rules

A sub-issue should:

- Ship in one PR
- Be completable in 1 session (not 5 hours of work)
- Have its own acceptance criteria, independent of siblings
- NOT depend on an unmerged sibling

If you're writing a sub-issue that says "do X after Y is merged" — that's a dependency, list it. Don't assume order.

---

## When to push back on requirements

Stop and flag to user if:

- Acceptance criteria can't be tested (too vague)
- Scope includes 3+ unrelated things (split the issue)
- "Out of scope" section is empty on anything >medium complexity
- Breaking change with no migration path defined
- Security-sensitive and no threat model mentioned

---

## Quick reference

| Action | Command |
|--------|---------|
| List open issues | `gh issue list` |
| Search issues | `gh issue list --search "keyword"` |
| View issue | `gh issue view 42` |
| Create branch from issue | `gh issue develop 42` |
| Link sub-issue | `gh api repos/OWNER/REPO/issues/PARENT/sub_issues --method POST -f sub_issue_id=CHILD` |
| Close issue | `gh issue close 42 --comment "reason"` |
