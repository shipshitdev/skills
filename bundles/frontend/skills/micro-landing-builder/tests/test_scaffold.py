from __future__ import annotations

import json
import re
import shutil
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


class SlugConfinementTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name).resolve()
        self.root = self.base / "root"
        self.root.mkdir()
        self.outside = self.base / "outside"
        self.outside.mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def scaffold(self, slug: str, root: Path | None = None) -> subprocess.CompletedProcess:
        return run(
            "scaffold.py",
            "--root", str(root or self.root),
            f"--slug={slug}",
            "--name", "X",
            "--allow-outside",
        )

    def assertNothingOutside(self) -> None:
        self.assertEqual(list(self.outside.iterdir()), [])
        self.assertEqual(list(self.root.iterdir()), [])

    def test_absolute_slug_is_rejected(self) -> None:
        target = self.outside / "abs"
        result = self.scaffold(str(target))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(target.exists())
        self.assertNothingOutside()

    def test_parent_traversal_slug_is_rejected(self) -> None:
        result = self.scaffold("../outside/x")
        self.assertNotEqual(result.returncode, 0)
        self.assertNothingOutside()
        result = self.scaffold("../x")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.base / "x").exists())

    def test_nested_and_unsafe_slugs_are_rejected(self) -> None:
        for slug in ("a/b", "A", "a b", ".hidden", "-lead", ".."):
            result = self.scaffold(slug)
            self.assertNotEqual(result.returncode, 0, slug)
        self.assertNothingOutside()

    def test_symlinked_destination_cannot_escape_root(self) -> None:
        (self.root / "link").symlink_to(self.outside / "target")
        result = self.scaffold("link")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(self.outside.iterdir()), [])

    def test_symlinked_root_outside_cwd_needs_allow_outside(self) -> None:
        cwd = self.base / "cwd"
        cwd.mkdir()
        (cwd / "sites").symlink_to(self.outside)
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "scaffold.py"), "--root", "sites", "--slug", "ok", "--name", "X"],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(self.outside.iterdir()), [])

    def test_invalid_theme_color_is_rejected_at_scaffold_time(self) -> None:
        for flag in ("--primary", "--accent", "--background"):
            result = run(
                "scaffold.py", "--root", str(self.root), "--slug", "c", "--name", "X",
                "--allow-outside", flag, "rgb(0, 255, 0)",
            )
            self.assertNotEqual(result.returncode, 0, flag)
            self.assertIn("color", result.stdout + result.stderr)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_injection_strings_are_rejected_at_scaffold_time(self) -> None:
        for payload in ("#fff;outline:10px solid red", "#fff\n", "#fff} body{display:none"):
            for flag in ("--primary", "--accent", "--background"):
                result = run(
                    "scaffold.py", "--root", str(self.root), "--slug", "inj", "--name", "X",
                    "--allow-outside", f"{flag}={payload}",
                )
                self.assertNotEqual(result.returncode, 0, f"{flag} {payload!r}")
        self.assertEqual(list(self.root.iterdir()), [])

    def test_batch_validates_theme_colors_per_project(self) -> None:
        projects = self.base / "themed.json"
        projects.write_text(
            json.dumps(
                [
                    {"slug": "bad", "name": "A", "primary": "#fff;outline:10px solid red"},
                    {"slug": "good", "name": "B", "primary": "#00ff00", "background": "#f4f4f5"},
                ]
            )
        )
        result = run(
            "batch_create.py", "--root", str(self.root), "--json", str(projects), "--allow-outside",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "bad").exists())
        theme = json.loads((self.root / "good" / "app.json").read_text())["theme"]
        self.assertEqual(theme["primary"], "#00ff00")
        self.assertEqual(theme["background"], "#f4f4f5")

    def test_theme_color_flags_are_written_to_app_json(self) -> None:
        result = run(
            "scaffold.py", "--root", str(self.root), "--slug", "c", "--name", "X",
            "--allow-outside", "--primary", "#00ff00", "--background", "#f4f4f5",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        theme = json.loads((self.root / "c" / "app.json").read_text())["theme"]
        self.assertEqual(theme["primary"], "#00ff00")
        self.assertEqual(theme["background"], "#f4f4f5")
        self.assertNotIn("mode", theme)
        self.assertNotIn("foreground", theme)

    def test_valid_slug_still_scaffolds(self) -> None:
        result = self.scaffold("my-site-2")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / "my-site-2" / "package.json").is_file())

    def test_batch_rejects_unsafe_slugs_and_exits_nonzero(self) -> None:
        projects = self.base / "projects.json"
        projects.write_text(
            json.dumps(
                [
                    {"slug": "../outside/x", "name": "A"},
                    {"slug": str(self.outside / "abs"), "name": "B"},
                    {"slug": "fine", "name": "C"},
                ]
            )
        )
        result = run(
            "batch_create.py",
            "--root", str(self.root),
            "--json", str(projects),
            "--allow-outside",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(self.outside.iterdir()), [])
        self.assertTrue((self.root / "fine" / "package.json").is_file())


