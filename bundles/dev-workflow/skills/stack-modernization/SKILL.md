---
name: stack-modernization
description: "Modernizes a stack: upgrades outdated dependencies, removes dead or deprecated packages, migrates stale framework patterns, verifying latest versions first. Edits package.json."
argument-hint: "[deps | dead | patterns | all]"
compatibility: Requires bun and git. Uses WebSearch to confirm current package versions.
allowed-tools: Bash(git *) Bash(bun *)
metadata:
  version: "2.2.3"
  tags: "modernization, dependencies, upgrades, framework-migration, maintenance"
  author: Ship Shit Dev
when_to_use: "update dependencies, upgrade packages, /refactor stack"
---

# Stack Modernization

Keep a project on current, minimal, idiomatic dependencies. Three jobs: upgrade what
is behind, delete what is unused, and migrate patterns a major upgrade left stranded
(the v3 config still sitting in a v4 repo). Edits `package.json` and source, so it
runs behind a confirmation gate and verifies before it upgrades.

Never trust training data for a version number — the current latest is looked up, not
recalled.

## Authorized Scope

Act only within the user's request and existing approval; loading this skill
grants no new authority. Keep report-only requests report-only, honor the
caller's target, host, provider, and cost limits, ask before expanding scope,
and forward these limits to delegates.

## Contract

Inputs:

- A repo; optional focus (`deps` / `dead` / `patterns` / `all`, default `all`).

Outputs:

- A modernization plan (per package: current → latest, risk, migration notes), then
  applied upgrades with tests passing between steps.

Creates/Modifies:

- Edits `package.json`, lockfile, and source during pattern migration. Only after the
  plan is approved.

External Side Effects:

- `bun` install/upgrade commands; `WebSearch` to confirm latest versions. No deploys.

Confirmation Required:

- Before applying any upgrade or removal. Show the plan first.
- Before a major-version bump with a migration cost — call it out explicitly.

Delegates To:

- `refactor-code` when a migration is a real code refactor, not a mechanical swap.
- `dependency-audit` for the security/CVE angle (this skill is about currency, that
  one about vulnerability).

## Step 1 — Inventory

```bash
bun outdated                 # what is behind, and by how much (patch / minor / major)
bun pm ls                    # installed tree
# Dead/unused packages: run knip or depcheck if present; else grep imports per dep.
```

Also flag **framework-pattern drift** — a stale lockfile or config alongside a newer
major:

- `npm`/`yarn`/`pnpm` lockfiles or install commands in a Bun project.
- A `tailwind.config.{js,ts}` or `@apply`/`@tailwind` directives in a Tailwind v4
  project (v4 configures in the CSS `@theme` block).
- `middleware.ts` where the framework's current major expects `proxy.ts`.
- Deprecated APIs the installed major has replaced (check the package's migration guide).

## Step 2 — Verify latest before proposing

For each candidate upgrade, confirm the **current** latest with `WebSearch` (npm/GitHub
releases) — do not use a version from memory. Note the target major and whether the
package publishes a breaking-change / migration guide.

## Step 3 — Plan

```markdown
## Stack Modernization Plan — <repo>

### Upgrade
| Package | Current | Latest | Jump | Migration |
|---------|---------|--------|------|-----------|
| <name>  | x.y.z   | a.b.c  | major/minor/patch | <link or "none"> |

### Remove (unused)
- <package> — no imports found

### Pattern migration
- <stale pattern> → <current pattern>
```

Order the work: security/patch and minor upgrades first (low risk), then majors with
migrations one at a time, then dead-package removal, then pattern migration.

## Step 4 — Apply incrementally

One change at a time; tests between each so a regression is attributable:

```bash
bun add <pkg>@<verified-latest>     # or `bun remove <pkg>` for dead deps
bun run type-check || bunx tsc --noEmit
bun run test <affected-area>
```

Commit each successful step so any failure rolls back cleanly. For a major with a
migration guide, follow it explicitly rather than guessing the new API.

## Anti-Patterns

- **Upgrading to a version from memory.** Always verify the current latest first —
  training data is stale for version numbers.
- **A big-bang upgrade of everything at once.** One package (or one coherent group) at
  a time, tests between, so a break is traceable.
- **Bumping a major without reading its migration guide** — the breaking changes are
  the whole point of the major.
- **Removing a package on a missing import alone** — check for dynamic imports, config
  references, and peer-dependency roles before deleting.
- **Reintroducing npm/yarn** — this project uses Bun; upgrades go through `bun add`.
