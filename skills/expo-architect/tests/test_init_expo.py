from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "init-expo.py"


def scaffold(directory: Path, *args: str) -> Path:
    root = directory / "app"
    subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), "--name", "My App", "--allow-outside", *args],
        check=True,
        capture_output=True,
        text=True,
        cwd=directory,
    )
    return root


def tree_text(root: Path) -> str:
    return "\n".join(
        path.read_text() for path in root.rglob("*") if path.is_file() and ".git" not in path.parts
    )


class InitExpoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.base = Path(self.directory.name)

    def test_auth_scaffold_uses_better_auth_on_sdk_57(self) -> None:
        root = scaffold(self.base, "--auth")
        package = json.loads((root / "package.json").read_text())
        deps = package["dependencies"]
        self.assertTrue(deps["expo"].startswith("57."))
        for name in ("better-auth", "@better-auth/expo", "expo-secure-store", "expo-network", "expo-web-browser"):
            self.assertIn(name, deps)
        self.assertNotIn("clerk", tree_text(root).lower())
        client = (root / "lib" / "auth-client.ts").read_text()
        self.assertIn("expoClient", client)
        self.assertIn('scheme: "my-app"', client)
        self.assertTrue((root / "app" / "(auth)" / "sign-in.tsx").exists())
        self.assertFalse((root / "providers").exists())

    def test_plain_scaffold_has_no_auth_dependencies(self) -> None:
        root = scaffold(self.base)
        deps = json.loads((root / "package.json").read_text())["dependencies"]
        self.assertNotIn("better-auth", deps)
        self.assertFalse((root / "lib" / "auth-client.ts").exists())
        self.assertNotIn("authClient", (root / "lib" / "api.ts").read_text())

    def test_pins_are_exact_and_config_is_current(self) -> None:
        root = scaffold(self.base, "--auth")
        package = json.loads((root / "package.json").read_text())
        for section in ("dependencies", "devDependencies"):
            for name, version in package[section].items():
                self.assertFalse(version[0] in "~^", f"{name} is not pinned exactly: {version}")
        tsconfig = json.loads((root / "tsconfig.json").read_text())
        self.assertNotIn("baseUrl", tsconfig["compilerOptions"])
        biome = json.loads((root / "biome.json").read_text())
        self.assertIn("includes", biome["files"])
        self.assertNotIn("ignore", biome["files"])


if __name__ == "__main__":
    unittest.main()
