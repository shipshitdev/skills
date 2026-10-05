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

    def plan(self, *args, **kwargs):
        plan = self.repo.plan(*args, **kwargs)
        # Fixtures attest their explicitly constructed behavior. Production
        # plans start empty and require an actual code/intent review.
        for action in plan["actions"]:
            audit = action["proof"]["content_audit"]
            plan["intent_reviews"][f"{action['oid']}:{audit['base_oid']}"] = {
                "status": "verified", "candidate_oid": action["oid"],
                "trunk_oid": audit["trunk_oid"], "base_oid": audit["base_oid"],
                "summary": "Fixture candidate behavior is preserved",
                "evidence": ["Explicit Git fixture content and assertions"],
            }
        return plan

    def action_names(self, plan):
        return [action["ref"] for action in plan["actions"]]

    def test_exact_squash_head_is_proven_and_deleted_with_cas(self):
        self.squash()
        plan = self.plan("local-branches")
        self.assertEqual(self.action_names(plan), ["refs/heads/feature"])
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "exact-pr-head-squash")
        self.assertEqual(self.repo.apply(plan, "local-branches")["actions"][0]["result"], "removed")
        self.assertNotIn("feature", self.git("branch", "--format=%(refname:short)").splitlines())

    def test_commits_added_after_merged_pr_are_preserved(self):
        self.squash()
        self.git("switch", "feature")
        self.commit("same subject", "unmerged\n")
        self.git("switch", "main")
        plan = self.plan("local-branches")
        self.assertEqual(plan["actions"], [])
        self.assertTrue(plan["skipped"][0]["reason"].startswith(
            "not on trunk: commits beyond merged PR #1;"))

    def test_fork_pr_metadata_cannot_prove_squash(self):
        self.squash(head_repo="fork/repo")
        plan = self.plan("local-branches")
        self.assertEqual(self.action_names(plan), ["refs/heads/feature"])
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "content-on-trunk")

    def test_missing_head_repository_cannot_prove_squash(self):
        self.squash()
        self.prs[0]["head"]["repo"] = None
        plan = self.plan("local-branches")
        self.assertEqual(self.action_names(plan), ["refs/heads/feature"])
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "content-on-trunk")

    def test_same_subject_different_patch_is_not_proof(self):
        self.git("switch", "-c", "feature")
        self.commit("same subject", "branch only\n")
        self.git("switch", "main")
        self.commit("same subject", "trunk only\n")
        self.git("push", "origin", "main")
        self.assertEqual(self.plan("local-branches")["actions"], [])

    def test_mixed_ahead_commits_are_not_hidden_by_one_matching_patch(self):
        self.git("switch", "-c", "feature")
        first = self.commit("first", "first\n")
        self.commit("second", "second\n")
        self.git("switch", "main")
        self.git("cherry-pick", first)
        self.git("push", "origin", "main")
        self.assertEqual(self.plan("local-branches")["actions"], [])

    def test_patch_proof_covers_every_rebased_commit(self):
        self.git("switch", "-c", "feature")
        first = self.commit("first", "first\n")
        second = self.commit("second", "second\n")
        self.git("switch", "main")
        self.commit("other", "other\n", "other.txt")
        self.git("cherry-pick", first, second)
        self.git("push", "origin", "main")
        plan = self.plan("local-branches")
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "content-on-trunk")
        self.assertEqual(len(plan["actions"][0]["proof"]["ahead"]), 2)

    def test_whitespace_difference_is_not_patch_equivalence(self):
        self.git("switch", "-c", "feature")
        self.commit("indent", " x\n")
        self.git("switch", "main")
        self.commit("indent", "  x\n")
        self.git("push", "origin", "main")
        self.assertEqual(self.plan("local-branches")["actions"], [])

    def test_terminal_added_line_whitespace_is_not_stripped_from_proof(self):
        self.git("switch", "-c", "feature")
        feature = self.commit("trailing whitespace", "x \n")
        self.git("switch", "main")
        trunk = self.commit("no trailing whitespace", "x\n")
        base = self.git("merge-base", feature, trunk)
        self.assertNotEqual(self.repo.patch(base, feature), self.repo.patch(base, trunk))
        self.git("push", "origin", "main")
        self.assertEqual(self.plan("local-branches")["actions"], [])

    def test_historical_path_blobs_do_not_prove_current_content_after_reverts(self):
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
        plan = self.plan("local-branches")
        self.assertEqual(plan["actions"], [])
        audit = next(item["content_audit"] for item in plan["skipped"] if item["ref"] == "refs/heads/feature")
        self.assertFalse(audit["current_content_present"])
        self.assertEqual([item["path"] for item in audit["paths"]], ["first.txt", "second.txt"])
        self.assertTrue(all(item["history_reference"] for item in audit["paths"]))

    def test_empty_commit_is_not_content_proof(self):
        self.git("switch", "-c", "feature")
        self.git("commit", "--allow-empty", "-m", "empty")
        self.git("switch", "main")
        self.assertEqual(self.plan("local-branches")["actions"], [])

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
        plan = self.plan("local-branches")
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
        plan = self.plan("local-branches", "release.v1")
        self.assertEqual(self.action_names(plan), ["refs/heads/releaseXv1"])

    def test_changed_ref_is_skipped(self):
        self.git("branch", "feature")
        plan = self.plan("local-branches")
        self.git("switch", "feature")
        new = self.commit("new", "new\n")
        self.git("switch", "main")
        self.assertEqual(self.repo.apply(plan, "local-branches")["actions"][0]["result"], "skipped")
        self.assertEqual(self.git("rev-parse", "feature"), new)

    def test_current_head_or_trunk_change_stops_apply(self):
        self.git("branch", "feature")
        plan = self.plan("local-branches")
        self.commit("new trunk", "new\n")
        with self.assertRaises(Refused):
            self.repo.apply(plan, "local-branches")

    def test_alternate_push_destination_is_rejected_before_planning(self):
        self.git("config", "remote.origin.pushurl", "https://github.com/other/repo.git")
        with self.assertRaises(Refused):
            self.plan("remote-branches")

    def test_scope_and_repository_identity_are_bound_to_plan(self):
        self.git("branch", "feature")
        plan = self.plan("local-branches")
        with self.assertRaises(Refused):
            self.repo.apply(plan, "all")
        plan["context"]["repository"] = "different/repo"
        with self.assertRaises(Refused):
            self.repo.apply(plan, "local-branches")

    def test_open_pr_prevents_deletion_even_when_ancestor(self):
        self.git("branch", "feature")
        self.prs = [{"state": "open", "head": {"ref": "feature", "repo": {"full_name": "owner/repo"}},
                     "base": {"repo": {"full_name": "owner/repo"}}}]
        self.assertEqual(self.plan("local-branches")["actions"], [])

    def test_open_stacked_pr_preserves_its_base_branch(self):
        self.git("branch", "feature")
        self.prs = [{"state": "open", "head": {"ref": "child", "repo": {"full_name": "owner/repo"}},
                     "base": {"ref": "feature", "repo": {"full_name": "owner/repo"}}}]
        self.assertEqual(self.plan("local-branches")["actions"], [])

    def test_apply_does_not_replan_every_branch_for_every_action(self):
        for index in range(4):
            self.git("branch", f"feature-{index}")
        plan = self.plan("local-branches")
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
        self.assertNotIn("refs/heads/feature", self.action_names(self.plan("local-branches")))

    def test_current_content_proofs_need_no_historical_patch_scan(self):
        self.git("switch", "-c", "feature")
        feature = self.commit("feature", "feature\n")
        self.git("branch", "feature-1")
        self.git("branch", "feature-2")
        self.git("switch", "main")
        self.commit("other", "other\n", "other.txt")
        self.git("cherry-pick", feature)
        self.git("push", "origin", "main")
        self.repo.run.reset_mock()
        plan = self.plan("local-branches")
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
        plan = self.plan("local-branches")
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
                plan = self.plan("local-branches")
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
        plan = self.plan("local-branches")
        self.prs = [{"state": "open", "head": {"ref": "child", "repo": {"full_name": "fork/repo"}},
                     "base": {"ref": "feature", "repo": {"full_name": "owner/repo"}}}]
        self.assertEqual(self.repo.apply(plan, "local-branches")["actions"][0]["result"], "skipped")
        self.assertEqual(self.git("rev-parse", "feature"), self.git("rev-parse", "main"))

    def test_tampered_action_cannot_bypass_protection_scope_or_proof(self):
        self.git("branch", "feature")
        plan = self.plan("local-branches")
        for field, value in (("ref", "refs/heads/main"), ("kind", "remote"), ("proof", {})):
            changed = copy.deepcopy(plan)
            changed["actions"][0][field] = value
            self.assertEqual(self.repo.apply(changed, "local-branches")["actions"][0]["result"], "skipped")
        self.assertEqual(self.git("rev-parse", "feature"), self.git("rev-parse", "main"))

    def test_main_requires_authorization_and_emits_complete_report_without_jq(self):
        self.git("branch", "feature")
        plan = self.plan("local-branches")
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
        plan = self.plan("local-branches")
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
        plan = self.plan("local-branches")
        # Git am and rebase --apply use this metadata while the original ref can
        # remain detached from HEAD. Exercise the execution-time guard directly.
        operation = self.root / ".git/rebase-apply"
        operation.mkdir()
        (operation / "head-name").write_text("refs/heads/feature\n")
        result = self.repo.apply(plan, "local-branches")
        self.assertEqual(result["actions"][0]["result"], "skipped")
        self.assertEqual(self.git("rev-parse", "feature"), self.git("rev-parse", "main"))

    def test_git_error_is_never_an_empty_success(self):
        self.git("switch", "-c", "feature")
        self.commit("feature", "feature\n")
        self.git("switch", "main")
        self.git("merge", "--ff-only", "feature")
        self.git("push", "origin", "main")
        original = self.repo.git
        def git(*args):
            if args[0] == "rev-list":
                raise Refused("injected rev-list failure")
            return original(*args)
        with patch.object(self.repo, "git", side_effect=git):
            self.assertEqual(self.plan("local-branches")["actions"], [])
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
        plan = self.plan("worktrees")
        result = self.repo.apply(plan, "worktrees", exclusive_worktrees=True)
        self.assertEqual(result["actions"][0]["result"], "removed")
        self.assertFalse(worktree.exists())
        after = set(self.git("show-ref").splitlines())
        self.assertEqual(after - set(before.splitlines()), set())
        self.assertTrue(set(before.splitlines()).issubset(after))
        commands = [call.args for call in self.repo.run.call_args_list]
        self.assertFalse(any(len(cmd) >= 3 and cmd[1:3] in (("worktree", "prune"), ("remote", "prune"))
                             for cmd in commands))
        self.assertFalse(any(len(cmd) >= 2 and cmd[1] == "fetch" and "--prune" in cmd
                             and "--no-prune" not in cmd for cmd in commands))

    def test_dirty_untracked_or_changed_worktree_is_preserved(self):
        worktree = self.make_worktree()
        plan = self.plan("worktrees")
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
        plan = self.plan("worktrees")
        self.assertEqual(self.repo.apply(plan, "worktrees")["actions"][0]["result"], "skipped")
        self.assertTrue(worktree.exists())

    def test_ignored_files_preserve_worktree_and_code(self):
        worktree = self.make_worktree()
        (self.root / ".git/info/exclude").write_text("local-code.py\n")
        code = worktree / "local-code.py"
        code.write_text("irreplaceable source")
        plan = self.plan("worktrees")
        self.assertEqual(plan["actions"], [])
        self.assertIn("ignored files present", plan["skipped"][0]["reason"])
        self.repo.apply(plan, "worktrees", exclusive_worktrees=True)
        self.assertEqual(code.read_text(), "irreplaceable source")

    def test_operation_in_one_worktree_pins_only_its_candidates(self):
        busy = self.make_worktree()
        idle = self.root / ".worktrees/idle"
        self.git("worktree", "add", "-b", "idle", str(idle), "main")
        self.git("branch", "loose")
        operation = Path(self.command("git", "-C", str(busy), "rev-parse", "--absolute-git-dir")) / "rebase-apply"
        operation.mkdir()
        (operation / "head-name").write_text("refs/heads/feature\n")
        plan = self.plan("all")
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
        plan = self.plan("worktrees")
        result = self.repo.apply(plan, "worktrees", exclusive_worktrees=True)
        self.assertEqual(result["actions"][0]["result"], "removed")
        self.assertFalse(worktree.exists())

    def test_worktree_is_rechecked_after_other_candidate_proofs(self):
        worktree = self.make_worktree()
        plan = self.plan("worktrees")
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
        self.assertEqual(self.plan("all")["actions"], [])
        self.git("worktree", "unlock", str(worktree))

    def test_dry_run_does_not_mutate_refs_index_or_worktrees(self):
        self.git("branch", "feature")
        before = self.git("show-ref"), (self.root / ".git/index").read_bytes(), self.git("worktree", "list", "--porcelain")
        self.plan("all")
        after = self.git("show-ref"), (self.root / ".git/index").read_bytes(), self.git("worktree", "list", "--porcelain")
        self.assertEqual(after, before)

    def test_remote_deletion_lease_rejects_ref_moved_after_revalidation(self):
        self.git("branch", "feature")
        self.git("push", "origin", "feature")
        plan = self.plan("remote-branches")
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
        plan = self.plan("local-branches")
        self.assertEqual(self.action_names(plan), ["refs/heads/feature"])
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "content-on-trunk")

    def test_unfetched_pr_merge_commit_falls_through_to_content_proof(self):
        self.squash()
        self.prs[0]["merge_commit_sha"] = "0123456789abcdef0123456789abcdef01234567"
        plan = self.plan("local-branches")
        self.assertEqual(self.action_names(plan), ["refs/heads/feature"])
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "content-on-trunk")

    def test_squash_then_trunk_replaces_same_path_is_preserved(self):
        self.squash()
        self.prs = []
        self.git("switch", "main")
        self.commit("later trunk edit", "third\n")
        self.git("push", "origin", "main")
        plan = self.plan("local-branches")
        self.assertEqual(plan["actions"], [])

    def test_merged_pr_head_later_edited_on_trunk_is_removed_without_intent_review(self):
        head, _merge = self.squash()
        self.commit("later trunk edit", "third\n")
        self.git("push", "origin", "main")
        plan = self.repo.plan("local-branches")
        self.assertEqual(self.action_names(plan), ["refs/heads/feature"])
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "merged-pr-head")
        self.assertEqual(plan["intent_reviews"], {})
        self.assertEqual(self.repo.apply(plan, "local-branches")["actions"][0]["result"], "removed")
        self.assertNotIn("feature", self.git("branch", "--format=%(refname:short)").splitlines())
        self.assertEqual(self.git("for-each-ref", "refs/cleanup/"), "")

    def test_merged_pr_head_needs_same_repository_and_merge_on_trunk(self):
        for change in ({"head_repo": "fork/repo"}, {"merge_commit_sha": "0" * 40},
                       {"merged_at": None}, {"head_sha": "1" * 40}):
            with self.subTest(change=change):
                self.setUp()
                self.squash(head_repo=change.get("head_repo", "owner/repo"))
                self.prs[0].update({key: value for key, value in change.items()
                                    if key in ("merge_commit_sha", "merged_at")})
                if "head_sha" in change:
                    self.prs[0]["head"]["sha"] = change["head_sha"]
                self.commit("later trunk edit", "third\n")
                self.git("push", "origin", "main")
                plan = self.repo.plan("local-branches")
                self.assertEqual(plan["actions"], [])
                self.assertEqual(plan["skipped"][0]["ref"], "refs/heads/feature")

    def test_forged_merged_pr_head_kind_cannot_skip_intent_review(self):
        self.squash()
        plan = self.repo.plan("local-branches")
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "exact-pr-head-squash")
        plan["actions"][0]["proof"]["kind"] = "merged-pr-head"
        result = self.repo.apply(plan, "local-branches")
        self.assertEqual(result["actions"][0]["result"], "skipped")
        self.assertIn("differs from the reviewed plan", result["actions"][0]["reason"])
        self.assertEqual(self.git("for-each-ref", "refs/cleanup/recovery/"), "")

    def behind_merged_head(self):
        """Feature tip lags the PR head: a commit was pushed to the PR from elsewhere."""
        self.git("switch", "-c", "feature")
        tip = self.commit("feature", "feature\n")
        self.git("switch", "-c", "pushed-elsewhere")
        head = self.commit("ci fix", "ci\n", "ci.txt")
        self.git("switch", "main")
        self.git("merge", "--squash", "pushed-elsewhere")
        self.git("commit", "-m", "feature (#1)")
        merge = self.git("rev-parse", "HEAD")
        self.git("branch", "-D", "pushed-elsewhere")
        self.commit("later trunk edit", "rewritten\n")
        self.git("push", "origin", "main")
        self.prs = [{"number": 1, "state": "closed", "merged_at": "2026-01-01",
                     "merge_commit_sha": merge,
                     "head": {"ref": "feature", "sha": head, "repo": {"full_name": "owner/repo"}},
                     "base": {"repo": {"full_name": "owner/repo"}}}]
        return tip, head

    def test_tip_behind_merged_pr_head_is_removed(self):
        _tip, head = self.behind_merged_head()
        plan = self.repo.plan("local-branches")
        self.assertEqual(self.action_names(plan), ["refs/heads/feature"])
        self.assertEqual((plan["actions"][0]["proof"]["kind"], plan["actions"][0]["proof"]["head"]),
                         ("merged-pr-head", head))
        self.assertEqual(self.repo.apply(plan, "local-branches")["actions"][0]["result"], "removed")

    def test_missing_merged_pr_head_is_fetched_from_the_pull_ref(self):
        _tip, head = self.behind_merged_head()
        self.git("push", "origin", f"{head}:refs/pull/1/head")
        self.git("reflog", "expire", "--expire=now", "--all")
        self.git("gc", "--prune=now", "--quiet")
        self.assertFalse(self.repo.has_commit(head))
        plan = self.repo.plan("local-branches")
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "merged-pr-head")
        self.assertEqual(self.git("for-each-ref", "refs/pull/"), "")

    def test_ambiguous_merge_base_with_merged_pr_head_is_removed(self):
        base = self.git("rev-parse", "HEAD")
        self.git("switch", "-c", "feature")
        side = self.commit("feature", "feature\n", "feature.txt")
        self.git("switch", "main")
        trunk_side = self.commit("trunk", "trunk\n", "trunk.txt")
        self.git("merge", "--no-edit", side)
        self.git("switch", "feature")
        self.git("merge", "--no-edit", trunk_side)
        head = self.git("rev-parse", "HEAD")
        self.git("switch", "main")
        self.git("merge", "--squash", "feature")
        self.git("commit", "--allow-empty", "-m", "feature (#1)")
        merge = self.git("rev-parse", "HEAD")
        self.git("push", "origin", "main")
        self.assertEqual(len(self.git("merge-base", "--all", head, merge).split()), 2, base)
        self.prs = [{"number": 1, "state": "closed", "merged_at": "2026-01-01",
                     "merge_commit_sha": merge,
                     "head": {"ref": "feature", "sha": head, "repo": {"full_name": "owner/repo"}},
                     "base": {"repo": {"full_name": "owner/repo"}}}]
        plan = self.repo.plan("local-branches")
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "merged-pr-head")
        self.assertEqual(plan["actions"][0]["proof"]["content_audit"]["scope"], "unavailable")

    def test_detached_worktree_at_merged_pr_head_is_found_by_commit(self):
        head, _merge = self.squash()
        self.commit("later trunk edit", "third\n")
        self.git("push", "origin", "main")
        self.git("branch", "-D", "feature")
        worktree = self.root / ".worktrees/detached"
        self.git("worktree", "add", "--detach", str(worktree), head)
        plan = self.repo.plan("worktrees")
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "merged-pr-head")
        calls = [call.args for call in self.repo.run.call_args_list if call.args[:2] == ("gh", "api")]
        self.assertTrue(any(f"repos/owner/repo/commits/{head}/pulls" in call for call in calls))
        result = self.repo.apply(plan, "worktrees", exclusive_worktrees=True)
        self.assertEqual(result["actions"][0]["result"], "removed")

    def test_unproven_reasons_and_summary_name_pr_history(self):
        self.git("switch", "-c", "no-pr")
        self.commit("unshipped", "unshipped\n", "a.txt")
        self.git("switch", "-c", "closed-pr", "main")
        self.commit("rejected", "rejected\n", "b.txt")
        self.git("switch", "main")
        prs = {"no-pr": [], "closed-pr": [{"number": 7, "state": "closed", "merged_at": None,
                                           "head": {"sha": "x"}}]}
        with patch.object(self.repo, "pull_requests", side_effect=lambda _repo, branch: prs[branch]):
            plan = self.repo.plan("local-branches")
        reasons = {item["ref"]: item["reason"].split(";")[0] for item in plan["skipped"]}
        self.assertEqual(reasons["refs/heads/no-pr"], "not on trunk: no PR")
        self.assertEqual(reasons["refs/heads/closed-pr"], "not on trunk: PR #7 closed without merging")
        self.assertEqual(plan["summary"], {"removable": 0, "kept": {
            "not on trunk: PR #N closed without merging": 1, "not on trunk: no PR": 1,
            "protected branch": 1}})

    def test_remote_branch_objects_are_fetched_before_proof(self):
        clone = self.directory / "clone"
        self.command("git", "clone", "-q", str(self.remote), str(clone))
        for args in (("config", "user.name", "x"), ("config", "user.email", "x@example.invalid"),
                     ("switch", "-c", "remote-only")):
            self.command("git", "-C", str(clone), *args)
        (clone / "remote.txt").write_text("remote\n")
        self.command("git", "-C", str(clone), "add", "remote.txt")
        self.command("git", "-C", str(clone), "commit", "-m", "remote work")
        self.command("git", "-C", str(clone), "push", "-q", "origin", "remote-only")
        plan = self.repo.plan("remote-branches")
        skipped = next(item for item in plan["skipped"] if item["ref"] == "refs/heads/remote-only")
        self.assertTrue(skipped["reason"].startswith("not on trunk: no PR"), skipped["reason"])
        self.assertNotIn("remote-only", self.git("for-each-ref", "--format=%(refname)"))

    def test_trunk_advancing_after_plan_does_not_abort_prune(self):
        self.squash()
        plan = self.plan("local-branches")
        self.advance_trunk(("unrelated.txt", "unrelated\n"))
        result = self.repo.apply(plan, "local-branches")
        self.assertEqual(result["actions"][0]["result"], "removed")

    def test_forged_kind_after_trunk_advanced_is_still_rejected(self):
        head, _merge = self.squash()
        plan = self.repo.plan("local-branches")
        plan["actions"][0]["proof"]["kind"] = "merged-pr-head"
        self.advance_trunk(("unrelated.txt", "unrelated\n"))
        result = self.repo.apply(plan, "local-branches")
        self.assertEqual(result["actions"][0]["result"], "skipped")
        self.assertEqual(self.git("rev-parse", "feature"), head)

    def test_scratch_generated_files_and_linked_modules_do_not_block_removal(self):
        worktree = self.make_worktree()
        (self.root / ".git/info/exclude").write_text(".tmp/\nnext-env.d.ts\nnode_modules\n")
        (self.root / "node_modules/dep").mkdir(parents=True)
        (worktree / ".tmp").mkdir()
        (worktree / ".tmp/pr-body.md").write_text("scratch\n")
        (worktree / "next-env.d.ts").write_text("/// generated\n")
        (worktree / "node_modules").symlink_to(self.root / "node_modules")
        plan = self.plan("worktrees")
        ignored = plan["actions"][0]["ignored"]
        self.assertEqual(ignored["scratch"], [".tmp/"])
        self.assertEqual(ignored["regenerable"], ["next-env.d.ts", "node_modules"])
        result = self.repo.apply(plan, "worktrees", exclusive_worktrees=True)
        self.assertEqual(result["actions"][0]["result"], "removed")
        self.assertFalse(worktree.exists())
        self.assertTrue((self.root / "node_modules/dep").is_dir())

    def test_stale_local_trunk_is_fetched_and_fast_forwarded(self):
        base = self.git("rev-parse", "HEAD")
        self.git("branch", "feature")
        self.git("switch", "main")
        newer = self.commit("newer trunk", "newer\n", "other.txt")
        self.git("push", "origin", "main")
        self.git("reset", "--hard", base)
        self.assertEqual(self.git("rev-parse", "HEAD"), base)
        plan = self.plan("local-branches")
        self.assertEqual(self.git("rev-parse", "main"), newer)
        self.assertEqual(self.action_names(plan), ["refs/heads/feature"])
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "no-own-commits")

    def test_current_content_receipt_works_under_another_pr_and_commit(self):
        head, landed = self.squash()
        self.prs[0]["head"]["ref"] = "replacement-pr"
        self.assertNotEqual(head, landed)
        plan = self.plan("local-branches")
        audit = plan["actions"][0]["proof"]["content_audit"]
        self.assertTrue(audit["current_content_present"])
        self.assertEqual(audit["candidate_oid"], head)
        self.assertEqual(audit["trunk_oid"], landed)
        entry = audit["paths"][0]
        self.assertEqual(entry["state"], "exact-entry")
        self.assertEqual(entry["candidate"], entry["trunk"])

    def test_reverted_merged_pr_head_is_removed(self):
        head, merge = self.squash()
        self.git("revert", "--no-edit", "HEAD")
        self.git("push", "origin", "main")
        plan = self.repo.plan("local-branches")
        proof = plan["actions"][0]["proof"]
        self.assertEqual((proof["kind"], proof["pr"], proof["merge"]), ("merged-pr-head", 1, merge))
        self.assertFalse(proof["content_audit"]["current_content_present"])
        self.assertEqual(self.repo.apply(plan, "local-branches")["actions"][0]["result"], "removed")
        self.assertEqual(self.git("for-each-ref", "refs/cleanup/"), "")

    def test_ancestor_history_cannot_bypass_reverted_current_content(self):
        self.git("switch", "-c", "feature")
        head = self.commit("feature", "feature\n")
        self.git("switch", "main")
        self.git("merge", "--ff-only", "feature")
        self.git("revert", "--no-edit", "HEAD")
        self.git("push", "origin", "main")
        self.assertTrue(self.repo.ancestor(head, self.git("rev-parse", "main")))
        plan = self.plan("local-branches")
        self.assertEqual(plan["actions"], [])
        audit = next(item["content_audit"] for item in plan["skipped"] if item["ref"] == "refs/heads/feature")
        self.assertEqual(audit["scope"], "candidate-snapshot")
        self.assertFalse(audit["current_content_present"])

    def test_ancestor_deletion_restored_on_trunk_is_preserved(self):
        self.commit("add config", "setting\n", "config")
        self.git("push", "origin", "main")
        self.git("switch", "-c", "feature")
        self.git("rm", "config")
        self.git("commit", "-m", "candidate removes config")
        head = self.git("rev-parse", "HEAD")
        self.git("switch", "main")
        self.git("merge", "--ff-only", "feature")
        self.git("checkout", "HEAD~1", "--", "config")
        self.git("commit", "-m", "trunk restores config")
        self.git("push", "origin", "main")
        self.assertTrue(self.repo.ancestor(head, self.git("rev-parse", "main")))
        plan = self.plan("local-branches")
        self.assertEqual(plan["actions"], [])
        audit = next(item["content_audit"] for item in plan["skipped"] if item["ref"] == "refs/heads/feature")
        self.assertEqual(audit["scope"], "candidate-snapshot")
        self.assertFalse(audit["current_content_present"])
        restored = next(item for item in audit["paths"] if item["path"] == "config")
        self.assertEqual(restored["state"], "restored-on-trunk")
        self.assertIsNone(restored["candidate"])

    def test_ancestor_with_later_trunk_addition_stays_removable(self):
        self.git("switch", "-c", "feature")
        self.commit("feature", "feature\n")
        self.git("switch", "main")
        self.git("merge", "--ff-only", "feature")
        self.commit("later trunk work", "later\n", "later.txt")
        self.git("push", "origin", "main")
        plan = self.plan("local-branches")
        self.assertEqual(self.action_names(plan), ["refs/heads/feature"])
        audit = plan["actions"][0]["proof"]["content_audit"]
        self.assertEqual(audit["scope"], "candidate-snapshot")
        self.assertNotIn("later.txt", [item["path"] for item in audit["paths"]])

    def test_current_patch_with_independent_trunk_edits_uses_isolated_index(self):
        original = "".join(f"line {index}\n" for index in range(20))
        self.commit("context", original)
        self.git("push", "origin", "main")
        self.git("switch", "-c", "feature")
        self.commit("feature", original.replace("line 1\n", "feature 1\n"))
        self.git("switch", "main")
        self.commit("another PR", original.replace("line 1\n", "feature 1\n")
                    .replace("line 18\n", "trunk 18\n"))
        self.git("push", "origin", "main")
        index_path = Path(self.git("rev-parse", "--absolute-git-dir")) / "index"
        index_before, working_before = index_path.read_bytes(), (self.root / "file.txt").read_bytes()
        plan = self.plan("local-branches")
        self.assertEqual(self.action_names(plan), ["refs/heads/feature"])
        audit = plan["actions"][0]["proof"]["content_audit"]
        self.assertEqual(audit["paths"][0]["state"], "patch-present")
        self.assertEqual(len(audit["paths"][0]["patch_sha256"]), 64)
        self.assertEqual(index_path.read_bytes(), index_before)
        self.assertEqual((self.root / "file.txt").read_bytes(), working_before)

    def test_partial_patch_with_independent_trunk_edits_stays_unproven(self):
        original = "".join(f"line {index}\n" for index in range(20))
        self.commit("context", original)
        self.git("push", "origin", "main")
        self.git("switch", "-c", "feature")
        self.commit("feature", original.replace("line 1\n", "feature 1\n")
                    .replace("line 18\n", "feature 18\n"))
        self.git("switch", "main")
        self.commit("partial", original.replace("line 1\n", "feature 1\n"))
        self.git("push", "origin", "main")
        self.assertEqual(self.plan("local-branches")["actions"], [])

    def test_current_blob_with_wrong_executable_mode_is_not_proof(self):
        self.squash()
        self.prs = []
        self.git("update-index", "--chmod=+x", "file.txt")
        self.git("commit", "-m", "mode changed")
        self.git("push", "origin", "main")
        self.assertEqual(self.plan("local-branches")["actions"], [])

    def test_deletion_restored_on_trunk_is_not_proof(self):
        self.git("switch", "-c", "feature")
        self.git("rm", "file.txt")
        self.git("commit", "-m", "delete")
        self.git("switch", "main")
        self.git("merge", "--squash", "feature")
        self.git("commit", "-m", "land deletion")
        self.git("revert", "--no-edit", "HEAD")
        self.git("push", "origin", "main")
        self.assertEqual(self.plan("local-branches")["actions"], [])

    def test_binary_replacement_is_not_inferred_from_historical_blob(self):
        self.git("switch", "-c", "feature")
        (self.root / "asset.bin").write_bytes(b"\x00candidate")
        self.git("add", "asset.bin")
        self.git("commit", "-m", "binary")
        self.git("switch", "main")
        self.git("merge", "--squash", "feature")
        self.git("commit", "-m", "land binary")
        (self.root / "asset.bin").write_bytes(b"\x00replacement")
        self.git("add", "asset.bin")
        self.git("commit", "-m", "replace binary")
        self.git("push", "origin", "main")
        self.assertEqual(self.plan("local-branches")["actions"], [])

    def test_missing_intent_review_blocks_deletion_and_creates_no_recovery_ref(self):
        head, _merge = self.squash()
        plan = self.repo.plan("local-branches")
        result = self.repo.apply(plan, "local-branches")
        self.assertEqual(result["actions"][0]["result"], "skipped")
        self.assertIn("intent review missing", result["actions"][0]["reason"])
        self.assertEqual(self.git("rev-parse", "feature"), head)
        self.assertEqual(self.git("for-each-ref", "refs/cleanup/recovery/"), "")

    def test_stale_or_unverified_intent_review_cannot_authorize_deletion(self):
        head, _merge = self.squash()
        plan = self.plan("local-branches")
        for field, value in (("candidate_oid", "bad"), ("trunk_oid", "bad"),
                             ("base_oid", "bad"), ("status", "unresolved"),
                             ("evidence", []), ("summary", "")):
            with self.subTest(field=field):
                changed = copy.deepcopy(plan)
                key = f"{head}:{plan['actions'][0]['proof']['content_audit']['base_oid']}"
                changed["intent_reviews"][key][field] = value
                result = self.repo.apply(changed, "local-branches")
                self.assertEqual(result["actions"][0]["result"], "skipped")
                self.assertEqual(self.git("rev-parse", "feature"), head)

    def test_noprefix_diff_config_cannot_verify_a_different_path(self):
        self.git("config", "diff.noprefix", "true")
        (self.root / "src").mkdir()
        (self.root / "file.py").write_text("x\n")
        (self.root / "src/file.py").write_text("x\n")
        self.git("add", "file.py", "src/file.py")
        self.git("commit", "-m", "two files")
        self.git("switch", "-c", "feature")
        self.commit("candidate edit", "y\n", "src/file.py")
        self.git("switch", "main")
        self.commit("trunk edits another path", "y\n", "file.py")
        self.git("push", "origin", "main")
        plan = self.plan("local-branches")
        self.assertEqual(plan["actions"], [])
        self.assertEqual(plan["skipped"][0]["content_audit"]["paths"][0]["state"],
                         "unchanged-on-trunk")

    def test_deleted_path_replaced_by_trunk_directory_is_preserved(self):
        self.commit("add config", "setting\n", "config")
        self.git("push", "origin", "main")
        self.git("switch", "-c", "feature")
        self.git("rm", "config")
        self.git("commit", "-m", "candidate removes config")
        self.git("switch", "main")
        self.git("rm", "config")
        (self.root / "config").mkdir()
        (self.root / "config/settings").write_text("nested\n")
        self.git("add", "config/settings")
        self.git("commit", "-m", "trunk replaces config with a directory")
        self.git("push", "origin", "main")
        plan = self.plan("local-branches")
        self.assertEqual(plan["actions"], [])
        item = plan["skipped"][0]["content_audit"]["paths"][0]
        self.assertEqual(item["trunk"]["type"], "tree")
        self.assertEqual(item["state"], "both-changed")

    def test_same_sha_aliases_with_different_audit_bases_keep_separate_reviews(self):
        self.git("switch", "-c", "feature")
        head = self.commit("feature work", "feature\n", "feature.txt")
        self.git("switch", "main")
        self.git("merge", "--no-ff", "feature", "-m", "merge feature")
        merge = self.git("rev-parse", "HEAD")
        self.git("push", "origin", "main")
        self.git("branch", "alias", head)
        self.prs = [{"number": 1, "state": "closed", "merged_at": "2026-01-01",
                     "merge_commit_sha": merge,
                     "head": {"ref": "feature", "sha": head, "repo": {"full_name": "owner/repo"}},
                     "base": {"repo": {"full_name": "owner/repo"}}}]
        plan = self.plan("local-branches")
        self.assertEqual(sorted(self.action_names(plan)), ["refs/heads/alias", "refs/heads/feature"])
        self.assertEqual(len({a["proof"]["content_audit"]["base_oid"] for a in plan["actions"]}), 2)
        result = self.repo.apply(plan, "local-branches")
        self.assertEqual([a["result"] for a in result["actions"]], ["removed", "removed"])

    def test_subdirectory_invocation_audits_the_whole_repository(self):
        (self.root / "sub").mkdir()
        (self.root / "sub/a.txt").write_text("a\n")
        (self.root / "top.txt").write_text("t\n")
        self.git("add", "sub/a.txt", "top.txt")
        self.git("commit", "-m", "two areas")
        self.git("push", "origin", "main")
        self.git("switch", "-c", "feature")
        (self.root / "sub/a.txt").write_text("a2\n")
        (self.root / "top.txt").write_text("t2\n")
        self.git("commit", "-am", "edit both")
        self.git("switch", "main")
        self.commit("land only sub", "a2\n", "sub/a.txt")
        self.git("push", "origin", "main")
        scoped = Repository(self.root / "sub")
        self.assertEqual(scoped.root, self.root.resolve())
        original = scoped.run
        scoped.run = lambda *args, **kwargs: (
            self.repo.run(*args, **kwargs) if args[:1] == ("gh",) else original(*args, **kwargs))
        plan = scoped.plan("local-branches")
        self.assertEqual(plan["actions"], [])
        self.assertEqual({item["path"] for item in plan["skipped"][0]["content_audit"]["paths"]},
                         {"sub/a.txt", "top.txt"})

    def test_v1_historical_plan_is_refused(self):
        self.git("branch", "feature")
        plan = self.plan("local-branches")
        plan["version"] = 1
        with self.assertRaises(Refused):
            self.repo.apply(plan, "local-branches")

    def test_ignored_code_added_after_plan_blocks_worktree_removal(self):
        worktree = self.make_worktree()
        plan = self.plan("worktrees")
        (self.root / ".git/info/exclude").write_text("local.py\n")
        (worktree / "local.py").write_text("preserve")
        result = self.repo.apply(plan, "worktrees", exclusive_worktrees=True)
        self.assertEqual(result["actions"][0]["result"], "skipped")
        self.assertTrue(worktree.exists())

    def advance_trunk(self, *changes):
        for index, (filename, content) in enumerate(changes):
            self.commit(f"trunk {index}", content, filename)
        self.git("push", "origin", "main")

    def test_pointer_branch_on_old_trunk_is_removed_without_review(self):
        self.git("branch", "pointer")
        self.git("branch", "-m", "pointer", "renamed")
        self.advance_trunk(("file.txt", "rewritten\n"), ("other.txt", "added\n"))
        plan = self.repo.plan("local-branches")
        self.assertEqual(self.action_names(plan), ["refs/heads/renamed"])
        proof = plan["actions"][0]["proof"]
        self.assertEqual(proof["kind"], "no-own-commits")
        self.assertEqual(proof["content_audit"]["paths"], [])
        self.assertEqual(plan["intent_reviews"], {})
        self.assertEqual(self.repo.apply(plan, "local-branches")["actions"][0]["result"], "removed")
        self.assertNotIn("renamed", self.git("branch", "--format=%(refname:short)").splitlines())
        self.assertEqual(self.git("for-each-ref", "refs/cleanup/"), "")

    def test_branch_that_held_a_commit_is_not_a_pointer(self):
        self.git("switch", "-c", "feature")
        self.commit("feature", "feature\n")
        self.git("reset", "--hard", "main")
        self.git("switch", "main")
        self.advance_trunk(("file.txt", "rewritten\n"))
        plan = self.repo.plan("local-branches")
        skipped = next(item for item in plan["skipped"] if item["ref"] == "refs/heads/feature")
        self.assertEqual(skipped["content_audit"]["scope"], "candidate-snapshot")
        self.assertEqual(plan["actions"], [])

    def test_pointer_branch_without_reflog_keeps_conservative_audit(self):
        self.git("branch", "pointer")
        self.git("reflog", "delete", "--rewrite", "refs/heads/pointer@{0}")
        self.advance_trunk(("file.txt", "rewritten\n"))
        plan = self.repo.plan("local-branches")
        self.assertEqual(plan["actions"], [])

    def test_forged_pointer_proof_cannot_skip_intent_review(self):
        head, _merge = self.squash()
        plan = self.repo.plan("local-branches")
        plan["actions"][0]["proof"]["kind"] = "no-own-commits"
        result = self.repo.apply(plan, "local-branches")
        self.assertEqual(result["actions"][0]["result"], "skipped")
        self.assertEqual(self.git("rev-parse", "feature"), head)

    def test_detached_worktree_on_old_trunk_is_removable(self):
        worktree = self.root / ".worktrees/detached"
        self.git("worktree", "add", "--detach", str(worktree), "main")
        self.advance_trunk(("file.txt", "rewritten\n"))
        plan = self.repo.plan("worktrees")
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "no-own-commits")
        result = self.repo.apply(plan, "worktrees", exclusive_worktrees=True)
        self.assertEqual(result["actions"][0]["result"], "removed")

    def test_ignored_copies_and_build_output_do_not_block_removal(self):
        worktree = self.make_worktree()
        (self.root / ".git/info/exclude").write_text(".env\nnode_modules/\npkg/generated/\nlocal/\n")
        for checkout in (self.root, worktree):
            (checkout / ".env").write_text("SECRET=same\n")
            (checkout / "local").mkdir()
            (checkout / "local/settings.json").write_text("{}\n")
        (worktree / "node_modules/dep").mkdir(parents=True)
        (worktree / "node_modules/dep/index.js").write_text("module.exports = 1\n")
        (worktree / "pkg/generated").mkdir(parents=True)
        (worktree / "pkg/generated/client.ts").write_text("export {}\n")
        plan = self.plan("worktrees")
        ignored = plan["actions"][0]["ignored"]
        self.assertEqual(ignored["duplicated"], [".env", "local/settings.json"])
        self.assertEqual(ignored["regenerable"], ["node_modules/", "pkg/generated/"])
        result = self.repo.apply(plan, "worktrees", exclusive_worktrees=True)
        self.assertEqual(result["actions"][0]["result"], "removed")
        self.assertEqual((self.root / ".env").read_text(), "SECRET=same\n")

    def test_ignored_file_differing_from_main_checkout_preserves_worktree(self):
        worktree = self.make_worktree()
        (self.root / ".git/info/exclude").write_text(".env\n")
        (self.root / ".env").write_text("SECRET=main\n")
        (worktree / ".env").write_text("SECRET=worktree-only\n")
        plan = self.plan("worktrees")
        self.assertEqual(plan["actions"], [])
        self.assertIn(".env", plan["skipped"][0]["reason"])
        self.repo.apply(plan, "worktrees", exclusive_worktrees=True)
        self.assertEqual((worktree / ".env").read_text(), "SECRET=worktree-only\n")

    def test_main_checkout_link_into_worktree_is_not_a_copy(self):
        worktree = self.make_worktree()
        (self.root / ".git/info/exclude").write_text("local\nlocal/\n")
        (worktree / "local").mkdir()
        (worktree / "local/settings.json").write_text("only copy\n")
        (self.root / "local").symlink_to(worktree / "local")
        plan = self.plan("worktrees")
        self.assertEqual(plan["actions"], [])
        self.assertIn("local/settings.json", plan["skipped"][0]["reason"])

    def test_copy_of_a_main_checkout_link_target_is_a_duplicate(self):
        worktree = self.make_worktree()
        (self.root / ".git/info/exclude").write_text("*.env.local\n")
        (self.root / "api").mkdir()
        (self.root / "api/.env.local").write_text("SECRET=shared\n")
        (self.root / "workers").mkdir()
        (self.root / "workers/.env.local").symlink_to("../api/.env.local")
        (worktree / "workers").mkdir()
        (worktree / "workers/.env.local").write_text("SECRET=shared\n")
        plan = self.plan("worktrees")
        self.assertEqual(plan["actions"][0]["ignored"]["duplicated"], ["workers/.env.local"])
        result = self.repo.apply(plan, "worktrees", exclusive_worktrees=True)
        self.assertEqual(result["actions"][0]["result"], "removed")
        self.assertEqual((self.root / "workers/.env.local").read_text(), "SECRET=shared\n")

    def test_main_checkout_file_link_into_worktree_is_not_a_copy(self):
        worktree = self.make_worktree()
        (self.root / ".git/info/exclude").write_text("*.env.local\n")
        (worktree / "workers").mkdir()
        (worktree / "workers/.env.local").write_text("SECRET=only\n")
        (self.root / "workers").mkdir()
        (self.root / "workers/.env.local").symlink_to(worktree / "workers/.env.local")
        plan = self.plan("worktrees")
        self.assertEqual(plan["actions"], [])
        self.assertIn("workers/.env.local", plan["skipped"][0]["reason"])

    def test_regenerable_names_cover_directories_not_files(self):
        worktree = self.make_worktree()
        (self.root / ".git/info/exclude").write_text("generated\n")
        (worktree / "generated").write_text("hand-written notes\n")
        plan = self.plan("worktrees")
        self.assertEqual(plan["actions"], [])
        self.assertIn("generated", plan["skipped"][0]["reason"])

    def test_rename_after_expired_reflog_is_not_creation_evidence(self):
        self.git("switch", "-c", "feature")
        self.commit("feature", "feature\n")
        self.git("switch", "main")
        self.git("merge", "--ff-only", "feature")
        self.git("revert", "--no-edit", "HEAD")
        self.git("push", "origin", "main")
        self.git("reflog", "expire", "--expire=all", "refs/heads/feature")
        self.git("branch", "-m", "feature", "renamed")
        self.assertEqual(self.repo.plan("local-branches")["actions"], [])

    def test_detached_head_log_without_creation_is_audited(self):
        worktree = self.root / ".worktrees/detached"
        self.git("worktree", "add", "--detach", str(worktree), "main")
        # A truncated log keeps only a reset entry, without the creation record.
        log = Path(self.command("git", "-C", str(worktree), "rev-parse", "--absolute-git-dir")) / "logs/HEAD"
        _old, new, identity = log.read_text().splitlines()[-1].split("\t")[0].split(" ", 2)
        log.write_text(f"{new} {new} {identity}\treset: moving to HEAD\n")
        self.advance_trunk(("file.txt", "rewritten\n"))
        self.assertEqual(self.repo.plan("worktrees")["actions"], [])

    def test_worktree_and_its_branch_are_removed_in_one_pass(self):
        worktree = self.make_worktree()
        self.command("git", "-C", str(worktree), "commit", "--allow-empty", "-m", "own work")
        head = self.command("git", "-C", str(worktree), "rev-parse", "HEAD")
        self.git("merge", "--ff-only", "feature")
        self.git("push", "origin", "main")
        plan = self.plan("all")
        local = next(action for action in plan["actions"] if action["kind"] == "local")
        self.assertEqual(local["after_worktrees"], [str(worktree.resolve())])
        result = self.repo.apply(plan, "all", exclusive_worktrees=True)
        self.assertEqual([action["result"] for action in result["actions"]], ["removed", "removed"])
        self.assertFalse(worktree.exists())
        self.assertNotIn("feature", self.git("branch", "--format=%(refname:short)").splitlines())
        self.assertEqual(self.git("for-each-ref", "refs/cleanup/"), "")

    def test_branch_waits_for_its_worktree_removal(self):
        worktree = self.make_worktree()
        plan = self.plan("all")
        self.assertEqual({action["kind"] for action in plan["actions"]}, {"worktree", "local"})
        (worktree / "late").write_text("keep")
        result = self.repo.apply(plan, "all", exclusive_worktrees=True)
        self.assertEqual([action["result"] for action in result["actions"]], ["skipped", "skipped"])
        self.assertIn("not removed", result["actions"][1]["reason"])
        self.assertEqual(self.git("rev-parse", "feature"), self.git("rev-parse", "main"))

    def test_local_cas_rejects_ref_moved_after_revalidation(self):
        self.git("branch", "feature")
        plan = self.plan("local-branches")
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
