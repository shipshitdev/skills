# DB Load Test

Builds a load-testing suite for the database schema, finds which real queries
fail at scale, fixes them, and proves the fix with statistics and a chart.

## Authorized Scope

Follow `protocol.md`, especially the database safety rules. Everything runs on a
throwaway local database. Loading this playbook grants no new authority.

## Contract

Inputs:

- Optional scope (tables, modules, queries)
- Optional latency budget per query (default: p95 at or below 100 ms for
  interactive queries; say what you used)

Outputs:

- A committed, re-runnable suite
- Per query and scale tier: latency samples, rows, plan, failures
- Before/after HTML chart and table from `compare.py`

Creates/Modifies:

- Suite under the repository's conventional test or tooling directory
- Additive migrations (indexes) and query changes on `perf/dbload`
- Never generated data, dumps, or result files in git

External Side Effects:

- Starts and drops a local throwaway database
- Push and PR

Confirmation Required:

- Before pointing the suite at anything but a local or ephemeral database
- Before any migration beyond additive indexes
- Applying migrations anywhere shared or production: never performed here

Delegates To:

- `/git pr` playbook when installed

## Detect

Find the schema source (ORM schema, migration files, SQL dumps), engine and
version, ORM or query builder, how connections are made, and how tests create
databases. Pick the throwaway mechanism the project already uses (container,
local server, in-memory engine if it matches production semantics). A schemaless
or non-relational store changes the plan: scale by key and partition shape, and
say which parts do not apply. No database at all: stop.

## Safety gate

Before the first statement, assert the target host is local or ephemeral and the
database name carries a run marker the suite generated (for example
`perf_<random>`). Refuse otherwise. Do not read the environment's database URL
without this check. Drop the database on exit, including on failure.

## Extract the real queries

Run the application's own query paths, not hand-written lookalikes. Capture the
SQL actually issued through the ORM's query log or the database's statement
logging on the throwaway database, while running the existing tests or the
routes and jobs. Keep parameters shaped like real ones. List queries by code
location and frequency. Include writes that hit hot tables.

## Seed

Deterministic seed, bulk loading, same indexes and constraints as migrations.

- Define 1x as a small realistic tenant or dataset. Scale to 10x, 100x, and
  1000x by multiplying the root entities and applying each relationship's
  fan-out ratio from the schema (one-to-many counts, join table sizes).
- Skew like real data: a few huge tenants and a long tail, nullable ratios,
  text and jsonb size distributions, dates spread over time.
- Load in batches with the fastest bulk path the engine offers, then refresh
  planner statistics (for example `ANALYZE`) so plans match steady state.
- If 1000x does not fit local resources, state the largest tier that ran. Do not
  extrapolate silently.

## Run

For each query and tier: warm up, then take at least 30 samples, separating cold
from warm cache runs. Record latency, rows returned, errors and timeouts, and the
plan with actual timings and buffer or I/O counts (for example Postgres
`EXPLAIN (ANALYZE, BUFFERS)`, SQLite `EXPLAIN QUERY PLAN`). Flag as failing: over
the budget, timed out, errored, or growing worse than linearly across tiers
(fit the slope of log latency against log scale; above about 1 is superlinear).
Flag sequential scans on large tables, sorts spilling to disk, and nested loops
over large sets.

## Fix

Behavior-preserving only: add missing or composite indexes, replace offset
pagination with keyset where the contract allows, collapse N+1 into a join or
batch, narrow selected columns, remove redundant sorts. Index migrations are
additive; recommend non-blocking creation where the engine supports it. Anything
that changes results or the schema shape is reported, not done.

## Measure after

Re-run the identical suite on identical seeded data. Prefer a harness that holds
the before and after query variants side by side and alternates them in blocks.
Pass all samples to `compare.py` with `--out`. The report charts every
query-by-tier cell with confidence intervals and Holm-adjusted p-values. Attach
the HTML to the PR; do not commit it.

## PR

Follow `protocol.md`. Include the suite's run instructions, the tier table with
failures before and after, the chart, and the fixes. Put any migration under
**Approvals needed**.
