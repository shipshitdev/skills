#!/usr/bin/env python3
"""Report upstream drift for every tracked upstream as one aggregate issue.

Two kinds of sources feed one report:

- the pinned Pstack imports in upstream/pstack/lock.json (whole import scopes), and
- every skills/*/SKILL.md, and every skills/*/references/*.md with frontmatter (an
  absorbed upstream skill), whose `metadata.source` is a GitHub URL in a repository
  the lock file does not cover. Rolling pins (`upstream_commit`) are compared with
  the default branch; tagged pins (`upstream_version`) with the newest release tag
  of the same tag family.

Read-only against upstream: it only calls the GitHub compare/tags APIs. It never
imports, stages or pushes anything; `pstack-sync.py verify` stays the import gate.
One issue (found by MARKER in any state) tracks everything: updated in place,
commented on only when the drift set changes, reopened when drift returns and
closed only when every source is clean and conclusive.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
TITLE = "chore(upstream): drift detected in tracked upstreams"
MARKER = "<!-- pstack-drift-check -->"
MAX_FILES = 40
# Commit dates are not monotonic along ancestry; widen the date window and filter by ancestry.
DATE_SKEW = timedelta(days=30)
# The compare API returns at most 300 files; a full page may hide more changes.
COMPARE_FILE_CAP = 300
WRITE_TOKEN_ENV = "UPSTREAM_DRIFT_WRITE_TOKEN"
STATE_RE = re.compile(r"<!-- drift-state: (\{.*?\}) -->")

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
    """List commits in pin..head touching the tracked roots; None when it cannot be scoped."""
    roots = source.get("paths", ["."])
    if "." in roots:
        return None  # whole-repo scope has no path filter to narrow the history
    pinned_at = run(["api", f"repos/{repo}/commits/{source['commit']}",
                     "--jq", ".commit.committer.date"]).strip()
    since = (datetime.fromisoformat(pinned_at.replace("Z", "+00:00")) - DATE_SKEW).astimezone(timezone.utc)
    since_text = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    # Exact membership of pin..head: an ancestor of the pin can carry a later
    # timestamp and must never count as drift, whatever its date says.
    in_range = {
        commit["sha"]
        for page in decode_pages(run(["api", "--paginate",
                                      f"repos/{repo}/compare/{source['commit']}...{head}?per_page=100"]))
        for commit in page.get("commits", [])
    }
    found: dict[str, dict] = {}
    for root in roots:
        query = f"sha={head}&path={quote(root.rstrip('/'))}&since={quote(since_text)}&per_page=100"
        for commit in decode_pages(run(["api", "--paginate", f"repos/{repo}/commits?{query}"])):
            if commit["sha"] in in_range:
                subject = (commit.get("commit", {}).get("message") or "").splitlines()[:1]
                found[commit["sha"]] = {"sha": commit["sha"], "subject": subject[0] if subject else ""}
    return list(found.values())


class Context:
    """Per-run cache so sources sharing a repository or pin reuse one API call."""

    def __init__(self, run: Runner) -> None:
        self.run = run
        self.heads: dict[str, tuple[str, str]] = {}
        self.compares: dict[tuple[str, str, str], dict] = {}
        self.tags: dict[str, list[str]] = {}

    def head(self, repo: str) -> tuple[str, str]:
        if repo not in self.heads:
            branch = self.run(["api", f"repos/{repo}", "--jq", ".default_branch"]).strip()
            sha = self.run(["api", f"repos/{repo}/branches/{branch}", "--jq", ".commit.sha"]).strip()
            self.heads[repo] = (branch, sha)
        return self.heads[repo]

    def compare(self, repo: str, base: str, head: str) -> dict:
        key = (repo, base, head)
        if key not in self.compares:
            self.compares[key] = json.loads(self.run(["api", f"repos/{repo}/compare/{base}...{head}"]))
        return self.compares[key]

    def tag_names(self, repo: str) -> list[str]:
        if repo not in self.tags:
            pages = decode_pages(self.run(["api", "--paginate", f"repos/{repo}/tags?per_page=100"]))
            self.tags[repo] = [tag["name"] for tag in pages]
        return self.tags[repo]


def unresolvable_pin(error: subprocess.CalledProcessError) -> bool:
    detail = f"{error.stderr or ''} {error.stdout or ''}"
    return "404" in detail or "Not Found" in detail or "No common ancestor" in detail


def inspect(source: dict, run: Runner, ctx: Context | None = None, head: str | None = None,
            branch: str | None = None) -> dict:
    """Compare one pinned source with its upstream default branch (or an explicit head ref)."""
    ctx = ctx or Context(run)
    repo = slug(source["repository"])
    if head is None:
        branch, head = ctx.head(repo)
    branch = branch or head
    base = {
        "id": source["id"],
        "group": source.get("group", "pstack"),
        "repo": repo,
        "branch": branch,
        "pinned": source["commit"],
        "head": head,
        "paths": source.get("paths", ["."]),
        "compare_url": f"https://github.com/{repo}/compare/{source['commit']}...{head}",
        "unresolvable": "",
    }
    try:
        data = ctx.compare(repo, source["commit"], head)
    except subprocess.CalledProcessError as error:
        if source.get("group", "pstack") == "pstack" or not unresolvable_pin(error):
            raise
        return {**base, "status": "unknown", "ahead_by": 0, "files": [], "truncated": False,
                "commits": [], "inconclusive": True,
                "unresolvable": f"pin `{source['commit']}` cannot be compared with `{head}` (not found upstream)"}
    listed = data.get("files", [])
    # A rename is tracked when either side of it is, so moving a file out of a
    # tracked path still counts as drift.
    files = [{"filename": item["filename"], "previous": item.get("previous_filename"),
              "change": item.get("status")}
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
    return {**base, "status": data.get("status", "identical"), "ahead_by": data.get("ahead_by", 0),
            "files": files, "truncated": truncated, "commits": commits, "inconclusive": inconclusive}


def tag_family(tag: str) -> str:
    return re.match(r"^\D*", tag).group(0)


def tag_version(tag: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", tag))


def resolve_pin(pin: str, tags: list[str], latest: str = "") -> tuple[str | None, str]:
    """Match a stored version to a real tag, tolerating a bare prefix (`v1.2.3` for `skill-v1.2.3`)."""
    if pin in tags:
        return pin, ""
    wanted = tag_version(pin)
    family = tag_family(pin)
    # A bare pin may stand for the family `upstream_latest` names, but never for another
    # release stream: `v2.1.1` must not resolve to `cli-v2.1.1` when the skill tracks `skill-v*`.
    allowed = {family}
    if family in ("v", ""):
        allowed |= {"v", ""} | ({tag_family(latest)} if latest else set())
    matches = [tag for tag in tags if wanted and tag_version(tag) == wanted and tag_family(tag) in allowed
               and not re.search(r"\d-[A-Za-z]", tag)]
    if len(matches) == 1:
        return matches[0], ""
    if matches:
        return None, f"version `{pin}` matches several tags ({', '.join(f'`{m}`' for m in sorted(matches))})"
    return None, f"version `{pin}` matches no release tag"


def latest_tag(pinned: str, tags: list[str]) -> str:
    """Newest stable tag of the pinned tag's family."""
    family = tag_family(pinned)
    stable = [t for t in tags if tag_family(t) == family and tag_version(t) and not re.search(r"\d-[A-Za-z]", t)]
    return max(stable, key=tag_version, default=pinned)


