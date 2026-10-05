### Opening a PR

**Execution boundary:** Carry the caller's authorized target, action scope,
report-only mode, host and provider limits into every step. Scheduling, model
selection, account choice and worktree placement remain harness-owned. Publication,
external messages, destructive actions and configuration changes require authority
covering that action. The procedure supplies no new permission.

Invoked at the end of every other playbook.

**Worktree.** Work from a git worktree off main; subagents inherit it. Multiple `Agent` calls on the same branch each get their own worktree. To reuse one branch across worktrees, resolve and validate `<head-url>` through Shipping step 1, capture it as `head_url`, then run `git fetch -- "$head_url" "refs/heads/$branch" && git reset --hard FETCH_HEAD` between them. Dirty branch with unrelated work: patch out, fresh worktree, apply. Snarled worktree: reset from main, redo minimally.

**Commits.** Commit liberally; rebase into small, ordered commits before opening PRs. Each commit is a future PR: landable, ordered to tell the story. Amend when the fix belongs in a just-made commit; new commit when separable.

**PRs.** Run `/deslop` over the diff before commit. Run `/no-comments` before review. Write every PR title, PR description, and commit body with `/technical-writing`, then apply `/deslop prose`. Apply every technical-writing layer except Diátaxis. Use one word for each action, keep articles, and avoid `-ing` when a plain verb works.

**Titles.** Use Conventional Commits in the form `type(scope): subject`. Use `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, or `perf` as the type. Use the changed area, such as `pstack` or `pstack`, as the scope. Keep the subject short and imperative. Apply the same `/technical-writing` and `/deslop prose` pass as the body. Name a real symbol when one carries the change. For example, `fix(pstack): retarget opening-a-pr babysit trigger`. Do not add a trailing period.

**Descriptions.** The PR body is a briefing, not the lab notebook. A reviewer who has the diff should learn why the change exists, what it leaves out, what it could break, and how you proved it works, in under a minute. Write short, simple sentences with few identifiers. Do not write walls of text. The squash commit body is the PR body. If the body would make the squash commit longer than about 40 lines, cut the body.

Put each section under a `##` heading, not a bold lead-in, so the sections stand apart. Use these sections in order. Drop a section when it has nothing to say.

- `## Why` gives the problem and the approach in one to three short sentences. Do not list SHAs or rebase genealogy. Do not add a "based on main" preamble.
- `## What changed` has one to three short bullets. Name a real symbol or path only when it carries the change. Name both sides of a rename or retarget.
- `## Scope` always names what the PR covers and what it deliberately leaves out, for example a related follow-up or a known gap. Use one to three short items. Do not list symbols or paths, and do not write a file-by-file essay.
- `## Tradeoffs` names only rejected alternatives that a reviewer would otherwise ask about. Skip this section when there was no real choice.
- `## Blast Radius` gives one or two sentences on who or what the change touches and why that is safe or risky. If main is red without the fix, name the continuing cost.
- `## Verification` has one to three bullets. Each bullet names a real run path, such as the `run` skill, the `verify` skill, or the targeted tests, and the outcome of the check, not only the command name. For a performance change, report one primary number with its unit in `before → after` form. Link the arena or swarm directory for the remaining evidence. Do not include sample-size methodology, swarm recitals, or metric tables.

After these sections, attach videos or screenshots when they prove a claim. Do not paste full SHAs, swarm or arena lane recitals, lever-correction essays, file-by-file checklists, or "CLEAN" verdicts. Put these details in a linked artifact. Do not use `## Summary` or `## Test plan` boilerplate. A commit body does not restate its subject.

**Built-in PR tool.** When the active harness provides a PR creation tool, create, edit, retarget, and mark ready through it, never through a forge CLI. Its own instructions say how. A PR made with the CLI misses what the tool tracks, such as a description later runs can edit. Use the resolved forge for everything the tool does not cover, and for every PR operation when the harness has no such tool.

**Forge.** Resolve the forge before the first PR operation and keep that choice for create, edit, view, watch, and merge. GitHub CLI (`gh`) is the default. If `command -v origin` succeeds and Origin can resolve the repository, prefer `origin pr ...`; if Origin is absent or cannot resolve the repository, stay on `gh` and record the fallback. Record the intended PR base repository as canonical `<base-repo>` and validate it through the active forge. Do not infer it from the checkout's default remote. Capture it as a shell variable and pass `--repo "$base_repo"` to every `gh pr` command. When the head repository is a fork, validate its identity and record its owner and repository name as `<fork-owner>` and `<head-name>`. Do not require Graphite (`gt`).

**Size and stacks.** Prefer five narrow PRs to one large PR. Rebase each child branch onto its parent's exact tip and freeze the bottom-to-top order. When the head and base repositories are the same, make a base-branch chain. The root PR targets trunk and each child PR targets the parent branch. Create a same-repository child with `origin pr create --status open --base "$parent_branch"` or `gh pr create --base "$parent_branch" --repo "$base_repo"` according to the resolved forge. When the head repository is a fork, every PR targets trunk in the base repository while stacked local branches retain parent ancestry. Create every fork PR with the resolved Origin command. With GitHub, capture the approved PR title and body as `<title>` and `<body>`, then run `gh api --method POST "repos/$base_repo/pulls" -f "title=$title" -f "body=$body" -f "head=$fork_owner:$branch" -f "head_repo=$head_name" -f "base=$trunk" --jq .html_url`; add `-F draft=true` only when the readiness rule requires a draft. A fork-only parent branch cannot be a PR base. Before rebasing, force-pushing, or retargeting an existing child, apply Shipping step 4's disarm-and-confirm rule to that child and every descendant. Retarget a same-repository child with `origin pr edit "$pr" --base "$parent_branch"` or `gh pr edit "$pr" --base "$parent_branch" --repo "$base_repo"`. Retarget a fork child with the resolved Origin command or `gh pr edit "$pr" --base "$trunk" --repo "$base_repo"`. Branch from trunk only for independent work. Rebase on trunk before substantial stack work.

**Readiness.** Open each PR ready by default. A built-in PR tool can default to draft, so set its non-draft option on every creation call through it. With Origin, pass `--status open`. With the GitHub CLI create command, omit `--draft` and pass `--repo "$base_repo"`. With the GitHub fork API above, omit the `draft` field. If repository instructions require a draft until named evidence exists, keep the early PR draft and mark it ready only after recording that evidence. On GitHub, pass `--draft` to the CLI create command or `-F draft=true` to the fork API, then later run `gh pr ready "$pr" --repo "$base_repo"`. Use Origin's documented draft and ready operations when Origin is active. If no draft rule applies and a tool still opens the PR as a draft, run `origin pr ready "$pr"` or `gh pr ready "$pr" --repo "$base_repo"` according to the resolved forge. Run `origin pr view "$pr"` or `gh pr view "$pr" --repo "$base_repo"` before you refer to PR status.

**Babysit.** Opening a PR does not start a babysit. Post the URL and keep building. Finish the phase or stack first. Run a separate babysit pass only when the user asks for one after the whole stack exists, per `babysit.md`. A babysit for each new PR stalls the build and spends checks on commits that later waves restart. Push back when feedback drifts from intent.

A subagent that opens a PR runs `interrogate`, `/deslop`, and `/no-comments`. It returns the URL and does not babysit. Return to the parent.
