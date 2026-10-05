# Provider dispatch

The active harness owns the role map, account, model, requested effort, permitted
providers, workspace and execution host. Read its canonical configuration before
launching a role. Preserve existing choices, including generated adapters with a
separate source of truth. This distribution ships no default model assignments.

## Descriptor contract

A configured external lane supplies an explicit provider, model and requested
effort. The launcher requires every value; it never chooses a weaker fallback.
Resolve role aliases in the parent. Pass the resulting values as separate argv
entries, never interpolate them into shell code. Keep credentials in the provider
CLI's existing account configuration. Never copy authentication between hosts.

## Routes

| Parent | Same provider | Different supported provider |
|---|---|---|
| Claude | Native agent with the configured model and effort | External launcher |
| Codex | Native agent with the configured model and effort | External launcher |
| Other harness | Its documented native delegation | Report unsupported launcher parent |

The bundled launcher supports Claude, Codex and Grok children. It rejects a child
whose provider matches its parent. Native execution must retain task boundaries
and tool limits. Mixed panels use only providers explicitly authorized by the user.
If one is unavailable, report that lane as dropped; preserve the intended evidence
coverage and do useful remaining work without silently substituting a provider.

## External launcher

Resolve the installed pstack directory and run
`scripts/runner/pstack-runner --help`. Supply `--parent`, `--provider`,
`--model`, `--effort`, `--mode`, `--prompt`, `--cwd`, `--output` and
`--receipt` from the authorized task and harness configuration.

Modes are `read-only` and `isolated-write`. The harness must enforce host and
filesystem restrictions; the runner is not an operating-system sandbox. In
particular, Claude plan mode and tool exclusions do not make shell execution a
security boundary. Use read-only credentials and a real sandbox where required.
Give each writer its own harness-selected worktree. Pass `--timeout` only when
the task supplies a deadline. The default has no implicit timeout.

Grok lanes run in Grok's auto permission mode in both access modes, with its
`read-only` or `workspace` sandbox and a read-oriented or write-capable tool list.
Headless Grok cancels the whole turn when a permission prompt appears, and its
plan and accept-edits modes raise that prompt for any shell command outside Grok's
built-in list. Auto mode reports a blocked call to the model instead, and the
sandbox still confines writes. Treat auto mode as a lane-level posture change:
choose a Grok lane only when the task authorizes that sandbox.

The runner clears `BUN_OPTIONS` and `NODE_OPTIONS`, loads no environment file or
`bunfig`, checks CLI availability and credentials, captures output in exclusive
files and writes a receipt with status, requested argv, reported model, timings
and available usage. Inspect both the receipt and resulting artifact. A successful
process is not proof of task success. Receipts prove requested effort, not hidden
provider reasoning depth. A model/account probe is billable; run it only for a
user-selected lane within the task budget.

Grok authentication preflight has one bounded retry: after a result classified as
unauthenticated the runner waits five seconds and repeats the same preflight once.
The wait and second attempt share the absolute deadline and cancellation latch,
and the receipt keeps evidence from both attempts. A second failure is terminal.
Model execution is never retried.

Every concurrent lane needs distinct prompt, output and receipt paths. The runner
exclusively reserves the output, the receipt and the `<receipt>.stdout` and
`<receipt>.stderr` sidecars with private (`0600`) permissions and refuses to
overwrite existing files. All of these paths must differ from each other and from
the prompt. A failed reservation rolls back only files that attempt created.
Receipts add nullable `stdoutPath` and `stderrPath` fields naming the reserved
sidecars. They retain the model process's raw stdout and stderr, including on
dropouts and after cancellation or timeout, but not authentication-preflight
output. Keep them private beside the receipt and quote only chosen excerpts in
public evidence.

### Completion and failure classification

A `cancelled` receipt can come from a launcher signal or from a well-formed Grok
terminal cancellation. Provider cancellations exit 130. Other valid Grok terminal
failures exit 70 as `child-failed`. Invalid or incomplete terminal data stays
`malformed-output` (65) when the child exits 0; a nonzero child exit takes
precedence and classifies as `child-failed` (70). Provider failures keep the exact reason in
`error.message`, put it first in bounded evidence, and retain the reported
model, session, usage, cost and actual child exit code. Launcher cancellation and
timeout take precedence. The `signal` field is non-null only when the runner
signalled a still-active direct child. The provider CLI owns processes it starts
beneath that child; the receipt does not claim a process-tree kill. Never delete
or overwrite a receipt. A retry is a new attempt with new paths.

### Host and parent prerequisites

- The parent's tool sandbox governs whether a child CLI can reach its credentials
  and network. Verify with a live probe from the actual parent profile. A blocked
  external CLI is a loud dropout, never a reason to elevate permissions or
  substitute a model silently.
- On Linux, Grok's bounded `read-only` and `workspace` sandbox profiles need
  Landlock support and bubblewrap (`bwrap`). Hosts without them, including some
  cloud sessions, cannot run those lanes even when `grok models` succeeds. A
  sandbox-startup refusal is `child-failed` (70) with Grok's text in
  `error.evidence`. The runner never substitutes a weaker sandbox profile.
- A Codex parent whose workspace-write profile disables the network can block
  external Claude and Grok lanes (failed lookups, denied writes to state files
  outside the workspace). Read the parent's effective permissions rather than
  inferring them from the profile name. After a plain `child-failed` with no
  provider-reported reason, a Codex parent with `CODEX_SANDBOX_NETWORK_DISABLED=1`
  gets a likely-parent-sandbox hint in the error message. The status stays
  `child-failed` (70), raw evidence is kept, and the hint is not proof of cause.

## Packaged tools

- `scripts/watch-pr/watch-pr` observes and drives a PR using its selected mode.
- `scripts/orch/orch.ts` manages the local orchestration state store.
- `scripts/check-plan.mjs` checks the multi-phase plan contract.
- Worktree inventory and cleanup use the canonical `git-cleanup` skill's
  `scripts/cleanup.py` helper, resolved through that skill's installed directory.
  The old audit script is superseded; no second cleanup runtime ships here.

Read each tool’s CLI contract before use and preserve the caller’s mutation scope.
The plan checker accepts `node scripts/check-plan.mjs <plan.md>`; it has no
`--help` option. The three launchers above expose `--help`. Their imported
`bootstrap.ts` library installs locked dependencies when needed; it is not a
standalone command and has no CLI or help flag.
Runtime installation and execution happen only on the harness-approved host.
