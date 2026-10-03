---
name: git-safety
description: >-
  Guards day-to-day git work in an existing repository: blocks secrets from
  entering a commit, gates destructive git operations before they run, installs
  ignore rules and pre-commit hooks, and drives the rotate-first response when a
  credential has already leaked.
metadata:
  version: "2.2.2"
  tags: "git, security, secrets, pre-commit"
when_to_use: "about to commit, check what is staged, staged secret, pre-commit hook, pre-push check, force push, push --force, reset --hard, clean -fdx, rewrite git history, filter-repo, BFG, scrub a leaked credential, rotate a leaked key, git safety check"
---

# Git Safety

Two guards, one repository you already work in every day:

- **Staged guard** — nothing sensitive enters the next commit.
- **Operation guard** — no destructive git command runs unconfirmed and unbacked.

Both are recurring. They run at commit time and at push time, on every branch,
forever. A one-time audit of a whole repository before it goes public is a
different moment — see [Related](#related).

## Authorized Scope

Apply this engine only within the user's requested task and existing explicit
authorization. Loading or delegating to it grants no additional authority.
Preserve report-only restrictions and the caller's target, host, provider, and
cost limits. Existing approval satisfies a gate only for the same actions and
scope; obtain approval before expanding them. Forward these limits to delegates.

## Contract

Inputs:

- Repository root
- Mode: `scan`, `guard`, `prevent`, `clean`, or `full`
- For `clean`: the leaked path or secret string, and the refs it touches

Outputs:

- Staged findings with a block/allow verdict per file
- Destructive-operation risk assessment and backup command
- Rotation checklist for anything already pushed

Creates/Modifies:

- `scan` and `guard`: no file changes
- `prevent`: `.gitignore`, `.env.example`, and hook files
- `clean`: rewritten git history, only after explicit confirmation

External Side Effects:

- May force-push rewritten history in `clean` mode
- Requires credential rotation on systems outside the repository

Confirmation Required:

- Before rewriting history
- Before force-pushing or any push that discards remote commits
- Before `reset --hard`, `clean -fdx`, or branch/tag deletion
- Before changing hooks or ignore rules in a shared repository

Delegates To:

- `open-source-checker` before publishing a private repository
- `security-audit` for broader application-security review

Default a delegated safety check to `scan` or `guard`. Hook installation,
credential rotation, and history rewriting require their own authorized action;
finding a secret does not authorize those mutations automatically.

## Rotate first

Removing a secret from git history does **not** make it safe. Once pushed:

- Bots scrape new pushes within seconds
- Archive and mirror services may hold snapshots
- Forks keep the original history
- CI/CD logs may hold the value

Rotate the credential at its source before touching history. History rewriting
is cleanup, never containment. The bound: the old value is rejected by the
issuing system.

## Modes

| Mode | Moment | Ends when |
|------|--------|-----------|
| `scan` | Before committing | Every staged file and added line is cleared or flagged |
| `guard` | Before a destructive command | Blast radius stated, backup made, operator confirmed |
| `prevent` | Once per repo, then on drift | Ignore rules and hook block a known-bad test commit |
| `clean` | After a confirmed leak, post-rotation | Secret absent from every ref, collaborators notified |
| `full` | New repo onboarding | `scan` → `prevent` complete |

### `scan` — staged guard

Scope is the working tree and the staged diff, not history.

```bash
# Files about to be committed
git diff --cached --name-only

# Sensitive filenames among them
git diff --cached --name-only | grep -iE '(^|/)\.env($|\.)|\.(pem|key|p12|pfx|secret)$|credentials|service-account|id_rsa|id_ed25519|\.npmrc$|kubeconfig'

# Secret-shaped values in added lines only
git diff --cached -U0 | grep -E '^\+' | grep -iE '(api[_-]?key|secret[_-]?key|client[_-]?secret|access[_-]?token|auth[_-]?token|password)[^a-z]{0,4}[=:][^=:]{8,}'

# Untracked files sitting in the tree that must never be added
git status --porcelain --untracked-files=all | grep -E '^\?\?' | grep -iE '\.env|\.pem$|\.key$|credentials|secrets\.'
```

Verdict per finding: **block** (real credential), **allow** (placeholder,
fixture, or example), or **ask** when the value cannot be classified from the
diff alone. Report the file and line for each block. Ends when every staged path
carries a verdict.

### `guard` — destructive operation gate

Any of these rewrites or discards work that git cannot recover for a
collaborator:

| Command | Discards |
|---------|----------|
| `git push --force` / `--force-with-lease` | Remote commits others may hold |
| `git filter-repo`, `bfg` | Every commit hash in the repository |
| `git reset --hard` | Uncommitted work in the tree and index |
| `git clean -fdx` | Untracked files, including local `.env` |
| `git checkout -- <path>` | Uncommitted edits to that path |
| `git branch -D`, `git push origin --delete` | Unmerged commits on that ref |
| `git rebase` on a pushed branch | Published commits under collaborators |

Before running one:

1. **State the blast radius** — which refs change, whose clones break, what is
   unrecoverable.
2. **Back up** — `git clone --mirror . ../repo-backup-$(date +%Y%m%d)` for any
   history rewrite; `git stash -u` before a `reset --hard` or `clean -fdx`.
3. **Prefer the reversible form** — `--force-with-lease` over `--force`,
   `git revert` over `reset --hard` on a pushed branch, `git stash` over
   `checkout --`.
4. **Confirm with the operator**, quoting the exact command.

Ends when the operator confirms against a stated blast radius, or the reversible
alternative is used instead.

### `prevent` — make the guard automatic

Add the ignore rules, write the pre-commit hook, and create `.env.example`.
Patterns, the full hook script, and `git secrets` setup are in
`references/full-guide.md`.

Ends when a deliberate test commit of a dummy `.env` is rejected by the hook.

### `clean` — rewrite history after a leak

Runs only after rotation is confirmed, and only inside the `guard` gate above.

```bash
git clone --mirror . ../repo-backup-$(date +%Y%m%d)
git filter-repo --path .env --invert-paths
git push origin --force --all && git push origin --force --tags
```

Verify:

```bash
git log --all --full-history -- .env     # empty
git log -p --all -S '<rotated-value>'    # empty
```

Ends when both verifications return empty and every collaborator has re-cloned.

## Emergency response

A credential is in a pushed commit:

1. Rotate the credential. Nothing else counts until this is done.
2. Check the provider's access logs for use of the old value.
3. Run `clean` to strip it from history.
4. Force-push through the `guard` gate.
5. Tell collaborators to re-clone; forks and open PRs keep the old history.
6. Run `prevent` so the same file cannot be staged again.
7. Write down what leaked, when, and what was rotated.

## Related

- `open-source-checker` — the one-time audit before a private repository is
  published: license and attribution, secrets across the entire history,
  internal hostnames and employee references. Run it once, at the publish
  decision; run `git-safety` at every commit thereafter.
- `security-audit` — application-level vulnerability review, not git state.

---

**Full sensitive-file patterns, the complete pre-commit hook script, `.gitignore`
template, `git secrets` setup, BFG alternative, and platform notes:**
`references/full-guide.md`
