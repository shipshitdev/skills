---
name: env-setup
description: Finds the env vars a codebase reads, generates .env.example, validates .env, and checks .gitignore covers secrets. Use for /env or environment configuration setup.
metadata:
  version: "2.2.2"
  tags: "environment, dotenv, secrets, configuration, scaffolding, validation"
  author: Ship Shit Dev
when_to_use: "missing env var, secrets in git, env template"
---

# Env Setup

Make a project's environment configuration explicit: find every variable the
code reads, keep `.env.example` truthful, verify the developer's real `.env`
satisfies it, and make sure no secret file can reach git.

## Contract

Inputs:

- A repository; mode `setup` (default, discover + scaffold + validate),
  `validate` (check only), or `scaffold` (regenerate templates only).

Outputs:

- The discovered variable inventory grouped by service, gaps between code and
  `.env.example`, missing/unset required variables, and any `.gitignore` holes.

Creates/Modifies:

- `setup`/`scaffold`: creates or updates `.env.example` (and per-app templates
  in a monorepo). May add missing `.env*` rules to `.gitignore`.
- Never creates, edits, or overwrites a real `.env`/`.env.local` — it reports
  what is missing there and leaves the values to the developer.

External Side Effects:

- None. Reads the codebase and env files locally; never transmits values.

Confirmation Required:

- Before overwriting an existing `.env.example` that has hand-written comments
  or values the scan did not produce.

## When to Use

- Setting up environment variables for a new project or app
- Regenerating `.env.example` after configuration drift
- Validating that a `.env` satisfies what the code requires
- Auditing that `.gitignore` keeps secret env files out of git

## Phase 1: Discover Required Variables

Scan the codebase for environment reads:

```bash
grep -rEoh "(process\.env|import\.meta\.env)(\.[A-Z0-9_]+|\[['\"][A-Z0-9_]+['\"]\])" \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" \
  --include="*.mjs" --include="*.cjs" \
  --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build \
  --exclude-dir=.next --exclude-dir=coverage . \
  | grep -oE "[A-Z0-9_]{2,}" | sort -u
```

**Treat that grep as a starting inventory, never as the answer.** It knows one
language family (JS/TS) and two syntaxes (`process.env.X` and
`process.env["X"]`, plus the `import.meta.env` equivalents). It cannot see a
variable read through a helper (`getEnv("STRIPE_KEY")`), a destructure
(`const { DATABASE_URL } = process.env`), a dynamic key, or a non-JS service in
the same repo — Python `os.environ`, Go `os.Getenv`, Dockerfiles, CI workflows.
Exclusions are directory-scoped (`--exclude-dir`) because filtering `grep -oh`
output by path is impossible: `-o` prints only the matched text and `-h`
suppresses the filename, so a downstream `grep -v node_modules` matches nothing
and silently filters nothing.

Widen the sweep by hand from there: framework config (`next.config.*`,
`nest-cli.json`, deploy config), schema-based env validation modules
(zod/valibot env files), container and CI definitions, and existing `.env*`
files. In a monorepo, inventory per app/package — apps often need different
variables. Report the inventory as "found by scan + found by hand", so a reader
can see what the automated pass could not cover.

## Phase 2: Generate .env.example

Create or update `.env.example` from the inventory. Group by service with a
comment header per group, placeholder values only — never a real credential:

```env
# Application
NODE_ENV=development
PORT=3001

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Authentication
AUTH_SECRET=...

# Monitoring
SENTRY_DSN=https://...
```

For monorepos, write per-app templates when apps diverge. Preserve existing
hand-written comments; confirm before overwriting anything the scan did not
produce. Document any variable whose purpose is not obvious from its name.

## Phase 3: Validate

- Every variable the code reads appears in `.env.example`; every template
  variable is actually read somewhere (flag dead entries).
- The local `.env` (if present) sets every required variable; report gaps
  without printing secret values.
- For TypeScript projects, recommend schema-based env validation (e.g. zod) at
  app startup so missing variables fail fast — point at where to add it rather
  than wiring it unasked.

## Phase 4: Keep Secrets Out of Git

- `.gitignore` must cover `.env`, `.env.local`, and every `.env.*` variant
  **except** `.env.example` (which must be committed).
- Check nothing secret is already tracked: `git ls-files '.env*'` should return
  only templates. A tracked secret file is a finding to surface — removing it
  from history belongs to `git-safety`, not this skill.
- For production, point at platform-native secret stores (AWS Secrets Manager,
  Vercel/hosting env vars) — real values never live in the repo.

## Final Report

State the mode that ran, variables discovered (per app where relevant),
template files created or updated, validation gaps, and any `.gitignore` or
tracked-secret findings.

## Anti-Patterns

- **Writing real values.** This skill produces templates and reports; actual
  secrets are entered by the developer or a secret manager.
- **Printing secret values in output.** Name the variable, never its value.
- **Guessing variables the code never reads.** The template mirrors the code,
  not a generic stack checklist.
