# Pstack import verification

The source ledger covers 193 Open Pstack files and 164 files from the original
Cursor Pstack subtree. Each file has a canonical disposition. Archived source
coverage is not a claim that every harness supports every workflow.

## Automated evidence

The repository regression suite exercises source integrity, complete mappings,
destination changes, executable bits, candidate additions and removals, local
conflicts, immutable candidate output, archive path safety, and packaging that
excludes installed dependencies. See:

- `scripts/tests/test_pstack_sync.py`
- `scripts/tests/test_bundle_resources.py`
- `scripts/tests/test_pstack_model_boundary.py`
- `scripts/tests/test_skill_composition.py`

The packaged runtime retains upstream watcher, orchestration, bootstrap, plan
checker and provider-runner tests. Its CLI requires explicit provider, model and
effort values. Provider alias parsing and receipt fixtures are compatibility data;
they do not select runtime defaults.

Run the repository suite and the packaged runtime on the approved verification
host. CI repeats both, checks strict runtime types, validates skill composition
and versions, and verifies generated bundle content.

## 2026-10-05 sync (issue #188)

Open Pstack advanced to 1b03678 and Cursor Pstack to 807c031. The tooling gained
`ignored_paths` for repo-only upstream trees (open-pstack's verify harness), so the
archive no longer carries that harness. Adopted: the attack-the-premise, test-behavior
and explain-the-number principles, a benchmark checklist reference wired into the
perf-issue and hillclimb playbooks, the agent-proof architect lens and red flags,
`correct` folded into rules-capture, fresh-subagent and evidence-or-label rules, the
poteto-agent skill preload, show-me-your-work run markers and a non-truncating
`log.sh`, the Zod example, PR description headings, unslop rules 32 and 33, swarm
brief details and the prompting reference. Retired: how critique mode and the
duplicate commit-summary activity procedure (standup personal mode covers it).
Not adopted: model, routing and effort defaults, `/loop` and `/goal` autopilot
cadence, Cursor-only UI and open-pstack repository infrastructure.

The runner reliability bundle from open-pstack 1b03678 is copied verbatim:
terminal-event arrays, Grok and Claude terminal failure classification, retained
`<receipt>.stdout` and `<receipt>.stderr` sidecars, distinct-path reservation,
Grok preflight matching, a portable `sh` launcher that clears `BUN_OPTIONS` and
`NODE_OPTIONS` and loads no environment file or `bunfig`, and a likely-sandbox hint.
Two choices need explicit review. Grok lanes now use `--permission-mode auto` in
both access modes, because headless Grok cancels a whole turn on a permission
prompt and the Grok sandbox still confines writes. The runner also accepts the
`ultra` effort value, which selects nothing by itself. Model tables and setup
changes stay out; the user-owned role sheet keeps routing.

## Deliberate adaptations

- One Shipshit execution router replaces upstream poteto-mode entry points.
- Existing deslop code, product, UI and prose modes remain available.
- Principle procedures are installed resources rather than separate catalog skills.
- User-owned roles, accounts, host limits and provider opt-ins take precedence.
- Cleanup retains immutable merge proof and preservation of tracked, untracked,
  ignored, unpushed and active work; upstream deletion shortcuts are not imported.
- Session hooks and native agent definitions are explicit setup templates.
- Benny and Bot UI preserve their procedures behind capability and authority checks.
  Their inclusion does not schedule a routine or expose a service.
- The native model/effort template matrix becomes a configured-role adapter.
  Setup verifies selected roles without requiring unused providers.

## Installed-artifact and live boundaries

The official skills installer was exercised on Studio with all 188 canonical
skills selected for Codex, Claude Code and Cursor. The shared agent directory and
Claude-specific copies contain every selected skill with no extra identities,
missing resources or source-byte differences. No dependency directory was copied.
The installed runtime then passed all 155 tests (561 assertions) and strict
TypeScript checks, independent of the upstream checkouts.

A full live provider cutover additionally requires backed-up configuration
changes and a fresh-session routing check. Unit tests and static adapter review
cannot substitute for that evidence. Preserve user-generated routing sheets
and their source of truth when disabling duplicate plugins.
