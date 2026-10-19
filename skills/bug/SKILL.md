---
name: bug
description: File a GitHub issue of type Bug from a description — structures a clear bug report (summary, steps to reproduce, expected vs actual, environment), previews it, then on confirmation creates the issue with the Bug issue type (falling back to a bug label when the repo has no issue types). Use when the user asks to file a bug, open a bug report, create a GitHub bug issue, log a bug, or runs /bug.
argument-hint: "[draft] [description]"
compatibility: Requires git and GitHub CLI gh access to the target repository.
metadata:
  version: "2.2.4"
  tags: "github, issue, bug, report, gh, triage"
allowed-tools: Bash(gh *) Bash(git *)
disable-model-invocation: true
---

# Bug

Turn a description of something broken into a GitHub issue of type **Bug**. Draft the report from what the user gives (plus repo context), show it for approval, and only then file the issue: typed `Bug` where the repo supports issue types, otherwise labelled `bug`.

Never open an issue without confirmation, and never invent reproduction steps or facts the user did not provide; mark unknowns as such. Requires git and `gh` access to the target repository.

## Inputs

- A description of the bug (free text, an error/stack trace, or a title plus details)
- The target repository (auto-detected from the current directory's remote)
- Optional: labels, assignee, milestone, or severity the user specifies

## When to use

- Filing a clean bug report from a rough description or an error message
- Logging a bug found mid-session without leaving the terminal
- The user says "open a bug", "file this", "create a bug issue", or runs `/bug`

Do not use this to fix the bug, to file feature requests or tasks (different issue type), or to triage existing issues. If the bug is a failing CI check the user wants fixed rather than filed, or the user wants a root cause before filing, do that work instead and come back.

## Guardrails

- Creating the issue is visible to everyone with repo access: always print the drafted title and body and require an explicit yes first.
- Ask before creating a new `bug` label (fallback path) if it does not already exist.
- Apply only the labels, assignee, milestone, or project the user asked for. Do not edit code, close other issues, or modify repository settings.

## Phase 1: Repository and type detection

```bash
gh auth status -h github.com
gh repo view --json nameWithOwner,hasIssuesEnabled --jq '{repo:.nameWithOwner, issues:.hasIssuesEnabled}'
```

Stop if issues are disabled. Detect whether the repo's owner defines issue **types** and whether a `Bug` type exists:

```bash
gh issue create --help | grep -q -- '--type' && echo "type-flag: supported"
gh api "repos/{owner}/{repo}" --jq '.owner.type' 2>/dev/null
```

Decide the path:

- **Bug issue type:** preferred when the org/repo exposes a `Bug` type. Use `--type Bug`.
- **`bug` label:** fallback when no issue types exist. Check for the label and plan to create it only if needed:

```bash
gh label list --search bug --json name --jq '.[].name'
```

## Phase 2: Draft the report

Structure the report from what the user gave. Keep it factual and mark anything unknown as `_not provided_`.

**Title:** a short, specific summary of the symptom (not "bug" or "it's broken").

**Body** (omit sections that genuinely do not apply):

```markdown
## Summary
<one or two sentences: what is broken>

## Steps to Reproduce
1. …
2. …

## Expected
<what should happen>

## Actual
<what happens instead; include the error/stack trace verbatim if provided>

## Environment
<app/service, version or commit, OS/browser, anything relevant, or _not provided_>

## Notes
<links, related issues, suspected area; only if the user gave them>
```

Quote any pasted stack trace or error verbatim in a fenced block under **Actual**. Ask one concise follow-up only if the report is unusable without it (for example, no symptom at all); otherwise draft with what you have and mark gaps.

## Phase 3: Preview and confirm

Print the full drafted issue (title, body, the type/label decision, and any labels/assignee/milestone to apply), then stop and wait for an explicit yes. In a read-only or dry-run request, end here and file nothing.

## Phase 4: Create the issue

Only after confirmation, write the body to a temp file inside the repo's `.tmp/` (to preserve formatting) and create the issue.

Preferred, Bug issue type:

```bash
REPO_TMP="$(git rev-parse --show-toplevel)/.tmp"
mkdir -p "$REPO_TMP"
gh issue create --title "<title>" --body-file "$REPO_TMP/bug_body.md" --type Bug
```

Fallback, `bug` label (create the label first only if it is missing and the user agreed):

```bash
gh label create bug --color d73a4a --description "Something isn't working" 2>/dev/null || true
gh issue create --title "<title>" --body-file "$REPO_TMP/bug_body.md" --label bug
```

Add `--assignee`, `--label`, `--milestone`, or `--project` only for values the user specified. If `--type Bug` fails because the type does not exist, fall back to the label path and say so rather than failing the run.

## Modes

- `bug` / `bug <description>`: Phases 1-4. Draft, confirm, file. (Default.)
- `bug draft`: Phases 1-3. Draft and print only; create nothing.

If the user asks for a feature or task instead of a bug, say this skill files bugs and point them to the right issue type.

## Final status

Report:

- The repository and whether the issue was typed `Bug` or labelled `bug`
- The created issue number and URL
- Any labels, assignee, or milestone applied
- A suggested next step, such as root-causing the bug or fixing a failing check

## Contract

Inputs:

- A description of the bug (free text, an error/stack trace, or a title plus details)
- The target repository (auto-detected from the current directory's remote)
- Optional: labels, assignee, milestone, or severity the user specifies

Outputs:

- A structured bug report (title + body) shown before anything is created
- Whether the issue will be typed `Bug` or labelled `bug` (and why)
- The created issue number and URL

Creates/Modifies:

- Creates one GitHub issue of type `Bug` (or with the `bug` label) via `gh`
- Applies only the labels/assignee/milestone the user asked for
- Creates the `bug` label if it is used as a fallback and does not yet exist
- Does not edit code, close other issues, or modify repository settings

External Side Effects:

- Reads repository, label, and issue-type metadata from GitHub
- Creates a GitHub issue (visible to everyone with repo access)

Confirmation Required:

- Before creating the issue — always print the drafted title + body and require an
  explicit yes
- Before creating a new `bug` label (fallback path), if one does not already exist

Delegates To:

- `github-fix-ci` when the bug is a failing CI check the user wants fixed instead of filed
- `debug` when the user wants to root-cause before filing (it escalates to its
  four-phase loop on its own when a fix attempt has already failed)
