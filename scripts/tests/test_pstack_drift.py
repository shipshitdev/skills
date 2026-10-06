from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "pstack_drift", Path(__file__).resolve().parents[1] / "pstack-drift.py"
)
assert SPEC and SPEC.loader
drift = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(drift)

PIN_A = "a" * 40
PIN_B = "b" * 40
HEAD_A = "c" * 40
LOCK = {"schema_version": 1, "sources": [
    {"id": "open-pstack", "repository": "https://github.com/o/open", "commit": PIN_A,
     "paths": ["."], "ignored_paths": ["skip/"]},
    {"id": "cursor-pstack", "repository": "https://github.com/o/mono", "commit": PIN_B,
     "paths": ["pstack"]},
]}


class FakeGh:
    """Stands in for the gh CLI; never touches the network."""

    def __init__(self, compares: dict, issues: list | None = None) -> None:
        self.compares = compares  # repo -> (head sha, compare payload)
        self.issues = issues or []
        self.writes: list[list[str]] = []

    def __call__(self, args: list[str]) -> str:
        if args[0] == "api":
            repo = args[1].split("/")[1] + "/" + args[1].split("/")[2]
            head, payload = self.compares[repo]
            if args[1].endswith(f"repos/{repo}"):
                return "main\n"
            if "/branches/" in args[1]:
                return head + "\n"
            return json.dumps(payload)
        if args[:2] == ["issue", "list"]:
            return json.dumps(self.issues)
        self.writes.append(args)
        return "https://github.com/x/y/issues/9\n"


def identical() -> dict:
    return {"status": "identical", "ahead_by": 0, "files": []}


def ahead(*names: str, count: int = 3) -> dict:
    return {"status": "ahead", "ahead_by": count, "files": [{"filename": n} for n in names]}


class PstackDriftTests(unittest.TestCase):
    def setUp(self) -> None:
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        (self.root / "upstream/pstack").mkdir(parents=True)
        (self.root / "upstream/pstack/lock.json").write_text(json.dumps(LOCK))

    def run_main(self, gh: FakeGh, *extra: str) -> int:
        return drift.main(["--root", str(self.root), "--repo", "x/y", *extra], run=gh)

    def test_no_drift_opens_nothing(self) -> None:
        gh = FakeGh({"o/open": (PIN_A, identical()), "o/mono": (PIN_B, identical())})
        self.assertEqual(self.run_main(gh), 0)
        self.assertEqual(gh.writes, [])

    def test_ahead_only_outside_tracked_paths_is_not_drift(self) -> None:
        gh = FakeGh({"o/open": (PIN_A, ahead("skip/x.md")),
                     "o/mono": (HEAD_A, ahead("other-plugin/README.md"))})
        self.assertEqual(self.run_main(gh), 0)
        self.assertEqual(gh.writes, [])

    def test_drift_creates_issue_with_candidate_command(self) -> None:
        gh = FakeGh({"o/open": (PIN_A, identical()),
                     "o/mono": (HEAD_A, ahead("pstack/skills/a/SKILL.md", "other/x.md"))})
        self.assertEqual(self.run_main(gh), 0)
        (call,) = gh.writes
        self.assertEqual(call[:2], ["issue", "create"])
        body = call[call.index("--body") + 1]
        self.assertIn(drift.MARKER, body)
        self.assertIn(f"`{PIN_B}`", body)
        self.assertIn(f"`{HEAD_A}`", body)
        self.assertIn("Ahead by: 3 commits", body)
        self.assertIn(f"https://github.com/o/mono/compare/{PIN_B}...{HEAD_A}", body)
        self.assertIn("`pstack/skills/a/SKILL.md`", body)
        self.assertNotIn("other/x.md", body)
        self.assertIn(f"--source cursor-pstack \\\n  --checkout /path/to/cursor-pstack \\\n  --commit {HEAD_A}", body)
        self.assertNotIn("## open-pstack", body)

    def test_existing_issue_is_updated_not_duplicated(self) -> None:
        payloads = {"o/open": (PIN_A, identical()), "o/mono": (HEAD_A, ahead("pstack/a.md"))}
        existing = [{"number": 7, "title": "old", "body": drift.MARKER + "\nstale"}]
        gh = FakeGh(payloads, existing)
        self.assertEqual(self.run_main(gh), 0)
        (call,) = gh.writes
        self.assertEqual(call[:3], ["issue", "edit", "7"])

    def test_identical_existing_body_is_left_alone(self) -> None:
        payloads = {"o/open": (PIN_A, identical()), "o/mono": (HEAD_A, ahead("pstack/a.md"))}
        reports = [drift.inspect(s, FakeGh(payloads)) for s in LOCK["sources"]]
        gh = FakeGh(payloads, [{"number": 7, "title": drift.TITLE, "body": drift.render(reports)}])
        self.assertEqual(self.run_main(gh), 0)
        self.assertEqual(gh.writes, [])

    def test_resolved_drift_closes_open_issue(self) -> None:
        gh = FakeGh({"o/open": (PIN_A, identical()), "o/mono": (PIN_B, identical())},
                    [{"number": 7, "title": drift.TITLE, "body": drift.MARKER}])
        self.assertEqual(self.run_main(gh), 0)
        (call,) = gh.writes
        self.assertEqual(call[:3], ["issue", "close", "7"])

    def test_dry_run_never_writes(self) -> None:
        gh = FakeGh({"o/open": (PIN_A, identical()), "o/mono": (HEAD_A, ahead("pstack/a.md"))})
        self.assertEqual(drift.main(["--root", str(self.root), "--dry-run"], run=gh), 0)
        self.assertEqual(gh.writes, [])

    def test_long_file_list_is_truncated(self) -> None:
        names = [f"pstack/f{i}.md" for i in range(drift.MAX_FILES + 5)]
        report = drift.inspect(LOCK["sources"][1], FakeGh({"o/mono": (HEAD_A, ahead(*names))}))
        body = drift.render([report])
        self.assertIn("and 5 more", body)
        self.assertNotIn(f"f{drift.MAX_FILES + 4}.md", body)


if __name__ == "__main__":
    unittest.main()
