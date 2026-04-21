# Open Source Security Checker - Full Guide

Comprehensive guide for detecting and removing sensitive information from codebases before open sourcing.

---

## 1. What to Check

### 1.1 API Keys and Tokens

API keys are the most common leaked secret. Check for:

- **OpenAI**: `sk-...` (48 characters)
- **Anthropic**: `sk-ant-...`
- **Stripe**: `sk_live_...`, `sk_test_...`, `pk_live_...`, `pk_test_...`
- **AWS**: Access Key ID (`AKIA...`), Secret Access Key
- **GitHub**: `ghp_...`, `gho_...`, `ghu_...`, `ghs_...`, `ghr_...`
- **Google**: `AIza...` (39 characters)
- **Slack**: `xoxb-...`, `xoxp-...`, `xoxa-...`
- **Twilio**: Account SID (`AC...`), Auth Token
- **SendGrid**: `SG....`
- **Firebase**: Various patterns in config objects
- **Vercel**: `vercel_...`
- **npm**: `npm_...`

### 1.2 Database Credentials

- Connection strings with embedded passwords
- MongoDB URIs: `mongodb+srv://user:password@...`
- PostgreSQL: `postgresql://user:password@host:port/db`
- MySQL: `mysql://user:password@host:port/db`
- Redis: `redis://:password@host:port`

### 1.3 Private Keys and Certificates

```
# File extensions to check
*.pem
*.key
*.p12
*.pfx
*.cer
*.crt
id_rsa
id_rsa.pub
id_ed25519
id_ecdsa
*.keystore
*.jks
```

### 1.4 Personal Information

- Email addresses (especially internal/company emails)
- Phone numbers
- Physical addresses
- Names in comments (developer names, client names)
- IP addresses (especially internal network IPs)
- License keys

### 1.5 Environment Files

```
.env
.env.local
.env.development
.env.production
.env.staging
.env.test
.envrc
*.env
.env.*
```

### 1.6 Configuration Files

```
# Cloud provider configs
.aws/credentials
.aws/config
.gcp/credentials.json
.azure/credentials
kubeconfig
.kube/config

# Package manager auth
.npmrc (with auth tokens)
.yarnrc.yml (with auth)
.pypirc
.gem/credentials
.docker/config.json

# Application configs
config/secrets.yml
config/credentials.yml.enc
database.yml (check for passwords)
secrets.json
api_keys.json
auth.json
```

### 1.7 Code Comments

Developers often leave sensitive information in comments:

```bash
# Search for common patterns in comments
grep -rn "TODO.*password" --include="*.ts" --include="*.js"
grep -rn "FIXME.*key" --include="*.ts" --include="*.js"
grep -rn "// .*secret" --include="*.ts" --include="*.js"
grep -rn "password.*=" --include="*.ts" --include="*.js"
```

### 1.8 Git History

**CRITICAL**: Deleted files and previous commits still contain secrets.

```bash
# Files deleted from repo but in history
git log --all --full-history --diff-filter=D -- "*.env" ".env" "secrets.*"

# Commits that modified sensitive files
git log --all --oneline -- "*.env" "*.pem" "*.key" "credentials.*"
```

---

## 2. Common Patterns to Detect

### 2.1 API Key Patterns

```regex
# Generic API key patterns
[aA][pP][iI][_-]?[kK][eE][yY].*['\"][a-zA-Z0-9]{16,}['\"]
[aA][pP][iI][_-]?[sS][eE][cC][rR][eE][tT].*['\"][a-zA-Z0-9]{16,}['\"]

# AWS Access Key ID
AKIA[0-9A-Z]{16}

# AWS Secret Access Key
[a-zA-Z0-9+/]{40}

# GitHub Token
gh[pousr]_[A-Za-z0-9_]{36,}

# Generic Secret Key
[sS][eE][cC][rR][eE][tT][_-]?[kK][eE][yY].*['\"][a-zA-Z0-9]{16,}['\"]

# Bearer Token
[bB][eE][aA][rR][eE][rR][\s]+[a-zA-Z0-9\-_\.]{20,}

# JWT Token
eyJ[a-zA-Z0-9\-_]+\.eyJ[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+

# OpenAI API Key
sk-[a-zA-Z0-9]{48}

# Anthropic API Key
sk-ant-[a-zA-Z0-9\-_]{40,}

# Stripe API Key
sk_(live|test)_[a-zA-Z0-9]{24,}
pk_(live|test)_[a-zA-Z0-9]{24,}

# Slack Token
xox[baprs]-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{24}

# Google API Key
AIza[0-9A-Za-z\-_]{35}

# SendGrid API Key
SG\.[a-zA-Z0-9]{22}\.[a-zA-Z0-9\-_]{43}
```

