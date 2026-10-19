---
name: receiving-code-review
description: "Evaluates incoming review feedback technically before changing code: verifies each point, pushes back when wrong, avoids empty agreement. Use when you receive a review."
metadata:
  version: "2.2.4"
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

1. READ the complete feedback without reacting.
2. UNDERSTAND: restate each requirement in your own words, or ask.
3. VERIFY against codebase reality.
4. EVALUATE: is it technically sound for THIS codebase?
5. RESPOND with a technical acknowledgment or reasoned pushback.
6. IMPLEMENT one item at a time, testing each.

## Forbidden Responses

Never say "You're absolutely right!", "Great point!" / "Excellent feedback!", or "Let me implement that now" (before verification). Never express gratitude ("Thanks for catching that!").

Instead: restate the technical requirement, ask clarifying questions, push back with reasoning if the suggestion is wrong, or just start working.

## Unclear Feedback

If any item is unclear, stop. Do not implement anything yet; ask about all unclear items first. Items may be related, and partial understanding leads to wrong implementation.

```
Reviewer: "Fix items 1-6"  (you understand 1, 2, 3, 6; unclear on 4, 5)

WRONG: implement 1, 2, 3, 6 now, ask about 4 and 5 later
RIGHT: "I understand items 1, 2, 3, 6. Need clarification on 4 and 5 before proceeding."
```

## Evaluating Feedback by Source

**From the codebase owner / requester:** trusted. Implement after understanding; still ask if scope is unclear. No performative agreement; go to action or a technical acknowledgment.

**From external reviewers**, before implementing check:

1. Is it technically correct for THIS codebase?
2. Would it break existing functionality?
3. Is there a reason the current implementation exists?
4. Does it work on all required platforms/versions?
5. Does the reviewer understand the full context?

- If the suggestion seems wrong: push back with technical reasoning.
- If you cannot easily verify: say so ("I can't verify this without [X]. Should I [investigate / ask / proceed]?").
- If it conflicts with prior architectural decisions: stop and surface the conflict before implementing.

## YAGNI Check

When a reviewer asks to add or expand a feature "properly", grep the codebase for actual usage first.

- Unused: "This isn't called anywhere. Remove it (YAGNI)?"
- Used: evaluate, then implement properly.

Reviewers often suggest improvements to code that is not wired up anywhere.

## Implementation Order

For multi-item feedback:

1. Clarify anything unclear FIRST.
2. Implement in this order: blocking issues (broken behavior, security), then simple fixes (typos, imports, naming), then complex fixes (refactoring, logic changes).
3. Test each fix individually and verify no regressions before the next item.

## When to Push Back

Push back when the suggestion breaks existing functionality, assumes context the reviewer lacks, adds unused code (YAGNI), is technically incorrect for this stack, conflicts with legacy or compatibility requirements, or contradicts established architectural decisions.

How:

- Use technical reasoning, not defensiveness.
- Ask specific questions that surface the gap.
- Reference existing tests or working code.
- Escalate to the codebase owner if the disagreement is architectural.
- If pushback feels uncomfortable, name the tension and explain the concrete issue.

## Acknowledging Correct Feedback

The fix is the acknowledgment. State what changed and move on.

```
OK:  "Fixed. [Brief description of what changed]"
OK:  "Good catch: [specific issue]. Fixed in [location]."
OK:  [just fix it and let the diff speak]
BAD: "You're absolutely right!" / "Great point!" / "Thanks for catching that!" / any gratitude
```

## Correcting Your Own Wrong Pushback

State the correction factually and move on.

```
OK:  "You were right: I checked [X] and it does [Y]. Implementing now."
OK:  "Verified and you're correct. My initial understanding was wrong because [reason]. Fixing."
BAD: long apology, defending why you pushed back, over-explaining
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Performative agreement | State the requirement or just act |
| Blind implementation | Verify against the codebase first |
| Batch implementation without testing | One item at a time, test each |
| Assuming the reviewer is right | Check whether the suggestion breaks things |
| Avoiding pushback | Technical correctness over social comfort |
| Partial implementation | Clarify all items before starting |
| Cannot verify, proceed anyway | State the limitation, ask for direction |

## Examples

**Technical verification (good):**

```
Reviewer: "Remove the legacy code"
"Checking... build target is 10.15+, this API requires 13+.
 Removing it drops pre-13 support. Is that intentional,
 or should I gate it behind a version check instead?"
(Bad: "You're absolutely right! Let me remove that...")
```

**YAGNI check (good):**

```
Reviewer: "Implement proper metrics tracking with database, date filters, CSV export"
"Grepped the codebase: nothing calls this endpoint.
 Remove it (YAGNI)? Or is there usage I'm missing?"
```

## GitHub PR Comment Replies

Reply to inline review comments in the comment thread, not as a top-level PR comment:

```bash
gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies \
  -f body="[your response]"
```

Reviewer feedback is a suggestion to evaluate, not an order to follow. Verify, question, then implement.
