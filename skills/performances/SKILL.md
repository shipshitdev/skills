---
name: performances
description: "Performance refactoring behind one command: parallelize async calls, load-test the DB schema, add OTel tracing, wide-event logging, narrow selects, drop needless URL parsing, hoist regexes, and promote hot jsonb keys. One PR per action."
argument-hint: "<parallel|dbload|otel|logging|select|url|regex|jsonb|all> [scope or notes]"
compatibility: Requires git and an authenticated GitHub CLI gh for PRs; scripts/compare.py needs Python 3.9+ (standard library only); dbload and jsonb need a throwaway local database; logging reads loggingsucks.com.
metadata:
  tags: "performance, refactoring, async, database, load-testing, opentelemetry, tracing, logging, jsonb, regex, orm"
  author: Ship Shit Dev
when_to_use: "/performances, /performances all, speed up this app, performance audit, parallelize awaits, load test the schema, add tracing, wide events, select only needed fields, hoist regex, jsonb column"
disable-model-invocation: true
---

# Performances

One entry point for measured, behavior-preserving performance work on any
codebase. Every action detects the stack first, adapts to it, says what does
not apply, then follows the same loop: measure before, fix, measure after, ship
one PR. The first word of the arguments picks the action; everything after it
goes to that action unchanged.

| Action | Playbook | What it does |
|---|---|---|
| `parallel` | [references/parallel.md](references/parallel.md) | Finds sequential awaits on hot paths that are independent and runs them concurrently. Keeps authz gates, transactions, ordered writes, and ordered events sequential. Alias `parallel-async`. |
| `dbload` | [references/dbload.md](references/dbload.md) | Builds a load-test suite for the DB schema: seeds real relationships at 1x/10x/100x/1000x, runs the code's real queries, finds what fails at scale, fixes it, and charts before/after with confidence intervals. Never touches prod. Alias `db-load-test`. |
| `otel` | [references/otel.md](references/otel.md) | Adds OpenTelemetry tracing to the vendor already in use, applied at function definitions, enforced by a lint rule, with request context on every span and `traceparent` in and out. Alias `otel-tracing`. |
| `logging` | [references/logging.md](references/logging.md) | Replaces scattered log lines with one wide, context-rich event per request or job, tail-sampled, sharing trace ids with tracing. Alias `wide-event-logging`. |
| `select` | [references/select.md](references/select.md) | Finds whole-row loads that read a few fields and selects only what is needed. Alias `select-fields`. |
| `url` | [references/url.md](references/url.md) | Removes `new URL()` style parsing that does no validation or normalization of untrusted input. Alias `url-parsing`. |
| `regex` | [references/regex.md](references/regex.md) | Hoists regexes out of functions and loops, handling `g`/`y` state and dynamic patterns. Alias `hoist-regex`. |
| `jsonb` | [references/jsonb.md](references/jsonb.md) | Promotes a hot-path single key of a large jsonb column to a real column, with migration and backfill that a human approves for prod. Alias `jsonb-columns`. |
| `all` | [references/all.md](references/all.md) | Runs the eight actions in that order as separate workstreams, each with its own branch and PR. |

Every action also follows [references/protocol.md](references/protocol.md): the
shared stack-detection, evidence, behavior-preservation, safety, and PR rules.

## Dispatch

1. Read the first word of the arguments. Accept only the nine actions above or
   an alias from the table.
2. Bare `/performances`, or an unknown first word: print the table above and
   stop. Do not guess an action and do not run any command. Running everything
   is `/performances all`.
3. Otherwise read `references/protocol.md` and the action's playbook in full and
   follow them as if they were the skill, passing the remaining arguments as the
   scope. Each playbook keeps its own scope, confirmation gates, and final report.

Examples:

```text
/performances parallel                 # sequential awaits across the whole app
/performances parallel src/billing     # limit the scan to one area
/performances dbload                   # load-test the schema at 1x/10x/100x/1000x
/performances otel                     # tracing to the observability vendor already in use
/performances logging                  # wide events with tail sampling
/performances jsonb                    # promote hot jsonb keys, never applies to prod itself
/performances all                      # all eight, separate branch and PR each
```

## Scope

Loading this router authorizes nothing by itself. Only the selected playbook's
contract applies, and its confirmation gates stay in force. Never chain to a
second action unless the user asks for it (`all` is that ask) or the selected
playbook names that step as part of its own workflow; recommend it instead.

## Helper

`scripts/compare.py` compares before/after samples with bootstrap confidence
intervals, a Mann-Whitney test, Holm correction across scenarios, and writes a
self-contained HTML chart. Run it from the installed skill directory:

```bash
python3 <skill-dir>/scripts/compare.py samples.json --out .tmp/report.html
```

Input and exit codes are documented at the top of the script. Use it for every
before/after claim in every action.
