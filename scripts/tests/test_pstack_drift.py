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

    def __init__(self, compares: dict, issues: list | None = None, commits: dict | None = None,
                 range_commits: dict | None = None) -> None:
        self.compares = compares  # repo -> (head sha, compare payload)
        self.issues = issues or []
        self.commits = commits or {}  # repo -> commits touching the tracked path since the pin
        self.range_commits = range_commits or {}  # repo -> shas in pin..head
        self.calls: list[list[str]] = []
        self.writes: list[list[str]] = []

    def __call__(self, args: list[str]) -> str:
        self.calls.append(args)
        if args[0] == "api":
            endpoint = next(a for a in args[1:] if a.startswith("repos/"))
            repo = "/".join(endpoint.split("/")[1:3])
            if repo == "x/y":  # the tracking repository's issue list, served 100 per page
                pages = [self.issues[i:i + 100] for i in range(0, len(self.issues), 100)] or [[]]
                return "".join(json.dumps(page) for page in pages)
            head, payload = self.compares[repo]
            if "--paginate" in args and "/compare/" in endpoint:
                return json.dumps({"commits": [{"sha": sha} for sha in self.range_commits.get(repo, [])]})
            if "/commits/" in endpoint:
                return "2026-01-01T00:00:00Z\n"
            if "/commits?" in endpoint:
                return json.dumps(self.commits.get(repo, []))
            if endpoint == f"repos/{repo}":
                return "main\n"
            if "/branches/" in endpoint:
                return head + "\n"
            return json.dumps(payload)
        self.writes.append(args)
        return "https://github.com/x/y/issues/9\n"


def identical() -> dict:
    return {"status": "identical", "ahead_by": 0, "files": []}


def ahead(*names: str, count: int = 3) -> dict:
    return {"status": "ahead", "ahead_by": count, "files": [{"filename": n} for n in names]}


def renamed(old: str, new: str) -> dict:
    return {"status": "ahead", "ahead_by": 1,
            "files": [{"filename": new, "previous_filename": old, "status": "renamed"}]}


def gh_issue(number: int, body: str = "", pull: bool = False) -> dict:
    issue = {"number": number, "title": f"issue {number}", "body": body}
    if pull:
        issue["pull_request"] = {}
    return issue


class PstackDriftTests(unittest.TestCase):
    def setUp(self) -> None:
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        (self.root / "upstream/pstack").mkdir(parents=True)
        (self.root / "upstream/pstack/lock.json").write_text(json.dumps(LOCK))

    def run_main(self, gh: FakeGh, *extra: str) -> int:
        return drift.main(["--root", str(self.root), "--repo", "x/y", *extra], run=gh, write=gh)

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


    def test_rename_out_of_tracked_path_is_drift(self) -> None:
        report = drift.inspect(LOCK["sources"][1],
                               FakeGh({"o/mono": (HEAD_A, renamed("pstack/skills/a.md", "elsewhere/a.md"))}))
        self.assertTrue(drift.drifted(report))
        body = drift.render([report])
        self.assertIn("`elsewhere/a.md` (renamed from `pstack/skills/a.md`)", body)

    def test_rename_into_tracked_path_is_drift(self) -> None:
        report = drift.inspect(LOCK["sources"][1],
                               FakeGh({"o/mono": (HEAD_A, renamed("other/a.md", "pstack/a.md"))}))
        self.assertTrue(drift.drifted(report))

    def test_rename_outside_tracked_paths_is_not_drift(self) -> None:
        report = drift.inspect(LOCK["sources"][1],
                               FakeGh({"o/mono": (HEAD_A, renamed("other/a.md", "other/b.md"))}))
        self.assertFalse(drift.drifted(report))

    def truncated_payload(self) -> dict:
        return ahead(*[f"other/f{i}.md" for i in range(drift.COMPARE_FILE_CAP)], count=9)

    def test_truncated_compare_with_scoped_commits_is_drift(self) -> None:
        commits = {"o/mono": [{"sha": "d" * 40, "commit": {"message": "touch pstack\n\nbody"}},
                              {"sha": PIN_B, "commit": {"message": "the pin"}}]}
        gh = FakeGh({"o/open": (PIN_A, identical()), "o/mono": (HEAD_A, self.truncated_payload())},
                    commits=commits, range_commits={"o/mono": ["d" * 40]})
        report = drift.inspect(LOCK["sources"][1], gh)
        self.assertTrue(drift.drifted(report))
        self.assertEqual([c["subject"] for c in report["commits"]], ["touch pstack"])
        self.assertIn("checked through commit history", drift.render([report]))
        self.assertTrue(any("--paginate" in call and "path=pstack" in call[-1] for call in gh.calls))

    def test_ancestor_with_later_timestamp_is_not_drift(self) -> None:
        # The path listing returns an ancestor of the pin (date-window match) that is outside pin..head.
        commits = {"o/mono": [{"sha": "e" * 40, "commit": {"message": "old ancestor, later date"}}]}
        gh = FakeGh({"o/mono": (HEAD_A, self.truncated_payload())}, commits=commits,
                    range_commits={"o/mono": ["d" * 40]})
        report = drift.inspect(LOCK["sources"][1], gh)
        self.assertEqual(report["commits"], [])
        self.assertFalse(drift.drifted(report))

    def test_truncated_compare_with_no_scoped_commits_is_clean(self) -> None:
        gh = FakeGh({"o/mono": (HEAD_A, self.truncated_payload())}, commits={"o/mono": []})
        self.assertFalse(drift.drifted(drift.inspect(LOCK["sources"][1], gh)))

    def test_truncated_whole_repo_source_is_inconclusive_and_never_closes(self) -> None:
        payloads = {"o/open": (PIN_A, self.truncated_payload()), "o/mono": (PIN_B, identical())}
        gh = FakeGh(payloads, [gh_issue(7, drift.MARKER)])
        self.assertEqual(self.run_main(gh), 0)
        self.assertTrue(all(call[:2] != ["issue", "close"] for call in gh.writes))
        report = drift.inspect(LOCK["sources"][0], gh)
        self.assertTrue(report["inconclusive"])
        self.assertIn("INCONCLUSIVE", drift.render([report]))

    def test_lookup_finds_oldest_tracker_among_more_than_200_issues(self) -> None:
        issues = [gh_issue(i, "noise") for i in range(300, 0, -1)]
        issues.append(gh_issue(1000, drift.MARKER, pull=True))  # a PR carrying the marker is ignored
        issues.append(gh_issue(5, drift.MARKER))
        gh = FakeGh({}, issues)
        found = drift.find_open("x/y", gh)
        self.assertEqual(found["number"], 5)
        (call,) = gh.calls
        self.assertIn("--paginate", call)
        self.assertNotIn("--limit", call)

    def test_missing_write_token_fails_without_writing(self) -> None:
        gh = FakeGh({"o/open": (PIN_A, identical()), "o/mono": (HEAD_A, ahead("pstack/a.md"))})
        code = drift.main(["--root", str(self.root), "--repo", "x/y"], run=gh, env={})
        self.assertEqual(code, 1)
        self.assertEqual(gh.writes, [])
        self.assertEqual(gh.calls, [])

    def test_dry_run_does_not_need_write_token(self) -> None:
        gh = FakeGh({"o/open": (PIN_A, identical()), "o/mono": (PIN_B, identical())})
        self.assertEqual(drift.main(["--root", str(self.root), "--dry-run"], run=gh, env={}), 0)


if __name__ == "__main__":
    unittest.main()
