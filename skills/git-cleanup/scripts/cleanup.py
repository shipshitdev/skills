#!/usr/bin/env python3
"""Plan cleanup from immutable Git evidence; apply only an unchanged scoped plan."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


SCOPES = {
    "all": {"local", "remote", "worktree"},
    "branches": {"local", "remote"},
    "local-branches": {"local"},
    "remote-branches": {"remote"},
    "worktrees": {"worktree"},
}


class Refused(RuntimeError):
    """Evidence is missing, changed, or unsafe."""


FAILURES = (Refused, OSError, ValueError, KeyError, TypeError)


class Repository:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self._trunk_patches: dict[str, set[str]] = {}

    def run(self, *args: str, input_text: str | None = None,
            accepted: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess:
        env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_NO_REPLACE_OBJECTS="1")
        payload = input_text.encode("utf-8", "surrogateescape") if input_text is not None else None
        raw = subprocess.run(args, cwd=self.root, input=payload,
                             capture_output=True, env=env, check=False)
        result = subprocess.CompletedProcess(args, raw.returncode,
            raw.stdout.decode("utf-8", "surrogateescape"),
            raw.stderr.decode("utf-8", "surrogateescape"))
        if result.returncode not in accepted:
            raise Refused(f"{args[0]} {args[1]} failed ({result.returncode}); no proof")
        return result

    def git(self, *args: str) -> str:
        return self.run("git", *args).stdout.strip()

    def oid(self, ref: str) -> str:
        return self.git("rev-parse", "--verify", f"{ref}^{{commit}}")

    def has_commit(self, oid: str) -> bool:
        return self.run("git", "rev-parse", "--verify", "--quiet", f"{oid}^{{commit}}",
                        accepted=(0, 1)).returncode == 0

    def ancestor(self, older: str, newer: str) -> bool:
        return self.run("git", "merge-base", "--is-ancestor", older, newer,
                        accepted=(0, 1)).returncode == 0

    def patch_id(self, patch: str) -> str:
        # Exact whitespace matters for a deletion proof; --stable ignores it.
        output = self.run("git", "patch-id", "--verbatim", input_text=patch).stdout.split()
        return output[0] if output else ""

    def patch(self, older: str, newer: str) -> str:
        return self.patch_id(self.run("git", "diff", "--no-ext-diff", "--no-textconv",
                                      "--binary", older, newer, "--").stdout)

    def final_paths_match(self, oid: str, trunk: str) -> bool:
        base = self.git("merge-base", oid, trunk)
        changed = self.run("git", "diff", "--no-renames", "--name-only", "-z",
                           base, oid, "--").stdout.split("\0")
        trees = []
        for commit in (oid, trunk):
            entries = {}
            output = self.run("git", "ls-tree", "-r", "-t", "-z", commit).stdout
            for entry in output.split("\0"):
                if entry:
                    metadata, path = entry.split("\t", 1)
                    entries[path] = metadata
            trees.append(entries)
        # Compare blob IDs, modes, symlinks, gitlinks, directories, and deletion.
        # Independent historical patches do not prove their final combination.
        return all(trees[0].get(path) == trees[1].get(path) for path in changed if path)

    def worktrees(self) -> list[dict]:
        records = []
        for block in self.run("git", "worktree", "list", "--porcelain", "-z").stdout.split("\0\0"):
            record = {}
            for line in block.split("\0"):
                key, _, value = line.partition(" ")
                if key:
                    record[key] = value
            if record:
                records.append(record)
        return records

    def worktree_state(self, record: dict) -> dict:
        path = Path(record["worktree"])
        if path.is_symlink() or not path.is_dir():
            raise Refused("missing or symlink worktree")
        head = self.git("-C", str(path), "rev-parse", "HEAD")
        branch = self.run("git", "-C", str(path), "symbolic-ref", "-q", "HEAD",
                          accepted=(0, 1)).stdout.strip()
        status = self.run("git", "-C", str(path), "status", "--porcelain=v1", "-z",
                          "--untracked-files=all", "--ignore-submodules=none").stdout
        if status or "locked" in record or "prunable" in record:
            raise Refused("dirty, untracked files, locked, or stale worktree")
        return {"path": str(path.resolve()), "oid": head, "ref": branch}

    def remote_heads(self) -> dict[str, str]:
        return {ref: oid for oid, ref in (line.split("\t") for line in
                self.git("ls-remote", "--heads", "origin").splitlines())}

    def refresh_trunk(self, trunk: str) -> str:
        """Fetch origin trunk and fast-forward the local trunk ref when it is behind."""
        self.git("fetch", "--no-prune", "origin",
                 f"refs/heads/{trunk}:refs/remotes/origin/{trunk}")
        remote_oid = self.oid(f"refs/remotes/origin/{trunk}")
        local_ref = f"refs/heads/{trunk}"
        if self.run("git", "show-ref", "--verify", "--quiet", local_ref,
                    accepted=(0, 1)).returncode != 0:
            return remote_oid
        local_oid = self.oid(local_ref)
        if local_oid == remote_oid or not self.ancestor(local_oid, remote_oid):
            return remote_oid
        current = self.run("git", "symbolic-ref", "-q", "HEAD", accepted=(0, 1)).stdout.strip()
        if current == local_ref:
            self.git("merge", "--ff-only", remote_oid)
            return remote_oid
        for record in self.worktrees():
            if record.get("branch") == local_ref:
                self.git("-C", record["worktree"], "merge", "--ff-only", remote_oid)
                return remote_oid
        self.git("update-ref", local_ref, remote_oid, local_oid)
        return remote_oid

    def blob_at(self, commit: str, path: str) -> str | None:
        output = self.run("git", "ls-tree", "-z", "--full-tree", commit, "--", path).stdout
        if not output:
            return None
        metadata, _, _rest = output.partition("\t")
        parts = metadata.split()
        return parts[2] if len(parts) >= 3 else None

    def path_has_blob(self, trunk: str, path: str, blob: str) -> bool:
        if self.blob_at(trunk, path) == blob:
            return True
        found = self.git("log", "-1", "--pretty=%H", f"--find-object={blob}",
                         trunk, "--", path)
        return bool(found)

    def content_on_trunk(self, oid: str, trunk: str) -> bool:
        """True when every path the candidate changed already reached trunk.

        Squash-merge rewrites commit SHAs, so unique commits are not evidence.
        Compare blobs at each changed path against current trunk and that path's
        trunk history. An empty file delta is not proof (empty commits stay).
        """
        base = self.git("merge-base", oid, trunk)
        raw = self.run("git", "diff", "--raw", "--full-index", "-z", "--no-renames",
                       "--no-ext-diff", base, oid, "--").stdout
        if not raw:
            return False
        parts = raw.split("\0")
        index = 0
        saw_path = False
        while index < len(parts) and parts[index]:
            metadata = parts[index]
            path = parts[index + 1]
            index += 2
            fields = metadata.split()
            if len(fields) < 5:
                return False
            new_blob, status = fields[3], fields[4]
            saw_path = True
            if status == "D" or new_blob == "0" * 40:
                if self.blob_at(trunk, path) is not None:
                    return False
                continue
            if not self.path_has_blob(trunk, path, new_blob):
                return False
        return saw_path

    def context(self, trunk: str | None = None) -> dict:
        metadata = json.loads(self.run("gh", "repo", "view", "--json",
                                       "nameWithOwner,defaultBranchRef").stdout)
        trunk = trunk or metadata["defaultBranchRef"]["name"]
        self.git("check-ref-format", f"refs/heads/{trunk}")
        remote = self.git("remote", "get-url", "origin")
        push_urls = self.git("remote", "get-url", "--push", "--all", "origin").splitlines()
        if push_urls != [remote]:
            raise Refused("origin push destination differs or has multiple URLs")
        # Resolve the origin itself: gh's inferred repository may be a parent fork.
        origin_metadata = json.loads(self.run("gh", "repo", "view", remote, "--json",
                                              "nameWithOwner").stdout)
        if origin_metadata["nameWithOwner"].lower() != metadata["nameWithOwner"].lower():
            raise Refused("origin repository differs from selected GitHub repository")
        self.refresh_trunk(trunk)
        remote_oid = self.remote_heads().get(f"refs/heads/{trunk}")
        if not remote_oid or self.oid(remote_oid) != remote_oid:
            raise Refused("remote trunk object unavailable after fetching origin trunk")
        current = self.run("git", "symbolic-ref", "-q", "HEAD", accepted=(0, 1)).stdout.strip()
        return {"root": str(self.root), "common": self.git("rev-parse", "--path-format=absolute", "--git-common-dir"),
                "repository": metadata["nameWithOwner"], "remote": remote,
                "trunk": trunk, "trunk_oid": remote_oid, "current": current,
                "head": self.oid("HEAD")}

    OPERATION_MARKERS = ("rebase-merge", "rebase-apply", "MERGE_HEAD", "CHERRY_PICK_HEAD",
                         "REVERT_HEAD", "sequencer", "BISECT_LOG")
    OPERATION_REASON = "active operation in this worktree or on this branch; preserve until it finishes"

    def active_operations(self, worktrees: list[dict]) -> tuple[set[str], set[str]]:
        """Worktree paths and branch refs pinned by an in-progress or unreadable operation."""
        paths: set[str] = set()
        refs: set[str] = set()
        for record in worktrees:
            branch = record.get("branch")
            try:
                git_dir = Path(self.git("-C", record["worktree"], "rev-parse", "--absolute-git-dir"))
            except FAILURES:
                paths.add(record["worktree"])
                refs.update({branch} if branch else set())
                continue
            if not any((git_dir / marker).exists() for marker in self.OPERATION_MARKERS):
                continue
            paths.add(record["worktree"])
            if branch:
                refs.add(branch)
            # Rebase and bisect detach HEAD; their metadata names the original branch.
            for name in ("rebase-merge/head-name", "rebase-apply/head-name", "BISECT_START"):
                marker = git_dir / name
                if not marker.is_file():
                    continue
                value = marker.read_text().strip()
                if value.startswith("refs/heads/"):
                    refs.add(value)
                elif value and self.run("git", "check-ref-format", f"refs/heads/{value}",
                                        accepted=(0, 1)).returncode == 0:
                    refs.add(f"refs/heads/{value}")
        return paths, refs

    def assert_not_pinned(self, candidate: dict, operations: tuple[set[str], set[str]]) -> None:
        paths, refs = operations
        if candidate["kind"] == "worktree" and candidate["path"] in paths:
            raise Refused(self.OPERATION_REASON)
        if candidate["kind"] in ("local", "remote") and candidate["ref"] in refs:
            raise Refused(self.OPERATION_REASON)

    def pull_requests(self, repository: str, branch: str) -> list[dict]:
        owner = repository.split("/")[0]
        records = []
        for field, value, state in (("head", f"{owner}:{branch}", "all"), ("base", branch, "open")):
            pages = json.loads(self.run("gh", "api", "--method", "GET", "--paginate", "--slurp",
                                        f"repos/{repository}/pulls", "-f", f"state={state}", "-f",
                                        f"{field}={value}", "-f", "per_page=100").stdout)
            for page in pages:
                for pr in page:
                    head = pr.get("head") or {}
                    base = pr.get("base") or {}
                    head_repo = head.get("repo") or {}
                    base_repo = base.get("repo") or {}
                    same_head = head_repo.get("full_name", "").lower() == repository.lower()
                    same_base = base_repo.get("full_name", "").lower() == repository.lower()
                    if field == "head" and same_head and same_base and head.get("ref") == branch:
                        records.append(pr)
                    elif field == "base" and same_base and base.get("ref") == branch and pr.get("state") == "open":
                        # An open PR depends on its base even when its head is a fork.
                        records.append(pr)
        return records

    def trunk_patches(self, trunk: str) -> set[str]:
        if trunk not in self._trunk_patches:
            patches = set()
            for commit in self.git("rev-list", "--max-count=500", trunk).splitlines():
                parents = self.git("rev-list", "--parents", "-n", "1", commit).split()[1:]
                if len(parents) == 1:
                    patch = self.patch(parents[0], commit)
                    if patch:
                        patches.add(patch)
            self._trunk_patches[trunk] = patches
        return self._trunk_patches[trunk]

    def proof(self, oid: str, trunk: str, prs: list[dict]) -> dict:
        if any(pr.get("state") == "open" for pr in prs):
            raise Refused("in-flight open PR")
        ahead = self.git("rev-list", trunk + ".." + oid).splitlines()
        if self.ancestor(oid, trunk):
            return {"kind": "ancestor", "ahead": ahead}
        # Squash proof binds the entire candidate history to the exact merged
        # PR head, then compares its cumulative content with the landed commit.
        for pr in prs:
            merge = pr.get("merge_commit_sha")
            if not pr.get("merged_at") or pr["head"].get("sha") != oid or not merge:
                continue
            # A PR merged into a branch that was never fetched (stacked PRs)
            # leaves its merge commit absent locally: no evidence, not an error.
            if not self.has_commit(merge) or not self.ancestor(merge, trunk):
                continue
            parents = self.git("rev-list", "--parents", "-n", "1", merge).split()[1:]
            if len(parents) != 1:
                continue
            base = self.git("merge-base", oid, parents[0])
            candidate_patch = self.patch(base, oid)
            if candidate_patch and candidate_patch == self.patch(parents[0], merge):
                return {"kind": "exact-pr-head-squash", "pr": pr["number"],
                        "head": oid, "merge": merge, "ahead": ahead}
        # Squash-merge rewrites commit SHAs. Unique commits and per-commit
        # patch IDs are not merge evidence. Path blobs that already exist on
        # trunk (current tree or that path's history) prove the codebase landed.
        if self.content_on_trunk(oid, trunk):
            return {"kind": "content-on-trunk", "ahead": ahead}
        # Every non-upstream commit is accounted for. Merge commits and empty
        # patches are deliberately not silently omitted as they are by git cherry.
        upstream_patches = self.trunk_patches(trunk)
        covered = []
        for commit in ahead:
            parents = self.git("rev-list", "--parents", "-n", "1", commit).split()[1:]
            if len(parents) == 1 and self.patch(parents[0], commit) in upstream_patches:
                covered.append(commit)
        if ahead and covered == ahead and self.final_paths_match(oid, trunk):
            return {"kind": "every-commit-patch", "ahead": ahead}
        raise Refused("candidate history not proven in trunk")

    def evaluate(self, candidate: dict, context: dict, scope: str, *,
                 worktrees: list[dict] | None = None, heads: dict | None = None,
                 pr_cache: dict | None = None) -> dict:
        kind, ref, oid = candidate["kind"], candidate["ref"], candidate["oid"]
        if kind not in SCOPES[scope]:
            raise Refused("candidate outside authorized resource scope")
        if ref and not ref.startswith("refs/heads/"):
            raise Refused("candidate is not a branch ref")
        branch = ref.removeprefix("refs/heads/")
        protected = {"main", "master", "HEAD", context["trunk"],
                     context["current"].removeprefix("refs/heads/")}
        if branch and branch in protected:
            raise Refused("protected branch")
        worktrees = self.worktrees() if worktrees is None else worktrees
        result = {"kind": kind, "ref": ref, "oid": oid}
        if kind == "worktree":
            records = [wt for wt in worktrees if wt["worktree"] == candidate["path"]]
            if (len(records) != 1 or records[0] == worktrees[0]
                    or Path(candidate["path"]).resolve() == self.root):
                raise Refused("missing, main, or caller worktree")
            result.update(self.worktree_state(records[0]))
            if any(result[key] != candidate[key] for key in ("path", "oid", "ref")):
                raise Refused("worktree changed since discovery")
        elif kind == "local":
            self.git("check-ref-format", ref)
            if self.oid(ref) != oid:
                raise Refused("local ref changed since discovery")
            if any(wt.get("branch") == ref for wt in worktrees):
                raise Refused("branch checked out; remove worktree, then replan")
        elif kind == "remote":
            self.git("check-ref-format", ref)
            heads = self.remote_heads() if heads is None else heads
            if heads.get(ref) != oid:
                raise Refused("remote ref changed since discovery")
        if self.oid(oid) != oid:
            raise Refused("candidate must contain an immutable object ID")
        if branch:
            if pr_cache is not None:
                if branch not in pr_cache:
                    pr_cache[branch] = self.pull_requests(context["repository"], branch)
                prs = pr_cache[branch]
            else:
                prs = self.pull_requests(context["repository"], branch)
        else:
            prs = []
        result["proof"] = self.proof(oid, context["trunk_oid"], prs)
        return result

    def plan(self, scope: str, trunk: str | None = None) -> dict:
        context = self.context(trunk)
        worktrees = self.worktrees()
        remote_heads = self.remote_heads()
        candidates = []
        if "worktree" in SCOPES[scope]:
            for record in worktrees:
                path = record["worktree"]
                if Path(path).resolve() == self.root or record == worktrees[0]:
                    continue
                candidates.append({"kind": "worktree", "path": path,
                                   "ref": record.get("branch", ""), "oid": record.get("HEAD", "")})
        if "local" in SCOPES[scope]:
            for line in self.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/heads/").splitlines():
                ref, oid = line.split(" ")
                candidates.append({"kind": "local", "ref": ref, "oid": oid})
        if "remote" in SCOPES[scope]:
            for ref, oid in remote_heads.items():
                candidates.append({"kind": "remote", "ref": ref, "oid": oid})
        operations = self.active_operations(worktrees)
        actions, skipped, pr_cache = [], [], {}
        for candidate in candidates:
            try:
                self.assert_not_pinned(candidate, operations)
                actions.append(self.evaluate(candidate, context, scope, worktrees=worktrees,
                                             heads=remote_heads, pr_cache=pr_cache))
            except FAILURES as error:
                skipped.append({**candidate, "reason": str(error)})
        return {"version": 1, "scope": scope, "context": context, "actions": actions, "skipped": skipped}

    def revalidate(self, context: dict, action: dict) -> None:
        if self.context(context["trunk"]) != context:
            raise Refused("repository changed immediately before deletion")
        worktrees = self.worktrees()
        self.assert_not_pinned(action, self.active_operations(worktrees))
        if action["kind"] == "remote":
            if self.remote_heads().get(action["ref"]) != action["oid"]:
                raise Refused("remote ref changed immediately before deletion")
        elif action["kind"] == "local":
            if self.oid(action["ref"]) != action["oid"]:
                raise Refused("local ref changed immediately before deletion")
            if any(wt.get("branch") == action["ref"] for wt in worktrees):
                raise Refused("branch checked out immediately before deletion")
        elif action["kind"] == "worktree":
            records = [wt for wt in worktrees if wt["worktree"] == action["path"]]
            if len(records) != 1:
                raise Refused("worktree registration changed immediately before deletion")
            state = self.worktree_state(records[0])
            if any(state[key] != action[key] for key in ("path", "oid", "ref")):
                raise Refused("worktree HEAD changed immediately before deletion")

    def apply(self, plan: dict, scope: str, *, exclusive_worktrees: bool = False) -> dict:
        if (not isinstance(plan, dict) or plan.get("version") != 1 or plan.get("scope") != scope
                or not isinstance(plan.get("actions"), list) or not isinstance(plan.get("skipped"), list)
                or not all(isinstance(item, dict) for item in plan["actions"] + plan["skipped"])):
            raise Refused("plan format or authorized scope differs")
        if self.context(plan["context"]["trunk"]) != plan["context"]:
            raise Refused("repository, trunk, or current checkout changed; replan")
        results = []
        for action in plan["actions"]:
            try:
                if action["kind"] == "worktree" and not exclusive_worktrees:
                    raise Refused("exclusive worktree access not established")
                # Recompute proof and state immediately before each mutation.
                fresh = self.evaluate(action, plan["context"], scope)
                if fresh != action:
                    raise Refused("candidate evidence differs from the reviewed plan")
                self.revalidate(plan["context"], action)
                if action["kind"] == "local":
                    # CAS prevents deleting newer commits; never branch -D.
                    self.git("update-ref", "--no-deref", "-d", action["ref"], action["oid"])
                elif action["kind"] == "remote":
                    self.git("push", f"--force-with-lease={action['ref']}:{action['oid']}",
                             "origin", f":{action['ref']}")
                elif action["kind"] == "worktree":
                    self.git("worktree", "remove", "--", action["path"])
                else:
                    raise Refused("unknown action")
                results.append({**action, "result": "removed"})
            except FAILURES as error:
                results.append({**action, "result": "skipped", "reason": str(error)})
        return {**plan, "actions": results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("verify", "dry-run", "prune"), nargs="?", default="dry-run")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--scope", choices=SCOPES, default="all")
    parser.add_argument("--trunk")
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--confirmed", action="store_true")
    parser.add_argument("--exclusive-worktrees", action="store_true",
                        help="Assert exclusive access to candidate worktrees before removal")
    args = parser.parse_args()
    try:
        for executable in ("git", "gh"):
            if not shutil.which(executable):
                raise Refused(f"missing prerequisite: {executable}")
        repo = Repository(args.root)
        if args.mode == "prune":
            if not args.confirmed or not args.plan:
                raise Refused("prune requires the reviewed --plan and existing authorization via --confirmed")
            result = repo.apply(json.loads(args.plan.read_text()), args.scope,
                                exclusive_worktrees=args.exclusive_worktrees)
        else:
            result = repo.plan(args.scope, args.trunk)
        print(json.dumps(result, indent=2))
        return int(args.mode == "prune" and any(action["result"] == "skipped" for action in result["actions"]))
    except FAILURES as error:
        print(f"Cleanup stopped: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
