from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "upstream_drift", Path(__file__).resolve().parents[1] / "upstream-drift.py"
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
                 range_commits: dict | None = None, by_base: dict | None = None,
                 tags: dict | None = None, errors: dict | None = None) -> None:
        self.by_base = by_base or {}  # (repo, base) -> compare payload overriding the repo default
        self.tags = tags or {}  # repo -> tag names
        self.errors = errors or {}  # (repo, base) -> stderr of a failing compare
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
            if endpoint.startswith(f"repos/{repo}/tags"):
                return json.dumps([{"name": name} for name in self.tags.get(repo, [])])
            head, payload = self.compares[repo]
            if "/compare/" in endpoint and "--paginate" not in args:
                base = endpoint.split("/compare/")[1].split("...")[0]
                if (repo, base) in self.errors:
                    raise subprocess.CalledProcessError(1, args, stderr=self.errors[(repo, base)])
                payload = self.by_base.get((repo, base), payload)
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


def gh_issue(number: int, body: str = "", pull: bool = False, state: str = "open") -> dict:
    issue = {"number": number, "title": f"issue {number}", "body": body, "state": state}
    if pull:
        issue["pull_request"] = {}
    return issue


class UpstreamDriftTests(unittest.TestCase):
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
        self.assertNotIn("### open-pstack", body)

    def test_existing_issue_is_updated_not_duplicated(self) -> None:
        payloads = {"o/open": (PIN_A, identical()), "o/mono": (HEAD_A, ahead("pstack/a.md"))}
        existing = [{"number": 7, "title": "old", "body": drift.MARKER + "\nstale"}]
        gh = FakeGh(payloads, existing)
        self.assertEqual(self.run_main(gh), 0)
        self.assertEqual([call[:3] for call in gh.writes],
                         [["issue", "edit", "7"], ["issue", "comment", "7"]])

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

    def test_lookup_finds_tracker_among_more_than_200_issues(self) -> None:
        issues = [gh_issue(i, "noise") for i in range(300, 0, -1)]
        issues.append(gh_issue(1000, drift.MARKER, pull=True))  # a PR carrying the marker is ignored
        issues.append(gh_issue(5, drift.MARKER))
        gh = FakeGh({}, issues)
        found = drift.find_marker("x/y", gh)
        self.assertEqual(found["number"], 5)
        (call,) = gh.calls
        self.assertIn("--paginate", call)
        self.assertIn("state=all", call[-1])
        self.assertNotIn("--limit", call)

    def test_lookup_prefers_the_most_recent_marker_issue_in_any_state(self) -> None:
        gh = FakeGh({}, [gh_issue(3, drift.MARKER), gh_issue(9, drift.MARKER, state="closed")])
        self.assertEqual(drift.find_marker("x/y", gh)["number"], 9)

    def test_missing_write_token_fails_without_writing(self) -> None:
        gh = FakeGh({"o/open": (PIN_A, identical()), "o/mono": (HEAD_A, ahead("pstack/a.md"))})
        code = drift.main(["--root", str(self.root), "--repo", "x/y"], run=gh, env={})
        self.assertEqual(code, 1)
        self.assertEqual(gh.writes, [])
        self.assertEqual(gh.calls, [])

    def test_dry_run_does_not_need_write_token(self) -> None:
        gh = FakeGh({"o/open": (PIN_A, identical()), "o/mono": (PIN_B, identical())})
        self.assertEqual(drift.main(["--root", str(self.root), "--dry-run"], run=gh, env={}), 0)


SKILL_TEMPLATE = """---
name: {name}
description: test
metadata:
  version: "1.0.0"
  source: {source}
{pins}  last_synced: "2026-01-01"
---
body
"""
UP = "u/up"  # a derived-skill upstream not covered by lock.json
PIN_R = "r" * 12


