"""Exercise emitted colors, complete fallback and creation failure boundaries."""
import json
import random
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import test_scaffold
from test_scaffold import SKILL_DIR, run


@unittest.skipUnless(shutil.which("bun"), "bun is required for theme validation")
class WholeThemeTest(unittest.TestCase):
    def resolve_many(self, themes):
        module = SKILL_DIR / "assets/templates/landing/lib/theme.ts"
        with tempfile.TemporaryDirectory() as directory:
            probe = Path(directory) / "probe.ts"
            probe.write_text(
                f'import {{ resolveTheme }} from {json.dumps(str(module))}\n'
                'process.stdout.write(JSON.stringify(JSON.parse(await Bun.stdin.text()).map(resolveTheme)))\n'
            )
            result = subprocess.run(["bun", str(probe)], input=json.dumps(themes), capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)

    def assert_pairs(self, resolved):
        v = resolved["vars"]
        surfaces = ["background", "card", "muted", "secondary", "secondary-hover", "accent"]
        for surface in surfaces:
            for text in ["foreground", "muted-foreground", "primary-text", "brand-text", "destructive"]:
                self.assertGreaterEqual(test_scaffold.ThemeResolutionTest.ratio(v[f"--{surface}"], v[f"--{text}"]), 4.5,
                                        f"{text} on {surface}: {v}")
            for edge in ["ring", "input", "brand-text", "destructive"]:
                self.assertGreaterEqual(test_scaffold.ThemeResolutionTest.ratio(v[f"--{surface}"], v[f"--{edge}"]), 3)
        for fill in ["primary", "primary-hover", "brand", "destructive-fill", "destructive-hover"]:
            self.assertGreaterEqual(test_scaffold.ThemeResolutionTest.ratio(v[f"--{fill}"], v[f"--{fill}-foreground"]), 4.5)
        for value in v.values():
            self.assertRegex(value, r"^#[0-9a-f]{6}$")

    def test_known_impossible_themes_fall_back_as_a_whole(self):
        default, *results = self.resolve_many([
            {},
            {"primary": "#777777", "accent": "#777777", "background": "#777777"},
            {"primary": "#808080", "background": "#808080", "foreground": "#808080"},
            {"background": "#888888", "foreground": "#777777"},
            None,
            [],
        ])
        for result in results:
            self.assertEqual(result, default)

    def test_rounded_hex_and_transparent_tokens_are_safe(self):
        for resolved in self.resolve_many([
            {"primary": "#c300b7", "accent": "#7de6aa", "background": "#556601"},
            {"primary": "#00000000", "accent": "#fffe", "background": "#ffff"},
            {"background": "#f4f4f5", "mode": "dark"},
            {"background": "#0a0a0a", "mode": "light"},
        ]):
            self.assert_pairs(resolved)

    def test_five_thousand_random_themes_emit_only_valid_pairs(self):
        rng = random.Random(261)
        themes = [{key: f"#{rng.randrange(1 << 24):06x}" for key in ("primary", "accent", "background")}
                  for _ in range(5000)]
        for result in self.resolve_many(themes):
            self.assert_pairs(result)

    def test_scaffold_rejects_a_theme_before_creating_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run("scaffold.py", "--root", directory, "--slug", "bad", "--name", "Bad",
                         "--background", "#777777", "--allow-outside")
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((Path(directory) / "bad").exists())
            self.assertIn("contrast", result.stdout + result.stderr)

    def test_csv_surplus_cells_fail_before_any_project_is_created(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv = root / "projects.csv"
            csv.write_text("slug,name\ngood,Good\nbad,Bad,extra\n")
            result = run("batch_create.py", "--root", str(root / "apps"), "--csv", str(csv), "--allow-outside")
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / "apps/good").exists())

    def test_failed_clone_is_removed_and_other_projects_continue(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            template = root / "template"
            template.mkdir()
            (template / "app.json").write_text(json.dumps({"theme": {"background": "#777777"}, "meta": {}}))
            projects = root / "projects.json"
            projects.write_text(json.dumps([
                {"slug": "bad", "name": "Bad"},
                {"slug": "good", "name": "Good", "background": "#ffffff"},
            ]))
            result = run("batch_create.py", "--root", str(root / "apps"), "--json", str(projects),
                         "--template", str(template), "--allow-outside")
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / "apps/bad").exists())
            self.assertTrue((root / "apps/good/app.json").exists())
