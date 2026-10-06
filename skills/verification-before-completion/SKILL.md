---
name: verification-before-completion
description: Blocks done, fixed or passing claims until the verification command has run fresh and its full output was read. Use before claiming completion, committing, pushing or opening a PR.
metadata:
  version: "2.2.2"
  source: https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md
  upstream_repo: obra/superpowers
  upstream_ref: main
  upstream_commit: 8ca22dba9a94f28898bbce59f2537ff4d87c747d
  last_synced: "2026-10-06"
  license: MIT
  tags: "verification, completion, evidence, quality-gate, testing, ci-cd"
when_to_use: "tests passing, build succeeds, linter clean"
---
# Verification Before Completion

Claiming work is complete without verification is dishonesty, not efficiency.

**Core principle: evidence before claims, always.**

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If the verification command has not been run in the current action, no completion claim may be made.

## The Gate Function

Before claiming any status or expressing satisfaction:

1. **IDENTIFY** — What command proves this claim?
2. **RUN** — Execute the full command fresh and completely.
3. **READ** — Consume the full output; check exit code; count failures.
4. **VERIFY** — Does the output confirm the claim?
   - If NO: state the actual status with evidence.
   - If YES: state the claim WITH the evidence.
5. **ONLY THEN** — Make the claim.

Skipping any step = lying, not verifying.

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Reproduce original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Subagent completed | VCS diff shows actual changes | Subagent reports "success" |
| Requirements met | Line-by-line checklist verified | Tests passing |

## Red Flags — STOP

Stop before proceeding if any of these are true:

- Using "should", "probably", "seems to", "looks like"
- Expressing satisfaction before running verification ("Great!", "Perfect!", "Done!")
- About to commit, push, or open a PR without fresh verification
- Trusting a subagent's self-reported success
- Relying on a partial or scoped verification pass
- Thinking "just this once"
- Fatigued and wanting the task to be over
- Any wording implying success without having run the verification command

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | Run the verification |
| "I'm confident" | Confidence is not evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter is not the compiler |
| "Subagent said success" | Verify independently |
| "Partial check is enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |

## Key Patterns

**Tests:**

```
CORRECT:   [Run test command] → see "34/34 pass" → state "All tests pass"
INCORRECT: "Should pass now" / "Looks correct"
```

**Regression tests (red-green-refactor):**

```
CORRECT:   Write test → Run (must PASS) → Revert fix → Run (must FAIL) → Restore fix → Run (must PASS)
INCORRECT: "I've written a regression test" without running the red-green cycle
```

**Build:**

```
CORRECT:   [Run build command] → see exit 0 → state "Build passes"
INCORRECT: "Linter passed" (linter does not check compilation)
```

**Requirements checklist:**

```
CORRECT:   Re-read the original requirements → create a line-by-line checklist → verify each item → report gaps or completion
INCORRECT: "Tests pass, phase complete"
```

**Subagent delegation:**

```
CORRECT:   Subagent reports success → inspect VCS diff → run verification → report actual state
INCORRECT: Trust the subagent's self-report and propagate it as fact
```

## When to Apply

Apply **always** before:

- Any variation of success, completion, or done claims
- Any expression of satisfaction with work state
- Any positive statement about correctness
- Committing, opening a PR, or marking a task complete
- Moving on to the next task
- Reporting subagent results to the user

The rule applies to exact phrases, paraphrases, synonyms, and any implication of success — not just the literal word "done."

## The Bottom Line

Run the command. Read the output. Then make the claim.

No shortcuts. No exceptions.
