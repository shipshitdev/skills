from __future__ import annotations

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

INIT = Path(__file__).resolve().parents[1] / "scripts" / "init-artifact.sh"


def write_stub(bin_dir: Path, name: str, body: str) -> None:
    stub = bin_dir / name
    stub.write_text(f"#!/bin/sh\n{body}\n")
    stub.chmod(stub.stat().st_mode | stat.S_IXUSR)


def snapshot(root: Path) -> dict[str, bytes | None]:
    return {
        str(p.relative_to(root)): (p.read_bytes() if p.is_file() else None)
        for p in sorted(root.rglob("*"))
    }


class InitDestinationGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.log = self.root / "bun-calls.log"
        write_stub(self.bin, "node", "echo v22.12.0")
        # bun -v prints a version; any other call is logged and does nothing,
        # which models create-vite being cancelled without creating the project
        write_stub(
            self.bin,
            "bun",
            f'[ "$1" = "-v" ] && echo 1.4.2 && exit 0\necho "$@" >> "{self.log}"\nexit 0',
        )
        self.env = {**os.environ, "PATH": f"{self.bin}{os.pathsep}{os.environ['PATH']}"}

    def run_init(self, name: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(INIT), name], cwd=self.root, env=self.env, capture_output=True, text=True
        )

    def test_refuses_a_nonempty_destination_and_leaves_it_untouched(self) -> None:
        dest = self.root / "existing"
        (dest / "src").mkdir(parents=True)
        (dest / "index.html").write_text('<link rel="icon" href="/keep.svg"><title>mine</title>')
        (dest / "vite.config.ts").write_text("// my config\n")
        (dest / "src" / "App.tsx").write_text("// my app\n")
        before = snapshot(dest)

        result = self.run_init("existing")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(snapshot(dest), before)
        self.assertFalse(self.log.exists(), "no bun command may run against an existing project")

    def test_refuses_an_existing_file_as_destination(self) -> None:
        (self.root / "taken").write_text("data")
        result = self.run_init("taken")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.root / "taken").read_text(), "data")

    def test_stops_when_create_vite_creates_nothing(self) -> None:
        result = self.run_init("fresh")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "fresh").exists())
        calls = self.log.read_text().splitlines() if self.log.exists() else []
        self.assertTrue(all(call.startswith("create vite") for call in calls), calls)

    def test_allows_an_empty_existing_directory(self) -> None:
        (self.root / "empty").mkdir()
        result = self.run_init("empty")
        # create-vite is stubbed (no package.json appears), so it stops there, after being called
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("create vite", self.log.read_text())


if __name__ == "__main__":
    unittest.main()
