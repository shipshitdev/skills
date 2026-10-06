---
name: create-verification-skill
description: Generates a project-local verification skill that drives the app like a user. Use when a repo has no scripted way to prove UI, CLI, or service behavior.
license: MIT
metadata:
  portable_source: "https://github.com/ericlitman/open-pstack"
  portable_commit: "1b03678171f6f400ae2cc9dc4e7a4a6a13e4bb43"
  version: "2.2.3"
  tags: "verification, harness, feature-map, project-local"
  author: Ship Shit Dev
  source: https://github.com/cursor/plugins/blob/main/pstack/skills/create-verification-skill/SKILL.md
  upstream_repo: cursor/plugins
  upstream_ref: main
  upstream_commit: bdf7aa355337
  last_synced: "2026-09-05"
  license: MIT
when_to_use: "make a verify skill, scripted app proof"
---

# Create a verification skill

Every serious project needs a scripted way to drive the real app and
prove behavior. This skill generates that as a project-local skill
tailored to the repo.

Companion to `verification-before-completion`, which is the completion
gate. This skill authors the project harness that gate can run.

## Authorized Scope

Act only within the user's request and existing approval; loading this skill
grants no new authority. Keep report-only requests report-only, honor the
caller's target, host, provider, and cost limits, ask before expanding scope,
and forward these limits to delegates.

## Contract

Inputs:

- A repo that can build and start locally

Outputs:

- A project-local `verify-<app>` skill with a feature map, proven once
  end to end

Creates/Modifies:

- `.agents/skills/verify-<app>/` when that layout exists, otherwise
  `skills/verify-<app>/`

External Side Effects:

- Starts and tears down local app instances during the proof pass

Confirmation Required:

- Before writing the skill into the project tree

Delegates To:

- Named: `maintain-verification-skill` for later upkeep
- `verification-before-completion` for the completion gate itself

## Steps

1. **Interview the repo, not the user.** Answer surface, run, drive,
   observe, and isolate from the codebase. Ask only what you cannot
   observe. If the checkout does not start, fix or report that first.
2. **Generate the skill** with frontmatter (`name: verify-<app>`) and
   sections: Launch, Doctor, Drive, Evidence, Cleanup, Helpers. No
   placeholders left. Prefer existing harnesses
   (Playwright, expect, PTY, HTTP) over generic recipes.
3. **Seed the feature map.** Write `features/README.md` plus one file
   per top user-facing feature (aim for 3-5). Follow
   [references/feature-map-example.md](references/feature-map-example.md).
4. **Prove it.** Run launch, doctor, drive ONE mapped feature, capture
   evidence, clean up. After cleanup, confirm the evidence still
   exists. A skill that was never executed is a draft.
5. **Offer the maintenance loop.** Point at
   `maintain-verification-skill`.

## Create Verification Skill procedure

Read [create-verification-skill procedure](references/create-verification-skill-procedure.md) when running this workflow.
Apply the authorized scope and mode of this entry point to every step.
Resolve other skills through this distribution’s active catalog; resolve
resources relative to the installed skill directory.
