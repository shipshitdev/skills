---
description: "Review working changes, a PR, every open PR, the last N commits, or a time window such as 7d."
argument-hint: "[PR#|prs|commits <N>|7d|retro [window]] [--deep|--structural|grok]"
disable-model-invocation: true
---

# Review - One Front Door for Every Code Review

Review whatever you point it at — your working changes, a single PR, every open
PR, the last N commits, or a time window — through the same review engine.

## Usage

```bash
/review                  # review uncommitted + current-branch changes vs trunk (default, quick)
/review <PR#>            # review one open PR by number
/review pr <PR#>         # explicit single-PR form
/review prs              # report-only review of every open PR — no pushes or merges
/review commits <N>      # review the last N commits (HEAD~N..HEAD)
/review <duration>       # review commits in a time window: 24h, 7d, 2w
/review retro [window]   # retrospective over merged history (default 14d): cross-commit
                         #   bugs/optimizations/refactors as a backlog, optionally filed as issues
/review --deep [target]  # full multi-dimension review (structural + security + devex) on any target
/review --structural [target]  # structural/maintainability lens only (the thermo-nuclear pass)
/review grok [target]    # second opinion: same target, reviewed by the Grok CLI instead
```

`/review help` prints this Usage block and stops without running anything.

`--deep` and `--structural` combine with review targets, e.g. `/review --deep
142`, `/review --deep prs`, or `/review --structural commits 5`. They are
mutually exclusive; `--deep` wins if both are given.

## Depth

- **Default (quick):** the `code-review` skill — correctness + security gate.
  Fast, high-conviction, the right call for most reviews.
- **`--deep`:** the `full-code-review` skill — three parallel lenses
  (structural, security, devex/flags), adversarial verification, strongest-tier
  synthesis. Use for high-risk changes or production-readiness passes.
- **`--structural`:** the `structural-review` skill alone — the
  structural/maintainability "thermo-nuclear" lens (file size, abstraction,
  layering, design purity, directness-vs-magic), without the security/devex fan-out.

## External Engine

`/review grok [target]` routes the same resolved diff through the
`grok-review` skill: one headless Grok CLI invocation on the CLI's own default
model and effort (no model/effort flags are ever passed), followed by
in-session verification of every returned finding before anything is reported.
Combines with any target except `retro`; mutually exclusive with `--deep` and
`--structural`. Report-only like every other mode.

## Retro

`/review retro [window]` is not a merge gate — it mines a window of **already-merged**
history for what per-PR review structurally cannot see: the same helper copy-pasted
across separate commits, an optimization compounding over many changes, a bug fix
whose root cause recurs in siblings it never touched. It runs `full-code-review` with
the commit log attached (adding its cross-commit lens) and returns a **prioritized
backlog** — bugs / optimizations / refactors, ranked by (impact × recurrence) ÷ effort
— not an approve/block verdict. Windows: `7d`, `14d` (default), `30d`, or `since <ref>`.
On request it files the backlog as GitHub issues (confirmation-gated).

## Workflow

Use the `review-dispatch` skill. It resolves the target, gathers the diff(s)
with read-only `git`/`gh`, routes to the chosen depth, and renders the verdict.

1. **Parse the argument** into a target mode (none / PR# / `pr <n>` / `prs` /
   `commits <n>` / duration), a depth flag (`--deep`, `--structural`, or
   default quick), and an optional `grok` engine token.
2. **Detect the trunk** — resolve the default branch and verify it exists before
   diffing; stop and ask for a base if it can't be resolved.
3. **Resolve the target to diffs** — branch vs trunk, `gh pr diff`, a commit
   range, or a `git log --since` window.
4. **Route by depth** — apply `code-review` (quick), `full-code-review` (deep),
   or `structural-review` (structural) to each resolved diff — or hand the
   diff to `grok-review` when the `grok` engine is selected.
5. **Render** — a single verdict for one target, or a summary table (one verdict
   line per PR) for `prs`, with a `/review <PR#>` drill-down hint.

## Gates

- Every review target, including `prs`, is read-only. It never edits files,
  pushes, reruns CI, or merges.
- The one write path is `retro` filing its backlog as GitHub issues, and only after
  explicit confirmation — never automatically.
- `prs` defaults to quick depth — `--deep prs` fans out a full orchestrated
  review per PR and is token-heavy; the dispatcher warns before running it on
  more than a few PRs.

## Related

- `/merge review` runs the same per-PR review sweep before landing PRs into the
  trunk — `/review prs` is the standalone, report-only version.
- `/merge force` is the only non-serial queue-drain command. `force` means queue
  progress; it never means force-push, admin merge, or bypassing checks and
  branch protection.
