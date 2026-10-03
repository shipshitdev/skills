---
description: "Run, author, or set up tests: run and repair, QA pass, TDD, Playwright E2E, coverage gates, or CI init."
argument-hint: "[run [scope]|qa|tdd|e2e|coverage|init|regression]"
disable-model-invocation: true
---

# Test - One Front Door for Running, Authoring, and Setting Up Tests

Drive the whole testing lifecycle from one command — run tests and repair
authorized failures, author tests with TDD, scaffold E2E or CI infrastructure,
enforce coverage, or design
AI-targeted regression suites.

## Usage

```bash
/test                    # status: detected runner, coverage config + usage
/test run                # run changed tests and report; repair requires authorization
/test run full           # the whole suite (what CI runs)
/test run unit           # run existing unit tests
/test run integration    # run existing integration tests
/test run e2e            # run existing end-to-end tests
/test run types          # type-check and report; repair requires authorization
/test run coverage       # full run + coverage report
/test run <path|pattern> # run a focused test path or pattern
/test run --since <ref>  # tests related to a commit range
/test run --no-fix       # run and report only; make no edits
/test qa                 # structured multi-phase verification pass on completed work
/test tdd                # red-green-refactor workflow for a feature or bug fix
/test e2e                # scaffold Playwright E2E tests for a frontend project
/test coverage           # set up or verify Husky pre-commit coverage enforcement
/test init               # install Vitest + GitHub Actions CI with 80% coverage threshold
/test regression         # design regression tests targeting AI-generated code blind spots
```

`/test help` prints this Usage block and stops without running anything.

Note the run/setup split: `/test run e2e` executes existing E2E tests, while
`/test e2e` scaffolds Playwright from scratch. Likewise `/test run coverage`
runs the suite with coverage, while `/test coverage` installs the Husky gate.
`/test qa` is also reachable directly as `/qa`.

## Steps

- **`run`** — the `test-runner` skill: detect the test runner, run tests at the
  right scope (changed-only by default), and on failure read output and traces,
  report failures, and when repair is authorized apply a minimal fix and rerun
  until green or blocked. Scope tokens (`full`,
  `unit`/`integration`/`e2e`, `types`, `coverage`, a path/pattern,
  `--since <ref>`, `--no-fix`) forward to the runner verbatim.
- **`qa`** — the `qa-reviewer` skill: run a structured multi-phase verification
  pass on completed AI agent work, catching bugs, missed requirements, and
  incorrect assumptions before changes are committed.
- **`tdd`** — the `tdd` skill: drive a red-green-refactor cycle for a feature
  request or bug fix, producing a test-first implementation plan followed by
  verified, passing code.
- **`e2e`** — the `playwright-e2e-init` skill: initialize Playwright
  end-to-end testing for Next.js and React projects, including config, example
  tests, and CI integration.
- **`coverage`** — the `husky-test-coverage` skill: set up or verify Husky
  git hooks that enforce a configurable coverage threshold (default 80%) for
  Jest, Vitest, or Mocha, blocking commits that fall below it.
- **`init`** — the `testing-cicd-init` skill: install Vitest testing
  infrastructure and GitHub Actions CI/CD for TypeScript projects, configuring
  80% coverage thresholds and Bun-based workflows.
- **`regression`** — the `testing-expert` skill in AI regression mode: design
  regression tests that target AI model blind spots such as sandbox vs. production path drift,
  response-shape mismatches, and same-model review failures.

## Workflow

Use the `test-dispatch` skill. It parses the subcommand, resolves the mode, and
delegates to the right engine. Read-only until the delegated skill's own
confirmation gate; it never writes files, installs packages, or modifies config
directly.

1. **Parse the argument** into a mode (`status` / `run` / `qa` / `tdd` / `e2e` /
   `coverage` / `init` / `regression`), forwarding any scope token to the run
   engine. Unknown argument → print Usage, do not guess.
2. **For `status`**: print a one-line domain overview (detected runner, coverage
   config) and the Usage block — mutate nothing.
3. **Route** to the delegated skill.
4. **Defer** preconditions and confirmation to the delegated skill — this command
   does not relax them.

## Repair scope

Before the first source or test edit, obtain explicit repair authorization.
Existing explicit authorization within the agreed scope satisfies this gate;
do not ask again. Neither `/test run` nor a bare scope authorizes repairs.
`--no-fix` or report-only mode prohibits source and test edits even after earlier
repair authorization. Forward these constraints to the dispatcher and engine.
