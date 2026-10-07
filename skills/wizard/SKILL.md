---
name: wizard
description: "Generates an interactive bash wizard guiding a human through manual steps: provisioning, credentials, CI secrets, third-party dashboards, one-off migrations or cutovers."
license: MIT
metadata:
  version: "2.2.4"
  tags: "wizard, setup, secrets, human-in-the-loop, bash"
  author: Ship Shit Dev
  source: https://github.com/mattpocock/skills/blob/main/skills/engineering/wizard/SKILL.md
  upstream_repo: mattpocock/skills
  upstream_ref: main
  upstream_commit: 4588b32ecab9ecc9fc8cc6b6c5e7d675b6004b0d
  last_synced: "2026-10-06"
  license: MIT
when_to_use: "setup script, walk me through"
---

# Wizard

A **wizard** is a bash script that walks a human, step by step, through a manual
procedure that is tedious to do by hand and tedious to re-explain to an agent
every time. It opens each URL, says exactly what to click and copy, captures the
values, writes them where they belong (`.env`, GitHub secrets), confirms at every
stage, and shows how many stages are left.

The UX is already solved by [scripts/template.sh](scripts/template.sh) — stage
progress, confirmation gates, cross-platform URL opening, hidden secret entry,
idempotent `.env` upserts, `gh secret` / `gh variable` writes, and a closing
summary. Scope the procedure and author its stages. Leave the library above the
`STAGES` marker untouched.

A wizard is ephemeral by default — built for one run, saved to a scratch or
`scripts/` path, deleted when the job is done. Commit it only when the user wants
a repeatable setup path in the repo.

Skip this skill when the agent can perform the steps itself.

## Contract

Inputs:

- A manual procedure (dashboard clicks, credentials, cutover, one-off migration)
- Repo files that name the values: `.env.example`, README, CI workflows

Outputs:

- An executable bash wizard whose stages capture every required value

Creates/Modifies:

- A wizard script at a path the user confirms (`scripts/` or scratch)
- The wizard itself may later write `.env` and GitHub secrets when the human runs it

External Side Effects:

- None from this skill. The generated script writes env files and secrets when run.

Confirmation Required:

- Before writing the wizard file
- The generated script confirms before irreversible actions

Delegates To:

- None

## Process

### 1. Scope the procedure

Work out every manual step the human must take and every value that gets captured.
Read the repo first:

- For setup: `.env`, `.env.example`, `.env.*`, README, `docker-compose*`, framework
  config, and `.github/workflows/*` (every `secrets.*` / `vars.*` reference is a
  value the wizard must produce).
- For a migration: current state, target state, and the irreversible actions
  between them.

Show the user the ordered list of stages and the values each produces, and
confirm — they may add, drop, or reorder.

**Done when:** every stage is named in order, and for each captured value (a) where
the human gets it, (b) where it is written (`.env`, a GitHub secret, both, or
nowhere), and (c) whether it is secret or public.

### 2. Map each stage's journey

For each stage, write the precise path a human follows: which URL to open, what
to do there, where a value is shown, which variable it fills. When the current UI
or command is unknown, ask or check the docs — invent no steps.

**Done when:** every stage traces to concrete instructions a stranger could follow.

### 3. Author the wizard

Copy `scripts/template.sh` to the target path. Replace the example stage with one
`stage` per step, in dependency order. Use the library helpers — `stage`,
`say` / `step`, `open_url`, `ask` / `ask_secret`, `write_env`,
`set_secret` / `set_var`, `pause` / `confirm` — and set `TOTAL_STAGES` to the
number of stages written.

Hold the bar the template sets: open the URL before asking for its value, use
`ask_secret` for anything secret, `write_env` every persisted value, `set_secret`
only the values CI actually needs, and `confirm` before any irreversible action.
Each `stage` clears the screen so only the current step is visible — keep a stage
to one focused task. Leave the library above the marker untouched.

### 4. Verify and hand off

- `bash -n <script>`; run `shellcheck` if available.
- `chmod +x <script>`.
- Trace it statically rather than running it end-to-end (it opens browsers and
  blocks on human input): every value from step 1 is captured and lands where
  step 1 said, and every `set_secret` name matches a `secrets.*` reference in CI.
- Tell the user how to run it. If it is a repeatable setup path, commit it and
  link it from the README so the next person runs the script instead of asking
  an agent.
