# Correct procedure

Use this when the user keeps correcting agents for the same mistakes, or when a captured rule repeats one that already exists. Change the repo so the next agent cannot make the mistake. Recording the rule is the last resort, not the first.

Assume every contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Design the repo so a change that looks right from one file is right for the whole repo.

## Authorized scope

Finding mistake classes is read-only. Fixing them edits the repository the user named. Land each fix through the user's normal commit and review flow. Ask before changing shared CI, lint configuration, or rules other teams depend on.

## Find the mistake classes

Read recent commits, reverts, review comments, agent instruction files, and comments that explain workarounds. Group the mistakes into classes. A class counts once it has happened twice.

## Fix each class at the highest level that works

1. **Eliminate it with architecture.** Give each piece of state one owner and each task one supported way. Hide internals so the wrong import fails. Replace hand-synced lists with one source of truth. Delete old ways and dead code an agent would copy.
2. **Enforce it with types so the bad state cannot be written.** If bad code still compiles, add a lint or CI check whose error names the file, type, or function to use instead. If the pattern is already common, fail only when a change adds more.
3. **Test the behavior.** Fix or delete any test that would still pass if every function it calls returned nothing.
4. **Write docs or agent rules last, only for judgment calls.** Nothing fails when an agent skips them.

## Fix and prove

Fix the most frequent classes now, one commit each. Prove each new check fails on a real past mistake. Run the same command locally and in CI. Exceptions go on the offending line with a reason, an expiry date, and a human's approval.

## Keep the rule table

Keep a table in the agent instruction file that pairs each rule with what enforces it. When the user corrects you, fix the mistake and add the rule. If the rule was already there and nothing enforces it, that is a repeat, so fix it at the highest level in the same change. Drop a rule once its mistake can no longer happen.

## Report

Each class with its evidence, the level you picked, and why a higher level did not work.
