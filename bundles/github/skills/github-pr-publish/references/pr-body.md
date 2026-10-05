# PR body

Detail for the step 5 template in `SKILL.md`. Skip preambles, keep prose brief,
and name things in the repo's domain language (`CONTEXT.md`, or `GLOSSARY.md`
when the repo uses it). The reviewer is a human with little time: every section
earns its place or goes.

## Summary: the smallest visual

After the one or two sentences, add the smallest view that makes the point
obvious. Pick one, occasionally two; never the whole menu. Put each visual next
to the sentence it supports and keep only the calls, files, props, states and
boundaries that bear on the change.

| The point is | Show |
|---|---|
| New or changed logic | pseudocode of the rule |
| Runtime control flow | a call tree |
| UI structure or state ownership | a component tree with the module boundaries that matter |
| Which file owns what, or a broad refactor | a shallow file tree with a one-phrase role per entry |
| Interaction between parts, or data flow | a mermaid sequence or flow diagram |
| What changed in a shape that already exists | the same tree or flow as a `diff` (`+` and `-` lines) |
| Most of the block is new, or ordering matters, or the reader needs a copyable target | the whole block |

A call-tree diff reads like this:

```diff
 importInvoices
   parseRows
+  dedupeByExternalId
   saveBatch
-  notifyAll
+  notifyOnce
```

## Evidence

Show the change working, as a before and after.

1. **Screenshots**, best tier, when the change is visual and the environment can
   render it.
2. **Execution output**: the exact test or command that failed before and passes
   now. Show the assertion in pseudocode when the test file is long.
3. **Checks**: the commands that ran, the host they ran on, and the result. Write
   `Not run` with the reason for anything skipped.

## Merge danger

- **Door.** A two-way door can be walked back by reverting the PR. A one-way door
  cannot: destructive migrations, deleted data, published packages, changed
  public contracts, rotated secrets. State which, and why.
- **Blast radius.** One word for the scope (`local`, `module`, `consumers`,
  `fleet`), then the concrete ramifications: layout shift, mobile
  responsiveness, breaking consumers, migration or deploy ordering, env vars to
  set before merge.

## Review guide

Only for a large diff. Two lists: mechanical or generated files the reviewer can
skim or skip, and the core files in the order that reads best. Add rollout
sequencing when order matters.

## Follow-ups

Real remaining work only, each with an owner or an issue link. Delete the section
when empty.

---

Adapted from `pr` in [mattpocock/skills](https://github.com/mattpocock/skills)
(MIT, commit `4588b32ecab9`), whose visual menu comes from the `show-me` skill by
Dex Horthy in [humanlayer/skills](https://github.com/humanlayer/skills) (MIT).
Rewritten here; not a sync target.