class ThemeModeTest(unittest.TestCase):
    def build(self, *extra: str) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            result = run(
                "scaffold.py",
                "--root", directory,
                "--slug", "t",
                "--name", "T",
                "--allow-outside",
                *extra,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            app = Path(directory) / "t"
            return {
                "config": json.loads((app / "app.json").read_text()),
                "layout": (app / "app" / "layout.tsx").read_text(),
                "theme": (app / "lib" / "theme.ts").read_text(),
                "capture": (app / "components" / "sections" / "email-capture.tsx").read_text(),
            }

    @staticmethod
    def luminance(color: str) -> float:
        color = color.lstrip("#")
        if len(color) == 3:
            color = "".join(ch * 2 for ch in color)
        r, g, b = (int(color[i : i + 2], 16) / 255 for i in (0, 2, 4))
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def test_default_is_dark_and_unchanged(self) -> None:
        built = self.build()
        theme = built["config"]["theme"]
        self.assertEqual(theme["mode"], "dark")
        self.assertEqual(theme["background"], "#0a0a0a")
        self.assertGreater(self.luminance(theme["foreground"]), 0.5)
        self.assertIn('mode === "dark" ? "dark" : undefined', built["layout"])

    def test_light_mode_pairs_a_dark_foreground_with_a_light_background(self) -> None:
        theme = self.build("--theme-mode", "light")["config"]["theme"]
        self.assertEqual(theme["mode"], "light")
        self.assertGreater(self.luminance(theme["background"]), 0.5)
        self.assertLess(self.luminance(theme["foreground"]), 0.5)

    def test_theme_module_applies_paired_foreground_tokens(self) -> None:
        theme = self.build()["theme"]
        for token in ("--foreground", "--muted-foreground", "--card", "--card-foreground"):
            self.assertIn(f'"{token}"', theme)
        layout = self.build()["layout"]
        self.assertNotIn('className="dark"', layout)

    def test_email_capture_uses_unique_ids(self) -> None:
        capture = self.build()["capture"]
        self.assertIn("useId()", capture)
        self.assertNotIn('id="email"', capture)
        self.assertNotIn('htmlFor="email"', capture)


@unittest.skipUnless(shutil.which("bun"), "bun is required to evaluate lib/theme.ts")
class ThemeResolutionTest(unittest.TestCase):
    """Runs the generated app's lib/theme.ts (the logic layout.tsx applies) under bun."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        result = run(
            "scaffold.py",
            "--root", cls._tmp.name,
            "--slug", "t",
            "--name", "T",
            "--allow-outside",
        )
        assert result.returncode == 0, result.stderr
        cls.app = Path(cls._tmp.name) / "t"
        cls.default_theme = json.loads((cls.app / "app.json").read_text())["theme"]
        result = run(
            "scaffold.py",
            "--root", cls._tmp.name,
            "--slug", "l",
            "--name", "L",
            "--theme-mode", "light",
            "--allow-outside",
        )
        assert result.returncode == 0, result.stderr
        cls.light_theme = json.loads((Path(cls._tmp.name) / "l" / "app.json").read_text())["theme"]

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def resolve_raw(self, **theme: str) -> subprocess.CompletedProcess:
        base = {"primary": "#6366f1", "accent": "#f59e0b", "background": "#0a0a0a"}
        script = self.app / "probe.ts"
        script.write_text(
            'import { resolveTheme } from "./lib/theme"\n'
            f"console.log(JSON.stringify(resolveTheme({json.dumps({**base, **theme})})))\n"
        )
        return subprocess.run(
            ["bun", str(script)], capture_output=True, text=True, cwd=self.app
        )

    def resolve(self, **theme: str) -> dict:
        result = self.resolve_raw(**theme)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    @staticmethod
    def channel(value: int) -> float:
        c = value / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    @classmethod
    def wcag_luminance(cls, color: str) -> float:
        hex_ = color.lstrip("#")
        if len(hex_) in (3, 4):
            hex_ = "".join(ch * 2 for ch in hex_)
        r, g, b = (int(hex_[i : i + 2], 16) for i in (0, 2, 4))
        return 0.2126 * cls.channel(r) + 0.7152 * cls.channel(g) + 0.0722 * cls.channel(b)

    @classmethod
    def ratio(cls, a: str, b: str) -> float:
        hi, lo = sorted((cls.wcag_luminance(a), cls.wcag_luminance(b)), reverse=True)
        return (hi + 0.05) / (lo + 0.05)

    @staticmethod
    def _to_linear(value: float) -> float:
        return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

    @staticmethod
    def _from_linear(value: float) -> float:
        value = min(max(value, 0.0), 1.0)
        return value * 12.92 if value <= 0.0031308 else 1.055 * value ** (1 / 2.4) - 0.055

    @classmethod
    def _oklab(cls, color: str) -> tuple[float, float, float]:
        hex_ = color.lstrip("#")
        if len(hex_) in (3, 4):
            hex_ = "".join(ch * 2 for ch in hex_)
        r, g, b = (cls._to_linear(int(hex_[i : i + 2], 16) / 255) for i in (0, 2, 4))
        l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
        m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
        s_ = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
        return (
            0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s_,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s_,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s_,
        )

    @classmethod
    def mix(cls, first: str, first_pct: float, second: str) -> str:
        """CSS color-mix(in oklab, first pct%, second) back to an sRGB hex."""
        a, b = cls._oklab(first), cls._oklab(second)
        lab = [x * first_pct / 100 + y * (100 - first_pct) / 100 for x, y in zip(a, b)]
        l = (lab[0] + 0.3963377774 * lab[1] + 0.2158037573 * lab[2]) ** 3
        m = (lab[0] - 0.1055613458 * lab[1] - 0.0638541728 * lab[2]) ** 3
        s_ = (lab[0] - 0.0894841775 * lab[1] - 1.2914855480 * lab[2]) ** 3
        rgb = (
            4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s_,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s_,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s_,
        )
        return "#" + "".join(f"{round(cls._from_linear(c) * 255):02x}" for c in rgb)

    def test_every_default_color_pair_meets_wcag_aa(self) -> None:
        for label, theme in (("dark", self.default_theme), ("light", self.light_theme)):
            vars_ = self.resolve(**{k: v for k, v in theme.items() if k != "font"})["vars"]
            background = vars_["--background"]
            foreground = vars_["--foreground"]
            card = self.mix(background, 94, foreground)
            muted = self.mix(foreground, 70, background)
            pairs = {
                "primary / primary-foreground": (vars_["--primary"], vars_["--primary-foreground"]),
                "brand / brand-foreground": (vars_["--brand"], vars_["--brand-foreground"]),
                "background / foreground": (background, foreground),
                "card / card-foreground": (card, vars_["--card-foreground"]),
                "background / muted-foreground": (background, muted),
                "card / muted-foreground": (card, muted),
                "background / brand (text-brand icons and badges)": (background, vars_["--brand"]),
            }
            for name, (first, second) in pairs.items():
                self.assertGreaterEqual(
                    self.ratio(first, second), 4.5, f"{label}: {name} {first} on {second}"
                )
            # text-primary is only used for large stat figures and ring-primary for UI edges (3:1).
            self.assertGreaterEqual(self.ratio(background, vars_["--primary"]), 3.0, label)

    def test_default_primary_gets_a_foreground_that_passes_aa(self) -> None:
        vars_ = self.resolve(**{k: v for k, v in self.default_theme.items() if k != "font"})["vars"]
        self.assertGreaterEqual(self.ratio(vars_["--primary"], vars_["--primary-foreground"]), 4.5)

    def test_runtime_fallback_accent_passes_on_a_light_background(self) -> None:
        resolved = self.resolve(background="#ffffff", accent="not-a-color")
        self.assertGreaterEqual(self.ratio("#ffffff", resolved["vars"]["--brand"]), 4.5)

    def test_saturated_green_primary_gets_dark_text_with_aa_contrast(self) -> None:
        vars_ = self.resolve(primary="#00ff00")["vars"]
        self.assertGreaterEqual(self.ratio("#00ff00", vars_["--primary-foreground"]), 4.5)

    def test_opaque_eight_digit_white_is_light(self) -> None:
        resolved = self.resolve(background="#ffffffff")
        self.assertEqual(resolved["mode"], "light")
        self.assertGreaterEqual(self.ratio("#ffffff", resolved["vars"]["--foreground"]), 7)

    def test_short_and_alpha_forms_are_parsed(self) -> None:
        self.assertEqual(self.resolve(background="#fff")["mode"], "light")
        self.assertEqual(self.resolve(background="#fffe")["mode"], "light")
        self.assertEqual(self.resolve(background="#000f")["mode"], "dark")

    def test_mid_greys_pick_the_higher_contrast_foreground(self) -> None:
        near_black, near_white = "#0a0a0a", "#fafafa"
        for level in range(0x40, 0xC0, 0x10):
            grey = f"#{level:02x}{level:02x}{level:02x}"
            vars_ = self.resolve(primary=grey, background=grey)["vars"]
            best = max((near_black, near_white), key=lambda fg: self.ratio(grey, fg))
            for token in ("--primary-foreground", "--foreground"):
                self.assertEqual(vars_[token], best, f"{token} on {grey}")

    def test_accent_gets_a_paired_foreground(self) -> None:
        vars_ = self.resolve(accent="#facc15")["vars"]
        self.assertGreaterEqual(self.ratio("#facc15", vars_["--brand-foreground"]), 4.5)

    def test_mode_inference_matches_foreground_choice(self) -> None:
        for background in ("#767676", "#777777", "#808080", "#595959"):
            resolved = self.resolve(background=background)
            light = resolved["mode"] == "light"
            best_is_dark = (
                self.ratio(background, "#0a0a0a") >= self.ratio(background, "#fafafa")
            )
            self.assertEqual(light, best_is_dark, background)

    def test_invalid_colors_fall_back_to_defaults_with_a_warning(self) -> None:
        for bad in ("red", "rgb(0, 255, 0)", "#12", "#12345", "#ggg", "oklch(0.7 0.2 140)", ""):
            result = self.resolve_raw(primary=bad, accent=bad, background=bad)
            self.assertEqual(result.returncode, 0, bad)
            resolved = json.loads(result.stdout)
            self.assertEqual(resolved["vars"]["--primary"], self.default_theme["primary"], bad)
            self.assertEqual(resolved["vars"]["--brand"], self.default_theme["accent"], bad)
            self.assertEqual(resolved["vars"]["--background"], self.default_theme["background"], bad)
            self.assertEqual(resolved["mode"], "dark", bad)
            self.assertIn("unsupported color", result.stderr, bad)

    def test_invalid_foreground_is_ignored_and_rederived(self) -> None:
        result = self.resolve_raw(background="#ffffff", foreground="black")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["vars"]["--foreground"], "#0a0a0a")

    def test_css_injection_never_reaches_the_style_output(self) -> None:
        payloads = (
            "#fff;outline:10px solid red",
            "#fff\n",
            "#fff} body{display:none",
            "#ffffff;background:url(//evil.example/x)",
            "red;position:fixed",
        )
        for payload in payloads:
            for key in ("primary", "accent", "background", "foreground"):
                result = self.resolve_raw(**{key: payload})
                self.assertEqual(result.returncode, 0, result.stderr)
                for name, value in json.loads(result.stdout)["vars"].items():
                    for fragment in ("outline", "evil", "display", "position", ";", "}", "\n"):
                        self.assertNotIn(fragment, value, f"{key}={payload!r} -> {name}")

    def test_four_digit_white_is_light(self) -> None:
        self.assertEqual(self.resolve(background="#ffff")["mode"], "light")

    def test_translucent_color_warns_but_resolves(self) -> None:
        result = self.resolve_raw(primary="#00ff0080")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("alpha", result.stderr)

    def test_light_background_without_mode_infers_light_tokens(self) -> None:
        resolved = self.resolve(background="#f4f4f5")
        self.assertEqual(resolved["mode"], "light")
        self.assertEqual(resolved["vars"]["--foreground"], "#0a0a0a")

    def test_dark_background_without_mode_stays_dark(self) -> None:
        self.assertEqual(self.resolve()["mode"], "dark")
        self.assertEqual(self.resolve(background="#111827")["mode"], "dark")

    def test_explicit_mode_wins_over_background(self) -> None:
        self.assertEqual(self.resolve(background="#f4f4f5", mode="dark")["mode"], "dark")
        self.assertEqual(self.resolve(background="#0a0a0a", mode="light")["mode"], "light")

    def test_unknown_mode_falls_back_to_background(self) -> None:
        self.assertEqual(self.resolve(background="#ffffff", mode="sepia")["mode"], "light")

    def test_explicit_foreground_is_kept(self) -> None:
        resolved = self.resolve(background="#f4f4f5", foreground="#222222")
        self.assertEqual(resolved["vars"]["--foreground"], "#222222")

    def test_layout_uses_resolved_mode_for_the_dark_class(self) -> None:
        layout = (self.app / "app" / "layout.tsx").read_text()
        self.assertIn("resolveTheme", layout)
        self.assertIn('mode === "dark" ? "dark" : undefined', layout)


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
