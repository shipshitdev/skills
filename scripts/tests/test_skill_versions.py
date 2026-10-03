from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/sync-skill-versions.js"


class SharedVersionTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / ".tmp"
        scratch.mkdir(exist_ok=True)
        self.directory = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.release("2.2.2")
        self.skill = self.add_skill("example", "1.0.0")

    def release(self, version):
        (self.root / "package.json").write_text(json.dumps({"version": version}))

    def add_skill(self, name, version):
        path = self.root / "skills" / name
        path.mkdir(parents=True)
        (path / "SKILL.md").write_text(
            f'---\nname: {name}\ndescription: Example.\nmetadata:\n'
            f'  version: "{version}"\n  tags: "example"\n'
            'disable-model-invocation: true\n---\nBody version: "1.0.0" stays intact.\n'
        )
        (path / "plugin.json").write_text(json.dumps({"name": name, "version": version}))
        return path

    def run_sync(self, *args):
        return subprocess.run(["bun", str(SCRIPT), "--root", str(self.root), *args],
                              capture_output=True, text=True, check=False)

    def mapping(self, content):
        path = self.root / "upstream/pstack/mapping.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"files": {"source": {"destinations": [{
            "path": "skills/example/SKILL.md",
            "sha256": hashlib.sha256(content).hexdigest(), "executable": False
        }], "review_note": "Accepted behavior"}}}))
        return path

    def test_check_reports_release_drift_without_writing(self):
        before = (self.skill / "SKILL.md").read_bytes()
        result = self.run_sync("--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("repository 2.2.2", result.stderr)
        self.assertEqual((self.skill / "SKILL.md").read_bytes(), before)

    def test_release_changes_sync_both_metadata_fields_and_preserve_body(self):
        self.assertEqual(self.run_sync().returncode, 0)
        self.release("2.3.0")
        self.assertEqual(self.run_sync("--check").returncode, 1)
        self.assertEqual(self.run_sync().returncode, 0)
        body = (self.skill / "SKILL.md").read_text()
        self.assertIn('  version: "2.3.0"', body)
        self.assertIn('Body version: "1.0.0" stays intact.', body)
        self.assertEqual(json.loads((self.skill / "plugin.json").read_text())["version"], "2.3.0")
        self.assertEqual(self.run_sync("--check").returncode, 0)

    def test_invalid_later_skill_prevents_partial_source_updates(self):
        broken = self.add_skill("broken", "1.0.0")
        (broken / "plugin.json").write_text("invalid JSON")
        before = (self.skill / "SKILL.md").read_bytes()
        self.assertEqual(self.run_sync().returncode, 1)
        self.assertEqual((self.skill / "SKILL.md").read_bytes(), before)

    def test_accepted_fingerprints_follow_only_version_edits(self):
        path = self.mapping((self.skill / "SKILL.md").read_bytes())
        self.assertEqual(self.run_sync().returncode, 0)
        record = json.loads(path.read_text())["files"]["source"]
        self.assertEqual(record["destinations"][0]["sha256"],
                         hashlib.sha256((self.skill / "SKILL.md").read_bytes()).hexdigest())
        self.assertEqual(record["review_note"], "Accepted behavior")

    def test_unreviewed_body_changes_are_not_accepted_by_version_sync(self):
        path = self.mapping((self.skill / "SKILL.md").read_bytes())
        accepted = path.read_bytes()
        with (self.skill / "SKILL.md").open("a") as output:
            output.write("Unreviewed new behavior.\n")
        self.assertEqual(self.run_sync().returncode, 0)
        self.assertEqual(path.read_bytes(), accepted)
        self.assertIn('  version: "2.2.2"', (self.skill / "SKILL.md").read_text())

    def test_maintainer_skills_share_release_without_requiring_plugin(self):
        path = self.root / ".agents/skills/maintainer"
        path.mkdir(parents=True)
        text = '---\nname: maintainer\nmetadata:\n  version: "1.0.0"\n---\nBody\n'
        (path / "SKILL.md").write_text(text)
        self.assertEqual(self.run_sync().returncode, 0)
        self.assertEqual((path / "SKILL.md").read_text(), text.replace('"1.0.0"', '"2.2.2"'))
        self.assertEqual(self.run_sync("--check").returncode, 0)

    def test_invalid_mapping_prevents_source_writes(self):
        path = self.root / "upstream/pstack/mapping.json"
        path.parent.mkdir(parents=True)
        path.write_text("invalid JSON")
        before = (self.skill / "SKILL.md").read_bytes()
        self.assertEqual(self.run_sync().returncode, 1)
        self.assertEqual((self.skill / "SKILL.md").read_bytes(), before)

    def test_check_keeps_mapping_bytes_and_plugin_fingerprints_sync(self):
        raw = (self.skill / "plugin.json").read_bytes()
        path = self.mapping((self.skill / "SKILL.md").read_bytes())
        mapping = json.loads(path.read_text())
        mapping["files"]["source"]["destinations"].append({
            "path": "skills/example/plugin.json",
            "sha256": hashlib.sha256(raw).hexdigest(), "executable": False
        })
        path.write_text(json.dumps(mapping))
        before = path.read_bytes()
        self.assertEqual(self.run_sync("--check").returncode, 1)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(self.run_sync().returncode, 0)
        destinations = json.loads(path.read_text())["files"]["source"]["destinations"]
        self.assertEqual(destinations[1]["sha256"],
                         hashlib.sha256((self.skill / "plugin.json").read_bytes()).hexdigest())

    def test_missing_metadata_does_not_modify_sources(self):
        path = self.skill / "SKILL.md"
        path.write_text('---\nname: example\nversion: "1.0.0"\n---\nBody\n')
        before = path.read_bytes()
        self.assertEqual(self.run_sync().returncode, 1)
        self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
