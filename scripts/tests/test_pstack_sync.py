from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "pstack_sync", Path(__file__).resolve().parents[1] / "pstack-sync.py"
)
assert SPEC and SPEC.loader
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)


class PstackSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.base = Path(self.scratch.name)
        self.root = self.base / "maintained"
        self.directory = self.root / "upstream/pstack"
        self.directory.mkdir(parents=True)
        self.target = self.root / "skills/pstack/SKILL.md"
        self.target.parent.mkdir(parents=True)
        self.target.write_text("Canonical adapted procedure.\n")
        self.evidence = self.root / "docs/verification.md"
        self.evidence.parent.mkdir()
        self.evidence.write_text("Fixture review evidence.\n")
        self.source_name = "skills/poteto-mode/SKILL.md"
        self.files = {self.source_name: (b"Original procedure.\n", 0o644)}
        blob = sync.archive_bytes(self.files)
        (self.directory / "fixture.tar.gz").write_bytes(blob)
        self.source = {
            "id": "fixture", "repository": "https://example.com/pstack",
            "commit": "a" * 40, "paths": ["."],
            "archive": "upstream/pstack/fixture.tar.gz",
            "sha256": sync.digest(blob), "files": sync.inventory(self.files),
        }
        self.lock = {"schema_version": 1, "sources": [self.source]}
        self.entry = {
            "disposition": "adapted", "reason": "Preserve local invocation contract.",
            "destinations": [{"path": "skills/pstack/SKILL.md", "sha256": sync.digest(self.target.read_bytes()), "executable": False}],
            "verification": ["docs/verification.md"],
        }
        self.mapping = {"schema_version": 1, "files": {"fixture:" + self.source_name: self.entry}}
        self.save()

    def save(self) -> None:
        sync.write_json(self.directory / "lock.json", self.lock)
        sync.write_json(self.directory / "mapping.json", self.mapping)

    def test_unchanged_import_is_repeatably_verified(self) -> None:
        before = (self.directory / "mapping.json").read_bytes()
        self.assertEqual(sync.verify(self.root), [])
        self.assertEqual(sync.verify(self.root), [])
        self.assertEqual((self.directory / "mapping.json").read_bytes(), before)

    def test_archive_build_is_deterministic_and_preserves_modes(self) -> None:
        files = {"z/run.sh": (b"echo test\n", 0o755), **self.files}
        self.assertEqual(sync.archive_bytes(files), sync.archive_bytes(dict(reversed(list(files.items())))))
        self.assertEqual(sync.read_archive(sync.archive_bytes(files)), files)

    def test_archive_checksum_drift_fails(self) -> None:
        self.source["sha256"] = "0" * 64
        self.save()
        self.assertTrue(any("checksum mismatch" in e for e in sync.verify(self.root)))

    def test_unmapped_added_file_and_stale_mapping_fail(self) -> None:
        self.mapping["files"] = {"fixture:removed.md": self.entry}
        self.save()
        errors = sync.verify(self.root)
        self.assertTrue(any("Unmapped upstream file" in e for e in errors))
        self.assertTrue(any("no pinned source" in e for e in errors))

    def test_local_adaptation_change_requires_recorded_review(self) -> None:
        self.target.write_text("Changed local policy.\n")
        self.assertTrue(any("unreviewed destination" in e for e in sync.verify(self.root)))
        self.assertEqual(sync.record(self.root, "Reviewed local authorization contract."), 1)
        self.assertEqual(sync.verify(self.root), [])
        self.assertEqual(sync.record(self.root, "Unchanged follow-up."), 0)

    def test_executable_bit_changes_need_review(self) -> None:
        self.target.chmod(0o755)
        self.assertTrue(any("executable-bit change" in e for e in sync.verify(self.root)))
        sync.record(self.root, "Reviewed script invocation mode.")
        self.assertEqual(sync.verify(self.root), [])

    def test_identical_claim_cannot_hide_semantic_adaptation(self) -> None:
        self.entry["disposition"] = "identical"
        self.save()
        self.assertTrue(any("identical disposition differs" in e for e in sync.verify(self.root)))

    def test_runtime_cannot_be_marked_archive_only(self) -> None:
        self.entry["disposition"] = "metadata"
        self.entry["destinations"] = [{
            "path": "upstream/pstack/fixture.tar.gz",
            "sha256": self.source["sha256"],
        }]
        self.save()
        self.assertTrue(any("cannot be archive-only" in e for e in sync.verify(self.root)))

    def test_extensionless_executables_and_additional_script_types_cannot_be_archive_only(self) -> None:
        for name, mode in [
            ("skills/pstack/scripts/runner/pstack-runner", 0o755),
            ("skills/pstack/scripts/helper.py", 0o644),
            ("skills/pstack/scripts/helper.ps1", 0o644),
            ("skills/pstack/scripts/component.tsx", 0o644),
        ]:
            with self.subTest(name=name):
                files = {name: (b"runtime fixture\n", mode)}
                blob = sync.archive_bytes(files)
                (self.directory / "fixture.tar.gz").write_bytes(blob)
                self.source.update(sha256=sync.digest(blob), files=sync.inventory(files))
                self.mapping["files"] = {"fixture:" + name: {
                    "disposition": "metadata", "reason": "Invalid archive-only runtime.",
                    "destinations": [{"path": "upstream/pstack/fixture.tar.gz",
                                      "sha256": sync.digest(blob), "executable": False}],
                    "verification": ["docs/verification.md"],
                }}
                self.save()
                self.assertTrue(any("cannot be archive-only" in e for e in sync.verify(self.root)))

    def test_pending_mapping_and_missing_evidence_fail(self) -> None:
        self.entry.update(disposition="pending", verification=["missing-review.md"])
        self.save()
        errors = sync.verify(self.root)
        self.assertTrue(any("pending disposition" in e for e in errors))
        self.assertTrue(any("missing verification" in e for e in errors))

    def test_destination_traversal_and_symlinks_are_rejected(self) -> None:
        for path in ("../outside", "/outside", "skills/../../outside"):
            with self.assertRaises(ValueError):
                sync.local_file(self.root, path)
        outside = self.base / "outside"
        outside.write_text("outside")
        (self.root / "link").symlink_to(outside)
        with self.assertRaises(ValueError):
            sync.local_file(self.root, "link")

    def test_archive_links_and_traversal_are_rejected_without_extraction(self) -> None:
        for name, kind in (("../escape", tarfile.REGTYPE), ("link", tarfile.SYMTYPE)):
            buffer = io.BytesIO()
            with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
                entry = tarfile.TarInfo(name)
                entry.type = kind
                entry.linkname = "/outside" if kind == tarfile.SYMTYPE else ""
                archive.addfile(entry)
            with self.assertRaises(ValueError):
                sync.read_archive(buffer.getvalue())

    def test_duplicate_json_keys_are_rejected(self) -> None:
        path = self.root / "duplicate.json"
        path.write_text('{"schema_version": 1, "schema_version": 2}')
        with self.assertRaises(ValueError):
            sync.read_json(path)

    def git(self, checkout: Path, *args: str) -> str:
        return subprocess.check_output(["git", "-C", str(checkout), *args], stderr=subprocess.DEVNULL).decode().strip()

    def repository(self) -> tuple[Path, str, str]:
        checkout = self.base / "checkout"
        checkout.mkdir()
        self.git(checkout, "init", "-q")
        self.git(checkout, "config", "user.email", "fixture@example.com")
        self.git(checkout, "config", "user.name", "Fixture")
        self.git(checkout, "remote", "add", "origin", self.source["repository"])
        path = checkout / self.source_name
        path.parent.mkdir(parents=True)
        path.write_bytes(self.files[self.source_name][0])
        (checkout / "removed.txt").write_text("removed")
        self.git(checkout, "add", ".")
        self.git(checkout, "commit", "-qm", "base")
        first = self.git(checkout, "rev-parse", "HEAD")
        old = sync.snapshot(checkout, first, ["."])
        blob = sync.archive_bytes(old)
        (self.directory / "fixture.tar.gz").write_bytes(blob)
        self.source.update(commit=first, files=sync.inventory(old), sha256=sync.digest(blob))
        self.mapping["files"]["fixture:removed.txt"] = {
            **self.entry, "disposition": "metadata", "reason": "Historical source metadata.",
        }
        self.save()
        path.write_text("Updated upstream procedure.\n")
        (checkout / "removed.txt").unlink()
        (checkout / "added.txt").write_text("new")
        self.git(checkout, "add", ".")
        self.git(checkout, "commit", "-qm", "candidate")
        return checkout, first, self.git(checkout, "rev-parse", "HEAD")

    def test_candidate_reports_add_remove_change_and_local_conflict_without_promotion(self) -> None:
        checkout, _, commit = self.repository()
        self.target.write_text("Local independent edit.\n")
        accepted = (self.directory / "lock.json").read_bytes()
        output = self.base / "candidate"
        report = sync.candidate(self.root, "fixture", checkout, commit, output)
        self.assertEqual(report["added"], ["added.txt"])
        self.assertEqual(report["removed"], ["removed.txt"])
        self.assertEqual(report["changed"], [self.source_name])
        changed = next(row for row in report["adaptations_requiring_review"] if row["source_file"] == self.source_name)
        self.assertTrue(changed["destinations"][0]["changed_since_acceptance"])
        self.assertIn("Local independent edit", changed["destinations"][0]["upstream_to_local_diff"])
        self.assertEqual((self.directory / "lock.json").read_bytes(), accepted)
        self.assertEqual(self.target.read_text(), "Local independent edit.\n")
        candidate = json.loads((output / "candidate-mapping.json").read_text())
        self.assertEqual(candidate["files"]["fixture:added.txt"]["disposition"], "pending")
        self.assertNotIn("fixture:removed.txt", candidate["files"])

    def test_candidate_unchanged_rerun_is_identical_and_output_cannot_be_overwritten(self) -> None:
        checkout, first, _ = self.repository()
        left, right = self.base / "left", self.base / "right"
        report = sync.candidate(self.root, "fixture", checkout, first, left)
        sync.candidate(self.root, "fixture", checkout, first, right)
        self.assertEqual(report["changed"], [])
        self.assertEqual((left / "report.json").read_bytes(), (right / "report.json").read_bytes())
        self.assertEqual((left / "fixture.tar.gz").read_bytes(), (right / "fixture.tar.gz").read_bytes())
        with self.assertRaises(FileExistsError):
            sync.candidate(self.root, "fixture", checkout, first, left)

    def test_candidate_rejects_wrong_upstream_and_in_repository_output(self) -> None:
        checkout, _, commit = self.repository()
        with self.assertRaises(ValueError):
            sync.candidate(self.root, "fixture", checkout, commit, self.root / "candidate")
        self.git(checkout, "remote", "set-url", "origin", "https://example.com/unrelated")
        with self.assertRaises(ValueError):
            sync.candidate(self.root, "fixture", checkout, commit, self.base / "candidate")

    def test_moving_ref_and_upstream_symlink_fail(self) -> None:
        checkout, _, _ = self.repository()
        with self.assertRaises(ValueError):
            sync.snapshot(checkout, "HEAD", ["."])
        (checkout / "unsafe").symlink_to("/outside")
        self.git(checkout, "add", ".")
        self.git(checkout, "commit", "-qm", "symlink")
        with self.assertRaises(ValueError):
            sync.snapshot(checkout, self.git(checkout, "rev-parse", "HEAD"), ["."])

    def test_declared_ignored_symlink_is_skipped_and_unlisted_symlinks_still_fail(self) -> None:
        checkout, _, _ = self.repository()
        (checkout / "repo-only").symlink_to("/outside")
        (checkout / "unsafe").symlink_to("/outside")
        self.git(checkout, "add", ".")
        self.git(checkout, "commit", "-qm", "symlinks")
        commit = self.git(checkout, "rev-parse", "HEAD")
        skipped: list[str] = []
        files = sync.snapshot(checkout, commit, ["."], ["repo-only", "unsafe"], skipped)
        self.assertEqual(skipped, ["repo-only", "unsafe"])
        self.assertNotIn("repo-only", files)
        with self.assertRaises(ValueError):
            sync.snapshot(checkout, commit, ["."], ["repo-only"])
        with self.assertRaises(ValueError):
            sync.snapshot(checkout, commit, ["."])

    def test_candidate_records_ignored_paths_and_rejects_mapped_or_malformed_lists(self) -> None:
        checkout, _, _ = self.repository()
        (checkout / "repo-only").symlink_to("/outside")
        self.git(checkout, "add", ".")
        self.git(checkout, "commit", "-qm", "symlink")
        commit = self.git(checkout, "rev-parse", "HEAD")
        with self.assertRaises(ValueError):
            sync.candidate(self.root, "fixture", checkout, commit, self.base / "unlisted")
        self.source["ignored_paths"] = ["repo-only"]
        self.save()
        report = sync.candidate(self.root, "fixture", checkout, commit, self.base / "listed")
        self.assertEqual(report["ignored_paths"], ["repo-only"])
        candidate = json.loads((self.base / "listed/candidate-lock.json").read_text())
        self.assertEqual(candidate["sources"][0]["ignored_paths"], ["repo-only"])
        self.source["ignored_paths"] = ["removed.txt"]
        self.save()
        self.assertTrue(any("also archived" in e for e in sync.verify(self.root)))
        self.source["ignored_paths"] = ["../escape"]
        self.save()
        self.assertTrue(any("Unsafe path" in e for e in sync.verify(self.root)))
        self.source["ignored_paths"] = ["a", "a"]
        self.save()
        with self.assertRaises(ValueError):
            sync.candidate(self.root, "fixture", checkout, commit, self.base / "dup")


if __name__ == "__main__":
    unittest.main()
