from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "bundles/planning"
HELPER = "skills/executing-plans/scripts/plan-header.mjs"
HEAD = "a" * 40


class PlanningBundleTests(unittest.TestCase):
    def test_documented_helper_path_is_packaged(self) -> None:
        # Instructions name the helper as the `executing-plans` skill's `scripts/plan-header.mjs`.
        documented = [
            path
            for path in BUNDLE.rglob("*.md")
            if "executing-plans" in path.read_text()
            and "scripts/plan-header.mjs" in path.read_text()
            and "executing-plans" not in path.parts
        ]
        self.assertTrue(documented, "planning bundle no longer documents plan-header.mjs")
        for path in documented:
            self.assertTrue(re.search(r"executing-plans`? skill's\s+`scripts/plan-header\.mjs", path.read_text()), path)
        self.assertTrue((BUNDLE / HELPER).is_file(), f"bundles/planning/{HELPER} is not packaged")

    def test_planning_only_install_runs_digest_and_check(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            # Resolve symlinks (macOS /var): plan-header.mjs only runs as a CLI on its real path.
            root = Path(directory).resolve()
            installed = root / "installed"
            shutil.copytree(BUNDLE, installed)  # the planning bundle and nothing else
            helper = installed / HELPER
            issue = "Ship the complete feature.\nKeep the settled scope.\n"
            (root / "issue.md").write_text(issue)

            digest = subprocess.run(
                ["node", str(helper), "digest", str(root / "issue.md")],
                capture_output=True, text=True,
            )
            self.assertEqual(digest.returncode, 0, digest.stderr)
            fingerprint = digest.stdout.strip()
            self.assertEqual(fingerprint, hashlib.sha256(issue.strip().encode()).hexdigest())

            plan = (
                "## Implementation Plan\nPlan revision: 1\n"
                f"Base commit: {HEAD}\nRequirements SHA256: {fingerprint}\nReadiness: READY\n"
                "- [ ] S-1: Implement the settled change\n  - Touch: README.md\n"
                "  - Pattern: D-1\n  - Check: bun run lint\n  - Stop if: the pattern is absent\n"
            )
            (root / "plan.md").write_text(plan)
            check = subprocess.run(
                ["node", str(helper), "check", str(root / "issue.md"), str(root / "plan.md"), HEAD],
                capture_output=True, text=True,
            )
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
            self.assertIn('"ready":true', check.stdout)

            (root / "plan.md").write_text(plan.replace("Readiness: READY", "Readiness: BLOCKED"))
            blocked = subprocess.run(
                ["node", str(helper), "check", str(root / "issue.md"), str(root / "plan.md"), HEAD],
                capture_output=True, text=True,
            )
            self.assertEqual(blocked.returncode, 1, blocked.stdout + blocked.stderr)


if __name__ == "__main__":
    unittest.main()