### 2.2 Password Patterns

```regex
# Password assignments
[pP][aA][sS][sS][wW][oO][rR][dD].*[=:].*['\"][^'\"]{4,}['\"]

# DB Password
[dD][bB][_-]?[pP][aA][sS][sS][wW][oO][rR][dD].*[=:].*['\"][^'\"]+['\"]

# Admin Password
[aA][dD][mM][iI][nN][_-]?[pP][aA][sS][sS].*[=:].*['\"][^'\"]+['\"]

# Generic password in URL
://[^:]+:[^@]+@
```

### 2.3 Connection String Patterns

```regex
# MongoDB
mongodb(\+srv)?://[^:]+:[^@]+@[^/]+

# PostgreSQL
postgres(ql)?://[^:]+:[^@]+@[^/]+

# MySQL
mysql://[^:]+:[^@]+@[^/]+

# Redis
redis://:[^@]+@[^/]+

# Generic database URL
DATABASE_URL.*[=:].*['\"][^'\"]+['\"]
```

### 2.4 Email Patterns

```regex
# Email addresses
[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}

# Specific internal domains (customize for your org)
[a-zA-Z0-9._%+-]+@(company|internal)\.com
```

### 2.5 Private Key Patterns

```regex
# RSA Private Key
-----BEGIN RSA PRIVATE KEY-----

# EC Private Key
-----BEGIN EC PRIVATE KEY-----

# Generic Private Key
-----BEGIN PRIVATE KEY-----

# OpenSSH Private Key
-----BEGIN OPENSSH PRIVATE KEY-----

# PGP Private Key
-----BEGIN PGP PRIVATE KEY BLOCK-----
```

---

## 3. Scanning Workflow

### 3.1 File System Scan

**Step 1: Find sensitive file types**

```bash
# Find all potentially sensitive files
find . -type f \( \
  -name ".env" -o \
  -name ".env.*" -o \
  -name "*.env" -o \
  -name "credentials.json" -o \
  -name "service-account*.json" -o \
  -name "*.pem" -o \
  -name "*.key" -o \
  -name "*.p12" -o \
  -name "*.pfx" -o \
  -name "id_rsa*" -o \
  -name "id_ed25519*" -o \
  -name "id_ecdsa*" -o \
  -name "secrets.*" -o \
  -name "*.secret" -o \
  -name ".npmrc" -o \
  -name ".pypirc" -o \
  -name "kubeconfig" -o \
  -name ".htpasswd" -o \
  -name ".netrc" \
\) 2>/dev/null | grep -v node_modules | grep -v .git | grep -v vendor
```

**Step 2: Check if sensitive files are tracked**

```bash
# Check git status of each found file
for file in $(find . -name ".env*" -o -name "*.pem" -o -name "*.key" 2>/dev/null | grep -v node_modules); do
  if git ls-files --error-unmatch "$file" 2>/dev/null; then
    echo "TRACKED (DANGER): $file"
  else
    echo "Untracked (safe): $file"
  fi
done
```

### 3.2 Code Pattern Analysis

**Step 1: Search for hardcoded secrets**

```bash
# Search for API key patterns
git grep -E "(api[_-]?key|apikey|api[_-]?secret).*[=:].*['\"][a-zA-Z0-9]" -- '*.ts' '*.js' '*.py' '*.go' '*.java' '*.rb'

# Search for password patterns
git grep -E "(password|passwd|pwd).*[=:].*['\"][^'\"]+['\"]" -- '*.ts' '*.js' '*.py' '*.go' '*.java' '*.rb' ':!*.lock' ':!package-lock.json'

# Search for secret patterns
git grep -E "(secret|token|auth).*[=:].*['\"][a-zA-Z0-9]" -- '*.ts' '*.js' '*.py' '*.go' '*.java' '*.rb'

# Search for private keys
git grep -E "-----BEGIN.*PRIVATE KEY-----" -- '*'
```

