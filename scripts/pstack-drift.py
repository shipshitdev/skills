#!/usr/bin/env python3
"""Report upstream drift for the pinned Pstack imports as one tracking issue.

Read-only against upstream: it compares each pinned commit in
upstream/pstack/lock.json with the upstream default branch through the GitHub
compare API. It never imports, stages or pushes anything; the offline
`pstack-sync.py verify` stays the import gate.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
TITLE = "chore(pstack): upstream drift detected"
MARKER = "<!-- pstack-drift-check -->"
MAX_FILES = 40
# The compare API returns at most 300 files; a full page may hide more changes.
COMPARE_FILE_CAP = 300
WRITE_TOKEN_ENV = "PSTACK_DRIFT_WRITE_TOKEN"

Runner = Callable[[list[str]], str]


def gh(args: list[str]) -> str:
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def gh_with_token(token: str) -> Runner:
    """Return a gh runner that authenticates with `token` instead of GH_TOKEN."""
    def run(args: list[str]) -> str:
        env = {**os.environ, "GH_TOKEN": token}
        return subprocess.run(["gh", *args], check=True, capture_output=True, text=True, env=env).stdout
    return run


def decode_pages(text: str) -> list:
    """Flatten the concatenated JSON arrays that `gh api --paginate` prints."""
    decoder = json.JSONDecoder()
    items: list = []
    index = 0
    while index < len(text):
        if text[index].isspace():
            index += 1
            continue
        page, index = decoder.raw_decode(text, index)
        items.extend(page if isinstance(page, list) else [page])
    return items


def slug(repository: str) -> str:
    value = repository.removesuffix(".git").removeprefix("https://github.com/")
    if value.count("/") != 1 or ":" in value:
        raise ValueError(f"Not a GitHub repository URL: {repository}")
    return value


def tracked(path: str, source: dict) -> bool:
    for prefix in source.get("ignored_paths", []):
        if path == prefix or (prefix.endswith("/") and path.startswith(prefix)):
            return False
    roots = source.get("paths", ["."])
    return any(root == "." or path == root or path.startswith(root.rstrip("/") + "/") for root in roots)


def scoped_commits(repo: str, source: dict, head: str, run: Runner) -> list[dict] | None:
    """List commits touching the tracked roots since the pin; None when it cannot be scoped."""
    roots = source.get("paths", ["."])
    if "." in roots:
        return None  # whole-repo scope has no path filter to narrow the history
    since = run(["api", f"repos/{repo}/commits/{source['commit']}",
                 "--jq", ".commit.committer.date"]).strip()
    found: dict[str, dict] = {}
    for root in roots:
        query = f"sha={head}&path={quote(root.rstrip('/'))}&since={quote(since)}&per_page=100"
        for commit in decode_pages(run(["api", "--paginate", f"repos/{repo}/commits?{query}"])):
            if commit["sha"] != source["commit"]:
                subject = (commit.get("commit", {}).get("message") or "").splitlines()[:1]
                found[commit["sha"]] = {"sha": commit["sha"], "subject": subject[0] if subject else ""}
    return list(found.values())


def inspect(source: dict, run: Runner) -> dict:
    """Compare one pinned source with its upstream default branch."""
    repo = slug(source["repository"])
    branch = run(["api", f"repos/{repo}", "--jq", ".default_branch"]).strip()
    head = run(["api", f"repos/{repo}/branches/{branch}", "--jq", ".commit.sha"]).strip()
    data = json.loads(run(["api", f"repos/{repo}/compare/{source['commit']}...{head}"]))
    listed = data.get("files", [])
    # A rename is tracked when either side of it is, so moving a file out of a
    # tracked path still counts as drift.
    files = [{"filename": item["filename"], "previous": item.get("previous_filename")}
             for item in listed
             if tracked(item["filename"], source)
             or (item.get("previous_filename") and tracked(item["previous_filename"], source))]
    truncated = len(listed) >= COMPARE_FILE_CAP
    commits: list[dict] = []
    inconclusive = False
    if truncated and data.get("ahead_by", 0) > 0:
        scoped = scoped_commits(repo, source, head, run)
        if scoped is None:
            inconclusive = True
        else:
            commits = scoped
    return {
        "id": source["id"],
        "repo": repo,
        "branch": branch,
        "pinned": source["commit"],
        "head": head,
        "status": data.get("status", "identical"),
        "ahead_by": data.get("ahead_by", 0),
        "files": files,
        "truncated": truncated,
        "commits": commits,
        "inconclusive": inconclusive,
        "compare_url": f"https://github.com/{repo}/compare/{source['commit']}...{head}",
        "paths": source.get("paths", ["."]),
    }


def drifted(report: dict) -> bool:
    # A monorepo upstream can be ahead only in paths this import never ships.
    # An inconclusive check counts as drift so the tracking issue is never closed on it.
    return report["ahead_by"] > 0 and bool(report["files"] or report["commits"] or report["inconclusive"])


def describe_file(item: dict) -> str:
    if item["previous"] and item["previous"] != item["filename"]:
        return f"`{item['filename']}` (renamed from `{item['previous']}`)"
    return f"`{item['filename']}`"


def render(reports: list[dict]) -> str:
    lines = [
        MARKER,
        "The pinned Pstack imports are behind upstream. Nothing was imported: stage each",
        "candidate, review it, and keep `python3 scripts/pstack-sync.py verify` as the gate.",
        "",
    ]
    for report in (r for r in reports if drifted(r)):
        shown = report["files"][:MAX_FILES]
        extra = len(report["files"]) - len(shown)
        lines += [
            f"## {report['id']}",
            "",
            f"- Repository: https://github.com/{report['repo']} (`{report['branch']}`)",
            f"- Pinned: `{report['pinned']}`",
            f"- Upstream head: `{report['head']}`",
            f"- Ahead by: {report['ahead_by']} commits",
            f"- Range: {report['compare_url']}",
            f"- Changed files under {', '.join(f'`{p}`' for p in report['paths'])} ({len(report['files'])}):",
            *[f"  - {describe_file(item)}" for item in shown],
            *([f"  - ... and {extra} more (see the range link)"] if extra else []),
        ]
        if report["inconclusive"]:
            lines += [
                "",
                f"- INCONCLUSIVE: the compare file list hit GitHub's {COMPARE_FILE_CAP}-file cap and this",
                "  source tracks the whole repository, so changes cannot be scoped. Treated as drifted;",
                "  review the range link manually.",
            ]
        elif report["truncated"]:
            shown_commits = report["commits"][:MAX_FILES]
            lines += [
                "",
                f"- The compare file list hit GitHub's {COMPARE_FILE_CAP}-file cap, so tracked changes were",
                f"  checked through commit history instead ({len(report['commits'])} commits touch the tracked paths):",
                *[f"  - `{c['sha'][:12]}` {c['subject']}" for c in shown_commits],
                *([f"  - ... and {len(report['commits']) - len(shown_commits)} more"]
                  if len(report["commits"]) > len(shown_commits) else []),
            ]
        lines += [
            "",
            "Stage a review candidate from a clean upstream checkout, outside this repository:",
            "",
            "```bash",
            f"git clone https://github.com/{report['repo']} /path/to/{report['id']}",
            "python3 scripts/pstack-sync.py candidate \\",
            f"  --source {report['id']} \\",
            f"  --checkout /path/to/{report['id']} \\",
            f"  --commit {report['head']} \\",
            f"  --output /path/to/artifacts/{report['id']}-update",
            "```",
            "",
        ]
    lines.append("Opened by `.github/workflows/pstack-drift.yml`; this issue updates in place each run.")
    return "\n".join(lines) + "\n"


def find_open(repo: str, run: Runner) -> dict | None:
    """Find the open tracking issue across every page of open issues (PRs excluded)."""
    issues = decode_pages(run(["api", "--paginate", f"repos/{repo}/issues?state=open&per_page=100"]))
    for issue in issues:
        if "pull_request" not in issue and MARKER in (issue.get("body") or ""):
            return issue
    return None


def plan(reports: list[dict], existing: dict | None) -> tuple[str, str]:
    """Return (action, body) where action is none, create, update, unchanged or close."""
    if not any(drifted(r) for r in reports):
        return ("close", "") if existing else ("none", "")
    body = render(reports)
    if existing is None:
        return "create", body
    return ("unchanged" if (existing.get("body") or "") == body else "update"), body


def apply(action: str, body: str, existing: dict | None, repo: str, write: Runner) -> str:
    run = write
    if action == "create":
        return run(["issue", "create", "-R", repo, "--title", TITLE, "--body", body]).strip()
    number = str(existing["number"]) if existing else ""
    if action == "update":
        run(["issue", "edit", number, "-R", repo, "--title", TITLE, "--body", body])
    elif action == "close":
        run(["issue", "close", number, "-R", repo, "--comment",
             "The pinned Pstack imports match upstream again; closing."])
    return f"{action} #{number}" if number else action


def main(argv: list[str] | None = None, run: Runner = gh, write: Runner | None = None,
         env: dict[str, str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--repo", help="owner/name for the tracking issue (required unless --dry-run)")
    parser.add_argument("--dry-run", action="store_true", help="Read upstream only; print the would-be action and body")
    args = parser.parse_args(argv)
    if not args.dry_run and not args.repo:
        parser.error("--repo is required unless --dry-run")
    if not args.dry_run and write is None:
        # Issues written with the workflow's github.token do not trigger issue-governance.yml,
        # so writes need the PAT; refuse to create an ungoverned issue.
        token = (os.environ if env is None else env).get(WRITE_TOKEN_ENV, "")
        if not token:
            print(f"Pstack drift check failed: {WRITE_TOKEN_ENV} is not set; refusing to write an "
                  "issue that would skip issue governance (is the PROJECTS_TOKEN secret missing?)",
                  file=sys.stderr)
            return 1
        write = gh_with_token(token)
    try:
        lock = json.loads((args.root / "upstream/pstack/lock.json").read_text())
        reports = [inspect(source, run) for source in lock["sources"]]
        for report in reports:
            print(f"{report['id']}: {report['status']}, ahead {report['ahead_by']}, "
                  f"{len(report['files'])} tracked files changed", file=sys.stderr)
        existing = find_open(args.repo, run) if args.repo else None
        action, body = plan(reports, existing)
        if args.dry_run:
            print(f"action: {action}")
            if body:
                print(body)
            return 0
        print(apply(action, body, existing, args.repo, write))
    except (ValueError, KeyError, OSError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        detail = getattr(error, "stderr", "") or error
        print(f"Pstack drift check failed: {detail}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
