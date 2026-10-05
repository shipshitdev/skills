# Git Safety — Full Guide

Reference material for the two recurring guards: what must never enter a commit,
and what must never run without confirmation.

Scope note: this guide covers the **ongoing** moment — commit time, push time,
and leak response in a repository you already work in. The one-time audit of a
whole repository before publication (license, attribution, full-history sweep,
internal references) belongs to the `open-source-checker` skill.

---

## 1. Sensitive File Patterns

Filenames that should never be staged:

```
# Environment files
.env
.env.*
*.env
.envrc

# Credential files
credentials.json
service-account*.json
*-credentials.json
*.pem
*.key
*.p12
*.pfx
id_rsa*
id_ed25519*
id_ecdsa*

# Cloud provider configs
.aws/credentials
.aws/config
.gcp/credentials.json
.azure/credentials
kubeconfig
.kube/config

# API/secret files
secrets.yml
secrets.json
*.secret
api_keys.*
auth.json

# Package manager tokens
.npmrc
.pypirc
.gem/credentials
.docker/config.json

# Other
.htpasswd
.netrc
*.log          # may contain secrets
*.sql          # may contain passwords or production data
database.yml   # may contain passwords
```

Allowlist the safe siblings explicitly: `.env.example`, `.env.template`,
`schema.sql`, `migrations/*.sql`.

---

## 2. Staged Guard Commands

### 2.1 What is about to be committed

```bash
# Names only
git diff --cached --name-only

# With status letters (A/M/D)
git diff --cached --name-status

# Full added content, no context lines
git diff --cached -U0
```

### 2.2 Sensitive filenames in the staged set

```bash
git diff --cached --name-only | grep -iE \
  '(^|/)\.env($|\.)|\.(pem|key|p12|pfx|secret)$|credentials|service-account|id_rsa|id_ed25519|\.npmrc$|kubeconfig'
```

### 2.3 Secret-shaped values in added lines

Scan only lines the commit adds — existing lines are history's problem, not this
commit's.

```bash
# Generic assignment shapes
git diff --cached -U0 | grep -E '^\+' | grep -iE \
  '(api[_-]?key|apikey|secret[_-]?key|client[_-]?secret|access[_-]?token|auth[_-]?token|password|passwd)[^a-z]{0,4}[=:][^=:]{8,}'

# Private key material
git diff --cached -U0 | grep -E '^\+' | grep -E 'BEGIN (RSA|EC|OPENSSH|PGP)? ?PRIVATE KEY'

# Vendor key prefixes (extend for the providers you use)
git diff --cached -U0 | grep -E '^\+' | grep -E \
  'AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{36}|xox[baprs]-[0-9A-Za-z-]{10,}|AIza[0-9A-Za-z_-]{35}'

# Credentials embedded in a connection URI (scheme split so this file does not
# itself contain a URI-shaped literal that trips downstream secret scanners)
git diff --cached -U0 | grep -E '^\+' | grep -E '[a-z]+:'"//"'[^:@/]+:[^:@/]+@'
```

### 2.4 Untracked files sitting in the tree

Not staged today, easy to `git add -A` tomorrow:

```bash
git status --porcelain --untracked-files=all \
  | grep -E '^\?\?' \
  | grep -iE '\.env|\.pem$|\.key$|credentials|secrets\.'
```

### 2.5 Ignore-rule coverage

```bash
for pattern in ".env" ".env.*" "*.pem" "*.key" "credentials.json" "secrets.*"; do
  grep -q -- "$pattern" .gitignore 2>/dev/null || echo "Missing from .gitignore: $pattern"
done
```

### 2.6 Verdict format

```
## Staged Guard — <branch>, <n> files staged

BLOCK  src/config.ts:42        live-looking API key in an added line
BLOCK  credentials.json        forbidden filename, newly added
ASK    tests/fixtures/key.pem  private key — confirm it is a throwaway test key
ALLOW  .env.example            placeholder values only

Untracked but present: .env.local (ignored — OK)
.gitignore gaps: *.pem, credentials.json

Next: unstage the two BLOCK paths, then rerun.
```

---

## 3. Destructive Operation Gate

### 3.1 Blast radius by command

| Command | Rewrites | Discards | Recoverable via |
|---------|----------|----------|-----------------|
| `git push --force` | Remote refs | Remote commits others hold | Their local reflog only |
| `git push --force-with-lease` | Remote refs | Same, but aborts on unseen updates | Preferred form |
| `git filter-repo` / `bfg` | All commit hashes | Nothing, if mirrored first | Mirror backup |
| `git reset --hard` | Index and tree | Uncommitted work | `git stash` beforehand |
| `git clean -fdx` | Tree | Untracked files, local `.env` | Nothing |
| `git checkout -- <path>` | Tree | Uncommitted edits to that path | Nothing |
| `git branch -D` | Local ref | Unmerged commits | Local reflog, ~90 days |
| `git push origin --delete` | Remote ref | Unmerged commits on the remote | Nothing reliable |
| `git rebase` on a pushed branch | Local history | Published commit identity | Force-push follows |

