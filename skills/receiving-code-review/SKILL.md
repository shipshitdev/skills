---
name: receiving-code-review
description: "Evaluates incoming review feedback technically before changing code: verifies each point, pushes back when wrong, avoids empty agreement. Use when you receive a review."
metadata:
  version: "2.2.5"
  source: https://github.com/obra/superpowers/blob/main/skills/receiving-code-review/SKILL.md
  upstream_repo: obra/superpowers
  upstream_ref: main
  upstream_commit: 8ca22dba9a94f28898bbce59f2537ff4d87c747d
  last_synced: "2026-10-06"
  license: MIT
  tags: "code-review, feedback, review-response, pushback, verification"
allowed-tools: Bash(git *) Bash(gh *)
when_to_use: "got a review, respond to reviewer, push back, is this feedback right"
---
# Receiving Code Review

## Core Principle

Code review requires technical evaluation, not emotional performance.

**Verify before implementing. Ask before assuming. Technical correctness over social comfort.**

## Contract

Inputs:

- Incoming review feedback (PR comments, verbal review notes) and the codebase
  the feedback refers to.

Outputs:

- A per-point technical acknowledgment or reasoned pushback, plus an action
  plan for the changes that survive evaluation.

Creates/Modifies:

- None directly. This skill produces responses; code edits happen through other
  skills.

External Side Effects:

- Read-only `git` / `gh` invocations to verify claims against the codebase.

Confirmation Required:

- None. All output is advisory.

Delegates To:

- `pr-comments` (`address` mode) for posting the responses back to a PR.
- `code-review` for a fresh review pass once changes land.

## Response Pattern

```
WHEN receiving code review feedback:

1. READ: Complete feedback without reacting
2. UNDERSTAND: Restate the requirement in your own words (or ask)
3. VERIFY: Check against codebase reality
4. EVALUATE: Is this technically sound for THIS codebase?
5. RESPOND: Technical acknowledgment or reasoned pushback
6. IMPLEMENT: One item at a time, test each
```

## Forbidden Responses

**NEVER say:**

- "You're absolutely right!"
- "Great point!" / "Excellent feedback!"
- "Let me implement that now" (before verification)
- Any expression of gratitude ("Thanks for catching that!", "Thanks for [anything]")

**INSTEAD:**

- Restate the technical requirement
- Ask clarifying questions
- Push back with technical reasoning if the suggestion is wrong
- Just start working — actions speak louder than words

## Handling Unclear Feedback

```
IF any item is unclear:
  STOP — do not implement anything yet
  ASK for clarification on all unclear items before proceeding

WHY: Items may be related. Partial understanding leads to wrong implementation.
```

**Example:**

```
Reviewer: "Fix items 1-6"
You understand 1, 2, 3, 6. Unclear on 4, 5.

❌ WRONG: Implement 1, 2, 3, 6 now — ask about 4, 5 later
✅ RIGHT: "I understand items 1, 2, 3, 6. Need clarification on 4 and 5 before proceeding."
```

## Evaluating Feedback by Source

### From the codebase owner / requester

- **Trusted** — implement after understanding
- Still ask if scope is unclear
- No performative agreement
- Skip to action or technical acknowledgment

### From external reviewers

```
BEFORE implementing:
  1. Check: Is this technically correct for THIS codebase?
  2. Check: Would this break existing functionality?
  3. Check: Is there a reason the current implementation exists?
  4. Check: Does this work on all required platforms/versions?
  5. Check: Does the reviewer understand the full context?

IF the suggestion seems wrong:
  Push back with technical reasoning

IF you cannot easily verify:
  Say so: "I can't verify this without [X]. Should I [investigate / ask / proceed]?"

IF the suggestion conflicts with prior architectural decisions:
  Stop and surface the conflict before implementing
```

## YAGNI Check for "Implement Properly" Suggestions

```
IF a reviewer suggests adding or expanding a feature "properly":
  grep the codebase for actual usage

  IF unused: "This isn't called anywhere. Remove it (YAGNI)?"
  IF used: Then evaluate and implement properly
```

Reviewers often suggest improvements to code that isn't wired up anywhere. Verify usage before expanding scope.

## Implementation Order

```
FOR multi-item feedback:
  1. Clarify anything unclear FIRST
  2. Then implement in this order:
     - Blocking issues (broken behaviour, security)
     - Simple fixes (typos, imports, naming)
     - Complex fixes (refactoring, logic changes)
  3. Test each fix individually
  4. Verify no regressions before moving to the next item
```

## When to Push Back

Push back when the suggestion:

- Breaks existing functionality
- Assumes context the reviewer doesn't have
- Violates YAGNI (adds unused code)
- Is technically incorrect for this stack
- Conflicts with legacy or compatibility requirements
- Contradicts established architectural decisions

**How to push back:**

- Use technical reasoning, not defensiveness
- Ask specific questions that surface the gap
- Reference existing tests or working code
- Escalate to the codebase owner if the disagreement is architectural
- If pushback feels uncomfortable, name the tension and explain the concrete issue

## Acknowledging Correct Feedback

When feedback IS correct:

```
✅ "Fixed. [Brief description of what changed]"
✅ "Good catch — [specific issue]. Fixed in [location]."
✅ [Just fix it and let the diff speak]

❌ "You're absolutely right!"
❌ "Great point!"
❌ "Thanks for catching that!"
❌ Any gratitude expression
```

The fix is the acknowledgment. State what changed and move on.

## Gracefully Correcting Your Own Pushback

If you pushed back and were wrong:

```
✅ "You were right — I checked [X] and it does [Y]. Implementing now."
✅ "Verified this and you're correct. My initial understanding was wrong because [reason]. Fixing."

❌ Long apology
❌ Defending why you pushed back
❌ Over-explaining
```

State the correction factually and move on.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Performative agreement | State the requirement or just act |
| Blind implementation | Verify against the codebase first |
| Implementing in batch without testing | One item at a time, test each |
| Assuming the reviewer is right | Check whether the suggestion breaks things |
| Avoiding pushback | Technical correctness over social comfort |
| Partial implementation | Clarify all items before starting |
| Cannot verify — proceed anyway | State the limitation, ask for direction |

## Real Examples

**Performative agreement (bad):**

```
Reviewer: "Remove the legacy code"
❌ "You're absolutely right! Let me remove that..."
```

**Technical verification (good):**

```
Reviewer: "Remove the legacy code"
✅ "Checking... build target is 10.15+, this API requires 13+.
   Removing it drops pre-13 support. Is that intentional,
   or should I gate it behind a version check instead?"
```

**YAGNI check (good):**

```
Reviewer: "Implement proper metrics tracking with database, date filters, CSV export"
✅ "Grepped the codebase — nothing calls this endpoint.
   Remove it (YAGNI)? Or is there usage I'm missing?"
```

**Unclear item (good):**

```
Reviewer: "Fix items 1-6"
You understand 1, 2, 3, 6. Unclear on 4, 5.
✅ "Understand 1, 2, 3, 6. Need clarification on 4 and 5 before implementing."
```

## GitHub PR Comment Replies

When responding to inline review comments on GitHub, reply in the comment thread — not as a top-level PR comment:

```bash
gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies \
  -f body="[your response]"
```

Reviewer feedback = suggestions to evaluate, not orders to follow. Verify. Question. Then implement. No performative agreement. Technical rigor always.