**Step 2: Search for specific provider patterns**

```bash
# AWS
git grep -E "AKIA[0-9A-Z]{16}" -- '*'

# GitHub
git grep -E "gh[pousr]_[A-Za-z0-9_]{36,}" -- '*'

# OpenAI
git grep -E "sk-[a-zA-Z0-9]{48}" -- '*'

# Stripe
git grep -E "sk_(live|test)_[a-zA-Z0-9]{24,}" -- '*'
```

### 3.3 Content Analysis

**Automated scanning with gitleaks**

```bash
# Install gitleaks
brew install gitleaks

# Scan current directory
gitleaks detect --source . --verbose

# Scan with report
gitleaks detect --source . --report-format json --report-path ./gitleaks-report.json
```

**Automated scanning with truffleHog**

```bash
# Install truffleHog
pip install trufflehog

# Scan filesystem
trufflehog filesystem . --only-verified

# Scan with JSON output
trufflehog filesystem . --json > trufflehog-report.json
```

### 3.4 Git History Check

See dedicated section below.

---

## 4. Git History Scanning (CRITICAL)

This is the most commonly overlooked step. Secrets removed from current files remain in git history indefinitely.

### 4.1 Essential Commands

**Find all files ever committed**

```bash
# List all files that have ever existed in the repo
git log --all --pretty=format: --name-only --diff-filter=A | sort -u
```

**Search for sensitive filenames in history**

```bash
# Find when sensitive files were added
git log --all --full-history --diff-filter=A -- \
  "*.env" ".env" ".env.*" \
  "credentials.json" "service-account*.json" \
  "*.pem" "*.key" "id_rsa*" \
  "secrets.*" ".npmrc" "*.secret" \
  --name-only --oneline

# More detailed with dates
git log --all --full-history --diff-filter=A \
  --pretty=format:"%h %ad %s" --date=short -- \
  "*.env" "credentials.json" "*.pem" "*.key"
```

**Search for secret patterns in git history**

```bash
# Search commits that added/removed content matching pattern
git log -p --all -S 'API_KEY' --source -- ':(exclude)*.lock'

# Search for specific secret value (if known)
git log -p --all -S 'sk-ant-abc123...' --source

# Search using regex
git log -p --all -G 'AKIA[0-9A-Z]{16}' --source
```

**View content of deleted files**

```bash
# Find when a file was deleted
git log --all --full-history -- path/to/deleted/file.env

# View the file content at a specific commit
git show <commit-hash>:path/to/deleted/file.env

# View the last version before deletion
git log --all --full-history --diff-filter=D -- path/to/file.env
git show <commit-before-deletion>:path/to/file.env
```

### 4.2 Automated Tools for History Scanning

**gitleaks (Recommended)**

```bash
# Full history scan
gitleaks detect --source . --verbose

# Scan specific commit range
gitleaks detect --source . --log-opts="HEAD~50..HEAD"

# Generate baseline (for existing repos)
gitleaks detect --source . --baseline-path .gitleaks-baseline.json

# Custom config
gitleaks detect --source . --config .gitleaks.toml
```

**truffleHog**

```bash
# Scan git history
trufflehog git file://. --only-verified

# Scan remote repository
trufflehog git https://github.com/org/repo.git

# Include unverified findings
trufflehog git file://. --include-detectors all
```

**git-secrets (AWS-focused)**

```bash
# Install
brew install git-secrets

# Register AWS patterns
git secrets --register-aws

# Scan history
git secrets --scan-history

# Scan specific file
git secrets --scan path/to/file
```

### 4.3 Checking Deleted Files

```bash
# List all deleted files in history
git log --all --pretty=format: --name-only --diff-filter=D | sort -u

# Filter for sensitive patterns
git log --all --pretty=format: --name-only --diff-filter=D | sort -u | grep -iE '\.(env|pem|key|secret)$|credentials|secrets\.'

# For each deleted sensitive file, check its content
for file in $(git log --all --pretty=format: --name-only --diff-filter=D | sort -u | grep -iE '\.env$'); do
  echo "=== $file ==="
  git log --all --full-history -1 --format="%H" -- "$file" | xargs -I {} git show {}^:"$file" 2>/dev/null || echo "Could not retrieve"
done
```

### 4.4 Checking Merge Commits

