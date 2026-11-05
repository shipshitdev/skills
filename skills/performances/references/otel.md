# OTel Tracing

Adds OpenTelemetry tracing to the observability vendor the project already
uses, applied at function definitions, enforced by lint, with request context on
every span and trace context propagated in and out.

## Authorized Scope

Follow `protocol.md`. Loading this playbook grants no new authority, and adding
a new vendor is never implied.

## Contract

Inputs:

- Optional scope (services, modules)

Outputs:

- Tracing setup, a tracing helper, wrapped functions, a lint rule with tests
- Coverage list of traced and intentionally untraced functions
- Overhead measurement

Creates/Modifies:

- Tracing bootstrap, helper module, application code, lint config on
  `perf/otel`

External Side Effects:

- Exports spans to the vendor already configured; push and PR

Confirmation Required:

- Before adding any vendor, collector, or dependency that sends data somewhere new
- Before sending data to a third-party host from an environment that did not before

Delegates To:

- `/git pr` playbook when installed

## Detect and check fit

Detect language, framework, existing OTel SDKs, and the vendor in use (error
tracker, APM, log or trace backend, platform-provided tracing). Check that the
vendor accepts OpenTelemetry (OTLP or its OTel-compatible API) and what that
costs in volume and price. Export to that vendor. If none exists, or it cannot
take OTel, write the options and a recommendation in the PR and ask the user
before choosing one. Do not add a second vendor.

## Instrument at the definition, never inline

- Span creation, error recording, status, and timing live in one helper module.
  Call sites only declare a name and options.
- Use the stack's definition-site mechanism: a decorator (`@traced`) or a wrapper
  at declaration (`export const getOrder = traced("orders.getOrder", async (id) => ...)`).
  Where the language has neither, use the idiomatic equivalent (middleware,
  interface decorators, generated wrappers) and say what the stack cannot do.
- No `startSpan` or equivalent inside function bodies outside the helper.
- Trace route handlers, middleware, and helpers.
- Every exported async function that performs I/O is traced: database, HTTP,
  filesystem, queue, cache, subprocess, directly or by calling untraced I/O
  libraries. Pure async functions and thin pass-throughs are listed as
  intentionally untraced.
- Prefer library auto-instrumentation for drivers and HTTP clients, and the
  wrapper for application code.
- Span names are low-cardinality, `{verb} {object}` (`GET /orders/:id`, never
  the raw path or ids). Set status to error only when the operation finally
  failed, and record exceptions with trace ids.
- Cap the span count: a trace-shape test fails when one service emits more than
  a small, stated number of internal spans per trace, so wrapping every I/O
  function does not flood the vendor.

## Request context on every span

Set request context once at the edge (middleware) in the stack's context store
(`AsyncLocalStorage`, `contextvars`, Go `context`). Copy it onto every span from
a span processor at start, so wrappers need no arguments. Attach at least:
organization or business id, user id, outcome (success, error, denied, and so
on), route, and request id. Follow the semantic conventions where they exist and
namespace the rest (`app.org.id`). Use ids, never names, emails, tokens, request
bodies, or other PII. Allowlist attributes.

## Propagate

- Consume the incoming W3C `traceparent` (and `tracestate`) through the
  propagator on HTTP, queue messages, and webhooks. Never hand-parse it.
- For public endpoints, decide parent versus link. Untrusted callers can force
  sampling or flood traces, so a link to a fresh trace may fit better. Record the
  choice.
- Inject it on outgoing HTTP clients and queue producers. Send it to internal or
  allowlisted hosts by default, not to arbitrary third parties.
- Do not propagate baggage unless a feature needs it.

## Lint rule

Add a rule in the project's linter that fails when an exported async function in
an I/O module is not wrapped, and when span creation appears outside the helper.
Use the linter's native extension point (custom ESLint rule, Biome plugin,
analyzer, ruff-compatible plugin, or a small AST check in the test suite), with
valid and invalid cases tested first. Wire it into the existing lint script and
CI. Allow a suppression only with a written reason.

## Measure

Overhead, not speedup: run the same load with tracing off and on and compare
p50 and p95 latency and throughput with `compare.py`, state the overhead budget
you used, and record spans per request. Verify against the real exporter or a
local collector: spans arrive, attributes are present, parent and child
relationships are right, and `traceparent` round-trips across two services.
Sample in the pipeline: keep the SDK sampler always-on (a default parent-based
sampler lets an external `traceparent` with the sampled flag off silence
tracing) and do head or tail sampling in a collector, with tail rules that keep
errors and slow traces, when volume is high.

## PR

Follow `protocol.md`. Include the coverage list, the vendor-fit decision, the
lint rule, the overhead table, and a trace screenshot or exported span sample
with ids redacted.
