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
import subprocess
import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
TITLE = "chore(pstack): upstream drift detected"
MARKER = "<!-- pstack-drift-check -->"
MAX_FILES = 40

Runner = Callable[[list[str]], str]


def gh(args: list[str]) -> str:
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


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


def inspect(source: dict, run: Runner) -> dict:
    """Compare one pinned source with its upstream default branch."""
    repo = slug(source["repository"])
    branch = run(["api", f"repos/{repo}", "--jq", ".default_branch"]).strip()
    head = run(["api", f"repos/{repo}/branches/{branch}", "--jq", ".commit.sha"]).strip()
    data = json.loads(run(["api", f"repos/{repo}/compare/{source['commit']}...{head}"]))
    files = [item["filename"] for item in data.get("files", []) if tracked(item["filename"], source)]
    return {
        "id": source["id"],
        "repo": repo,
        "branch": branch,
        "pinned": source["commit"],
        "head": head,
        "status": data.get("status", "identical"),
        "ahead_by": data.get("ahead_by", 0),
        "files": files,
        "compare_url": f"https://github.com/{repo}/compare/{source['commit']}...{head}",
        "paths": source.get("paths", ["."]),
    }


def drifted(report: dict) -> bool:
    # A monorepo upstream can be ahead only in paths this import never ships.
    return report["ahead_by"] > 0 and bool(report["files"])


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
            *[f"  - `{name}`" for name in shown],
            *([f"  - ... and {extra} more (see the range link)"] if extra else []),
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
    issues = json.loads(run(["issue", "list", "-R", repo, "--state", "open", "--limit", "200",
                             "--json", "number,title,body"]))
    for issue in issues:
        if MARKER in (issue.get("body") or ""):
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


def apply(action: str, body: str, existing: dict | None, repo: str, run: Runner) -> str:
    if action == "create":
        return run(["issue", "create", "-R", repo, "--title", TITLE, "--body", body]).strip()
    number = str(existing["number"]) if existing else ""
    if action == "update":
        run(["issue", "edit", number, "-R", repo, "--title", TITLE, "--body", body])
    elif action == "close":
        run(["issue", "close", number, "-R", repo, "--comment",
             "The pinned Pstack imports match upstream again; closing."])
    return f"{action} #{number}" if number else action


def main(argv: list[str] | None = None, run: Runner = gh) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--repo", help="owner/name for the tracking issue (required unless --dry-run)")
    parser.add_argument("--dry-run", action="store_true", help="Read upstream only; print the would-be action and body")
    args = parser.parse_args(argv)
    if not args.dry_run and not args.repo:
        parser.error("--repo is required unless --dry-run")
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
        print(apply(action, body, existing, args.repo, run))
    except (ValueError, KeyError, OSError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        detail = getattr(error, "stderr", "") or error
        print(f"Pstack drift check failed: {detail}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