Merge commits can contain secrets that weren't in either branch:

```bash
# List all merge commits
git log --all --merges --oneline

# Check a specific merge for changes
git show --stat <merge-commit-hash>

# Diff merge against its parents
git diff <merge-commit>^1..<merge-commit>
git diff <merge-commit>^2..<merge-commit>
```

### 4.5 Checking Stashes

Stashes are often forgotten and may contain secrets:

```bash
# List all stashes
git stash list

# Show stash content
git stash show -p stash@{0}

# Check all stashes for sensitive patterns
for i in $(seq 0 $(git stash list | wc -l)); do
  echo "=== Stash $i ==="
  git stash show -p stash@{$i} 2>/dev/null | grep -iE "(api.?key|password|secret|token)" || true
done
```

### 4.6 Checking All Branches

```bash
# List all branches (local and remote)
git branch -a

# Scan each branch for sensitive files
for branch in $(git branch -a | sed 's/^[\* ]*//' | grep -v HEAD); do
  echo "=== Branch: $branch ==="
  git ls-tree -r --name-only "$branch" 2>/dev/null | grep -iE '\.(env|pem|key)$' || true
done
```

### 4.7 Checking Tags

```bash
# List all tags
git tag -l

# Check files in each tag
for tag in $(git tag -l); do
  echo "=== Tag: $tag ==="
  git ls-tree -r --name-only "$tag" 2>/dev/null | grep -iE '\.(env|pem|key)$' || true
done
```

---

## 5. Cleaning Git History

**WARNING**: Before cleaning history:

1. **Rotate all leaked credentials immediately** - cleaning history does NOT make secrets safe
2. Create a backup of the repository
3. Notify all collaborators
4. Understand that this rewrites history and requires force push

### 5.1 Using git-filter-repo (Recommended)

**Installation**

```bash
# pip
pip install git-filter-repo

# Homebrew
brew install git-filter-repo

# Verify installation
git filter-repo --version
```

**Remove specific files**

```bash
# Create backup first
git clone --mirror . ../repo-backup-$(date +%Y%m%d)

# Remove a single file
git filter-repo --path .env --invert-paths

# Remove multiple files
git filter-repo --path .env --path .env.local --path credentials.json --invert-paths

# Remove by pattern (glob)
git filter-repo --path-glob '*.env' --invert-paths
git filter-repo --path-glob '*.pem' --invert-paths

# Remove by regex
git filter-repo --path-regex '.*\.env(\..*)?' --invert-paths
```

**Remove content by pattern**

```bash
# Replace text in all files (useful for removing specific secrets)
git filter-repo --replace-text expressions.txt

# Where expressions.txt contains:
# literal:sk-ant-api123abc==>[REDACTED]
# regex:AKIA[0-9A-Z]{16}==>[REDACTED_AWS_KEY]
```

**Remove entire directories**

```bash
git filter-repo --path secrets/ --invert-paths
git filter-repo --path config/credentials/ --invert-paths
```

### 5.2 Using BFG Repo-Cleaner

**Installation**

```bash
# Homebrew
brew install bfg

# Or download JAR
curl -L -o bfg.jar https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar
```

**Remove files by name**

```bash
# Clone a fresh mirror
git clone --mirror git@github.com:org/repo.git

cd repo.git

# Remove files by name
bfg --delete-files .env
bfg --delete-files "*.pem"
bfg --delete-files credentials.json

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

**Remove content by pattern**

```bash
# Create a file with patterns to remove
echo "sk-ant-api123abc" > passwords.txt
echo "AKIAIOSFODNN7EXAMPLE" >> passwords.txt

# Replace matching content
bfg --replace-text passwords.txt

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

**Remove files by size**

```bash
# Remove files larger than 100M
bfg --strip-blobs-bigger-than 100M
```

### 5.3 Fresh Repository Approach

When history is too compromised, start fresh:

```bash
# Create new repo with clean history
mkdir new-repo
cd new-repo
git init

# Copy current files (excluding secrets)
rsync -av --exclude='.git' --exclude='.env*' --exclude='*.pem' --exclude='*.key' ../old-repo/ .

# Create initial commit
git add .
git commit -m "Initial commit (clean history)"

# Push to new remote (or rename old one)
git remote add origin git@github.com:org/new-repo.git
git push -u origin main
```

