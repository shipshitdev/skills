from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_DIR / "scripts"


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


init_workspace = load("init_workspace", "init-workspace.py")

EXACT_VERSION = re.compile(r"^\d+\.\d+\.\d+$")
# Stack guidance the scaffold must never emit again
BANNED = [
    "clerk",
    "@agenticindiedev",
    ".scss",
    "sass",
    "tailwind.config",
    "middleware.ts",
    "mongo",
    "bun.lockb",
]


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
        cls.root = Path(cls._tmp.name) / "workspace"
        result = run(
            "init-workspace.py",
            "--root", str(cls.root),
            "--name", "Smoke App",
            "--org", "smoke",
            "--entities", "task,project",
            "--allow-outside",
        )
        assert result.returncode == 0, result.stdout + result.stderr

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def text_files(self) -> list[Path]:
        return [
            path
            for path in self.root.rglob("*")
            if path.is_file() and ".agents" not in path.parts
        ]

    def package(self, relative: str) -> dict:
        return json.loads((self.root / relative / "package.json").read_text())

    def test_no_stale_stack_guidance_is_emitted(self) -> None:
        for path in self.text_files():
            content = path.read_text().lower()
            for banned in BANNED:
                self.assertNotIn(banned, content, f"{banned!r} found in {path.relative_to(self.root)}")
        for pattern in ("tailwind.config.*", "*.scss", "middleware.ts", "biome.json"):
            matches = [p for p in self.root.rglob(pattern) if "node_modules" not in p.parts]
            if pattern == "biome.json":
                self.assertEqual([m.relative_to(self.root) for m in matches], [Path("biome.json")])
            else:
                self.assertEqual(matches, [], pattern)

    def test_every_pin_is_exact_and_shared_pins_agree(self) -> None:
        packages = {
            name: self.package(name)
            for name in ("api", "frontend/apps/dashboard", "frontend/packages", "mobile")
        }
        packages["root"] = json.loads((self.root / "package.json").read_text())
        seen: dict[str, set[str]] = {}
        for name, pkg in packages.items():
            for section in ("dependencies", "devDependencies", "peerDependencies"):
                for dep, version in pkg.get(section, {}).items():
                    self.assertRegex(version, EXACT_VERSION, f"{name}: {dep}")
                    seen.setdefault(dep, set()).add(version)
        # React is intentionally pinned differently for the Expo app only
        mobile_only = {"react", "@types/react"}
        for dep, versions in seen.items():
            if dep not in mobile_only:
                self.assertEqual(len(versions), 1, f"{dep} pinned to {versions}")

    def test_prisma_config_tolerates_a_missing_database_url(self) -> None:
        config = (self.root / "api" / "prisma.config.ts").read_text()
        self.assertIn("datasource: { url: process.env.DATABASE_URL }", config)
        self.assertNotIn("url: env(", config)
        self.assertNotIn("import { defineConfig, env }", config)
        # The generated Dockerfile builds without any .env
        dockerfile = (self.root / "api" / "Dockerfile").read_text()
        self.assertIn('--filter "@smoke/api"', dockerfile)
        self.assertNotIn("DATABASE_URL", dockerfile.replace("prisma generate needs no DATABASE_URL", ""))

    def test_frontend_is_tailwind_v4_css_first_with_proxy(self) -> None:
        dashboard = self.root / "frontend" / "apps" / "dashboard"
        css = (dashboard / "app" / "globals.css").read_text()
        self.assertTrue(css.startswith('@import "tailwindcss";'))
        self.assertIn("@theme inline", css)
        self.assertEqual(
            (dashboard / "postcss.config.mjs").read_text().count("@tailwindcss/postcss"), 1
        )
        self.assertTrue((dashboard / "proxy.ts").exists())
        deps = self.package("frontend/apps/dashboard")
        self.assertNotIn("sass", deps["devDependencies"])
        self.assertIn("better-auth", deps["dependencies"])

    def test_api_vitest_config_emits_decorator_metadata(self) -> None:
        config = (self.root / "api" / "vitest.config.mts").read_text()
        self.assertIn('import swc from "unplugin-swc"', config)
        self.assertIn("swc.vite(", config)

    def test_generated_json_is_valid_and_ends_with_newline(self) -> None:
        for path in self.text_files():
            if path.suffix == ".json":
                json.loads(path.read_text())
                self.assertTrue(path.read_text().endswith("\n"), path.name)

    def test_entities_get_guarded_controllers_and_specs(self) -> None:
        collections = self.root / "api" / "apps" / "api" / "src" / "collections" / "tasks"
        controller = (collections / "tasks.controller.ts").read_text()
        self.assertIn("@UseGuards(AuthGuard)", controller)
        for name in ("tasks.controller.spec.ts", "tasks.service.spec.ts"):
            self.assertTrue((collections / name).exists(), name)
        schema = (self.root / "api" / "prisma" / "schema" / "task.prisma").read_text()
        self.assertIn("model Task", schema)
        self.assertTrue((self.root / "api" / "prisma" / "schema" / "auth.prisma").exists())

    def test_reserved_entity_names_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run(
                "init-workspace.py",
                "--root", str(Path(tmp) / "ws"),
                "--name", "Clash",
                "--entities", "user",
                "--allow-outside",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Better Auth", result.stdout)

    def test_dump_json_matches_biome_formatting(self) -> None:
        self.assertEqual(
            init_workspace.dump_json({"a": ["x", "y"], "b": {"c": 1}, "d": []}),
            '{\n  "a": ["x", "y"],\n  "b": {\n    "c": 1\n  },\n  "d": []\n}',
        )
        long_list = [f"item-number-{i}" for i in range(10)]
        rendered = init_workspace.dump_json({"list": long_list})
        self.assertTrue(rendered.startswith('{\n  "list": [\n    "item-number-0",'))


class AddScriptsTest(unittest.TestCase):
    def test_add_frontend_app_creates_a_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "workspace"
            result = run(
                "init-workspace.py", "--root", str(root), "--name", "Demo", "--org", "demo",
                "--allow-outside",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            frontend = root / "frontend"
            added = run("add-frontend-app.py", "--root", str(frontend), "--name", "admin")
            self.assertEqual(added.returncode, 0, added.stdout + added.stderr)
            app = frontend / "apps" / "admin"
            package = json.loads((app / "package.json").read_text())
            self.assertEqual(package["name"], "@demo/admin")
            for relative in (
                "next.config.ts", "postcss.config.mjs", "tsconfig.json", "vitest.config.mts",
                "app/layout.tsx", "app/page.tsx", "app/page.spec.tsx", "app/globals.css",
            ):
                self.assertTrue((app / relative).exists(), relative)
            self.assertIn('import "./globals.css"', (app / "app" / "layout.tsx").read_text())

    def test_add_api_collection_writes_prisma_model_and_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            api = Path(tmp) / "api"
            (api / "apps" / "api" / "src" / "collections").mkdir(parents=True)
            result = run("add-api-collection.py", "--root", str(api), "--name", "comments")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((api / "prisma" / "schema" / "comments.prisma").exists())
            service = api / "apps/api/src/collections/comments/services/comments.service.ts"
            self.assertIn("../../../generated/prisma/client", service.read_text())


if __name__ == "__main__":
    unittest.main()