class SkillDriftTests(unittest.TestCase):
    def setUp(self) -> None:
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        (self.root / "upstream/pstack").mkdir(parents=True)
        (self.root / "upstream/pstack/lock.json").write_text(json.dumps(LOCK))
        self.base = {"o/open": (PIN_A, identical()), "o/mono": (PIN_B, identical())}

    def add_skill(self, name: str, source: str, **pins: str) -> None:
        text = "".join(f"  {key}: {value}\n" for key, value in pins.items())
        folder = self.root / "skills" / name
        folder.mkdir(parents=True)
        (folder / "SKILL.md").write_text(SKILL_TEMPLATE.format(name=name, source=source, pins=text))

    def add_reference(self, skill: str, name: str, text: str) -> None:
        folder = self.root / "skills" / skill / "references"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{name}.md").write_text(text)

    def blob(self, path: str, repo: str = UP, ref: str = "main") -> str:
        return f"https://github.com/{repo}/blob/{ref}/{path}"

    def fake(self, **kwargs) -> FakeGh:
        compares = {**self.base, **kwargs.pop("compares", {})}
        return FakeGh(compares, **kwargs)

    def run_main(self, gh: FakeGh, *extra: str) -> int:
        return drift.main(["--root", str(self.root), "--repo", "x/y", *extra], run=gh, write=gh)

    def reports(self, gh: FakeGh) -> dict:
        return {r["id"]: r for r in drift.collect(self.root, gh)}

    def test_rolling_drift_lists_only_the_changed_skill(self) -> None:
        self.add_skill("changed", self.blob("skills/changed/SKILL.md"), upstream_commit=PIN_R)
        self.add_skill("quiet", self.blob("skills/quiet/SKILL.md"), upstream_commit=PIN_R)
        gh = self.fake(compares={UP: (HEAD_A, ahead("skills/changed/SKILL.md", "skills/x.md"))})
        reports = self.reports(gh)
        self.assertEqual(drift.state(reports["changed"]), "drifted")
        self.assertEqual(drift.state(reports["quiet"]), "clean")
        self.assertEqual(self.run_main(gh), 0)
        body = gh.writes[0][gh.writes[0].index("--body") + 1]
        self.assertIn("### u/up", body)
        self.assertIn(f"| changed | `skills/changed/SKILL.md` | `{PIN_R}` | `{HEAD_A}` |", body)
        self.assertIn(f"https://github.com/u/up/compare/{PIN_R}...{HEAD_A}", body)
        self.assertNotIn("quiet", body)
        self.assertIn("bump `metadata.upstream_commit`", body)

    def test_absorbed_reference_pin_reports_its_own_file(self) -> None:
        self.add_skill("host", self.blob("skills/host/SKILL.md", repo="o/other"), upstream_commit=PIN_R)
        self.add_reference("host", "absorbed", SKILL_TEMPLATE.format(
            name="absorbed", source=self.blob("skills/absorbed/SKILL.md"), pins=f"  upstream_commit: {PIN_R}\n"))
        gh = self.fake(compares={UP: (HEAD_A, ahead("skills/absorbed/SKILL.md")),
                                 "o/other": (PIN_R, identical())})
        reports = self.reports(gh)
        self.assertEqual(reports["host/absorbed"]["pin_file"], "skills/host/references/absorbed.md")
        self.assertEqual(reports["host"]["pin_file"], "skills/host/SKILL.md")
        self.assertEqual(drift.state(reports["host/absorbed"]), "drifted")
        self.assertIn("`host/absorbed` pin lives in `skills/host/references/absorbed.md`",
                      drift.render([reports["host/absorbed"]]))

    def test_reference_without_upstream_metadata_is_ignored(self) -> None:
        self.add_skill("host", self.blob("skills/host/SKILL.md"), upstream_commit=PIN_R)
        self.add_reference("host", "notes", "# Plain notes\n\nNo frontmatter here.\n")
        gh = self.fake(compares={UP: (PIN_R, identical())})
        self.assertNotIn("host/notes", self.reports(gh))

    def test_one_compare_serves_every_skill_sharing_a_pin(self) -> None:
        for name in ("a", "b", "c"):
            self.add_skill(name, self.blob(f"skills/{name}/SKILL.md"), upstream_commit=PIN_R)
        gh = self.fake(compares={UP: (HEAD_A, ahead("skills/a/SKILL.md"))})
        drift.collect(self.root, gh)
        compares = [c for c in gh.calls if any("/compare/" in a for a in c) and "repos/u/up" in " ".join(c)]
        self.assertEqual(len(compares), 1)

    def test_rolling_rename_is_drift(self) -> None:
        self.add_skill("moved", self.blob("skills/moved/SKILL.md"), upstream_commit=PIN_R)
        gh = self.fake(compares={UP: (HEAD_A, renamed("skills/moved/SKILL.md", "skills/new/SKILL.md"))})
        report = self.reports(gh)["moved"]
        self.assertEqual(drift.state(report), "drifted")
        self.assertIn("renamed from `skills/moved/SKILL.md` to `skills/new/SKILL.md`", drift.render([report]))

    def test_rolling_truncation_is_scoped_by_ancestry(self) -> None:
        self.add_skill("big", self.blob("skills/big/SKILL.md"), upstream_commit=PIN_R)
        payload = ahead(*[f"other/f{i}.md" for i in range(drift.COMPARE_FILE_CAP)], count=9)
        commits = {UP: [{"sha": "d" * 40, "commit": {"message": "touch big"}},
                        {"sha": "e" * 40, "commit": {"message": "ancestor with later date"}}]}
        gh = self.fake(compares={UP: (HEAD_A, payload)}, commits=commits, range_commits={UP: ["d" * 40]})
        report = self.reports(gh)["big"]
        self.assertEqual([c["subject"] for c in report["commits"]], ["touch big"])
        self.assertEqual(drift.state(report), "drifted")
        clean = self.fake(compares={UP: (HEAD_A, payload)}, commits={UP: []})
        self.assertEqual(drift.state(self.reports(clean)["big"]), "clean")

    def test_tagged_drift_tolerates_the_tag_prefix(self) -> None:
        self.add_skill("tagged", self.blob("ref/tagged.md"), upstream_version="v1.0.0",
                       upstream_latest="skill-v1.2.0")
        tags = {UP: ["skill-v1.2.0", "skill-v1.0.0", "skill-v1.1.0", "ext-v9.0.0", "skill-v1.3.0-rc.1"]}
        gh = self.fake(compares={UP: (HEAD_A, identical())}, tags=tags,
                       by_base={(UP, "skill-v1.0.0"): ahead("ref/tagged.md")})
        report = self.reports(gh)["tagged"]
        self.assertEqual(report["pinned"], "skill-v1.0.0")
        self.assertEqual(report["head"], "skill-v1.2.0")
        self.assertEqual(drift.state(report), "drifted")
        self.assertIn(f"compare/skill-v1.0.0...skill-v1.2.0", report["compare_url"])

    def test_tagged_at_latest_or_untouched_path_is_clean(self) -> None:
        self.add_skill("latest", self.blob("ref/latest.md"), upstream_version="skill-v1.2.0")
        self.add_skill("untouched", self.blob("ref/untouched.md"), upstream_version="skill-v1.0.0")
        gh = self.fake(compares={UP: (HEAD_A, ahead("ref/else.md"))},
                       tags={UP: ["skill-v1.0.0", "skill-v1.2.0"]})
        reports = self.reports(gh)
        self.assertEqual(drift.state(reports["latest"]), "clean")
        self.assertEqual(drift.state(reports["untouched"]), "clean")

    def test_bare_pin_never_switches_to_an_unrelated_tag_family(self) -> None:
        tags = {UP: ["cli-v2.1.1", "cli-v2.2.0", "skill-v3.0.4"]}
        self.add_skill("named", self.blob("ref/named.md"), upstream_version="v2.1.1",
                       upstream_latest="skill-v3.0.4")
        self.add_skill("unnamed", self.blob("ref/unnamed.md"), upstream_version="v2.1.1")
        gh = self.fake(compares={UP: (HEAD_A, identical())}, tags=tags)
        reports = self.reports(gh)
        for name in ("named", "unnamed"):
            self.assertEqual(drift.state(reports[name]), "inconclusive", name)
            self.assertNotEqual(reports[name]["pinned"], "cli-v2.1.1", name)

    def test_unresolvable_tag_pin_is_inconclusive_never_clean(self) -> None:
        self.add_skill("ghost", self.blob("ref/ghost.md"), upstream_version="skill-v2.1.1")
        gh = self.fake(compares={UP: (HEAD_A, identical())}, tags={UP: ["skill-v3.0.4", "cli-v2.1.1"]})
        report = self.reports(gh)["ghost"]
        self.assertEqual(drift.state(report), "inconclusive")
        self.assertTrue(drift.drifted(report))
        self.assertIn("UNRESOLVABLE", drift.render([report]))

    def test_missing_derived_head_or_tags_keeps_other_sources(self) -> None:
        self.add_skill("missing", self.blob("ref/missing.md"), upstream_commit=PIN_R)
        self.add_skill("tagged", self.blob("ref/tagged.md"), upstream_version="v1.0.0")
        self.add_skill("healthy", self.blob("ref/healthy.md", repo="u/healthy"), upstream_commit=PIN_R)
        gh = self.fake(compares={"u/healthy": (HEAD_A, ahead("ref/healthy.md"))})

        def missing(args):
            if "repos/u/up" in args or "repos/u/up/tags?per_page=100" in args:
                raise subprocess.CalledProcessError(1, args, stderr="gh: Not Found (HTTP 404)")
            return gh(args)

        reports = self.reports(missing)
        self.assertEqual(drift.state(reports["missing"]), "inconclusive")
        self.assertEqual(drift.state(reports["tagged"]), "inconclusive")
        self.assertEqual(drift.state(reports["healthy"]), "drifted")
        self.assertIn("UNRESOLVABLE", drift.render(list(reports.values())))

    def test_resolution_errors_still_fail_for_pstack_or_unrelated_errors(self) -> None:
        self.add_skill("broken", self.blob("ref/broken.md"), upstream_commit=PIN_R)
        for detail in ("gh: API rate limit exceeded (HTTP 403)", "gh: Server Error (HTTP 500)"):
            def unavailable(args):
                raise subprocess.CalledProcessError(1, args, stderr=detail)
            with self.assertRaises(subprocess.CalledProcessError):
                drift.inspect_skill(drift.discover_skills(self.root, set())[0], drift.Context(unavailable))
        def missing(args):
            raise subprocess.CalledProcessError(1, args, stderr="gh: Not Found (HTTP 404)")
        with self.assertRaises(subprocess.CalledProcessError):
            drift.inspect(LOCK["sources"][0], missing)

    def test_missing_pin_and_unknown_commit_are_unresolvable(self) -> None:
        self.add_skill("nopin", self.blob("ref/nopin.md"))
        self.add_skill("badpin", self.blob("ref/badpin.md"), upstream_commit=PIN_R)
        gh = self.fake(compares={UP: (HEAD_A, identical())}, errors={(UP, PIN_R): "gh: Not Found (HTTP 404)"})
        reports = self.reports(gh)
        self.assertEqual(drift.state(reports["nopin"]), "inconclusive")
        self.assertEqual(drift.state(reports["badpin"]), "inconclusive")

    def test_pstack_covered_repos_are_excluded_from_the_skill_scan(self) -> None:
        self.add_skill("covered", self.blob("pstack/skills/a/SKILL.md", repo="O/Mono"), upstream_commit=PIN_R)
        self.add_skill("setup", "https://github.com/o/open", upstream_commit=PIN_A)
        self.assertEqual(drift.discover_skills(self.root, {"o/mono", "o/open"}), [])
        gh = self.fake()
        self.assertEqual(set(self.reports(gh)), {"open-pstack", "cursor-pstack"})

    def test_pstack_section_precedes_repo_sections(self) -> None:
        self.add_skill("changed", self.blob("skills/changed/SKILL.md"), upstream_commit=PIN_R)
        gh = self.fake(compares={"o/mono": (HEAD_A, ahead("pstack/a.md")), UP: (HEAD_A, ahead("skills/changed/SKILL.md"))})
        reports = drift.collect(self.root, gh)
        body = drift.render(reports)
        self.assertLess(body.index("## Pstack imports"), body.index("## Derived skills"))
        self.assertEqual(drift.drift_set(reports), {"cursor-pstack": "drifted", "u/up:changed": "drifted"})
        self.assertIn(drift.MARKER, body)


class LifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        (self.root / "upstream/pstack").mkdir(parents=True)
        (self.root / "upstream/pstack/lock.json").write_text(json.dumps(LOCK))

    def payloads(self, drifted: bool) -> dict:
        mono = ahead("pstack/a.md") if drifted else identical()
        return {"o/open": (PIN_A, identical()), "o/mono": (HEAD_A if drifted else PIN_B, mono)}

    def body(self, drifted: bool) -> str:
        gh = FakeGh(self.payloads(drifted))
        return drift.render(drift.collect(self.root, gh))

    def run_main(self, gh: FakeGh) -> int:
        return drift.main(["--root", str(self.root), "--repo", "x/y"], run=gh, write=gh)

    def test_create_only_when_no_marker_issue_exists(self) -> None:
        gh = FakeGh(self.payloads(True), [gh_issue(1, "unrelated")])
        self.assertEqual(self.run_main(gh), 0)
        self.assertEqual([call[:2] for call in gh.writes], [["issue", "create"]])

    def test_update_comments_on_a_drift_set_change(self) -> None:
        stale = self.body(True).replace('"cursor-pstack": "drifted"', '"gone": "drifted"')
        gh = FakeGh(self.payloads(True), [gh_issue(7, stale)])
        self.assertEqual(self.run_main(gh), 0)
        self.assertEqual([call[:3] for call in gh.writes],
                         [["issue", "edit", "7"], ["issue", "comment", "7"]])
        comment = gh.writes[1][gh.writes[1].index("--body") + 1]
        self.assertIn("Newly drifted: `cursor-pstack`", comment)
        self.assertIn("Resolved: `gone`", comment)

    def test_body_only_change_edits_without_a_comment(self) -> None:
        old = self.body(True).replace("Ahead by: 3 commits", "Ahead by: 1 commits")
        gh = FakeGh(self.payloads(True), [gh_issue(7, old)])
        self.assertEqual(self.run_main(gh), 0)
        self.assertEqual([call[:3] for call in gh.writes], [["issue", "edit", "7"]])

    def test_unchanged_run_writes_nothing(self) -> None:
        gh = FakeGh(self.payloads(True), [gh_issue(7, self.body(True))])
        self.assertEqual(self.run_main(gh), 0)
        self.assertEqual(gh.writes, [])

    def test_closed_issue_is_reopened_not_duplicated(self) -> None:
        gh = FakeGh(self.payloads(True), [gh_issue(7, drift.MARKER + "\nold", state="closed")])
        self.assertEqual(self.run_main(gh), 0)
        self.assertEqual([call[:3] for call in gh.writes],
                         [["issue", "edit", "7"], ["issue", "reopen", "7"]])
        self.assertIn("Newly drifted: `cursor-pstack`", gh.writes[1][gh.writes[1].index("--comment") + 1])

    def test_clean_closes_open_issue_and_leaves_closed_alone(self) -> None:
        gh = FakeGh(self.payloads(False), [gh_issue(7, self.body(True))])
        self.assertEqual(self.run_main(gh), 0)
        self.assertEqual([call[:3] for call in gh.writes], [["issue", "close", "7"]])
        shut = FakeGh(self.payloads(False), [gh_issue(7, self.body(True), state="closed")])
        self.assertEqual(self.run_main(shut), 0)
        self.assertEqual(shut.writes, [])

    def test_inconclusive_result_never_closes(self) -> None:
        truncated = ahead(*[f"x/f{i}.md" for i in range(drift.COMPARE_FILE_CAP)], count=9)
        payloads = {"o/open": (PIN_A, truncated), "o/mono": (PIN_B, identical())}
        gh = FakeGh(payloads, [gh_issue(7, self.body(False))])
        self.assertEqual(self.run_main(gh), 0)
        self.assertTrue(all(call[:2] != ["issue", "close"] for call in gh.writes))
        self.assertIn("Newly inconclusive: `open-pstack`", gh.writes[-1][gh.writes[-1].index("--body") + 1])

    def test_dry_run_reports_the_plan_without_writing(self) -> None:
        gh = FakeGh(self.payloads(True), [gh_issue(7, drift.MARKER, state="closed")])
        self.assertEqual(drift.main(["--root", str(self.root), "--repo", "x/y", "--dry-run"], run=gh), 0)
        self.assertEqual(gh.writes, [])


if __name__ == "__main__":
    unittest.main()