### 5.4 Force Push After Cleaning

```bash
# After cleaning with git-filter-repo or BFG
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push ALL branches
git push origin --force --all

# Force push ALL tags
git push origin --force --tags
```

### 5.5 Notify Collaborators

All collaborators must re-clone or rebase:

```bash
# Option 1: Re-clone (safest)
rm -rf local-repo
git clone git@github.com:org/repo.git

# Option 2: Fetch and reset (advanced)
git fetch origin
git reset --hard origin/main
git clean -fd
```

### 5.6 Verify Cleanup

```bash
# Verify file is gone from all history
git log --all --full-history -- .env
# Should return empty

# Verify content pattern is gone
git log -p --all -S 'your-secret-value' --source
# Should return empty

# Run gitleaks again
gitleaks detect --source . --verbose
```

---

## 6. Git Hooks and Pre-Commit Hooks

### 6.1 git-secrets

**Installation and setup**

```bash
# Install
brew install git-secrets

# Install hooks in repository
git secrets --install

# Register AWS patterns
git secrets --register-aws

# Add custom patterns
git secrets --add 'sk-ant-[a-zA-Z0-9\-_]{40,}'
git secrets --add 'sk-[a-zA-Z0-9]{48}'
git secrets --add 'ghp_[A-Za-z0-9_]{36,}'
git secrets --add 'ANTHROPIC_API_KEY.*=.*sk-ant-'
git secrets --add 'OPENAI_API_KEY.*=.*sk-'

# Add allowed patterns (false positives)
git secrets --add --allowed 'sk-ant-example-key-not-real'
```

**Configuration file** (`.git/config` or global):

```gitconfig
[secrets]
    providers = git secrets --aws-provider
    patterns = sk-ant-[a-zA-Z0-9\\-_]{40,}
    patterns = sk-[a-zA-Z0-9]{48}
    patterns = ghp_[A-Za-z0-9_]{36,}
    allowed = example-api-key
```

### 6.2 gitleaks Pre-Commit Hook

**Using pre-commit framework**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.1
    hooks:
      - id: gitleaks
```

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
```

**Custom gitleaks configuration**

```toml
# .gitleaks.toml
title = "Gitleaks Custom Config"

[allowlist]
description = "Global allowlist"
paths = [
    '''\.env\.example$''',
    '''\.env\.template$''',
]

[[rules]]
id = "anthropic-api-key"
description = "Anthropic API Key"
regex = '''sk-ant-[a-zA-Z0-9\-_]{40,}'''
tags = ["key", "anthropic"]

[[rules]]
id = "openai-api-key"
description = "OpenAI API Key"
regex = '''sk-[a-zA-Z0-9]{48}'''
tags = ["key", "openai"]

[[rules]]
id = "generic-api-key"
description = "Generic API Key"
regex = '''(?i)(api[_-]?key|apikey)['":\s]*[=:]\s*['"][a-zA-Z0-9]{16,}['"]'''
tags = ["key", "generic"]

[[rules]]
id = "generic-password"
description = "Generic Password"
regex = '''(?i)(password|passwd|pwd)['":\s]*[=:]\s*['"][^'"]{4,}['"]'''
tags = ["password"]
```

### 6.3 detect-secrets

**Installation and baseline**

```bash
# Install
pip install detect-secrets

# Generate baseline
detect-secrets scan > .secrets.baseline

# Audit baseline (mark false positives)
detect-secrets audit .secrets.baseline

# Update baseline after adding new secrets
detect-secrets scan --baseline .secrets.baseline
```

**Pre-commit hook**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

### 6.4 Husky (Node.js Projects)

**Installation**

```bash
# Install husky
npm install --save-dev husky

# Initialize husky
npx husky init
```

**Pre-commit hook for secrets**

```bash
# Create pre-commit hook
cat > .husky/pre-commit << 'EOF'
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Check for secrets with gitleaks
if command -v gitleaks &> /dev/null; then
  gitleaks protect --staged --verbose
  if [ $? -ne 0 ]; then
    echo "Secrets detected! Commit blocked."
    exit 1
  fi
fi

# Check for forbidden files
FORBIDDEN_PATTERNS=".env .env.* *.pem *.key credentials.json secrets.*"
for pattern in $FORBIDDEN_PATTERNS; do
  if git diff --cached --name-only | grep -E "$pattern"; then
    echo "ERROR: Attempting to commit forbidden file: $pattern"
    exit 1
  fi
done

exit 0
EOF

chmod +x .husky/pre-commit
```

