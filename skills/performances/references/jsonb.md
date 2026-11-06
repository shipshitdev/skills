# JSONB Columns

Finds hot-path reads of a single key from a large jsonb column and promotes that
key to a real column, with a migration and backfill that a human approves before
production.

## Authorized Scope

Follow the shared protocol, especially the database safety rules. This playbook writes
migration and backfill code; it never runs them anywhere but a throwaway local
database. Loading it grants no new authority.

## Contract

Inputs:

- Optional scope (tables, columns)
- Optionally sanitized size statistics the user supplies

Outputs:

- Ranked list of candidate keys with evidence
- Migration, backfill, dual-write change, read switch, and tests
- Approval section for the production plan

Creates/Modifies:

- Migration files, a resumable backfill script, application code on `perf/jsonb`

External Side Effects:

- Push and PR. No database outside a throwaway local one.

Confirmation Required:

- Before any production or shared-environment migration or backfill. Human
  approval is required, and this playbook only prepares the plan.
- Before querying any database other than a throwaway local one

Delegates To:

- `/performances dbload` harness for seeded data when present, and for timing the backfill
- `/git pr` playbook when installed

## Detect

Engine and ORM. Postgres `jsonb`, MySQL `JSON`, SQLite JSON text. Find every
json or jsonb column in the schema. Document stores and databases without a
JSON column type do not apply: say so and stop.

## Find

1. List json columns and their size. Do not query production. Ask for sanitized
   statistics (average, p95, and max stored size per column, for example from
   `pg_column_size`) or measure on seeded data.
2. Scan code for hot-path single-key reads: path operators (`col->>'key'`,
   `#>>`), ORM JSON path filters, selects of the whole column to read one key in
   application code, and filters, sorts, or joins on a key.
3. Rank by frequency times column size, and confirm with observed size, plan, or
   I/O evidence before ranking. How a large value is stored and read is
   engine-specific (for example Postgres stores it out of line and decompresses
   the whole value on each read, and updates rewrite it; check the detected
   engine's behavior instead of assuming it).

## Decide per key

Promote when the key is scalar, present in most rows, of stable type, and read,
filtered, sorted, or joined on a hot path. Prefer an expression index or a
generated column when the need is only filtering and no application change is
wanted; say why one fits better. Leave sparse, user-defined, rarely read, or
deeply nested keys alone. Where the jsonb can simply go away, say so, since
large jsonb is avoided wherever possible.

Check the key's types first (for example `jsonb_typeof` distribution) and decide
explicitly what missing, null, and mistyped values become. Keep the difference
between missing and null if callers observe it.

## Migration plan (expand and contract)

1. Add the nullable column with no default (no table rewrite).
2. Dual-write: every writer sets both (ORM paths, raw SQL, scripts, triggers,
   other services in the repo). Also list writers outside the repository that
   touch the table (other services, jobs, manual scripts). Do not switch reads
   until each external writer can dual-write, or the inventory records that
   none exist.
3. Backfill in keyset batches: small transactions, throttled, idempotent,
   resumable, with progress logging. No long locks. Build indexes concurrently
   where the engine supports it, outside a transaction.
4. Verify: a query counting rows where the caller-visible state differs is zero,
   comparing key presence, JSON type, and normalized value, so a missing key never
   equals JSON null. Then add constraints in a non-blocking order (for example a check
   constraint added unvalidated, then validated).
5. Switch reads to the column behind the project's flag mechanism if it has one.
6. Stop writing the key into the jsonb and remove it in a later PR, not this one.

Every step is reversible except step 6. The PR includes the rollback for each.

## Measure

On seeded data at the `dbload` tiers: hot-query latency, buffers read, and bytes
per row before and after; write cost; backfill duration at the largest tier to
estimate production time and lock behavior. Use at least 20 samples and
`compare.py`.

## Tests

Characterization tests for each read path, a dual-write test, a backfill test
(idempotent, resumable, handles missing and mistyped values), and a rollback test
on the throwaway database.

## PR

Put an **Approvals needed** section first: the exact
production steps in order, estimated duration and lock impact from the measured
data, monitoring to watch, and rollback. State plainly that nothing was applied
outside a throwaway database.
