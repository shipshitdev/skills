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
        installed = run(
            "bun",
            "add",
            "-d",
            "vite-plugin-singlefile",
            "parse5@8.0.1",
            "css-tree@3.2.1",
            cwd=cls.template,
        )
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
        before = {p.name for p in project.iterdir()}

        result = self.bundle(project)

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((project / "bundle.html").read_text(), "PREVIOUS BUNDLE")
        leftovers = sorted(p.name for p in project.iterdir() if p.name not in before)
        self.assertEqual(leftovers, ["vite.singlefile.config.ts"])

    def test_retained_custom_singlefile_config_still_builds_into_the_run_directory(self) -> None:
        project = self.project()
        # No marker line: the script must keep this file and its hard-coded outDir
        (project / "vite.singlefile.config.ts").write_text(
            'import { defineConfig, mergeConfig } from "vite"\n'
            'import { viteSingleFile } from "vite-plugin-singlefile"\n'
            'import baseConfig from "./vite.config.js"\n'
            "export default mergeConfig(baseConfig, defineConfig({\n"
            "  plugins: [viteSingleFile()],\n"
            '  build: { outDir: "dist-bundle", emptyOutDir: true },\n'
            "}))\n"
        )

        result = self.bundle(project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("<title>fixture</title>", (project / "bundle.html").read_text())
        self.assertFalse((project / "dist-bundle").exists())
        self.assertIn("dist-bundle", (project / "vite.singlefile.config.ts").read_text())


    def test_bun_installs_are_exact_and_cold_start_runs_do_not_race(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        project = Path(tmp.name) / "app"
        project.mkdir()
        # no node_modules at all: both runs have to install (from the warm cache) at the same time
        (project / "package.json").write_text(
            '{"name":"fixture","private":true,"type":"module","devDependencies":{"vite":"^8.3.0"}}\n'
        )
        (project / "vite.config.js").write_text('import { defineConfig } from "vite"\nexport default defineConfig({})\n')
        (project / "index.html").write_text(INDEX_HTML.format(head="", body=""))
        (project / "main.js").write_text('document.title = "x"\n')
        procs = [
            subprocess.Popen(
                ["bash", str(BUNDLE)], cwd=project, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            for _ in range(3)
        ]
        outputs = [p.communicate()[0] for p in procs]
        self.assertEqual([p.returncode for p in procs], [0, 0, 0], "\n".join(outputs))
        manifest = (project / "package.json").read_text()
        self.assertIn('"parse5": "8.0.1"', manifest)
        self.assertIn('"css-tree": "3.2.1"', manifest)
        self.assertRegex(manifest, r'"vite-plugin-singlefile": "\d')  # exact, no caret

    def cold_project(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        project = Path(tmp.name) / "app"
        project.mkdir()
        (project / "package.json").write_text(
            '{"name":"fixture","private":true,"type":"module","devDependencies":{"vite":"^8.3.0"}}\n'
        )
        (project / "vite.config.js").write_text('import { defineConfig } from "vite"\nexport default defineConfig({})\n')
        (project / "index.html").write_text(INDEX_HTML.format(head="", body=""))
        (project / "main.js").write_text('document.title = "x"\n')
        return project

    def stub_bun(self, project: Path, on_add: str) -> dict:
        """A bun wrapper in front of PATH whose `bun add` runs `on_add` instead of installing."""
        import os

        real = shutil.which("bun")
        bin_dir = project.parent / "stubbin"
        bin_dir.mkdir(exist_ok=True)
        stub = bin_dir / "bun"
        stub.write_text(f'#!/bin/sh\nif [ "$1" = add ]; then\n{on_add}\nfi\nexec "{real}" "$@"\n')
        stub.chmod(0o755)
        return {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"}

    def leftovers(self, project: Path) -> list[str]:
        return sorted(p.name for p in project.iterdir() if p.name.startswith((".bundle-", "bundle.html.", "vite.singlefile.config.ts.")))

    def test_stale_install_lock_of_a_killed_run_is_recovered(self) -> None:
        import os
        import signal
        import time

        project = self.cold_project()
        env = self.stub_bun(project, "sleep 120")  # the first run hangs inside `bun add`
        first = subprocess.Popen(
            ["bash", str(BUNDLE)], cwd=project, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        lock = project / ".bundle-install.lock"
        deadline = time.time() + 30
        while not lock.exists() and time.time() < deadline:
            time.sleep(0.1)
        self.assertTrue(lock.exists(), "the first run never took the install lock")
        time.sleep(0.5)  # let it finish writing its owner record
        os.killpg(first.pid, signal.SIGKILL)  # kill -9 during the install
        first.wait()
        self.assertTrue(lock.exists(), "kill -9 leaves the lock behind, which is what is being tested")

        result = self.bundle(project)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("<title>fixture</title>", (project / "bundle.html").read_text())
        self.assertFalse(lock.exists())

    def test_failures_and_signals_clean_up_the_lock_and_temp_files(self) -> None:
        import os
        import signal
        import time

        # 1. the install itself fails: lock released, nothing left behind
        project = self.cold_project()
        env = self.stub_bun(project, "exit 1")
        result = subprocess.run(["bash", str(BUNDLE)], cwd=project, env=env, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.leftovers(project), [])
        self.assertFalse((project / "bundle.html").exists())

        # 2. SIGTERM while the install holds the lock: the EXIT trap still runs
        project = self.cold_project()
        env = self.stub_bun(project, "sleep 120")
        proc = subprocess.Popen(
            ["bash", str(BUNDLE)], cwd=project, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        deadline = time.time() + 30
        while not (project / ".bundle-install.lock").exists() and time.time() < deadline:
            time.sleep(0.1)
        # like a terminal or a CI runner: the signal goes to the whole process group
        os.killpg(proc.pid, signal.SIGTERM)
        proc.wait(timeout=30)
        self.assertEqual(self.leftovers(project), [])

        # 3. the inliner rejects the page after the build: work directory removed, config kept
        project = self.project(body='<img alt="gone" src="/not-in-public.png" />')
        result = self.bundle(project)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.leftovers(project), [])
        self.assertTrue((project / "vite.singlefile.config.ts").exists())  # the config itself is kept
        self.assertFalse((project / ".bundle-install.lock").exists())

    def test_public_symlink_escape_is_rejected_end_to_end(self) -> None:
        project = self.project(body='<img alt="x" src="/secret.png" />')
        outside = project.parent / "outside"
        outside.mkdir()
        (outside / "secret.png").write_bytes(b"TOP-SECRET")
        (project / "public").mkdir()
        (project / "public" / "secret.png").symlink_to(outside / "secret.png")

        result = self.bundle(project)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("/secret.png", result.stdout + result.stderr)
        self.assertFalse((project / "bundle.html").exists())

    def test_concurrent_runs_use_separate_build_directories(self) -> None:
        project = self.project()
        procs = [
            subprocess.Popen(
                ["bash", str(BUNDLE)], cwd=project, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            for _ in range(2)
        ]
        outputs = [p.communicate()[0] for p in procs]
        self.assertEqual([p.returncode for p in procs], [0, 0], "\n".join(outputs))
        self.assertIn("<title>fixture</title>", (project / "bundle.html").read_text())
        leftovers = [p.name for p in project.iterdir() if p.name.startswith((".bundle-", "bundle.html.", "vite.singlefile.config.ts."))]
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
