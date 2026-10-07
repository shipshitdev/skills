---
name: open-source-checker
description: "Audits a private repo once before it goes public: license, secrets in git history, private references, publish readiness. Returns a publish or block verdict."
metadata:
  version: "2.2.4"
  tags: "open-source, publishing, license, audit"
when_to_use: "open source this repo, make repo public, is this safe to publish"
---

# Open Source Checker

The publish gate. This runs **once**, on a repository that has lived its whole
life private, at the moment someone proposes making it public. Everything in a
private repo was written on the assumption nobody outside would read it —
comments, hostnames, client names, and every commit ever made. This audit finds
what that assumption left behind.

Four passes, then a verdict. The recurring commit-time guard is a different
skill — see [Related](#related).

## Contract

Inputs:

- Repository root, with full history fetched (`git fetch --all --tags`)
- Intended public license, if already chosen
- Names to treat as private: company domains, client names, internal hostnames

Outputs:

- Per-pass findings with file, line or commit, and severity
- A publish / block verdict with the blocking set enumerated
- A rotation list and a history-rewrite list, handed to `git-safety`

Creates/Modifies:

- Nothing. This audit is read-only.

External Side Effects:

- None. Remediation is delegated, not performed here.

Confirmation Required:

- Before the repository is flipped public — the verdict is advice, the flip is
  the owner's action

Delegates To:

- `git-safety` to rotate credentials, rewrite history, and install the ongoing
  commit-time guard
- `security-audit` for application-level vulnerability review

## Preflight

The audit is only as complete as the refs present locally.

```bash
git fetch --all --tags --prune
git log --all --oneline | wc -l    # commits in scope
git branch -a && git tag -l        # refs in scope
git stash list                     # stashes are not in --all
```

Ends when every remote branch and tag is present locally.

---

## Pass 1 — License and attribution

A private repo needs no license. A public one that ships without a clear one is
legally unusable by anyone who finds it, and code borrowed under one license
cannot always be re-published under another.

Check:

- **`LICENSE` file present** at the root, matching what the owner intends
- **Dependency licenses compatible** with the intended outgoing license —
  copyleft (GPL, AGPL) dependencies constrain a permissive release
- **Vendored and copy-pasted code attributed** — snippets lifted from Stack
  Overflow, blog posts, or another repo carry their origin's terms
- **Copyright headers** consistent, and naming the right entity
- **Employer ownership** settled if the code was written on company time

```bash
ls LICENSE* COPYING* 2>/dev/null
bunx license-checker --summary                      # JS dependency licenses
grep -rniE 'copyright|\(c\) [0-9]{4}|SPDX-License' --include='*.*' -l . | head -30
grep -rniE 'adapted from|based on|taken from|source: http' --include='*.*' . | head -30
```

Ends when the outgoing license is named, every dependency license is compatible
with it, and every borrowed block is attributed or removed.

---

## Pass 2 — Secrets in history

Deleting a secret from the working tree leaves it in every commit that ever held
it. Publishing the repo publishes those commits.

Scan every ref, not just `HEAD`:

```bash
# Automated sweep across all history — start here
gitleaks detect --source . --verbose
trufflehog git file://. --only-verified

# Every file that ever existed
git log --all --pretty=format: --name-only --diff-filter=A | sort -u \
  | grep -iE '\.(env|pem|key|secret)$|credentials|secrets\.|id_rsa'

# Files deleted from the tree but alive in history
git log --all --pretty=format: --name-only --diff-filter=D | sort -u \
  | grep -iE '\.(env|pem|key|secret)$|credentials'

# Content search across every commit
git log -p --all -S 'API_KEY' --source -- ':(exclude)*.lock'
git log -p --all -G 'AKIA[0-9A-Z]{16}' --source
```

Also sweep the places `--all` misses: stashes, merge commits, and every tag.
Commands in `references/full-guide.md` §3.

Every hit is a **rotation item first** and a history-rewrite item second.
Cleaning history does not un-leak a credential that was ever pushed.

Ends when gitleaks and truffleHog both return clean across full history, and
every earlier hit has a confirmed rotation.

---

## Pass 3 — Private references

The pass with no tooling, and the one that leaks the most. These are not
credentials; they are facts about the company that only made sense inside it.

| Category | What to look for |
|----------|------------------|
| Internal hosts | `*.internal`, `*.corp`, `*.local`, VPN hostnames, RFC1918 IPs |
| Internal services | Jira/Linear ticket URLs, internal wikis, admin dashboards |
| People | Employee emails, personal emails, names in TODO and FIXME comments |
| Customers | Client names, logos, contract terms, customer data in fixtures |
| Infrastructure | Account IDs, bucket names, cluster names, staging URLs |
| Commercial | Pricing logic, unreleased product names, internal roadmap notes |
| Commit metadata | Author emails on every commit — these become public too |

```bash
# Internal domains and hosts (substitute your own)
grep -rniE '@(yourcompany|internal|corp)\.(com|net|local)' . | grep -v node_modules
grep -rniE '\b(10|192\.168|172\.(1[6-9]|2[0-9]|3[01]))\.[0-9]+\.[0-9]+\b' . | grep -v node_modules

# People and intent left in comments
grep -rniE '(TODO|FIXME|HACK|XXX|NOTE)[:( ].*(ask|per|@[a-z]+)' --include='*.*' . | head -40

# Author identities that ship with the history
git log --all --format='%ae' | sort -u
git log --all --format='%an <%ae>' | sort -u | head -30
```

Judge each hit by one question: **would a stranger reading this learn something
the company would not say publicly?** A staging URL is a finding. A public docs
link is not.

Ends when every category has been searched and each hit is redacted, replaced
with a neutral placeholder, or explicitly accepted by the owner.

---

## Pass 4 — Publication readiness

What a stranger finds in the first thirty seconds:

- **README** written for an outsider — what it is, how to run it, no "ask the
  team in #eng" instructions
- **`.env.example`** present and complete, so setup is possible without internal
  access
- **Docs** free of links to internal wikis, dashboards, and runbooks
- **Issue and PR templates** that do not route to internal processes
- **CI config** referencing only secrets a fork could plausibly supply, and no
  internal registry or runner
- **Test fixtures** carrying synthetic data, not production exports
- **Repository settings** — an existing `.github/` config may expose internal
  team names in `CODEOWNERS`

```bash
ls README* .env.example .github/ 2>/dev/null
grep -rniE 'internal|confidential|do not distribute|proprietary' README* docs/ 2>/dev/null
cat .github/CODEOWNERS 2>/dev/null
```

Ends when a reader with no internal access can install, run, and contribute from
what is in the repository.

---

## Verdict

Report one of two outcomes. No middle state — "mostly clean" publishes secrets.

**BLOCK** — enumerate every blocking finding:

```
BLOCK — 3 blockers

License   No LICENSE file; two AGPL dependencies conflict with intended MIT
History   AWS key in commit a1b2c3d (deleted in e4f5g6h, still in history)
Private   Client name "Acme Corp" in 14 files and 3 commit messages

Rotate now:      AWS key AKIA…  (leak precedes any rewrite)
Then hand to:    git-safety clean — strip .env from all refs, force-push
Re-run this audit after the rewrite; commit hashes will have changed.
```

**PUBLISH** — state what was verified, so the verdict is auditable:

```
PUBLISH

License   MIT at root; 214 deps all permissive; 2 adapted blocks attributed
History   gitleaks + truffleHog clean across 1,847 commits, 12 branches, 40 tags
Private   No internal hosts, customer names, or employee emails outside git authorship
Ready     README, .env.example, CI runs on a fork without internal secrets

Note: 4 distinct author emails remain in commit history and will be public.
Next: install the ongoing commit-time guard — git-safety prevent
```

A rewrite invalidates every commit hash in the findings, so re-run passes 2 and
3 after `git-safety` finishes.

## Related

- `git-safety` — the recurring guard for a repository already in daily use:
  blocks secrets from entering the next commit, gates force-pushes and history
  rewrites, and installs ignore rules and pre-commit hooks. It also performs the
  rotation and history rewrite this audit hands off. Run it at every commit;
  run this audit once, at the publish decision.
- `security-audit` — application-level vulnerability review of the code itself.

---

**Full credential-pattern catalog, all-refs history commands (stashes, merges,
tags, branches), license-compatibility matrix, private-reference search recipes,
and the report template:** `references/full-guide.md`