### 6.5 Custom Pre-Commit Hook Script

```bash
#!/bin/bash
# .git/hooks/pre-commit

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "Running secret detection..."

# Forbidden file patterns
FORBIDDEN_FILES=(
  ".env"
  ".env.*"
  "*.env"
  "credentials.json"
  "*-credentials.json"
  "service-account*.json"
  "secrets.yml"
  "secrets.json"
  "*.pem"
  "*.key"
  "*.p12"
  "*.pfx"
  "id_rsa"
  "id_rsa.*"
  "id_ed25519"
  "id_ecdsa"
  ".npmrc"
  ".pypirc"
)

# Secret patterns to detect in content
SECRET_PATTERNS=(
  "-----BEGIN.*PRIVATE KEY-----"
  "api[_-]?key.*[=:].*['\"][a-zA-Z0-9]{16,}['\"]"
  "password.*[=:].*['\"][^'\"]{4,}['\"]"
  "secret.*[=:].*['\"][a-zA-Z0-9]{16,}['\"]"
  "sk-ant-[a-zA-Z0-9\-_]{40,}"
  "sk-[a-zA-Z0-9]{48}"
  "AKIA[0-9A-Z]{16}"
  "ghp_[A-Za-z0-9_]{36,}"
  "xox[baprs]-[0-9]{10,}"
)

ERRORS=0

# Check for forbidden files
for pattern in "${FORBIDDEN_FILES[@]}"; do
  files=$(git diff --cached --name-only | grep -E "^$pattern$|/$pattern$" || true)
  if [ -n "$files" ]; then
    echo -e "${RED}ERROR: Forbidden file pattern '$pattern' detected:${NC}"
    echo "$files"
    ERRORS=$((ERRORS + 1))
  fi
done

# Check for secret patterns in staged content
for pattern in "${SECRET_PATTERNS[@]}"; do
  matches=$(git diff --cached -U0 | grep -E "^\+" | grep -E "$pattern" || true)
  if [ -n "$matches" ]; then
    echo -e "${YELLOW}WARNING: Possible secret detected (pattern: $pattern):${NC}"
    echo "$matches" | head -3
    ERRORS=$((ERRORS + 1))
  fi
done

# Run gitleaks if available
if command -v gitleaks &> /dev/null; then
  gitleaks protect --staged --verbose --redact
  if [ $? -ne 0 ]; then
    ERRORS=$((ERRORS + 1))
  fi
fi

if [ $ERRORS -gt 0 ]; then
  echo ""
  echo -e "${RED}===============================================${NC}"
  echo -e "${RED}COMMIT BLOCKED: $ERRORS potential secret(s) found${NC}"
  echo -e "${RED}===============================================${NC}"
  echo ""
  echo "If these are false positives, you can:"
  echo "  1. Add to .gitleaks.toml allowlist"
  echo "  2. Use: git commit --no-verify (NOT RECOMMENDED)"
  echo ""
  exit 1
fi

echo -e "${GREEN}No secrets detected. Proceeding with commit.${NC}"
exit 0
```

```bash
# Make executable
chmod +x .git/hooks/pre-commit
```

---

## 7. CI/CD Integration

### 7.1 GitHub Actions

```yaml
# .github/workflows/secrets-scan.yml
name: Secret Scanning

on:
  push:
    branches: [main, master, develop]
  pull_request:
    branches: [main, master]

jobs:
  gitleaks:
    name: Gitleaks Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }} # Optional for enterprise

  trufflehog:
    name: TruffleHog Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run TruffleHog
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
          extra_args: --only-verified

  detect-secrets:
    name: Detect Secrets
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Install detect-secrets
        run: pip install detect-secrets

      - name: Run detect-secrets
        run: |
          detect-secrets scan --baseline .secrets.baseline
          detect-secrets audit --report --baseline .secrets.baseline
```

### 7.2 GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - security

gitleaks:
  stage: security
  image: zricethezav/gitleaks:latest
  script:
    - gitleaks detect --source . --verbose --report-format json --report-path gitleaks-report.json
  artifacts:
    reports:
      secret_detection: gitleaks-report.json
    when: always
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'