def inspect_tagged(skill: dict, ctx: Context) -> dict:
    repo = skill["repo"]
    source = {"id": skill["id"], "group": skill["group"], "repository": repo, "commit": skill["pin"],
              "paths": [skill["path"]]}
    pinned, reason = resolve_pin(skill["pin"], ctx.tag_names(repo), skill.get("latest", ""))
    if pinned is None:
        return {"id": skill["id"], "group": skill["group"], "repo": repo, "branch": "", "pinned": skill["pin"],
                "head": "", "paths": [skill["path"]], "status": "unknown", "ahead_by": 0, "files": [],
                "truncated": False, "commits": [], "inconclusive": True, "unresolvable": reason,
                "compare_url": f"https://github.com/{repo}/tags"}
    newest = latest_tag(pinned, ctx.tag_names(repo))
    if newest == pinned:
        return {"id": skill["id"], "group": skill["group"], "repo": repo, "branch": "", "pinned": pinned,
                "head": newest, "paths": [skill["path"]], "status": "identical", "ahead_by": 0, "files": [],
                "truncated": False, "commits": [], "inconclusive": False, "unresolvable": "",
                "compare_url": f"https://github.com/{repo}/compare/{pinned}...{newest}"}
    return inspect({**source, "commit": pinned}, ctx.run, ctx, head=newest, branch="release tags")


