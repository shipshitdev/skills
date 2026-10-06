from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "validate.py"
SPEC = importlib.util.spec_from_file_location("stack_validate", SCRIPT)
assert SPEC and SPEC.loader
validate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validate
SPEC.loader.exec_module(validate)


def write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def package(**sections: dict) -> str:
    return json.dumps({"name": "fixture", "private": True, **sections})


GOOD_BIOME = {
    "$schema": "https://biomejs.dev/schemas/2.3.12/schema.json",
    "linter": {
        "enabled": True,
        "rules": {"recommended": True, "correctness": {"useAwaitThenable": "error"}},
        "domains": {"react": "on", "next": "on"},
    },
    "assist": {"actions": {"source": {"organizeImports": "on"}}},
    "formatter": {"enabled": True, "indentStyle": "space"},
}


class FixtureCase(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def run_stack(self, runner) -> "validate.ValidationResult":
        result = validate.ValidationResult()
        runner(self.root, result)
        return result

    def messages(self, result: "validate.ValidationResult", severity: str) -> list[str]:
        return [issue.message for issue in result.issues if issue.severity == severity]


class BiomeTests(FixtureCase):
    def test_current_config_is_clean(self) -> None:
        write(self.root, "package.json", package(devDependencies={"@biomejs/biome": "^2.3.0"}))
        write(self.root, "biome.json", json.dumps(GOOD_BIOME))
        result = self.run_stack(validate.validate_biome)
        self.assertEqual(result.issues, [])
        self.assertEqual(result.meta["schema_version"], "2.3.12")

    def test_jsonc_comments_are_stripped_but_urls_survive(self) -> None:
        write(self.root, "package.json", package(devDependencies={"@biomejs/biome": "^2.3.0"}))
        write(self.root, "biome.jsonc", '{\n  // comment\n  "$schema": "https://biomejs.dev/schemas/2.3.12/schema.json", /* block */\n  "formatter": {"enabled": true}\n}\n')
        result = self.run_stack(validate.validate_biome)
        self.assertEqual(result.meta["schema_version"], "2.3.12")
        self.assertFalse(any("Invalid JSON" in m for m in self.messages(result, "error")))

    def test_legacy_config_is_flagged(self) -> None:
        write(self.root, "package.json", package(devDependencies={"@biomejs/biome": "^1.9.0"}))
        write(self.root, "biome.json", json.dumps({
            "$schema": "https://biomejs.dev/schemas/1.9.0/schema.json",
            "organizeImports": {"enabled": True},
        }))
        write(self.root, ".eslintrc.json", "{}")
        result = self.run_stack(validate.validate_biome)
        errors = self.messages(result, "error")
        self.assertTrue(any("Biome 1.x" in m for m in errors))
        self.assertTrue(any("Schema version 1.9.0" in m for m in errors))
        self.assertTrue(any("organizeImports at root" in m for m in errors))
        self.assertTrue(any("Old config file" in m for m in self.messages(result, "warning")))


class BunTests(FixtureCase):
    def build_workspace(self, lockfile: str, dependency_version: str) -> None:
        write(self.root, "package.json", package(workspaces=["apps/*", "packages/*"], catalog={"react": "^19.0.0"}))
        write(self.root, lockfile, "")
        write(self.root, "packages/ui/package.json", json.dumps({"name": "@org/ui"}))
        write(self.root, "apps/web/package.json", json.dumps({
            "name": "@org/web",
            "dependencies": {"@org/ui": dependency_version, "react": "catalog:"},
        }))

    def run_structure(self) -> "validate.ValidationResult":
        result = validate.ValidationResult()
        pkg = validate.check_bun_root_package(self.root, result)
        self.assertIsNotNone(pkg)
        validate.check_bun_workspace_structure(self.root, validate.find_bun_workspaces(self.root, pkg), result)
        validate.check_bun_single_lockfile(self.root, result)
        return result

    def test_clean_workspace_with_bun_lock_has_no_issues(self) -> None:
        self.build_workspace("bun.lock", "workspace:*")
        result = self.run_structure()
        self.assertEqual(result.issues, [])
        self.assertIn("Single bun.lock at root", result.passed)

    def test_lone_legacy_lockfile_warns_with_migration(self) -> None:
        self.build_workspace("bun.lockb", "workspace:*")
        result = self.run_structure()
        self.assertEqual(self.messages(result, "error"), [])
        warnings = [issue for issue in result.issues if issue.severity == "warning"]
        self.assertEqual(len(warnings), 1)
        self.assertIn("bun.lock is the canonical lockfile", warnings[0].message)
        self.assertIn("--save-text-lockfile", warnings[0].fix)

    def test_missing_lockfile_asks_for_bun_lock(self) -> None:
        self.build_workspace("bun.lock", "workspace:*")
        (self.root / "bun.lock").unlink()
        warnings = self.messages(self.run_structure(), "warning")
        self.assertEqual(warnings, ["No bun.lock at root (run bun install)"])

    def test_hardcoded_local_version_and_stray_lockfile_are_errors(self) -> None:
        self.build_workspace("bun.lock", "1.0.0")
        write(self.root, "apps/web/bun.lock", "")
        errors = self.messages(self.run_structure(), "error")
        self.assertTrue(any("should use workspace: protocol" in m for m in errors))
        self.assertTrue(any("Lockfile found in workspace" in m for m in errors))
        self.assertTrue(any("Extra lockfile" in m for m in errors))

    def test_both_root_lockfiles_are_an_error(self) -> None:
        self.build_workspace("bun.lock", "workspace:*")
        write(self.root, "bun.lockb", "")
        result = self.run_structure()
        self.assertTrue(any("Both bun.lock and bun.lockb" in m for m in self.messages(result, "error")))
        self.assertNotIn("Single lockfile at root", result.passed)

    def test_root_dependencies_and_missing_catalog_warn(self) -> None:
        write(self.root, "package.json", package(workspaces=["apps/*"], dependencies={"react": "^19.0.0"}))
        result = validate.ValidationResult()
        validate.check_bun_root_package(self.root, result)
        warnings = self.messages(result, "warning")
        self.assertTrue(any("has dependencies" in m for m in warnings))
        self.assertTrue(any("No dependency catalog" in m for m in warnings))


class NextjsTests(FixtureCase):
    def test_current_project_has_no_errors(self) -> None:
        write(self.root, "package.json", package(dependencies={"next": "^16.0.0"}))
        write(self.root, "next.config.ts", "export default {};\n")
        write(self.root, "proxy.ts", "export const proxy = 1;\n")
        write(self.root, "app/page.tsx", "'use cache';\nexport default function P() { return null; }\n")
        self.assertEqual(self.run_stack(validate.validate_nextjs).issues, [])

    def test_v15_patterns_are_errors(self) -> None:
        write(self.root, "package.json", package(dependencies={"next": "^15.0.0"}))
        write(self.root, "middleware.ts", "export function middleware() {}\n")
        write(self.root, "pages/index.tsx", "export async function getServerSideProps() { return { props: {} }; }\n")
        errors = self.messages(self.run_stack(validate.validate_nextjs), "error")
        self.assertTrue(any("Next.js 15 detected" in m for m in errors))
        self.assertTrue(any("No app/ directory" in m for m in errors))
        self.assertTrue(any("middleware.ts is deprecated" in m for m in errors))
        self.assertTrue(any("migrate to App Router" in m for m in errors))
        self.assertTrue(any("getServerSideProps" in m for m in errors))


class TailwindTests(FixtureCase):
    def test_v4_css_first_setup_is_clean(self) -> None:
        write(self.root, "package.json", package(dependencies={"tailwindcss": "^4.0.0"}))
        write(self.root, "postcss.config.mjs", "export default { plugins: { '@tailwindcss/postcss': {} } };\n")
        write(self.root, "app/globals.css", '@import "tailwindcss";\n@theme {\n  --color-primary: red;\n}\n')
        self.assertEqual(self.run_stack(validate.validate_tailwind).issues, [])

    def test_v3_patterns_are_flagged(self) -> None:
        write(self.root, "package.json", package(dependencies={"tailwindcss": "^3.4.0"}))
        write(self.root, "tailwind.config.js", "module.exports = {};\n")
        write(self.root, "postcss.config.js", "module.exports = { plugins: { tailwindcss: {}, autoprefixer: {} } };\n")
        write(self.root, "src/index.css", "@tailwind base;\n")
        result = self.run_stack(validate.validate_tailwind)
        errors = self.messages(result, "error")
        self.assertTrue(any("Tailwind v3 detected" in m for m in errors))
        self.assertTrue(any("tailwind.config.js" in m for m in errors))
        self.assertTrue(any("@tailwind directive" in m for m in errors))
        self.assertTrue(any("No @import" in m for m in errors))
        warnings = self.messages(result, "warning")
        self.assertTrue(any("old tailwindcss PostCSS plugin" in m for m in warnings))
        self.assertTrue(any("autoprefixer" in m for m in warnings))


class CliTests(FixtureCase):
    def cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), *args],
            capture_output=True, text=True, check=False,
        )

    def test_detection_selects_stacks_from_the_project(self) -> None:
        write(self.root, "package.json", package(dependencies={"next": "^16.0.0", "tailwindcss": "^4.0.0"}))
        write(self.root, "biome.json", "{}")
        self.assertEqual(validate.detect_stacks(self.root), ["biome", "nextjs", "tailwind"])

    def test_only_current_stacks_are_offered(self) -> None:
        self.assertEqual(set(validate.STACKS), {"biome", "bun", "nextjs", "tailwind"})
        self.assertNotEqual(self.cli("--stack", "legacy-auth").returncode, 0)

    def test_bun_is_detected_from_either_lockfile(self) -> None:
        write(self.root, "bun.lock", "")
        self.assertEqual(validate.detect_stacks(self.root), ["bun"])
        (self.root / "bun.lock").unlink()
        write(self.root, "bun.lockb", "")
        self.assertEqual(validate.detect_stacks(self.root), ["bun"])

    def test_no_detectable_stack_asks_for_one(self) -> None:
        write(self.root, "package.json", package())
        completed = self.cli()
        self.assertEqual(completed.returncode, 1)
        self.assertIn("--stack", completed.stdout)

    def test_ci_exits_nonzero_on_errors_and_plain_run_does_not(self) -> None:
        write(self.root, "package.json", package(dependencies={"tailwindcss": "^3.4.0"}))
        self.assertEqual(self.cli("--stack", "tailwind").returncode, 0)
        self.assertEqual(self.cli("--stack", "tailwind", "--ci").returncode, 1)

    def test_strict_fails_on_warnings(self) -> None:
        write(self.root, "package.json", package(dependencies={"tailwindcss": "^4.0.0"}))
        write(self.root, "app/globals.css", '@import "tailwindcss";\n')
        self.assertEqual(self.cli("--stack", "tailwind", "--ci").returncode, 0)
        self.assertEqual(self.cli("--stack", "tailwind", "--strict").returncode, 1)

    def test_json_shape_single_and_multiple(self) -> None:
        write(self.root, "package.json", package(dependencies={"tailwindcss": "^4.0.0", "next": "^16.0.0"}))
        single = json.loads(self.cli("--stack", "tailwind", "--json").stdout)
        self.assertEqual(single["tailwind_version"], "^4.0.0")
        self.assertIn("issues", single)
        multiple = json.loads(self.cli("--stack", "tailwind", "--stack", "nextjs", "--json").stdout)
        self.assertEqual(set(multiple), {"tailwind", "nextjs"})
        self.assertEqual(multiple["nextjs"]["next_version"], "^16.0.0")


if __name__ == "__main__":
    unittest.main()
