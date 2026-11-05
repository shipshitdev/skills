# All

Runs the eight performance actions in order as separate workstreams, each with
its own branch and PR.

## Authorized Scope

Running `all` is the user's request for all eight actions
and nothing more. Each action keeps its own confirmation gates.

## Contract

Inputs:

- Optional scope applied to every action

Outputs:

- One stack profile shared by all actions
- A summary table of the eight workstreams

Creates/Modifies:

- One branch and PR per action that changes code, via each action's playbook

External Side Effects:

- Up to eight pushes and PRs

Confirmation Required:

- Once, before starting: show the stack profile and the plan below and wait for a go-ahead
- Each action's own gates still apply (new vendor, production migration)

Delegates To:

- The eight action playbooks, which the router loads for `all`; follow each one
  for its workstream.

## Order

1. `parallel`
2. `dbload`
3. `otel`
4. `logging`
5. `select`
6. `url`
7. `regex`
8. `jsonb`

## Procedure

1. Detect the stack once, using the shared protocol. For each action, mark it
   applicable, partly applicable, or not applicable, with the reason. Show this
   plan and wait for the user's go-ahead.
2. Run the actions in order, each as a separate workstream:
   - Its own branch `perf/<action>` and worktree off freshly fetched
     the default remote's default branch. Never stack one action's branch on another's.
   - Its own baseline, fix, and after measurement. Never share before/after
     numbers between actions.
   - Its own PR, opened by its playbook.
3. Where the harness supports parallel sessions, workstreams may run at the same
   time in separate worktrees. Otherwise run them one after the other. Never run
   two in the same checkout.
4. Dependencies are soft. `logging` uses the active trace span's ids when
   `otel` has merged or is present, and generates compatible ids otherwise.
   `select` and `jsonb` use the `dbload` harness only if it is already on the
   default branch when their branch is cut; otherwise each builds its own minimal
   seed. Never wait on, copy from, or stack on another workstream's branch, and
   state which seed was used.
5. A workstream with nothing to change, nothing applicable, or a blocker is
   reported, not forced. Continue to the next one.
6. If two PRs touch the same files, say so and recommend a merge order. Do not
   resolve it by combining PRs.

## Final report

A table, then the approvals the user owes:

| Action | Status | PR | Headline before/after | Needs |
|---|---|---|---|---|

Status is one of: PR opened, nothing found, not applicable, blocked. Close with
the merge order and every pending approval (new vendor, production migration).
