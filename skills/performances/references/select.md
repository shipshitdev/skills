# Select Fields

Finds every place a whole row is loaded from the database only to read a few
fields, and selects only what is needed.

## Authorized Scope

Follow `protocol.md`. Loading this playbook grants no new authority.

## Contract

Inputs:

- Optional scope (modules, tables)

Outputs:

- Ranked list of narrowed queries with bytes and latency evidence
- List of whole-row loads kept, with the reason

Creates/Modifies:

- Query code, shared select definitions, and tests on `perf/select`

External Side Effects:

- Push and PR

Confirmation Required:

- None beyond `protocol.md`

Delegates To:

- `/performances dbload` harness for seeded measurement when present
- `/git pr` playbook when installed

## Detect

ORM and query style decide the idiom. Examples: Prisma `select` or `omit`,
Drizzle `select({ ... })`, TypeORM `select` or `QueryBuilder.select`, Sequelize
`attributes`, Mongoose `select` and `lean`, SQLAlchemy `load_only` and `defer`,
Django `only`, `values`, and `values_list`, ActiveRecord `select` and `pluck`,
Ecto `select`, GORM `Select`, Hibernate projections, and raw `SELECT *`. Also
nested loads (`include`, `joinedload`, `prefetch`) that pull whole related rows.

## Find

Scan every read query in the scope. For each whole-row load, follow the result
through the code and list the fields actually used. Count a field as used when
it is read, spread, serialized, logged, cached, passed to a function that reads
it, or needed by a hook, getter, or computed property.

Rank by row width times rows times call frequency. Large text, jsonb, bytea,
and array columns dominate. Rows loaded for existence checks, counts, ids, or
display of one or two fields are the usual wins.

## Keep the whole row when

- The whole row is returned or serialized on purpose
- The result is passed to code that reads fields dynamically or too widely to enumerate
- An entity is loaded to be saved or updated through the ORM, where a partial
  entity can write wrong values
- Virtual or computed fields, hooks, or authorization checks read other columns
- Selecting would make the type unsound for later callers and the gain is small

When unsure, keep it and list it.

## Fix

Select exactly the needed fields. Define the selection once and derive the
result type from it (a shared select constant with `satisfies`, a view type, or
the ORM's projection types) so a missing field is a compile or test error, not a
runtime `undefined`. Narrow nested loads too. Do not change returned shapes
seen by callers.

## Measure

Per query, on seeded data (reuse the `dbload` harness when present): bytes
transferred, rows, and latency over at least 20 samples, plus the plan. Note when
a narrowed select enables an index-only or covering scan. Use `compare.py`.
Profile first: skip queries whose payload is tiny and rare.

## Tests

Before: characterization tests that fail if a consumer loses a field it reads.
Type checks count where the language has them; say so.

## PR

Follow `protocol.md`. Table of queries with columns before and after, bytes, and
latency; list of kept whole-row loads.
