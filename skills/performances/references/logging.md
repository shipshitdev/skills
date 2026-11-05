# Wide Event Logging

Replaces scattered log lines with one wide, context-rich event per request or
job, tail-sampled, sharing trace ids with tracing.

## Authorized Scope

Loading this playbook grants no new authority.

## Contract

Inputs:

- Optional scope (services, modules)

Outputs:

- Event builder, emit point, tail sampler, with tests
- Log volume and overhead measurements

Creates/Modifies:

- Logging setup, middleware, call sites that logged mid-request, tests on `perf/logging`

External Side Effects:

- Reads loggingsucks.com; push and PR

Confirmation Required:

- Before changing log destinations or vendors
- Before dropping any log that compliance or audit needs

Delegates To:

- `/performances otel` playbook for trace ids, when tracing exists or is added
- `/git pr` playbook when installed

## Read the source first

Read loggingsucks.com (Boris Tane) in full before editing. Its core ideas:
logging should record what happened to the request, not what the code is doing;
emit one wide event per request per service hop, built up over the lifecycle and
written once at the end in a `finally` path; make events high-cardinality and
high-dimensionality; tail-sample after the outcome is known; wide events and
traces are complementary, ideally the same data. If the page cannot be fetched,
say so and stop instead of working from memory.

## Detect

Logger (pino, winston, structlog, stdlib logging, zerolog, zap, slog, logback,
Serilog, `console`), framework hooks (middleware, interceptors, job wrappers),
log destination and vendor, tracing setup, serverless versus long-lived runtime
(flushing), and existing redaction.

## Design the event

- One event per request or job, per service hop. Middleware creates it at the
  start (request id, timestamp, method, route, service, version, deployment id,
  region), stores it in the context store, and emits it once in a `finally` path
  with `duration_ms`, status, and `outcome`.
- Handlers and helpers enrich it as they work: user and organization ids, plan,
  business entities (cart, order, job type), dependency timings (database,
  payment, external API), feature flags, cache hits, retry counts.
- Errors become fields on the event (type, code, message, retriable), then
  rethrow as before.
- The event emits exactly once on success, throw, timeout, client abort, and
  process shutdown where the runtime allows. Serverless runtimes flush before
  return.
- Cap event size, truncate large values, redact secrets, tokens, authorization
  headers, request bodies, and PII by allowlist.
- Background jobs, queue consumers, and scheduled tasks get the same treatment,
  one event per job run.

## Replace, do not duplicate

Convert mid-request log lines into fields on the event. Keep logs that have no
request to belong to: startup, shutdown, scheduler ticks, library output.
Keep audit and compliance logs untouched unless the user says otherwise. Do not
remove an error log until its information is on the event.

## Tail sampling

Decide at emit time, with the whole event in hand:

1. Always keep errors (5xx, thrown, explicit failure).
2. Always keep slow requests, above a configured threshold near the route's p99.
3. Always keep important traffic: configured tenants or plans, internal and test
   accounts, flagged sessions, new releases or canaries, and routes such as
   payments and auth.
4. Keep a small share of the rest, chosen deterministically: hash the trace id
   (the request id when there is no trace) and keep ids below a configured
   threshold (start at 1 to 5 percent).

Record `sample_rate` on kept events so counts can be reweighted. Make
thresholds and rules configuration, not constants. If tracing is also sampled,
both decisions must use the same rules keyed by the same trace id, including when
a collector makes the trace decision (see `otel.md`), so a kept trace has its
event and the reverse. Test this across service hops.

## Trace ids

Take `trace_id` and `span_id` from the active tracing span so events and traces
join. With no tracing, generate W3C-compatible ids, propagate them, and keep
the field names so tracing added later lines up. Where wide events can double as
span data, prefer that over duplicating.

## Measure

Before: log lines and bytes per request, and how many lines are needed to explain
one failed request. After: events per request (one), bytes per request, volume
reduction from sampling, and request overhead with `compare.py`. Test the
sampler (errors, slow, and important traffic are always kept), single-emit on
throw, redaction, and size caps.

## PR

Include a before/after sample of one request's output, the
volume table, the sampling rules and their configuration, and what was left as
ordinary logs.