### 3.2 Backup commands

```bash
# Before any history rewrite
git clone --mirror . ../repo-backup-$(date +%Y%m%d)

# Before reset --hard or clean -fdx
git stash push --include-untracked -m "pre-destructive-op $(date +%FT%T)"

# Before deleting a branch, keep a pointer
git tag archive/<branch-name> <branch-name>
```

### 3.3 Reversible alternatives

| Instead of | Use | Why |
|-----------|-----|-----|
| `push --force` | `push --force-with-lease` | Aborts if the remote moved since your last fetch |
| `reset --hard` on a pushed branch | `git revert <sha>` | Adds a commit; collaborators keep their history |
| `checkout -- <path>` | `git stash push <path>` | Recoverable from the stash list |
| `clean -fdx` | `git clean -nd` first | Dry run lists what would be deleted |
| `branch -D` | `git branch -d` | Refuses when the branch has unmerged commits |

### 3.4 Dry runs

```bash
git clean -nd                          # list what clean would remove
git push --force-with-lease --dry-run  # show refs that would move
git filter-repo --path .env --invert-paths --dry-run
```

---

## 4. Prevention Setup

### 4.1 `.gitignore` template

```gitignore
# Environment files
.env
.env.*
*.env
.envrc
!.env.example
!.env.template

# Credentials and secrets
credentials.json
*-credentials.json
service-account*.json
secrets.yml
secrets.json
*.secret
api_keys.*
auth.json

# Private keys
*.pem
*.key
*.p12
*.pfx
id_rsa
id_rsa.*
id_ed25519
id_ed25519.*
id_ecdsa
id_ecdsa.*

# Cloud provider configs
.aws/
.gcp/
.azure/
kubeconfig
.kube/config

# Package manager auth
.npmrc
.pypirc
.gem/credentials
.docker/config.json

# Database
*.sql
!schema.sql
!migrations/*.sql

# Logs (may contain secrets)
*.log
logs/

# OS files
.DS_Store
Thumbs.db

# IDE with potential secrets
.idea/
.vscode/settings.json
```

### 4.2 Pre-commit hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Block sensitive files and secret-shaped values from entering a commit.

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

FORBIDDEN_FILES=(
  "(^|/)\.env($|\.)"
  "credentials\.json"
  "service-account.*\.json"
  "secrets\.(yml|json)"
  "\.(pem|key|p12|pfx)$"
  "id_rsa"
  "^\.npmrc$"
)

SECRET_PATTERNS=(
  "BEGIN (RSA|EC|OPENSSH|PGP)? ?PRIVATE KEY"
  "(api[_-]?key|apikey)[^a-z]{0,4}[=:][^=:]{8,}"
  "(secret[_-]?key|client[_-]?secret)[^a-z]{0,4}[=:][^=:]{8,}"
  "password[^a-z]{0,4}[=:]['\"][^'\"]{6,}['\"]"
  "AKIA[0-9A-Z]{16}"
  "gh[pousr]_[A-Za-z0-9]{36}"
)

ERRORS=0

for pattern in "${FORBIDDEN_FILES[@]}"; do
  files=$(git diff --cached --name-only | grep -E "$pattern" || true)
  if [ -n "$files" ]; then
    echo -e "${RED}BLOCKED: forbidden file matching '$pattern':${NC}"
    echo "$files"
    ERRORS=$((ERRORS + 1))
  fi
done

for pattern in "${SECRET_PATTERNS[@]}"; do
  matches=$(git diff --cached -U0 | grep -E "^\+" | grep -iE "$pattern" || true)
  if [ -n "$matches" ]; then
    echo -e "${YELLOW}BLOCKED: possible secret matching '$pattern':${NC}"
    echo "$matches" | head -5
    ERRORS=$((ERRORS + 1))
  fi
done

if [ $ERRORS -gt 0 ]; then
  echo ""
  echo -e "${RED}Commit blocked. Rotate anything real before retrying.${NC}"
  echo "False positive? Confirm the value is fake, then: git commit --no-verify"
  exit 1
fi

exit 0
```

Make it executable and prove it bites:

```bash
chmod +x .git/hooks/pre-commit

