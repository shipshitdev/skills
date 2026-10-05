#!/usr/bin/env python3
"""Plan cleanup from immutable Git evidence; apply only an unchanged scoped plan."""

from __future__ import annotations

import argparse
import filecmp
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
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

    def __init__(self, message: str, audit: dict | None = None):
        super().__init__(message)
        self.audit = audit


FAILURES = (Refused, OSError, ValueError, KeyError, TypeError)

# Ignored directory names that tooling rebuilds from tracked sources or lockfiles.
REGENERABLE = {"node_modules", ".next", ".turbo", ".cache", ".parcel-cache", "dist", "build",
               "coverage", "generated", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
# Ignored files that tooling writes on every run.
REGENERABLE_FILES = {"next-env.d.ts"}
# Top-level ignored directory that holds disposable agent scratch.
SCRATCH = ".tmp"
# Reflog messages that move a ref without creating work on it.
CREATED = ("branch: Created from ", "Branch: renamed ")
# Proof kinds whose evidence is mechanical, so pruning needs no intent review.
REVIEW_FREE = ("no-own-commits", "merged-pr-head")


class Repository:
    def __init__(self, root: Path):
        # Audit the whole repository even when invoked from a subdirectory:
        # tree listings, pathspecs and `git apply` are all cwd-relative.
        top = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=False)
        self.root = Path(top.stdout.strip() if top.returncode == 0 and top.stdout.strip()
                         else root).resolve()
        self._trunk_entries: tuple[str, dict, set | None] | None = None

    def run(self, *args: str, input_text: str | None = None,
            accepted: tuple[int, ...] = (0,), extra_env: dict | None = None) -> subprocess.CompletedProcess:
        env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_NO_REPLACE_OBJECTS="1")
        env.update(extra_env or {})
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
        state = {"path": str(path.resolve()), "oid": head, "ref": branch}
        ignored = self.ignored_disposition(path, Path(self.worktrees()[0]["worktree"]))
        if any(ignored.values()):
            state["ignored"] = ignored
        return state

    def ignored_disposition(self, path: Path, main: Path) -> dict:
        """Classify ignored files; refuse any that exist only in this worktree."""
        listing = self.run("git", "-C", str(path), "ls-files", "--others", "--ignored",
                           "--exclude-standard", "--directory", "-z").stdout
        regenerable, duplicated, scratch, unique = [], [], [], []
        for entry in sorted(item for item in listing.split("\0") if item):
            relative = entry.rstrip("/")
            target = path / relative
            if relative == SCRATCH or relative.startswith(SCRATCH + "/"):
                scratch.append(entry)
                continue
            # Removal unlinks a symlink without following it, so a linked
            # node_modules counts as regenerable like a real directory.
            if self.regenerable(relative, target.is_dir() or target.is_symlink()):
                regenerable.append(entry)
                continue
            if target.is_dir() and not target.is_symlink():
                files = []
                for directory, names, filenames in os.walk(target):
                    links = [name for name in names if (Path(directory) / name).is_symlink()]
                    rebuilt = [name for name in names if name in REGENERABLE and name not in links]
                    regenerable.extend((Path(directory) / name).relative_to(path).as_posix() + "/"
                                       for name in sorted(rebuilt))
                    names[:] = sorted(name for name in names if name not in links + rebuilt)
                    files.extend(Path(directory) / name for name in sorted(filenames + links))
            else:
                files = [target]
            for file in files:
                name = file.relative_to(path).as_posix()
                if self.regenerable(name, False):
                    regenerable.append(name)
                elif self.duplicate(file, main / name, path):
                    duplicated.append(name)
                else:
                    unique.append(name)
        if unique:
            raise Refused("ignored files present only in this worktree; preserve or relocate them "
                          "before cleanup: " + ", ".join(unique[:5]))
        return {"regenerable": sorted(set(regenerable)), "duplicated": sorted(set(duplicated)),
                "scratch": sorted(scratch)}

    @staticmethod
    def regenerable(relative: str, is_directory: bool) -> bool:
        # The names cover directories only; a file called `build` is not output.
        *parents, last = relative.split("/")
        return (any(part in REGENERABLE for part in parents)
                or (is_directory and last in REGENERABLE) or last.endswith(".tsbuildinfo")
                or last in REGENERABLE_FILES)

    @staticmethod
    def duplicate(file: Path, original: Path, worktree: Path) -> bool:
        # A byte-identical copy in the main checkout survives the removal, unless
        # the main checkout reaches it through a link into this worktree.
        original = Path(os.path.realpath(original.parent)) / original.name
        if original.parent == worktree.resolve() or worktree.resolve() in original.parent.parents:
            return False
        if file.is_symlink():
            return original.is_symlink() and os.readlink(file) == os.readlink(original)
        # A main-checkout link (apps/workers/.env.local -> ../api/.env.local)
        # keeps its target, so a copy of that target survives unless the link
        # resolves into this worktree.
        target = Path(os.path.realpath(original))
        if target == worktree.resolve() or worktree.resolve() in target.parents:
            return False
        return file.is_file() and target.is_file() and filecmp.cmp(file, target, shallow=False)

    def unmoved_since_creation(self, ref: str, oid: str, worktree: str | None = None) -> bool:
        """The ref's reflog proves it never held a commit of its own."""
        prefix = ("-C", worktree) if worktree else ()
        log = self.run("git", *prefix, "reflog", "show", "--format=%H%x00%gs", ref, "--",
                       accepted=(0, 128)).stdout
        entries = [line.split("\0", 1) for line in log.splitlines() if line]
        if not entries or any(len(entry) != 2 or entry[0] != oid for entry in entries):
            return False
        # The oldest entry must record creation: an expired log restarted by a
        # rename or reset says nothing about commits the ref held before.
        if ref == "HEAD":
            # `worktree add --detach` logs an empty message, then resets to itself.
            return entries[-1][1] == "" and all(
                message in ("", "reset: moving to HEAD") for _, message in entries)
        return (entries[-1][1].startswith(CREATED[0])
                and all(message.startswith(CREATED) for _, message in entries))

    def remote_heads(self) -> dict[str, str]:
        return {ref: oid for oid, ref in (line.split("\t") for line in
                self.git("ls-remote", "--heads", "origin").splitlines())}

    def fetch_objects(self, *refs: str) -> None:
        """Fetch objects for refs without creating or moving any local ref."""
        # An empty refmap stops the opportunistic remote-tracking update.
        fetch = ("git", "fetch", "--no-write-fetch-head", "--no-prune", "--refmap=", "origin")
        if refs and self.run(*fetch, *refs, accepted=(0, 1, 128)).returncode != 0:
            # One vanished ref fails the batch; retry the rest one at a time.
            for ref in refs if len(refs) > 1 else ():
                self.run(*fetch, ref, accepted=(0, 1, 128))

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

    def tree_entries(self, commit: str) -> dict[str, dict]:
        entries = {}
        for entry in self.run("git", "ls-tree", "-r", "-z", commit).stdout.split("\0"):
            if entry:
                metadata, path = entry.split("\t", 1)
                mode, kind, blob = metadata.split()
                entries[path] = {"mode": mode, "type": kind, "oid": blob}
        return entries

    def current_content_audit(self, oid: str, trunk: str, prs: list[dict]) -> dict:
        bases = self.git("merge-base", "--all", oid, trunk).splitlines()
        if len(bases) != 1:
            raise Refused("ambiguous merge base; current content cannot be proven")
        base = bases[0]
        scope = "branch-delta"
        # An ancestor has no ahead delta. Recover a complete PR boundary when
        # available; otherwise compare its entire snapshot conservatively.
        if base == oid:
            for pr in prs:
                merge = pr.get("merge_commit_sha")
                if (pr.get("merged_at") and pr["head"].get("sha") == oid
                        and merge and self.has_commit(merge) and self.ancestor(merge, trunk)):
                    parents = self.git("rev-list", "--parents", "-n", "1", merge).split()[1:]
                    if parents:
                        boundaries = self.git("merge-base", "--all", oid, parents[0]).splitlines()
                        if len(boundaries) == 1 and boundaries[0] != oid:
                            base = boundaries[0]
                            break
            if base == oid:
                scope = "candidate-snapshot"
        if self._trunk_entries is None or self._trunk_entries[0] != trunk:
            self._trunk_entries = (trunk, self.tree_entries(trunk), None)
        trunk_entries = self._trunk_entries[1]
        candidate_entries = trunk_entries if oid == trunk else self.tree_entries(oid)
        base_entries = {} if scope == "candidate-snapshot" else self.tree_entries(base)
        paths = sorted(path for path in base_entries.keys() | candidate_entries.keys()
                       if base_entries.get(path) != candidate_entries.get(path))
        if self._trunk_entries[2] is None:
            self._trunk_entries = (*self._trunk_entries[:2], {
                parent for path in trunk_entries
                for parent in (path.rsplit("/", i)[0] for i in range(1, path.count("/") + 1))})
        trunk_dirs = self._trunk_entries[2]
        if scope == "candidate-snapshot":
            # Without a boundary, a trunk-only path is either a later trunk
            # addition or a candidate deletion that trunk restored. Audit every
            # trunk path the candidate's history deleted so a restore cannot
            # pass as present.
            trunk_only = trunk_entries.keys() - candidate_entries.keys()
            if trunk_only:
                deleted = set(self.git("log", "--no-renames", "--diff-filter=D", "--name-only",
                                       "-z", "--format=", oid).split("\0"))
                paths = sorted(set(paths) | (deleted & trunk_only))
        evidence = []
        for path in paths:
            before, candidate, current = (entries.get(path) for entries in
                                          (base_entries, candidate_entries, trunk_entries))
            # Trunk may replace a deleted file or symlink with a directory; the
            # blob-only listing omits it, so absence must not be inferred there.
            if current is None and path in trunk_dirs:
                current = {"mode": "040000", "type": "tree", "oid": None}
            state = "exact-entry" if candidate == current else (
                "restored-on-trunk" if candidate is None and scope == "candidate-snapshot" else
                "unchanged-on-trunk" if current == before else "both-changed")
            item = {"path": path, "base": before, "candidate": candidate,
                    "trunk": current, "state": state}
            if (state != "exact-entry" and scope != "candidate-snapshot"
                    and candidate and candidate["type"] == "blob"):
                item["history_reference"] = self.git("log", "-1", "--pretty=%H",
                    f"--find-object={candidate['oid']}", trunk, "--", path) or None
            evidence.append(item)
        # For ordinary text modifications, a reverse application against an
        # isolated index proves the complete candidate patch is still present
        # despite independent trunk edits. Never touch the real index/worktree.
        unmatched = [item for item in evidence if item["state"] != "exact-entry"]
        if unmatched and scope == "branch-delta":
            eligible = []
            for item in unmatched:
                before, candidate, current = item["base"], item["candidate"], item["trunk"]
                if (before and candidate and current
                        and before["mode"] in ("100644", "100755")
                        and candidate["mode"] == current["mode"]
                        and candidate["mode"] in ("100644", "100755")):
                    stat = self.run("git", "diff", "--no-ext-diff", "--no-textconv",
                        "--numstat", "-z", base, oid, "--", ":(literal)" + item["path"]).stdout
                    if stat and not stat.startswith("-\t"):
                        eligible.append(item)
            if eligible:
                patch = self.run("git", "diff", "--no-ext-diff", "--no-textconv", "--no-renames",
                    "--src-prefix=a/", "--dst-prefix=b/",
                    "--binary", base, oid, "--", *[":(literal)" + item["path"] for item in eligible]).stdout
                with tempfile.TemporaryDirectory(prefix="git-cleanup-index-") as directory:
                    env = {"GIT_INDEX_FILE": str(Path(directory) / "index")}
                    self.run("git", "read-tree", trunk, extra_env=env)
                    check = self.run("git", "-c", "apply.ignoreWhitespace=no", "apply", "--cached",
                        "--reverse", "--check", "--whitespace=nowarn", input_text=patch,
                        accepted=(0, 1), extra_env=env)
                if check.returncode == 0:
                    digest = hashlib.sha256(patch.encode("utf-8", "surrogateescape")).hexdigest()
                    for item in eligible:
                        item.update(state="patch-present", patch_sha256=digest)
        present = bool(evidence) and all(item["state"] in ("exact-entry", "patch-present")
                                        for item in evidence)
        if not evidence and self.git("rev-parse", oid + "^{tree}") == self.git("rev-parse", trunk + "^{tree}"):
            present = self.ancestor(oid, trunk)
        return {"base_oid": base, "candidate_oid": oid, "trunk_oid": trunk,
                "scope": scope, "candidate_in_trunk_history": self.ancestor(oid, trunk),
                "current_content_present": present, "paths": evidence}

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

    def merged_pr_head(self, oid: str, trunk: str, prs: list[dict]) -> dict | None:
        """A same-repository PR merged into trunk whose head is or contains this tip."""
        for pr in prs:
            head, merge = (pr.get("head") or {}).get("sha"), pr.get("merge_commit_sha")
            if not (pr.get("merged_at") and head and merge
                    and self.has_commit(merge) and self.ancestor(merge, trunk)):
                continue
            if head == oid:
                return pr
            # Commits pushed to the PR from elsewhere leave this tip behind the
            # merged head; everything it holds was still delivered.
            if not self.has_commit(head):
                self.fetch_objects(f"refs/pull/{pr['number']}/head")
            if self.has_commit(head) and self.ancestor(oid, head):
                return pr
        return None

    def commit_pull_requests(self, repository: str, oid: str) -> list[dict]:
        """PRs containing a commit; a detached worktree has no branch to look up."""
        result = self.run("gh", "api", "--method", "GET", "--paginate", "--slurp",
                          f"repos/{repository}/commits/{oid}/pulls", "-f", "per_page=100",
                          accepted=(0, 1))
        if result.returncode != 0:
            # An unpushed commit has no PR on GitHub.
            return []
        records = []
        for page in json.loads(result.stdout):
            for pr in page:
                repos = [((pr.get(side) or {}).get("repo") or {}).get("full_name", "").lower()
                         for side in ("head", "base")]
                if repos == [repository.lower()] * 2:
                    records.append(pr)
        return records

    @staticmethod
    def unproven(prs: list[dict]) -> str:
        """Why a candidate's work is not on trunk, in terms of its PR history."""
        merged = [pr["number"] for pr in prs if pr.get("merged_at")]
        closed = [pr["number"] for pr in prs if pr.get("state") == "closed" and not pr.get("merged_at")]
        if merged:
            return f"not on trunk: commits beyond merged PR #{merged[0]}"
        if closed:
            return f"not on trunk: PR #{closed[0]} closed without merging"
        return "not on trunk: no PR"

    def proof(self, oid: str, trunk: str, prs: list[dict], *, unmoved: bool = False) -> dict:
        if any(pr.get("state") == "open" for pr in prs):
            raise Refused("in-flight open PR")
        if unmoved and self.ancestor(oid, trunk):
            # The ref only ever pointed at a trunk commit, so it never held work
            # that trunk could have reverted; there is no delta to audit.
            return {"kind": "no-own-commits", "ahead": [], "content_audit": {
                "base_oid": oid, "candidate_oid": oid, "trunk_oid": trunk,
                "scope": "no-own-commits", "candidate_in_trunk_history": True,
                "current_content_present": True, "paths": []}}
        ahead = self.git("rev-list", trunk + ".." + oid).splitlines()
        try:
            audit = self.current_content_audit(oid, trunk, prs)
        except Refused as error:
            # Criss-cross merges leave no single audit base; a merged PR head
            # still proves delivery without one.
            pr = self.merged_pr_head(oid, trunk, prs)
            if not pr:
                raise
            audit = {"base_oid": oid, "candidate_oid": oid, "trunk_oid": trunk,
                     "scope": "unavailable", "error": str(error),
                     "candidate_in_trunk_history": False, "current_content_present": False,
                     "paths": []}
        if not audit["current_content_present"]:
            # Trunk may edit or revert code after it lands. When GitHub records
            # this exact tip as a merged PR whose merge commit is on trunk, the
            # work was delivered; later trunk changes are trunk's own decisions.
            pr = self.merged_pr_head(oid, trunk, prs)
            if pr:
                return {"kind": "merged-pr-head", "pr": pr["number"], "head": pr["head"]["sha"],
                        "merge": pr["merge_commit_sha"], "ahead": ahead, "content_audit": audit}
            raise Refused(self.unproven(prs) + "; inspect code and intent, preserve candidate", audit)
        if self.ancestor(oid, trunk):
            return {"kind": "ancestor", "ahead": ahead, "content_audit": audit}
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
                        "head": oid, "merge": merge, "ahead": ahead, "content_audit": audit}
        # Current content, independent of commit identities or the original PR.
        return {"kind": "content-on-trunk", "ahead": ahead, "content_audit": audit}

    def evaluate(self, candidate: dict, context: dict, scope: str, *,
                 worktrees: list[dict] | None = None, heads: dict | None = None,
                 pr_cache: dict | None = None, released: set[str] = frozenset()) -> dict:
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
        unmoved = False
        if kind == "worktree":
            records = [wt for wt in worktrees if wt["worktree"] == candidate["path"]]
            if (len(records) != 1 or records[0] == worktrees[0]
                    or Path(candidate["path"]).resolve() == self.root):
                raise Refused("missing, main, or caller worktree")
            result.update(self.worktree_state(records[0]))
            if any(result[key] != candidate[key] for key in ("path", "oid", "ref")):
                raise Refused("worktree changed since discovery")
            unmoved = (self.unmoved_since_creation(ref, oid) if ref else
                       self.unmoved_since_creation("HEAD", oid, records[0]["worktree"]))
        elif kind == "local":
            self.git("check-ref-format", ref)
            if self.oid(ref) != oid:
                raise Refused("local ref changed since discovery")
            checkouts = sorted(wt["worktree"] for wt in worktrees if wt.get("branch") == ref)
            if any(path not in released for path in checkouts):
                raise Refused("branch checked out; remove worktree, then replan")
            if checkouts:
                # Deleted in the same run, only after its worktree removal succeeds.
                result["after_worktrees"] = checkouts
            unmoved = self.unmoved_since_creation(ref, oid)
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
        elif pr_cache is not None:
            if "@" + oid not in pr_cache:
                pr_cache["@" + oid] = self.commit_pull_requests(context["repository"], oid)
            prs = pr_cache["@" + oid]
        else:
            prs = self.commit_pull_requests(context["repository"], oid)
        result["proof"] = self.proof(oid, context["trunk_oid"], prs, unmoved=unmoved)
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
            # Only trunk is fetched; prove other remote branches from their own objects.
            self.fetch_objects(*sorted(ref for ref, oid in remote_heads.items()
                                       if not self.has_commit(oid)))
            for ref, oid in remote_heads.items():
                candidates.append({"kind": "remote", "ref": ref, "oid": oid})
        operations = self.active_operations(worktrees)
        actions, skipped, pr_cache, released = [], [], {}, set()
        # Worktree candidates come first, so a branch checked out only in
        # removable worktrees is planned in the same pass.
        for candidate in candidates:
            try:
                self.assert_not_pinned(candidate, operations)
                actions.append(self.evaluate(candidate, context, scope, worktrees=worktrees,
                                             heads=remote_heads, pr_cache=pr_cache,
                                             released=released))
                if candidate["kind"] == "worktree":
                    released.add(candidate["path"])
            except FAILURES as error:
                item = {**candidate, "reason": str(error)}
                if isinstance(error, Refused) and error.audit is not None:
                    item["content_audit"] = error.audit
                skipped.append(item)
        kept: dict[str, int] = {}
        for item in skipped:
            reason = re.sub(r"#\d+", "#N", item["reason"].split(";")[0])
            kept[reason] = kept.get(reason, 0) + 1
        return {"version": 2, "scope": scope, "context": context,
                "summary": {"removable": len(actions), "kept": dict(sorted(kept.items()))},
                "actions": actions, "skipped": skipped, "intent_reviews": {}}

    def same_repository(self, planned: dict, current: dict) -> bool:
        """Only trunk may have moved forward, and HEAD with it when HEAD is the trunk checkout."""
        if planned.keys() != current.keys() or any(
                planned[key] != current[key] for key in planned if key not in ("trunk_oid", "head")):
            return False
        if not self.ancestor(planned["trunk_oid"], current["trunk_oid"]):
            return False
        # Fetching fast-forwards a trunk checkout; a local commit there still stops.
        return planned["head"] == current["head"] or (
            current["current"] == f"refs/heads/{current['trunk']}"
            and current["head"] == current["trunk_oid"]
            and self.ancestor(planned["head"], current["head"]))

    @staticmethod
    def unchanged(action: dict, fresh: dict) -> bool:
        """Fresh evidence still matches the reviewed action.

        Against the planned trunk every field must match. After trunk advanced,
        the candidate and proof kind must match, plus whatever the intent review
        is bound to; the fresh evaluation already re-proved it on the new trunk.
        """
        planned = {key: value for key, value in action.items() if key != "after_worktrees"}
        if fresh == planned:
            return True
        old, new = planned.get("proof", {}), fresh.get("proof", {})
        if old.get("content_audit", {}).get("trunk_oid") == new.get("content_audit", {}).get("trunk_oid"):
            return False
        return ({k: v for k, v in fresh.items() if k != "proof"} == {k: v for k, v in planned.items() if k != "proof"}
                and old.get("kind") == new.get("kind") and old.get("pr") == new.get("pr")
                and old["content_audit"]["base_oid"] == new["content_audit"]["base_oid"])

    def revalidate(self, context: dict, action: dict) -> None:
        if not self.same_repository(context, self.context(context["trunk"])):
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
        if (not isinstance(plan, dict) or plan.get("version") != 2 or plan.get("scope") != scope
                or not isinstance(plan.get("actions"), list) or not isinstance(plan.get("skipped"), list)
                or not all(isinstance(item, dict) for item in plan["actions"] + plan["skipped"])):
            raise Refused("plan format or authorized scope differs")
        context = self.context(plan["context"]["trunk"])
        if not self.same_repository(plan["context"], context):
            raise Refused("repository, trunk, or current checkout changed; replan")
        results, removed = [], {}
        for action in plan["actions"]:
            try:
                reviews = plan.get("intent_reviews", {})
                if not isinstance(reviews, dict):
                    raise Refused("invalid intent review records; preserve candidate")
                audit = action["proof"]["content_audit"]
                review = reviews.get(f"{action['oid']}:{audit['base_oid']}", {})
                if not isinstance(review, dict):
                    raise Refused("invalid intent review record; preserve candidate")
                # A ref that never held its own commits has no intent to review,
                # and a merged PR head already carries GitHub's merge record;
                # the fresh evaluation below rejects a forged proof kind.
                if action["proof"].get("kind") not in REVIEW_FREE and (
                        review.get("status") != "verified"
                        or review.get("candidate_oid") != action["oid"]
                        or review.get("trunk_oid") != plan["context"]["trunk_oid"]
                        or review.get("base_oid") != audit["base_oid"]
                        or not isinstance(review.get("summary"), str) or not review["summary"].strip()
                        or not isinstance(review.get("evidence"), list) or not review["evidence"]
                        or not all(isinstance(item, str) and item.strip() for item in review["evidence"])):
                    raise Refused("verified code/intent review missing or stale; preserve candidate")
                if action["kind"] == "worktree" and not exclusive_worktrees:
                    raise Refused("exclusive worktree access not established")
                if any(removed.get(path) != "removed" for path in action.get("after_worktrees", [])):
                    raise Refused("worktree holding this branch was not removed")
                # Recompute proof and state immediately before each mutation, against
                # the trunk fetched for this run; revalidation accepts later advances.
                if not self.unchanged(action, self.evaluate(action, context, scope)):
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
            if action.get("kind") == "worktree":
                removed[action.get("path")] = results[-1]["result"]
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
