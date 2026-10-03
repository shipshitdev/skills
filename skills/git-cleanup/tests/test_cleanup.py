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
        self.assertEqual(self.plan("local-branches")["actions"], [])

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
        self.git("branch", "feature")
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
        self.assertEqual(after - set(before.splitlines()), {
            result["actions"][0]["oid"] + " " + result["actions"][0]["recovery_ref"]})
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
        self.assertEqual(plan["actions"][0]["proof"]["kind"], "ancestor")

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

    def test_exact_merged_pr_cannot_bypass_reverted_current_content(self):
        self.squash()
        self.git("revert", "--no-edit", "HEAD")
        self.git("push", "origin", "main")
        self.assertEqual(self.plan("local-branches")["actions"], [])

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

    def test_recovery_ref_retains_entire_squashed_history_after_deletion_and_gc(self):
        head, _merge = self.squash()
        parent = self.git("rev-parse", head + "^")
        plan = self.plan("local-branches")
        recovery = plan["actions"][0]["recovery_ref"]
        result = self.repo.apply(plan, "local-branches")
        self.assertEqual(result["actions"][0]["result"], "removed")
        self.assertEqual(self.git("rev-parse", recovery), head)
        self.git("reflog", "expire", "--expire=now", "--all")
        self.git("gc", "--prune=now")
        self.assertEqual(self.git("show", parent + ":file.txt"), "first")
        self.assertEqual(self.git("show", recovery + ":file.txt"), "second")

    def test_recovery_failure_prevents_candidate_deletion(self):
        self.squash()
        plan = self.plan("local-branches")
        with patch.object(self.repo, "preserve_history", side_effect=Refused("backup failed")):
            result = self.repo.apply(plan, "local-branches")
        self.assertEqual(result["actions"][0]["result"], "skipped")
        self.assertIn("feature", self.git("branch", "--format=%(refname:short)").splitlines())

    def test_symbolic_recovery_ref_cannot_disappear_with_candidate(self):
        self.squash()
        plan = self.plan("local-branches")
        recovery = plan["actions"][0]["recovery_ref"]
        self.git("symbolic-ref", recovery, "refs/heads/feature")
        result = self.repo.apply(plan, "local-branches")
        self.assertEqual(result["actions"][0]["result"], "skipped")
        self.assertIn("symbolic recovery", result["actions"][0]["reason"])
        self.assertEqual(self.git("rev-parse", recovery), self.git("rev-parse", "feature"))

    def test_conflicting_recovery_ref_preserves_both_histories(self):
        head, landed = self.squash()
        plan = self.plan("local-branches")
        recovery = plan["actions"][0]["recovery_ref"]
        self.git("update-ref", recovery, landed)
        result = self.repo.apply(plan, "local-branches")
        self.assertEqual(result["actions"][0]["result"], "skipped")
        self.assertEqual(self.git("rev-parse", recovery), landed)
        self.assertEqual(self.git("rev-parse", "feature"), head)

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