secret_detection:
  stage: security
  image: registry.gitlab.com/gitlab-org/security-products/analyzers/secrets:latest
  script:
    - /analyzer run
  artifacts:
    reports:
      secret_detection: gl-secret-detection-report.json
```

### 7.3 CircleCI

```yaml
# .circleci/config.yml
version: 2.1

orbs:
  gitleaks: upsidr/gitleaks@2.0.0

jobs:
  secret-scan:
    docker:
      - image: cimg/base:stable
    steps:
      - checkout
      - run:
          name: Install gitleaks
          command: |
            curl -sSfL https://github.com/gitleaks/gitleaks/releases/download/v8.18.1/gitleaks_8.18.1_linux_x64.tar.gz | tar xz
            sudo mv gitleaks /usr/local/bin/
      - run:
          name: Run gitleaks
          command: gitleaks detect --source . --verbose

workflows:
  security:
    jobs:
      - secret-scan
```

### 7.4 Jenkins

```groovy
// Jenkinsfile
pipeline {
    agent any

    stages {
        stage('Secret Scan') {
            steps {
                sh '''
                    # Install gitleaks if not present
                    if ! command -v gitleaks &> /dev/null; then
                        curl -sSfL https://github.com/gitleaks/gitleaks/releases/download/v8.18.1/gitleaks_8.18.1_linux_x64.tar.gz | tar xz
                        mv gitleaks /usr/local/bin/
                    fi

                    # Run scan
                    gitleaks detect --source . --verbose --report-format json --report-path gitleaks-report.json
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'gitleaks-report.json', allowEmptyArchive: true
                }
            }
        }
    }
}
```

---

## 8. Checklist

### Pre-Open Source Checklist

```markdown
## File System Scan
- [ ] No .env files tracked in repository
- [ ] No credential files (*.pem, *.key, *.p12) tracked
- [ ] No service account JSON files tracked
- [ ] No .npmrc with auth tokens tracked
- [ ] .gitignore includes all sensitive patterns

## Code Scan
- [ ] No hardcoded API keys in source files
- [ ] No hardcoded passwords in source files
- [ ] No hardcoded connection strings with credentials
- [ ] No private keys embedded in code
- [ ] No personal information (emails, names) in comments

## Git History Scan
- [ ] Ran gitleaks on full history
- [ ] No sensitive files ever committed (including deleted)
- [ ] No secrets in any branch or tag
- [ ] Checked merge commits for leaks
- [ ] Checked stashes for sensitive data

## Configuration
- [ ] .env.example exists with placeholder values
- [ ] README documents required environment variables
- [ ] No default credentials in config files
- [ ] Database seeds use fake data

## Prevention Setup
- [ ] Pre-commit hooks installed (gitleaks or git-secrets)
- [ ] .gitleaks.toml configured for project
- [ ] CI/CD secret scanning enabled
- [ ] Team trained on secret hygiene

## Credential Rotation
- [ ] All previously leaked credentials rotated
- [ ] New credentials generated for open source version
- [ ] Access logs reviewed for unauthorized usage
```

### Emergency Response Checklist

```markdown
## Immediate Actions (within minutes)
- [ ] Rotate compromised credential immediately
- [ ] Revoke access tokens
- [ ] Change affected passwords
- [ ] Disable exposed API keys

## Investigation (within hours)
- [ ] Check access logs for unauthorized usage
- [ ] Identify scope of exposure (which commits, branches)
- [ ] Determine if credential was scraped by bots
- [ ] Check for unusual account activity

## Remediation (within day)
- [ ] Clean git history using git-filter-repo or BFG
- [ ] Force push cleaned history
- [ ] Notify all collaborators to re-clone
- [ ] Update .gitignore to prevent recurrence
- [ ] Set up pre-commit hooks

## Documentation
- [ ] Document incident timeline
- [ ] Document affected systems
- [ ] Document remediation steps taken
- [ ] Update security procedures
```

---

## 9. Output Format

### Scan Report Template

```markdown
# Security Scan Report

**Repository**: [repo-name]
**Scan Date**: [YYYY-MM-DD HH:MM]
**Scanned By**: [tool/person]

## Summary

| Category | Status | Count |
|----------|--------|-------|
| Sensitive Files (Current) | [PASS/FAIL] | [N] |
| Sensitive Files (History) | [PASS/FAIL] | [N] |
| Hardcoded Secrets | [PASS/FAIL] | [N] |
| .gitignore Coverage | [PASS/FAIL] | [N] missing |

## Findings

### Critical (Immediate Action Required)

| File/Location | Type | Details | Commit |
|---------------|------|---------|--------|
| .env | Environment File | Tracked in repo | abc1234 |
| src/config.ts:42 | API Key | OpenAI key detected | def5678 |

### Warning (Review Required)

| File/Location | Type | Details | Commit |
|---------------|------|---------|--------|
| config/db.yml | Connection String | May contain password | - |

### Info (False Positives / Reviewed)

| File/Location | Type | Details | Status |
|---------------|------|---------|--------|
| .env.example | Example File | Contains placeholders | OK |

## Recommendations

1. **URGENT**: Rotate OpenAI API key immediately
2. **HIGH**: Remove .env from git history using git-filter-repo
3. **MEDIUM**: Add missing patterns to .gitignore
4. **LOW**: Set up pre-commit hooks for ongoing protection

## Commands to Execute

```bash
# Step 1: Create backup
git clone --mirror . ../repo-backup-$(date +%Y%m%d)

# Step 2: Remove sensitive files from history
git filter-repo --path .env --invert-paths

# Step 3: Update .gitignore
echo ".env" >> .gitignore
echo "*.pem" >> .gitignore

# Step 4: Force push
git push origin --force --all
```

```

---

## 10. Best Practices

### Development Workflow

1. **Never commit secrets** - Use environment variables
2. **Use .env.example** - Document required variables without values
3. **Git hooks from day one** - Install pre-commit hooks immediately
4. **Regular audits** - Run gitleaks weekly in CI/CD
5. **Principle of least privilege** - Use separate keys for dev/staging/prod

### Environment Variable Management

```bash
# .env.example (safe to commit)
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
OPENAI_API_KEY=your_openai_key_here
STRIPE_SECRET_KEY=your_stripe_key_here

# .env (NEVER commit)
DATABASE_URL=postgresql://realuser:realpassword@prod.example.com:5432/proddb
OPENAI_API_KEY=sk-abc123...
STRIPE_SECRET_KEY=sk_live_abc123...
```

### Secret Management Tools

For production applications, use dedicated secret management:

- **AWS Secrets Manager**
- **HashiCorp Vault**
- **Google Secret Manager**
- **Azure Key Vault**
- **Doppler**
- **1Password Secrets Automation**

### Team Training

1. Educate team on risks of committed secrets
2. Establish code review checklist for secrets
3. Create incident response procedures
4. Regular security awareness sessions
5. Maintain up-to-date .gitignore templates

### Gitignore Template

```gitignore
# Environment files
.env
.env.*
*.env
.envrc
!.env.example
!.env.template

# Credentials
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
*.keystore
*.jks

# Cloud provider
.aws/
.gcp/
.azure/
kubeconfig
.kube/

# Package manager auth
.npmrc
.yarnrc.yml
.pypirc
.gem/credentials
.docker/config.json

# IDE (may contain secrets)
.idea/
.vscode/settings.json
*.sublime-workspace

# Logs (may contain secrets)
*.log
logs/

# Database
*.sql
!schema.sql
!migrations/*.sql

# OS files
.DS_Store
Thumbs.db
```

---

## Quick Reference Commands

```bash
# === SCANNING ===
# Quick file scan
find . -name ".env*" -o -name "*.pem" -o -name "*.key" | grep -v node_modules

# Quick history scan
git log --all --pretty=format: --name-only --diff-filter=A | sort -u | grep -iE 'env|secret|credential|key'

# Full gitleaks scan
gitleaks detect --source . --verbose

# === CLEANING ===
# Remove file from history
git filter-repo --path .env --invert-paths --force

# Force push after clean
git push origin --force --all

# === PREVENTION ===
# Install git-secrets
brew install git-secrets && git secrets --install && git secrets --register-aws

# Install gitleaks pre-commit
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.1
    hooks:
      - id: gitleaks
EOF
pre-commit install
```

---

**Remember**: Removing secrets from git history does NOT make them safe. Always rotate leaked credentials immediately. Cleaning history is for compliance and reducing exposure, not security.
