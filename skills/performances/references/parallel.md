# Parallel Async

Finds sequential async calls on hot paths that do not depend on each other and
runs them concurrently, without changing what the code observably does.

## Authorized Scope

Follow `protocol.md`. Edit only application code and tests within the requested
scope. Loading this playbook grants no new authority.

## Contract

Inputs:

- Optional scope (path, endpoint, module)

Outputs:

- Ranked list of changed sites with before/after latency evidence
- List of sites deliberately left sequential, with the reason each

Creates/Modifies:

- Application code and tests on `perf/parallel`

External Side Effects:

- Push and PR

Confirmation Required:

- Before changing any site that touches money, auth, or externally visible ordering

Delegates To:

- `/git pr` playbook when installed

## Detect

Language and async model decide the idiom. Examples: JavaScript or TypeScript
`Promise.all`, Python `asyncio.gather` or `TaskGroup`, Go `errgroup`, Rust
`try_join!`, C# `Task.WhenAll`, Kotlin `awaitAll`, Swift `async let`. Also detect
the DB client, HTTP client, and pool sizes. A codebase with no async I/O does
not apply: say so and stop.

## Scan

Deep scan every hot path, not a sample: route handlers, server actions, page
loaders and server components, resolvers, queue consumers, cron jobs, and the
helpers they call. Rank by traces or APM when present; otherwise by call graph
from entry points.

Flag each of these:

- Consecutive awaits where a later call does not consume an earlier result
- Awaits inside loops over independent items (use bounded concurrency)
- Sequential awaits split across helper functions, where the fix is at the caller
- Awaits chained through `then` or intermediate variables that hide independence

## Independence test

A pair is independent only if all hold:

1. No data dependency, including through variables, closures, or mutated objects.
2. No shared mutable state or ordering the outside world can observe.
3. Neither call is gated by the other's success, permission, or side effect.
4. Running together stays inside connection, pool, and rate-limit limits.
5. Error behavior is preserved. Sequential code surfaces the first failure in
   program order and never starts later calls. Parallel code starts all of them.
   Choose `all` versus `allSettled` (or the language equivalent) deliberately, make
   sure no promise is left unhandled, and keep the same error surfaced.

## Keep sequential

- Authorization or ownership checks that gate reads. Do not read speculatively.
- Everything inside a transaction. One connection serializes statements anyway.
- Ordered writes, webhooks, payments, emails, and anything with read-after-write.
- Ordered progress events, streamed output, and audit trails.
- Calls bound by rate limits, retry/backoff sequencing, or idempotency order.
- Loops over large collections with no concurrency cap. Bound them (for example
  chunks of 5 to 10) or leave them.

## Fix

Replace the pattern with the stack's concurrent form, keeping result variables
and types the same. Add a concurrency cap for loops. Keep sequential parts
sequential even when they sit between parallel parts. Do not add comments that
only narrate the change.

## Measure

Per changed site, time the enclosing endpoint, job, or function over at least 20
samples after warmup with realistic dependency latency: the real local database
where possible, otherwise stubs that add fixed delays. Record the number of
sequential awaits on the critical path before and after (a trace waterfall
shows it). Expect the sum of independent latencies to become roughly the
maximum; if it does not, find out why before shipping.

## Tests

Before the change: characterization tests of results and error behavior for each
site. Add a test that a failure in one call still surfaces the same error as
before. Where order mattered, assert it.

## PR

Follow `protocol.md`. List each changed site with its latency delta, then each
site left sequential with the reason.
