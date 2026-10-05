# ask-dev-loop

A user-invoked router over the flagship Dev Loop. Type it when the question is "which skill do I run?" — it names the skill and why, and does not fire other user-invoked skills.

Keep this map in sync when a user-reachable Dev Loop skill is added, renamed, removed, or rerouted. A router that still points at a stale skill is a router that lies.

## What it covers

- Main flow: `interview` → `prd-writer` / `feature-intake` → `writing-plans` → `executing-plans`
- On-ramps: bugs (`debug`), intake, large/foggy work
- Phase boundaries: continue / `/clear` / `handoff` / subagent / `/compact`
- Upkeep: `codebase-advisor`, `tech-debt`, `codebase-design`
- Review: `review-dispatch` / `code-review`
- Setup: `setup-agent-routing`