def parse_frontmatter_metadata(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return {}
    values: dict[str, str] = {}
    in_metadata = False
    for line in match.group(1).splitlines():
        if re.match(r"^metadata:\s*$", line):
            in_metadata = True
        elif in_metadata and line.startswith("  "):
            key, _, value = line.strip().partition(":")
            values[key] = value.strip().strip("\"'")
        elif line and not line.startswith(" "):
            in_metadata = False
    return values


def parse_source(source: str, ref: str) -> tuple[str, str] | None:
    """Split a GitHub blob URL into (owner/repo, path); None for anything else."""
    match = re.match(r"^https://github\.com/([^/\s]+/[^/\s]+)/blob/(.+)$", source)
    if not match:
        return None
    rest = match.group(2)
    if ref and rest.startswith(ref + "/"):
        return match.group(1), rest[len(ref) + 1:]
    _, _, path = rest.partition("/")
    return (match.group(1), path) if path else None


def tracked_files(root: Path) -> list[tuple[str, Path]]:
    """Every file that may carry upstream provenance, with the id it reports under.

    A skill's SKILL.md reports under the skill name. A skill that absorbed another
    upstream skill keeps that skill's pin in the frontmatter of the reference file
    holding its body, which reports as `<skill>/<reference>`.
    """
    found = [(path.parent.name, path) for path in (root / "skills").glob("*/SKILL.md")]
    found += [(f"{path.parent.parent.name}/{path.stem}", path)
              for path in (root / "skills").glob("*/references/*.md")]
    return sorted(found)


def discover_skills(root: Path, covered: set[str]) -> list[dict]:
    """Every skill deriving from a GitHub repo the pstack lock file does not already cover."""
    skills: list[dict] = []
    for skill_id, skill_file in tracked_files(root):
        meta = parse_frontmatter_metadata(skill_file.read_text())
        parsed = parse_source(meta.get("source", ""), meta.get("upstream_ref", ""))
        if not parsed or parsed[0].lower() in covered:
            continue
        repo, path = parsed
        pin, kind = (meta["upstream_commit"], "rolling") if meta.get("upstream_commit") else (
            (meta["upstream_version"], "tagged") if meta.get("upstream_version") else ("", "none"))
        skills.append({"id": skill_id, "group": repo, "repo": repo, "path": path,
                       "pin": pin, "kind": kind, "latest": meta.get("upstream_latest", ""),
                       "pin_file": skill_file.relative_to(root).as_posix()})
    return skills


def inspect_skill(skill: dict, ctx: Context) -> dict:
    report = _inspect_skill(skill, ctx)
    report["pin_file"] = skill["pin_file"]
    return report


def _inspect_skill(skill: dict, ctx: Context) -> dict:
    if skill["kind"] == "none":
        return {"id": skill["id"], "group": skill["group"], "repo": skill["repo"], "branch": "", "pinned": "",
                "head": "", "paths": [skill["path"]], "status": "unknown", "ahead_by": 0, "files": [],
                "truncated": False, "commits": [], "inconclusive": True,
                "unresolvable": "no `upstream_commit` or `upstream_version` pin recorded",
                "compare_url": f"https://github.com/{skill['repo']}"}
    if skill["kind"] == "tagged":
        return inspect_tagged(skill, ctx)
    source = {"id": skill["id"], "group": skill["group"], "repository": skill["repo"],
              "commit": skill["pin"], "paths": [skill["path"]]}
    return inspect(source, ctx.run, ctx)


def drifted(report: dict) -> bool:
    """True when the source needs attention: real drift or an inconclusive check.

    A monorepo upstream can be ahead only in paths this import never ships. An
    inconclusive or unresolvable check counts here so it never reads as clean.
    """
    return bool(report["unresolvable"]) or (
        report["ahead_by"] > 0 and bool(report["files"] or report["commits"] or report["inconclusive"]))


def state(report: dict) -> str:
    if report["unresolvable"] or report["inconclusive"] and report["ahead_by"] > 0:
        return "inconclusive"
    return "drifted" if drifted(report) else "clean"


def item_key(report: dict) -> str:
    return report["id"] if report["group"] == "pstack" else f"{report['repo']}:{report['id']}"


def drift_set(reports: list[dict]) -> dict[str, str]:
    return {item_key(r): state(r) for r in reports if state(r) != "clean"}


def describe_file(item: dict) -> str:
    if item["previous"] and item["previous"] != item["filename"]:
        return f"`{item['filename']}` (renamed from `{item['previous']}`)"
    return f"`{item['filename']}`"


def render_pstack(report: dict) -> list[str]:
    shown = report["files"][:MAX_FILES]
    extra = len(report["files"]) - len(shown)
    lines = [
        f"### {report['id']}",
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
    return lines + [
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


def row_change(report: dict) -> str:
    if report["unresolvable"]:
        return f"UNRESOLVABLE: {report['unresolvable']}"
    if report["inconclusive"]:
        return "INCONCLUSIVE: compare truncated, review the compare link"
    if report["files"]:
        item = report["files"][0]
        if item["previous"] and item["previous"] != item["filename"]:
            return f"renamed from `{item['previous']}` to `{item['filename']}`"
        return item["change"] or "modified"
    return f"{len(report['commits'])} commits touch the path (compare truncated)"


def render_repo(repo: str, reports: list[dict]) -> list[str]:
    lines = [f"### {repo}", "", "| Skill | Upstream path | Pin | Upstream head | Change | Compare |",
             "|-------|---------------|-----|---------------|--------|---------|"]
    for r in reports:
        pin = f"`{r['pinned']}`" if r["pinned"] else "none"
        head = f"`{r['head']}`" if r["head"] else "n/a"
        lines.append(f"| {r['id']} | `{r['paths'][0]}` | {pin} | {head} | {row_change(r)} | [compare]({r['compare_url']}) |")
    absorbed = [r for r in reports if r.get("pin_file") and not r["pin_file"].endswith("/SKILL.md")]
    if absorbed:
        lines.append("")
        lines += [f"- `{r['id']}` pin lives in `{r['pin_file']}`" for r in absorbed]
    return lines + [""]


def render(reports: list[dict]) -> str:
    attention = [r for r in reports if drifted(r)]
    pstack = [r for r in attention if r["group"] == "pstack"]
    by_repo: dict[str, list[dict]] = {}
    for r in attention:
        if r["group"] != "pstack":
            by_repo.setdefault(r["repo"], []).append(r)
    lines = [
        MARKER,
        f"<!-- drift-state: {json.dumps(drift_set(reports), sort_keys=True)} -->",
        "Tracked upstreams moved or could not be checked. Nothing was imported or changed.",
        "Only drifted or inconclusive skills are listed; everything else matches its pin.",
        "",
    ]
    if pstack:
        lines += ["## Pstack imports", "",
                  "Stage each candidate, review it, and keep `python3 scripts/pstack-sync.py verify` as the gate.", ""]
        for report in pstack:
            lines += render_pstack(report)
    if by_repo:
        lines += ["## Derived skills", ""]
        for repo, group in sorted(by_repo.items()):
            lines += render_repo(repo, group)
        lines += [
            "Porting reminder: after porting what is worth bringing home, bump `metadata.upstream_commit`",
            "(or `metadata.upstream_version`) and `metadata.last_synced` in the file holding that pin (the",
            "skill's `SKILL.md`, or the reference file listed above for an absorbed skill), and the same",
            "fields in the matching `## Upstream` or \"Absorbed upstream\" table of its `README.md`.",
            "",
        ]
    lines.append("Opened by `.github/workflows/upstream-drift.yml`; this issue updates in place each run.")
    return "\n".join(lines) + "\n"


def find_marker(repo: str, run: Runner) -> dict | None:
    """Find the tracking issue in any state across every page (PRs excluded); the newest wins."""
    issues = decode_pages(run(["api", "--paginate", f"repos/{repo}/issues?state=all&per_page=100"]))
    found = [i for i in issues if "pull_request" not in i and MARKER in (i.get("body") or "")]
    return max(found, key=lambda i: i["number"], default=None)


def previous_set(existing: dict | None) -> dict[str, str]:
    match = STATE_RE.search((existing or {}).get("body") or "")
    try:
        return dict(json.loads(match.group(1))) if match else {}
    except (ValueError, TypeError):
        return {}


def summarize_change(before: dict[str, str], after: dict[str, str]) -> str:
    groups = {
        "Newly drifted": sorted(k for k, v in after.items() if v == "drifted" and before.get(k) != "drifted"),
        "Newly inconclusive": sorted(k for k, v in after.items() if v == "inconclusive" and before.get(k) != "inconclusive"),
        "Resolved": sorted(k for k in before if k not in after),
    }
    return "\n".join(f"- {label}: {', '.join(f'`{k}`' for k in keys)}" for label, keys in groups.items() if keys)


Op = tuple[str, str]


def plan(reports: list[dict], existing: dict | None) -> list[Op]:
    """Return ordered (op, text) pairs: create, edit, reopen, comment or close; empty when nothing to do."""
    current = drift_set(reports)
    is_open = bool(existing) and existing.get("state", "open") == "open"
    if not current:
        return [("close", "All tracked upstreams match their pins again; closing.")] if is_open else []
    body = render(reports)
    if existing is None:
        return [("create", body)]
    before = previous_set(existing)
    changed = summarize_change(before, current) if before != current else ""
    ops: list[Op] = [("edit", body)] if (existing.get("body") or "").strip() != body.strip() else []
    if not is_open:
        return ops + [("reopen", f"Upstream drift returned; reopening.\n\n{changed}".strip())]
    return ops + ([("comment", f"The drift set changed.\n\n{changed}")] if changed else [])


def apply(ops: list[Op], existing: dict | None, repo: str, run: Runner) -> str:
    number = str(existing["number"]) if existing else ""
    done: list[str] = []
    for op, text in ops:
        if op == "create":
            done.append(run(["issue", "create", "-R", repo, "--title", TITLE, "--body", text]).strip())
            continue
        if op == "edit":
            run(["issue", "edit", number, "-R", repo, "--title", TITLE, "--body", text])
        elif op == "reopen":
            run(["issue", "reopen", number, "-R", repo, "--comment", text])
        elif op == "comment":
            run(["issue", "comment", number, "-R", repo, "--body", text])
        elif op == "close":
            run(["issue", "close", number, "-R", repo, "--comment", text])
        done.append(f"{op} #{number}")
    return ", ".join(done) or "none"


def collect(root: Path, run: Runner) -> list[dict]:
    lock = json.loads((root / "upstream/pstack/lock.json").read_text())
    ctx = Context(run)
    reports = [inspect(source, run, ctx) for source in lock["sources"]]
    covered = {slug(source["repository"]).lower() for source in lock["sources"]}
    return reports + [inspect_skill(skill, ctx) for skill in discover_skills(root, covered)]


def print_summary(reports: list[dict]) -> None:
    groups: dict[str, list[dict]] = {}
    for r in reports:
        groups.setdefault(r["repo"], []).append(r)
    for repo, items in sorted(groups.items()):
        marked = [state(r) for r in items]
        print(f"{repo}: {marked.count('drifted')} drifted, {marked.count('inconclusive')} inconclusive "
              f"of {len(items)}", file=sys.stderr)


def main(argv: list[str] | None = None, run: Runner = gh, write: Runner | None = None,
         env: dict[str, str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--repo", help="owner/name for the tracking issue (required unless --dry-run)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Read only; print the would-be actions and body (pass --repo to look up the issue)")
    args = parser.parse_args(argv)
    if not args.dry_run and not args.repo:
        parser.error("--repo is required unless --dry-run")
    if not args.dry_run and write is None:
        # Issues written with the workflow's github.token do not trigger issue-governance.yml,
        # so writes need the PAT; refuse to create an ungoverned issue.
        token = (os.environ if env is None else env).get(WRITE_TOKEN_ENV, "")
        if not token:
            print(f"Upstream drift check failed: {WRITE_TOKEN_ENV} is not set; refusing to write an "
                  "issue that would skip issue governance (is the PROJECTS_TOKEN secret missing?)",
                  file=sys.stderr)
            return 1
        write = gh_with_token(token)
    try:
        reports = collect(args.root, run)
        print_summary(reports)
        existing = find_marker(args.repo, run) if args.repo else None
        if existing:
            existing = {**existing, "state": existing.get("state", "open")}
        ops = plan(reports, existing)
        if args.dry_run:
            print("actions: " + (", ".join(op for op, _ in ops) or "none"))
            for op, text in ops:
                print(f"--- {op} ---\n{text}")
            return 0
        print(apply(ops, existing, args.repo, write))
    except (ValueError, KeyError, OSError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        detail = getattr(error, "stderr", "") or error
        print(f"Upstream drift check failed: {detail}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
