from __future__ import annotations

import base64
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

BUNDLE = Path(__file__).resolve().parents[1] / "scripts" / "bundle-artifact.sh"

# 1x1 transparent PNG
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)

INDEX_HTML = """<!doctype html>
<html>
  <head><meta charset="UTF-8" /><title>fixture</title>{head}</head>
  <body>{body}<div id="root"></div><script type="module" src="/main.js"></script></body>
</html>
"""


def run(*cmd: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


@unittest.skipUnless(shutil.which("bun") and shutil.which("node"), "bun and node are required")
class BundleArtifactTest(unittest.TestCase):
    template: Path
    template_tmp: tempfile.TemporaryDirectory

    @classmethod
    def setUpClass(cls) -> None:
        cls.template_tmp = tempfile.TemporaryDirectory()
        cls.template = Path(cls.template_tmp.name) / "template"
        cls.template.mkdir()
        (cls.template / "package.json").write_text(
            '{"name":"fixture","private":true,"type":"module","devDependencies":{"vite":"^8.3.0"}}\n'
        )
        installed = run("bun", "add", "-d", "vite-plugin-singlefile", cwd=cls.template)
        if installed.returncode != 0:
            raise unittest.SkipTest(f"cannot install fixture dependencies: {installed.stderr[-300:]}")
        (cls.template / "vite.config.js").write_text(
            'import { defineConfig } from "vite"\nexport default defineConfig({})\n'
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.template_tmp.cleanup()

    def project(self, *, head: str = "", body: str = "", main: str = 'document.title = "x"\n') -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        project = Path(tmp.name) / "app"
        shutil.copytree(self.template, project, symlinks=True)
        (project / "index.html").write_text(INDEX_HTML.format(head=head, body=body))
        (project / "main.js").write_text(main)
        return project

    def bundle(self, project: Path) -> subprocess.CompletedProcess[str]:
        return run("bash", str(BUNDLE), cwd=project)

    def test_inlines_public_images_referenced_by_the_html(self) -> None:
        project = self.project(
            head='<link rel="icon" type="image/png" href="/logo.png" />',
            body='<img alt="logo" src="/logo.png" />',
        )
        (project / "public").mkdir()
        (project / "public" / "logo.png").write_bytes(PNG)

        result = self.bundle(project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        html = (project / "bundle.html").read_text()
        self.assertNotIn('"/logo.png"', html)
        self.assertIn("data:image/png;base64,", html)

    def test_fails_loudly_when_a_local_file_is_still_referenced(self) -> None:
        project = self.project(body='<img alt="gone" src="/not-in-public.png" />')

        result = self.bundle(project)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not-in-public.png", result.stdout + result.stderr)
        self.assertFalse((project / "bundle.html").exists())

    def test_resolves_function_based_vite_configs(self) -> None:
        project = self.project(main='document.title = __BUILD_MODE__\n')
        (project / "vite.config.js").write_text(
            'import { defineConfig } from "vite"\n'
            "export default defineConfig(({ mode }) => ({\n"
            "  define: { __BUILD_MODE__: JSON.stringify(`mode-${mode}`) },\n"
            "}))\n"
        )

        result = self.bundle(project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("mode-production", (project / "bundle.html").read_text())

    def test_failed_build_keeps_the_previous_bundle_and_leaves_no_temp_output(self) -> None:
        project = self.project(main='import "./does-not-exist.js"\n')
        (project / "bundle.html").write_text("PREVIOUS BUNDLE")

        result = self.bundle(project)

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((project / "bundle.html").read_text(), "PREVIOUS BUNDLE")
        self.assertFalse((project / "dist-bundle").exists())
        leftovers = [p.name for p in project.iterdir() if p.name.startswith("bundle.html.")]
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
