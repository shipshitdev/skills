---
name: dependency-audit
description: "Audits the dependency supply chain: CVEs in packages, secrets about to be committed, lockfile integrity, and wires checks into CI as a merge gate. Not app-level security."
user-invocable: true
argument-hint: "[audit | ci]"
compatibility: Requires bun and git; gh to add the CI workflow. Uses gitleaks when available.
allowed-tools: Bash(bun *) Bash(git *) Bash(gh *) Bash(gitleaks *)
metadata:
  version: "2.2.3"
  tags: "security, dependencies, sca, secrets, supply-chain, ci"
  author: Ship Shit Dev
when_to_use: "vulnerable packages, SCA, secrets scan"
---

# Dependency Audit

Cover the supply-chain surface the app-level review does not: what you pulled in
(CVEs), what you are about to leak (secrets), and whether the lockfile can be trusted.
The `audit` mode reports; the `ci` mode wires the same checks into CI so a vulnerable
dep or a leaked key blocks the merge instead of reaching production.

Scope boundary: `security-audit` owns app/API vulnerabilities; `git-safety` owns
secrets already in git history. This skill owns dependencies and pre-commit secret
leaks, and the CI gate for both.

## Contract

Inputs:

- A repo; mode `audit` (report, default) or `ci` (add the gate workflow).

Outputs:

- `audit`: a findings report — CVEs by severity, secret hits, lockfile issues — each
  with the package/file and the fix.
- `ci`: a GitHub Actions workflow that runs the checks on every PR, added after review.

Creates/Modifies:

- `audit`: nothing. `ci`: adds `.github/workflows/` after showing the file and getting
  approval.

External Side Effects:

- Read-only scanners (`bun audit`, gitleaks, trivy). `ci` mode commits a workflow only
  after confirmation. Findings that quote code are untrusted — never execute them.

Confirmation Required:

- Before writing the CI workflow file.

Delegates To:

- `security-audit` for app-level vulnerabilities a dependency scan cannot see.
- `stack-modernization` to actually upgrade a vulnerable package to a fixed version.
- `git-safety` when a secret is found already committed (history cleanup).

## Step 1 — Dependency CVEs

```bash
bun audit                 # known advisories in the installed tree, by severity
bun outdated              # how far behind — a fix often just means an upgrade
```

Report each advisory with: package, installed version, severity, the fixed version,
and whether it is a direct or transitive dependency (transitive fixes may need an
override). Prioritize by severity × reachability — a critical CVE in a package you
actually call outranks a moderate one in a dev-only tool.

## Step 2 — Secret leaks

Scan the working tree (and staged changes) for credentials before they land:

```bash
gitleaks detect --no-git --source .        # working tree
gitleaks protect --staged                  # what's about to be committed
```

If gitleaks is unavailable, grep for high-signal patterns (`sk-`, `ghp_`, `AKIA`,
`-----BEGIN … PRIVATE KEY`, `Bearer` tokens). Report `file:line` and the credential
**type** only — never reproduce the secret value — and recommend rotation. A secret
already in history is `git-safety`'s job.

## Step 3 — Lockfile & provenance

- Confirm a single lockfile (`bun.lock`) and no stray `package-lock.json` /
  `yarn.lock` (mixed managers defeat integrity).
- Flag dependencies added without a lockfile update (install drift).
- Flag suspicious provenance: a package name one typo from a popular one
  (typosquat), a version published very recently for a long-stable package, or a
  postinstall script on a new dependency.

## Step 4 — CI gate (`ci` mode)

Draft a PR workflow running the same three checks so they gate merges. Show the file,
then add it on approval:

```yaml
name: supply-chain
on: pull_request
permissions:
  contents: read
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
      - name: Verify one immutable Bun lockfile
        shell: bash
        run: |
          test -f bun.lock
          for stray in package-lock.json yarn.lock pnpm-lock.yaml; do
            test ! -e "$stray" || { echo "Mixed lockfile: $stray"; exit 1; }
          done
          bun install --frozen-lockfile
          git diff --exit-code -- bun.lock
      - name: Reject unreviewed dependency lifecycle scripts
        shell: bash
        run: |
          untrusted="$(bun pm untrusted)"
          printf '%s\n' "$untrusted"
          if [[ "$untrusted" == *"These dependencies had their lifecycle scripts blocked during install."* ]]; then
            echo "Review package provenance before adding it to trustedDependencies."
            exit 1
          fi
      - run: bun audit --audit-level=high      # fail the PR on high/critical CVEs
      - uses: gitleaks/gitleaks-action@v2       # fail on any leaked secret
```

The lockfile step rejects mixed package managers and install drift. The lifecycle step
blocks newly introduced install scripts until their package provenance is reviewed and
the package is explicitly trusted. Typosquat and package-age checks still require
human judgment in `audit` mode; do not claim the CI gate can infer them reliably.

Pin action versions, keep `permissions` least-privilege (`contents: read`), and set the
audit threshold to the team's risk tolerance (default: fail on high/critical).

## Anti-Patterns

- **Reproducing a secret value** in a report or issue — cite `file:line` and type,
  recommend rotation.
- **Failing CI on every advisory including low/dev-only** — noise trains people to
  bypass the gate; threshold at high/critical.
- **Upgrading blindly to clear an advisory** — verify the fix version and its
  breaking changes via `stack-modernization`.
- **Adding the CI workflow without confirmation**, or with a broad `permissions`
  block (default GITHUB_TOKEN scope) — keep it `contents: read`.
