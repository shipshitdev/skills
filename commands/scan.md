---
description: "Security audit of the app and API, or of the dependency supply chain."
argument-hint: "[deps [ci]]"
disable-model-invocation: true
---

# Scan - Run a Security Audit

Run a structured security audit of the current project — app and API
vulnerabilities, auth and session handling, input validation, configuration
hardening — or focus on the dependency supply chain.

## Usage

```bash
/scan              # full security audit of the app/API (default)
/scan deps         # dependency supply chain: CVEs, secrets about to leak, lockfile integrity
/scan deps ci      # wire the dependency + secrets checks into CI as a merge gate
```

`/scan help` prints this Usage block and stops without running anything.

## Workflow

- **default** — the `security-audit` skill: scope and reconnaissance, baseline
  review, manual web app testing, API security review, hardening review, and a
  severity-ordered findings report. Read-only; it audits and reports, it does
  not edit code.
- **`deps`** — the `dependency-audit` skill in `audit` mode: known CVEs in
  installed packages, secrets scanning, and lockfile/provenance integrity.
- **`deps ci`** — the `dependency-audit` skill in `ci` mode: adds the GitHub
  Actions gate workflow, behind that skill's own confirmation.

1. **Parse the argument** (`deps` / `deps ci` / empty = full audit). Unknown
   argument → print Usage, do not guess.
2. **Route** to the skill and defer to its scope, safety, and confirmation
   rules — the audit confirms target and boundaries before active probing.

## Gates

- The default audit and `deps` are read-only reports. Only `deps ci` writes
  files, behind `dependency-audit`'s confirmation gate.
- No destructive checks, fuzzing, or DoS-style traffic — the `security-audit`
  skill's safety rules apply unchanged.

## Related

- `/review --deep` runs the multi-pass code review (which includes a security
  pass on the diff); `/scan` audits the running project and its supply chain.
- The `security-expert` skill is the implementation persona — use it to *build*
  the fixes this audit surfaces.
