from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_DIR / "scripts"
EXACT_VERSION = re.compile(r"^\d+\.\d+\.\d+$")
DEAD_PACKAGE = "@agenticindiedev"


def run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True,
        text=True,
    )


class ScaffoldTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls._tmp.name)
        result = run(
            "scaffold.py",
            "--root", str(cls.root),
            "--slug", "demo",
            "--name", "Demo App",
            "--domain", "demo.example",
            "--concept", "AI-powered analytics",
            "--allow-outside",
        )
        assert result.returncode == 0, result.stderr
        cls.app = cls.root / "demo"

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def test_no_dead_ui_package_anywhere(self) -> None:
        for path in self.app.rglob("*"):
            if path.is_file():
                self.assertNotIn(DEAD_PACKAGE, path.read_text(), str(path))

    def test_dependencies_are_exact_live_pins(self) -> None:
        package = json.loads((self.app / "package.json").read_text())
        for section in ("dependencies", "devDependencies"):
            for name, version in package[section].items():
                self.assertRegex(version, EXACT_VERSION, name)
        for name in (
            "shadcn",
            "radix-ui",
            "class-variance-authority",
            "cn",
            "lucide-react",
            "tw-animate-css",
        ):
            self.assertIn(name, package["dependencies"])

    def test_shadcn_conventions(self) -> None:
        components = json.loads((self.app / "components.json").read_text())
        self.assertEqual(components["tailwind"]["config"], "")
        self.assertTrue(components["tailwind"]["cssVariables"])
        self.assertEqual(components["aliases"]["ui"], "@/components/ui")
        self.assertFalse(list(self.app.glob("tailwind.config.*")))
        self.assertTrue((self.app / "lib" / "utils.ts").is_file())
        css = (self.app / "app" / "globals.css").read_text()
        self.assertIn("@theme inline", css)
        self.assertIn('@import "tailwindcss";', css)
        self.assertIn(":root {", css)
        self.assertIn(".dark {", css)

    def test_every_section_type_has_a_component(self) -> None:
        config = json.loads((self.app / "app.json").read_text())
        page = (self.app / "app" / "page.tsx").read_text()
        for section in config["sections"]:
            self.assertRegex(page, rf"\b{section['type']}:\s")
        for name in (
            "header",
            "hero",
            "stats",
            "features",
            "pricing",
            "testimonials",
            "faq",
            "cta",
            "footer",
        ):
            path = self.app / "components" / "sections" / f"{name}.tsx"
            self.assertTrue(path.is_file(), name)

    def test_refuses_existing_directory(self) -> None:
        result = run(
            "scaffold.py",
            "--root", str(self.root),
            "--slug", "demo",
            "--name", "Demo App",
            "--allow-outside",
        )
        self.assertNotEqual(result.returncode, 0)

    def test_ui_package_flag_is_gone(self) -> None:
        result = run(
            "scaffold.py", "--slug", "x", "--name", "X", "--ui-package", "whatever"
        )
        self.assertNotEqual(result.returncode, 0)


class BatchCreateTest(unittest.TestCase):
    def test_batch_scaffolds_each_site_without_ui_package(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            projects = root / "projects.json"
            projects.write_text(
                json.dumps(
                    [
                        {"slug": "one", "name": "One", "domain": "one.example", "concept": "alpha"},
                        {"slug": "two", "name": "Two", "domain": "two.example", "concept": "beta"},
                    ]
                )
            )
            result = run(
                "batch_create.py",
                "--root", str(root / "sites"),
                "--json", str(projects),
                "--allow-outside",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            for slug in ("one", "two"):
                app = root / "sites" / slug
                self.assertTrue((app / "components.json").is_file())
                self.assertTrue((app / "components" / "ui" / "button.tsx").is_file())
                package = json.loads((app / "package.json").read_text())
                self.assertEqual(package["name"], slug)


if __name__ == "__main__":
    unittest.main()