# Verification: this must be rejected
printf 'API_KEY=abcd1234efgh5678\n' > .env.hooktest  # gitleaks:allow (synthetic fixture)
git add -f .env.hooktest && git commit -m "hook test"   # expect: BLOCKED
git reset && rm .env.hooktest
```

### 4.3 Shared hooks via pre-commit framework

`.git/hooks/` is not committed, so teammates get nothing. Use a tracked config:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

```bash
pip install pre-commit
pre-commit install
```

### 4.4 `git secrets`

```bash
brew install git-secrets
git secrets --install
git secrets --register-aws
git secrets --add 'ANTHROPIC_API_KEY.*=.*sk-ant-'
git secrets --add 'OPENAI_API_KEY.*=.*sk-'
```

### 4.5 `.env.example` template

```bash
# .env.example — safe template. Copy to .env and fill in real values.
# .env itself is ignored and must never be staged.

ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql:"//"USER:PASSWORD@HOST:5432/DBNAME
JWT_SECRET=generate_a_secure_random_string
SESSION_SECRET=generate_another_secure_string
```

### 4.6 Server-side backstops

- **GitHub** — enable secret scanning and push protection in repository
  settings; store CI values in Actions secrets.
- **GitLab** — enable the Secret Detection CI/CD component; use CI/CD variables.
- **Vercel / Netlify** — set environment variables in the dashboard, never in
  the repository.

Push protection rejects the push before the value reaches the remote, which is
the only control that prevents exposure rather than reacting to it.

### 4.7 CI secret scanning

A hook only runs on machines that installed it. CI catches what slipped past —
including commits pushed with `--no-verify`.

```yaml
# .github/workflows/secret-scan.yml
name: Secret Scan
on: [push, pull_request]

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0        # full history, or the scan sees one commit
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

```yaml
# .gitlab-ci.yml
include:
  - template: Jobs/Secret-Detection.gitlab-ci.yml

secret_detection:
  variables:
    SECRET_DETECTION_HISTORIC_SCAN: "true"
```

`fetch-depth: 0` is the line that matters. A shallow checkout scans only the tip
commit and reports clean on a repository full of leaked keys.

---

## 5. History Rewrite (post-rotation only)

Rewriting is cleanup. The credential must already be rotated.

### 5.1 Prerequisites

```bash
which git-filter-repo || pip install git-filter-repo   # or: brew install git-filter-repo
which bfg            || brew install bfg               # Java alternative
```

Before starting: every collaborator has pushed, a mirror backup exists, and the
operator has confirmed the force-push.

### 5.2 git-filter-repo

```bash
git clone --mirror . ../repo-backup-$(date +%Y%m%d)

# Remove one path from every commit
git filter-repo --path .env --invert-paths

# Several paths
git filter-repo --path .env --path credentials.json --path secrets.yml --invert-paths

# By glob
git filter-repo --path-glob '*.pem' --invert-paths

# Redact a value while keeping the file
git filter-repo --replace-text expressions.txt
# expressions.txt:
#   literal:<the-rotated-value>==>[REDACTED]
#   regex:AKIA[0-9A-Z]{16}==>[REDACTED_AWS_KEY]
```

### 5.3 BFG alternative

```bash
bfg --delete-files .env
bfg --delete-files '*.pem'
bfg --replace-text passwords.txt
git reflog expire --expire=now --all && git gc --prune=now --aggressive
```

### 5.4 Force-push and verify

```bash
git push origin --force --all
git push origin --force --tags

git log --all --full-history -- .env       # expect empty
git log -p --all -S '<rotated-value>'      # expect empty
```

### 5.5 Collaborator recovery

```bash
# Safest
rm -rf <clone> && git clone <remote-url>

# Advanced, for a clean local branch only
git fetch origin && git rebase origin/main
```

Open pull requests and forks keep the old history. Close and reopen PRs from
re-cloned branches; ask fork owners to delete or re-fork.

---

## 6. Emergency Response Checklist

Within minutes:

- [ ] Rotate the credential at the issuing provider
- [ ] Confirm the old value is rejected
- [ ] Revoke active sessions or tokens derived from it

Within hours:

- [ ] Read provider access logs for use of the old value
- [ ] Identify every ref, fork, and CI log holding the value
- [ ] Check whether the repository is public or was ever public

Within a day:

- [ ] Rewrite history (section 5)
- [ ] Force-push through the operation gate
- [ ] Notify collaborators to re-clone
- [ ] Install ignore rules and hooks (section 4)
- [ ] Record what leaked, when, how, and what was rotated

---

## 7. Quick Reference

```bash
# === STAGED GUARD ===
git diff --cached --name-only
git diff --cached -U0 | grep -E '^\+' | grep -iE '(api[_-]?key|password|secret|token)[^a-z]{0,4}[=:]'

# === OPERATION GUARD ===
git clean -nd                                    # dry run
git stash push --include-untracked               # before reset --hard
git clone --mirror . ../repo-backup-$(date +%Y%m%d)

# === PREVENTION ===
chmod +x .git/hooks/pre-commit
pre-commit install
git secrets --install && git secrets --register-aws

# === REWRITE (post-rotation) ===
git filter-repo --path .env --invert-paths
git push origin --force --all
```

For the pre-publication audit of a whole repository — license, attribution,
full-history secret sweep, internal hostnames and employee references — use the
`open-source-checker` skill instead.
