from __future__ import annotations

import copy
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))
import cleanup
from cleanup import Refused, Repository  # noqa: E402


class GitFixtureTests(unittest.TestCase):
    def setUp(self):
        scratch = SKILL_DIR.parents[1] / ".tmp"
        scratch.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.root = self.directory / "repo"
        self.remote = self.directory / "origin.git"
        self.command("git", "init", "--bare", str(self.remote))
        self.command("git", "init", "-b", "main", str(self.root))
        self.repo = Repository(self.root)
        self.git("config", "user.name", "Cleanup Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("remote", "add", "origin", str(self.remote))
        self.commit("base", "base\n")
        self.git("push", "-u", "origin", "main")
        self.prs = []
        original_run = self.repo.run

        def run(*args, **kwargs):
            if args[:2] == ("gh", "repo"):
                return subprocess.CompletedProcess(args, 0, json.dumps({
                    "nameWithOwner": "owner/repo", "defaultBranchRef": {"name": "main"}
                }), "")
            if args[:2] == ("gh", "api"):
                return subprocess.CompletedProcess(args, 0, json.dumps([self.prs]), "")
            return original_run(*args, **kwargs)

        self.run_mock = patch.object(self.repo, "run", side_effect=run)
        self.run_mock.start()
        self.addCleanup(self.run_mock.stop)

    def command(self, *args, **kwargs):
        return subprocess.run(args, text=True, capture_output=True, check=True, **kwargs).stdout.strip()

    def git(self, *args):
        return self.command("git", "-C", str(self.root), *args)

    def commit(self, message, content, filename="file.txt"):
        (self.root / filename).write_text(content)
        self.git("add", filename)
        self.git("commit", "-m", message)
        return self.git("rev-parse", "HEAD")

    def squash(self, *, head_repo="owner/repo"):
        self.git("switch", "-c", "feature")
        self.commit("same subject", "first\n")
        head = self.commit("same subject", "second\n")
        self.git("switch", "main")
        self.git("merge", "--squash", "feature")
        self.git("commit", "-m", "same subject")
        merge = self.git("rev-parse", "HEAD")
        self.git("push", "origin", "main")
        self.prs = [{"number": 1, "state": "closed", "merged_at": "2026-01-01",
                     "merge_commit_sha": merge,
                     "head": {"ref": "feature", "sha": head, "repo": {"full_name": head_repo}},
                     "base": {"repo": {"full_name": "owner/repo"}}}]
        return head, merge

    def action_names(self, plan):
        return [action["ref"] for action in plan["actions"]]

    def test_exact_squash_head_is_proven_and_deleted_with_cas(self):
        self.squash()
        plan = self.repo.plan("local-branches")
        self.assertEqual(self.action_names(plan), ["refs/heads/feature"])
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "exact-pr-head-squash")
        self.assertEqual(self.repo.apply(plan, "local-branches")["actions"][0]["result"], "removed")
        self.assertNotIn("feature", self.git("branch", "--format=%(refname:short)").splitlines())

    def test_commits_added_after_merged_pr_are_preserved(self):
        self.squash()
        self.git("switch", "feature")
        self.commit("same subject", "unmerged\n")
        self.git("switch", "main")
        self.assertEqual(self.repo.plan("local-branches")["actions"], [])

    def test_fork_pr_metadata_cannot_prove_squash(self):
        self.squash(head_repo="fork/repo")
        plan = self.repo.plan("local-branches")
        self.assertEqual(self.action_names(plan), ["refs/heads/feature"])
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "content-on-trunk")

    def test_missing_head_repository_cannot_prove_squash(self):
        self.squash()
        self.prs[0]["head"]["repo"] = None
        plan = self.repo.plan("local-branches")
        self.assertEqual(self.action_names(plan), ["refs/heads/feature"])
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "content-on-trunk")

    def test_same_subject_different_patch_is_not_proof(self):
        self.git("switch", "-c", "feature")
        self.commit("same subject", "branch only\n")
        self.git("switch", "main")
        self.commit("same subject", "trunk only\n")
        self.git("push", "origin", "main")
        self.assertEqual(self.repo.plan("local-branches")["actions"], [])

    def test_mixed_ahead_commits_are_not_hidden_by_one_matching_patch(self):
        self.git("switch", "-c", "feature")
        first = self.commit("first", "first\n")
        self.commit("second", "second\n")
        self.git("switch", "main")
        self.git("cherry-pick", first)
        self.git("push", "origin", "main")
        self.assertEqual(self.repo.plan("local-branches")["actions"], [])

    def test_patch_proof_covers_every_rebased_commit(self):
        self.git("switch", "-c", "feature")
        first = self.commit("first", "first\n")
        second = self.commit("second", "second\n")
        self.git("switch", "main")
        self.commit("other", "other\n", "other.txt")
        self.git("cherry-pick", first, second)
        self.git("push", "origin", "main")
        plan = self.repo.plan("local-branches")
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "content-on-trunk")
        self.assertEqual(len(plan["actions"][0]["proof"]["ahead"]), 2)

    def test_whitespace_difference_is_not_patch_equivalence(self):
        self.git("switch", "-c", "feature")
        self.commit("indent", " x\n")
        self.git("switch", "main")
        self.commit("indent", "  x\n")
        self.git("push", "origin", "main")
        self.assertEqual(self.repo.plan("local-branches")["actions"], [])

    def test_terminal_added_line_whitespace_is_not_stripped_from_proof(self):
        self.git("switch", "-c", "feature")
        feature = self.commit("trailing whitespace", "x \n")
        self.git("switch", "main")
        trunk = self.commit("no trailing whitespace", "x\n")
        base = self.git("merge-base", feature, trunk)
        self.assertNotEqual(self.repo.patch(base, feature), self.repo.patch(base, trunk))
        self.git("push", "origin", "main")
        self.assertEqual(self.repo.plan("local-branches")["actions"], [])

    def test_historical_path_blobs_prove_content_even_after_trunk_reverts(self):
        self.git("switch", "-c", "feature")
        first = self.commit("first feature", "first\n", "first.txt")
        second = self.commit("second feature", "second\n", "second.txt")
        self.git("switch", "main")
        self.commit("diverge", "other\n", "other.txt")
        self.git("cherry-pick", first)
        self.git("revert", "--no-edit", "HEAD")
        self.git("cherry-pick", second)
        self.git("revert", "--no-edit", "HEAD")
        self.git("push", "origin", "main")
        plan = self.repo.plan("local-branches")
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "content-on-trunk")

    def test_empty_commit_is_not_content_proof(self):
        self.git("switch", "-c", "feature")
        self.git("commit", "--allow-empty", "-m", "empty")
        self.git("switch", "main")
        self.assertEqual(self.repo.plan("local-branches")["actions"], [])

    def test_merge_of_already_landed_files_is_content_on_trunk(self):
        self.git("switch", "-c", "feature")
        self.git("commit", "--allow-empty", "-m", "empty")
        self.git("switch", "-c", "side")
        self.commit("side", "side\n", "side.txt")
        self.git("switch", "feature")
        self.git("merge", "--no-ff", "side", "-m", "merge")
        self.git("switch", "main")
        self.git("cherry-pick", "side")
        self.git("push", "origin", "main")
        plan = self.repo.plan("local-branches")
        self.assertIn("refs/heads/feature", self.action_names(plan))
        self.assertEqual(
            next(action["proof"]["kind"] for action in plan["actions"]
                 if action["ref"] == "refs/heads/feature"),
            "content-on-trunk")

    def test_protected_branch_names_are_literal_strings(self):
        self.git("branch", "release.v1")
        self.git("branch", "releaseXv1")
        self.git("branch", "master")
        self.git("push", "origin", "release.v1")
        plan = self.repo.plan("local-branches", "release.v1")
        self.assertEqual(self.action_names(plan), ["refs/heads/releaseXv1"])

    def test_changed_ref_is_skipped(self):
        self.git("branch", "feature")
        plan = self.repo.plan("local-branches")
        self.git("switch", "feature")
        new = self.commit("new", "new\n")
        self.git("switch", "main")
        self.assertEqual(self.repo.apply(plan, "local-branches")["actions"][0]["result"], "skipped")
        self.assertEqual(self.git("rev-parse", "feature"), new)

    def test_current_head_or_trunk_change_stops_apply(self):
        self.git("branch", "feature")
        plan = self.repo.plan("local-branches")
        self.commit("new trunk", "new\n")
        with self.assertRaises(Refused):
            self.repo.apply(plan, "local-branches")

    def test_alternate_push_destination_is_rejected_before_planning(self):
        self.git("config", "remote.origin.pushurl", "https://github.com/other/repo.git")
        with self.assertRaises(Refused):
            self.repo.plan("remote-branches")

    def test_scope_and_repository_identity_are_bound_to_plan(self):
        self.git("branch", "feature")
        plan = self.repo.plan("local-branches")
        with self.assertRaises(Refused):
            self.repo.apply(plan, "all")
        plan["context"]["repository"] = "different/repo"
        with self.assertRaises(Refused):
            self.repo.apply(plan, "local-branches")

    def test_open_pr_prevents_deletion_even_when_ancestor(self):
        self.git("branch", "feature")
        self.prs = [{"state": "open", "head": {"ref": "feature", "repo": {"full_name": "owner/repo"}},
                     "base": {"repo": {"full_name": "owner/repo"}}}]
        self.assertEqual(self.repo.plan("local-branches")["actions"], [])

    def test_open_stacked_pr_preserves_its_base_branch(self):
        self.git("branch", "feature")
        self.prs = [{"state": "open", "head": {"ref": "child", "repo": {"full_name": "owner/repo"}},
                     "base": {"ref": "feature", "repo": {"full_name": "owner/repo"}}}]
        self.assertEqual(self.repo.plan("local-branches")["actions"], [])

    def test_apply_does_not_replan_every_branch_for_every_action(self):
        for index in range(4):
            self.git("branch", f"feature-{index}")
        plan = self.repo.plan("local-branches")
        self.repo.run.reset_mock()
        self.repo.apply(plan, "local-branches")
        queries = [call.args for call in self.repo.run.call_args_list if call.args[:2] == ("gh", "api")]
        self.assertLessEqual(len(queries), 8)

    def test_non_utf8_patch_roundtrips_without_losing_bytes(self):
        base = self.git("rev-parse", "HEAD")
        (self.root / "file.txt").write_bytes(b"latin-1: \xe9\n")
        self.git("add", "file.txt")
        self.git("commit", "-m", "non utf8")
        first = self.git("rev-parse", "HEAD")
        self.git("reset", "--hard", base)
        (self.root / "file.txt").write_bytes(b"latin-1: \xe8\n")
        self.git("add", "file.txt")
        self.git("commit", "-m", "different non utf8")
        second = self.git("rev-parse", "HEAD")
        self.assertNotEqual(self.repo.patch(base, first), self.repo.patch(base, second))

    def test_rebase_pins_branch_while_worktree_head_is_detached(self):
        self.commit("second", "second\n")
        self.git("push", "origin", "main")
        worktree = self.make_worktree()
        editor = self.directory / "editor.py"
        editor.write_text("import sys\nfrom pathlib import Path\np=Path(sys.argv[1])\np.write_text(p.read_text().replace('pick ', 'edit ', 1))\n")
        self.command("git", "-C", str(worktree), "rebase", "-i", "--force-rebase", "HEAD~1",
                     env=dict(os.environ, GIT_SEQUENCE_EDITOR=f"{sys.executable} {editor}"))
        detached = subprocess.run(["git", "-C", str(worktree), "symbolic-ref", "-q", "HEAD"],
                                  capture_output=True, check=False)
        self.assertEqual(detached.returncode, 1)
        self.assertNotIn("refs/heads/feature", self.action_names(self.repo.plan("local-branches")))

    def test_trunk_patch_scan_is_cached_by_immutable_oid(self):
        self.git("switch", "-c", "feature")
        feature = self.commit("feature", "feature\n")
        self.git("branch", "feature-1")
        self.git("branch", "feature-2")
        self.git("switch", "main")
        self.commit("other", "other\n", "other.txt")
        self.git("cherry-pick", feature)
        self.git("push", "origin", "main")
        self.repo.run.reset_mock()
        plan = self.repo.plan("local-branches")
        result = self.repo.apply(plan, "local-branches")
        self.assertEqual(len(result["actions"]), 3)
        self.assertTrue(all(item["result"] == "removed" for item in result["actions"]))
        self.assertTrue(all(item["proof"]["kind"] == "content-on-trunk" for item in result["actions"]))
        scans = [call.args for call in self.repo.run.call_args_list
                 if call.args[:3] == ("git", "rev-list", "--max-count=500")]
        self.assertEqual(len(scans), 0)

    def test_exact_pr_proof_does_not_scan_trunk_history(self):
        self.squash()
        self.repo.run.reset_mock()
        plan = self.repo.plan("local-branches")
        self.assertEqual(len(plan["actions"]), 1)
        self.assertFalse(any(call.args[:3] == ("git", "rev-list", "--max-count=500")
                             for call in self.repo.run.call_args_list))

    def test_partial_apply_preserves_completed_results_after_data_errors(self):
        errors = [ValueError("bad JSON"), TypeError("bad metadata"),
                  UnicodeDecodeError("utf-8", b"\xff", 0, 1, "bad bytes")]
        original = self.repo.evaluate
        for index, error in enumerate(errors):
            with self.subTest(error=type(error).__name__):
                self.git("branch", f"a{index}")
                self.git("branch", f"b{index}")
                plan = self.repo.plan("local-branches")
                def evaluate(candidate, *args, **kwargs):
                    if candidate["ref"] == f"refs/heads/b{index}":
                        raise error
                    return original(candidate, *args, **kwargs)
                with patch.object(self.repo, "evaluate", side_effect=evaluate):
                    result = self.repo.apply(plan, "local-branches")
                self.assertEqual([item["result"] for item in result["actions"]], ["removed", "skipped"])
                self.assertEqual(result["context"], plan["context"])
                self.assertEqual(result["skipped"], plan["skipped"])
                self.git("branch", "-d", f"b{index}")

    def test_apply_refreshes_base_pr_protection_after_plan(self):
        self.git("branch", "feature")
        plan = self.repo.plan("local-branches")
        self.prs = [{"state": "open", "head": {"ref": "child", "repo": {"full_name": "fork/repo"}},
                     "base": {"ref": "feature", "repo": {"full_name": "owner/repo"}}}]
        self.assertEqual(self.repo.apply(plan, "local-branches")["actions"][0]["result"], "skipped")
        self.assertEqual(self.git("rev-parse", "feature"), self.git("rev-parse", "main"))

    def test_tampered_action_cannot_bypass_protection_scope_or_proof(self):
        self.git("branch", "feature")
        plan = self.repo.plan("local-branches")
        for field, value in (("ref", "refs/heads/main"), ("kind", "remote"), ("proof", {})):
            changed = copy.deepcopy(plan)
            changed["actions"][0][field] = value
            self.assertEqual(self.repo.apply(changed, "local-branches")["actions"][0]["result"], "skipped")
        self.assertEqual(self.git("rev-parse", "feature"), self.git("rev-parse", "main"))

    def test_main_requires_authorization_and_emits_complete_report_without_jq(self):
        self.git("branch", "feature")
        plan = self.repo.plan("local-branches")
        plan_path = self.directory / "plan.json"
        plan_path.write_text(json.dumps(plan))
        args = ["cleanup.py", "prune", "--root", str(self.root), "--scope", "local-branches", "--plan", str(plan_path)]
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(cleanup, "Repository", return_value=self.repo), \
             patch.object(cleanup.shutil, "which", side_effect=lambda name: None if name == "jq" else "/fixture/tool"), \
             patch.object(sys, "argv", args), patch.object(sys, "stdout", stdout), patch.object(sys, "stderr", stderr):
            self.assertEqual(cleanup.main(), 1)
            self.assertIn("requires the reviewed", stderr.getvalue())
            sys.argv = args + ["--confirmed"]
            self.assertEqual(cleanup.main(), 0)
        report = json.loads(stdout.getvalue())
        self.assertEqual(report["context"], plan["context"])
        self.assertEqual(report["scope"], "local-branches")
        self.assertEqual(report["skipped"], plan["skipped"])
        self.assertEqual(report["actions"][0]["result"], "removed")

    def test_main_reports_partial_completion_with_nonzero_status(self):
        self.git("branch", "a")
        self.git("branch", "b")
        plan = self.repo.plan("local-branches")
        plan_path = self.directory / "partial-plan.json"
        plan_path.write_text(json.dumps(plan))
        original = self.repo.evaluate
        def evaluate(candidate, *args, **kwargs):
            if candidate["ref"] == "refs/heads/b":
                raise ValueError("bad API metadata")
            return original(candidate, *args, **kwargs)
        args = ["cleanup.py", "prune", "--scope", "local-branches", "--plan", str(plan_path), "--confirmed"]
        stdout = io.StringIO()
        with patch.object(cleanup, "Repository", return_value=self.repo), \
             patch.object(self.repo, "evaluate", side_effect=evaluate), \
             patch.object(cleanup.shutil, "which", return_value="/fixture/tool"), \
             patch.object(sys, "argv", args), patch.object(sys, "stdout", stdout):
            self.assertEqual(cleanup.main(), 1)
        report = json.loads(stdout.getvalue())
        self.assertEqual([item["result"] for item in report["actions"]], ["removed", "skipped"])
        self.assertEqual(report["skipped"], plan["skipped"])

    def test_operation_started_after_planning_blocks_apply(self):
        self.git("branch", "feature")
        plan = self.repo.plan("local-branches")
        # Git am and rebase --apply use this metadata while the original ref can
        # remain detached from HEAD. Exercise the execution-time guard directly.
        operation = self.root / ".git/rebase-apply"
        operation.mkdir()
        (operation / "head-name").write_text("refs/heads/feature\n")
        result = self.repo.apply(plan, "local-branches")
        self.assertEqual(result["actions"][0]["result"], "skipped")
        self.assertEqual(self.git("rev-parse", "feature"), self.git("rev-parse", "main"))

    def test_git_error_is_never_an_empty_success(self):
        self.git("branch", "feature")
        original = self.repo.git
        def git(*args):
            if args[0] == "rev-list":
                raise Refused("injected rev-list failure")
            return original(*args)
        with patch.object(self.repo, "git", side_effect=git):
            self.assertEqual(self.repo.plan("local-branches")["actions"], [])
        with self.assertRaises(Refused):
            self.repo.ancestor("missing-object", self.git("rev-parse", "main"))

    def make_worktree(self):
        worktree = self.root / ".worktrees" / "feature"
        self.git("worktree", "add", "-b", "feature", str(worktree), "main")
        return worktree

    def test_worktree_only_removes_checkout_and_preserves_all_refs(self):
        worktree = self.make_worktree()
        self.git("push", "origin", "feature")
        self.git("update-ref", "refs/remotes/origin/stale", self.git("rev-parse", "main"))
        before = self.git("show-ref")
        plan = self.repo.plan("worktrees")
        result = self.repo.apply(plan, "worktrees", exclusive_worktrees=True)
        self.assertEqual(result["actions"][0]["result"], "removed")
        self.assertFalse(worktree.exists())
        self.assertEqual(self.git("show-ref"), before)
        commands = [call.args for call in self.repo.run.call_args_list]
        self.assertFalse(any(len(cmd) >= 3 and cmd[1:3] in (("worktree", "prune"), ("remote", "prune"))
                             for cmd in commands))
        self.assertFalse(any(len(cmd) >= 2 and cmd[1] == "fetch" and "--prune" in cmd
                             and "--no-prune" not in cmd for cmd in commands))

    def test_dirty_untracked_or_changed_worktree_is_preserved(self):
        worktree = self.make_worktree()
        plan = self.repo.plan("worktrees")
        (worktree / "untracked").write_text("keep")
        self.assertEqual(self.repo.apply(plan, "worktrees", exclusive_worktrees=True)["actions"][0]["result"], "skipped")
        (worktree / "untracked").unlink()
        (worktree / ".gitignore").write_text("cache\n")
        self.command("git", "-C", str(worktree), "add", ".gitignore")
        self.command("git", "-C", str(worktree), "commit", "-m", "new head")
        self.assertEqual(self.repo.apply(plan, "worktrees", exclusive_worktrees=True)["actions"][0]["result"], "skipped")
        self.assertTrue(worktree.exists())

    def test_worktree_removal_requires_exclusive_access_assertion(self):
        worktree = self.make_worktree()
        plan = self.repo.plan("worktrees")
        self.assertEqual(self.repo.apply(plan, "worktrees")["actions"][0]["result"], "skipped")
        self.assertTrue(worktree.exists())

    def test_ignored_files_do_not_block_worktree_removal(self):
        worktree = self.make_worktree()
        (self.root / ".git/info/exclude").write_text("node_modules\n")
        (worktree / "node_modules").mkdir()
        (worktree / "node_modules/dep.js").write_text("reproducible build output")
        plan = self.repo.plan("worktrees")
        self.assertEqual(plan["actions"][0]["path"], str(worktree.resolve()))
        result = self.repo.apply(plan, "worktrees", exclusive_worktrees=True)
        self.assertEqual(result["actions"][0]["result"], "removed")
        self.assertFalse(worktree.exists())

    def test_operation_in_one_worktree_pins_only_its_candidates(self):
        busy = self.make_worktree()
        idle = self.root / ".worktrees/idle"
        self.git("worktree", "add", "-b", "idle", str(idle), "main")
        self.git("branch", "loose")
        operation = Path(self.command("git", "-C", str(busy), "rev-parse", "--absolute-git-dir")) / "rebase-apply"
        operation.mkdir()
        (operation / "head-name").write_text("refs/heads/feature\n")
        plan = self.repo.plan("all")
        key = lambda item: item["path"] if item["kind"] == "worktree" else item["ref"]
        skipped = {key(item): item["reason"] for item in plan["skipped"]}
        self.assertEqual(skipped[str(busy.resolve())], self.repo.OPERATION_REASON)
        self.assertEqual(skipped["refs/heads/feature"], self.repo.OPERATION_REASON)
        self.assertIn(str(idle.resolve()), [action.get("path") for action in plan["actions"]])
        self.assertIn("refs/heads/loose", self.action_names(plan))
        result = self.repo.apply(plan, "all", exclusive_worktrees=True)
        results = {key(action): action["result"] for action in result["actions"]}
        self.assertEqual(results[str(idle.resolve())], "removed")
        self.assertEqual(results["refs/heads/loose"], "removed")
        self.assertTrue(busy.exists())
        self.assertEqual(self.git("rev-parse", "feature"), self.git("rev-parse", "main"))

    def test_detached_clean_worktree_ancestor_is_removable(self):
        worktree = self.root / ".worktrees/detached"
        self.git("worktree", "add", "--detach", str(worktree), "main")
        plan = self.repo.plan("worktrees")
        result = self.repo.apply(plan, "worktrees", exclusive_worktrees=True)
        self.assertEqual(result["actions"][0]["result"], "removed")
        self.assertFalse(worktree.exists())

    def test_worktree_is_rechecked_after_other_candidate_proofs(self):
        worktree = self.make_worktree()
        plan = self.repo.plan("worktrees")
        original = self.repo.evaluate
        def reevaluate(*args, **kwargs):
            fresh = original(*args, **kwargs)
            (worktree / "late-file").write_text("keep")
            return fresh
        with patch.object(self.repo, "evaluate", side_effect=reevaluate):
            result = self.repo.apply(plan, "worktrees", exclusive_worktrees=True)
        self.assertEqual(result["actions"][0]["result"], "skipped")
        self.assertTrue((worktree / "late-file").exists())

    def test_locked_worktree_and_checked_out_branch_are_preserved(self):
        worktree = self.make_worktree()
        self.git("worktree", "lock", str(worktree))
        self.assertEqual(self.repo.plan("all")["actions"], [])
        self.git("worktree", "unlock", str(worktree))

    def test_dry_run_does_not_mutate_refs_index_or_worktrees(self):
        self.git("branch", "feature")
        before = self.git("show-ref"), (self.root / ".git/index").read_bytes(), self.git("worktree", "list", "--porcelain")
        self.repo.plan("all")
        after = self.git("show-ref"), (self.root / ".git/index").read_bytes(), self.git("worktree", "list", "--porcelain")
        self.assertEqual(after, before)

    def test_remote_deletion_lease_rejects_ref_moved_after_revalidation(self):
        self.git("branch", "feature")
        self.git("push", "origin", "feature")
        plan = self.repo.plan("remote-branches")
        self.git("switch", "feature")
        new = self.commit("new", "new\n")
        self.git("push", "origin", "feature:staging")
        self.git("switch", "main")
        original = self.repo.git
        def git(*args):
            if args[0] == "push":
                self.command("git", "--git-dir", str(self.remote), "update-ref", "refs/heads/feature", new)
            return original(*args)
        with patch.object(self.repo, "git", side_effect=git):
            self.assertEqual(self.repo.apply(plan, "remote-branches")["actions"][0]["result"], "skipped")
        self.assertEqual(self.repo.remote_heads()["refs/heads/feature"], new)

    def test_squash_without_pr_is_proven_by_content_on_trunk(self):
        self.squash()
        self.prs = []
        plan = self.repo.plan("local-branches")
        self.assertEqual(self.action_names(plan), ["refs/heads/feature"])
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "content-on-trunk")

    def test_squash_then_trunk_edits_same_path_still_proven(self):
        self.squash()
        self.prs = []
        self.git("switch", "main")
        self.commit("later trunk edit", "third\n")
        self.git("push", "origin", "main")
        plan = self.repo.plan("local-branches")
        self.assertEqual(self.action_names(plan), ["refs/heads/feature"])
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "content-on-trunk")

    def test_stale_local_trunk_is_fetched_and_fast_forwarded(self):
        base = self.git("rev-parse", "HEAD")
        self.git("branch", "feature")
        self.git("switch", "main")
        newer = self.commit("newer trunk", "newer\n")
        self.git("push", "origin", "main")
        self.git("reset", "--hard", base)
        self.assertEqual(self.git("rev-parse", "HEAD"), base)
        plan = self.repo.plan("local-branches")
        self.assertEqual(self.git("rev-parse", "main"), newer)
        self.assertEqual(self.action_names(plan), ["refs/heads/feature"])
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "ancestor")

    def test_local_cas_rejects_ref_moved_after_revalidation(self):
        self.git("branch", "feature")
        plan = self.repo.plan("local-branches")
        self.git("switch", "-c", "other")
        new = self.commit("new", "new\n")
        self.git("switch", "main")
        original = self.repo.git
        def git(*args):
            if args[0] == "update-ref":
                self.git("update-ref", "refs/heads/feature", new)
            return original(*args)
        with patch.object(self.repo, "git", side_effect=git):
            self.assertEqual(self.repo.apply(plan, "local-branches")["actions"][0]["result"], "skipped")
        self.assertEqual(self.git("rev-parse", "feature"), new)


if __name__ == "__main__":
    unittest.main()
