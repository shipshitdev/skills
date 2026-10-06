from __future__ import annotations

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
CHECK = SCRIPTS / "node-version-check.sh"
INIT = SCRIPTS / "init-artifact.sh"


def supported(version: str) -> bool:
    result = subprocess.run(
        ["bash", "-c", f'source "{CHECK}"; node_version_supported "$1"', "_", version],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


class NodeVersionCheckTest(unittest.TestCase):
    def test_rejects_versions_below_the_vite_minimums(self) -> None:
        for version in ("v18.20.0", "v20.0.0", "20.18.9", "v21.7.0", "v22.0.0", "22.11.9"):
            with self.subTest(version=version):
                self.assertFalse(supported(version))

    def test_accepts_the_minimums_and_newer(self) -> None:
        for version in (
            "v20.19.0",
            "20.19.5",
            "v20.20.1",
            "v22.12.0",
            "22.12.1",
            "v22.20.0",
            "v24.0.0",
            "v26.10.0",
        ):
            with self.subTest(version=version):
                self.assertTrue(supported(version))

    def test_rejects_unparsable_input(self) -> None:
        for version in ("", "node", "v22", "v22.12"):
            with self.subTest(version=version):
                self.assertFalse(supported(version))

    def test_init_script_fails_fast_on_an_old_node(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            for name, output in (("node", "v20.0.0"), ("bun", "1.4.2")):
                stub = bin_dir / name
                stub.write_text(f"#!/bin/sh\necho {output}\n")
                stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
            env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"}
            result = subprocess.run(
                ["bash", str(INIT), "demo"], cwd=tmp, env=env, capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("20.19.0+ or 22.12.0+", result.stdout)
            self.assertFalse((Path(tmp) / "demo").exists())


if __name__ == "__main__":
    unittest.main()
