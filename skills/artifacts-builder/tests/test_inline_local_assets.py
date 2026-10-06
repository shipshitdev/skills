from __future__ import annotations

import base64
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

INLINER = Path(__file__).resolve().parents[1] / "scripts" / "inline-local-assets.mjs"

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)
WOFF2 = b"wOF2-fake-font-bytes"
SVG = b'<svg xmlns="http://www.w3.org/2000/svg" id="icon"/>'


def page(body: str = "", head: str = "") -> str:
    return f'<!doctype html><html><head><meta charset="UTF-8">{head}</head><body>{body}</body></html>'


@unittest.skipUnless(shutil.which("bun"), "bun is required")
class InlineLocalAssetsTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name).resolve()
        self.project = self.base / "project"
        self.dist = self.project / "dist"
        self.outside = self.base / "outside"
        self.dist.mkdir(parents=True)
        (self.project / "public").mkdir()
        self.outside.mkdir()
        (self.outside / "secret.png").write_bytes(b"TOP-SECRET")
        self.out = self.base / "out.html"

    def write_page(self, body: str = "", head: str = "") -> None:
        (self.dist / "index.html").write_text(page(body, head))

    def inline(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bun", str(INLINER), str(self.dist), str(self.out), str(self.project)],
            cwd=self.base,
            capture_output=True,
            text=True,
        )

    def ok(self) -> str:
        result = self.inline()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return self.out.read_text()

    def fails_naming(self, *names: str) -> None:
        result = self.inline()
        self.assertNotEqual(result.returncode, 0, "expected a failure")
        self.assertFalse(self.out.exists(), "no output may be written on failure")
        for name in names:
            self.assertIn(name, result.stdout + result.stderr)

    # --- HTML attribute parsing -------------------------------------------------------

    def test_attribute_syntax_variants_are_all_inlined(self) -> None:
        (self.dist / "x.png").write_bytes(PNG)
        self.write_page(
            "<img src=/x.png><IMG SRC=\"/x.png\"><img src = '/x.png'><img\n src\n=\n/x.png alt=a>"
        )
        html = self.ok()
        self.assertEqual(html.count("data:image/png;base64,"), 4)
        self.assertNotIn("/x.png", html)

    def test_unquoted_uppercase_and_spaced_attributes_are_validated(self) -> None:
        for body in ("<img src=/gone.png>", '<img SRC="/gone.png">', "<img src = '/gone.png'>"):
            with self.subTest(body=body):
                self.write_page(body)
                self.fails_naming("/gone.png")

    def test_plain_text_and_non_asset_attributes_are_left_alone(self) -> None:
        self.write_page(
            '<p title="url(foo)">Use url(foo) and src=/not-an-attr in prose</p>'
            "<!-- <img src=/commented.png> -->"
            '<a href="/about">about</a><script>const s = "<img src=/in-js.png> url(bar)"</script>'
        )
        html = self.ok()
        self.assertIn("Use url(foo) and src=/not-an-attr in prose", html)
        self.assertIn("/commented.png", html)
        self.assertIn('href="/about"', html)
        self.assertIn("/in-js.png", html)

    # --- CSS contexts ----------------------------------------------------------------

    def test_css_urls_are_processed_in_style_elements_and_style_attributes(self) -> None:
        (self.dist / "x.png").write_bytes(PNG)
        self.write_page(
            '<div style="background:url(/x.png)"></div>', "<style>.a{background:url('/x.png')}</style>"
        )
        html = self.ok()
        self.assertEqual(html.count("data:image/png;base64,"), 2)

    def test_unresolvable_css_urls_fail_in_styles(self) -> None:
        self.write_page("", "<style>.a{background:url(/nope.png)}</style>")
        self.fails_naming("/nope.png")

    def test_linked_stylesheet_dependencies_are_inlined_relative_to_the_stylesheet(self) -> None:
        (self.dist / "css").mkdir()
        (self.dist / "fonts").mkdir()
        (self.dist / "fonts" / "f.woff2").write_bytes(WOFF2)
        (self.dist / "css" / "i.png").write_bytes(PNG)
        (self.dist / "css" / "site.css").write_text(
            '@font-face{font-family:f;src:url("../fonts/f.woff2") format("woff2")}'
            ".a{background:url(i.png)}"
        )
        self.write_page("", '<link rel="stylesheet" href="/css/site.css">')
        html = self.ok()
        match = re.search(r'href="data:text/css[^"]*;base64,([^"]+)"', html)
        self.assertIsNotNone(match, html)
        css = base64.b64decode(match.group(1)).decode()
        self.assertIn("data:font/woff2;base64,", css)
        self.assertIn("data:image/png;base64,", css)
        self.assertNotIn("../fonts/f.woff2", css)
        self.assertNotIn("url(i.png)", css)

    def test_unresolvable_dependency_of_a_linked_stylesheet_fails(self) -> None:
        (self.dist / "site.css").write_text(".a{background:url(missing-bg.png)}")
        self.write_page("", '<link rel="stylesheet" href="/site.css">')
        self.fails_naming("missing-bg.png")

    # --- pathname decoding and fragments --------------------------------------------

    def test_percent_encoded_segments_resolve(self) -> None:
        (self.dist / "a#b.png").write_bytes(PNG)
        (self.dist / "sp ace.png").write_bytes(PNG)
        self.write_page('<img src="/a%23b.png"><img src="/sp%20ace.png">')
        html = self.ok()
        self.assertEqual(html.count("data:image/png;base64,"), 2)

    def test_fragments_are_kept_on_the_data_uri(self) -> None:
        (self.dist / "icon.svg").write_bytes(SVG)
        self.write_page('<img src="/icon.svg#view">', "<style>.i{background:url(/icon.svg#frag)}</style>")
        html = self.ok()
        self.assertRegex(html, r'src="data:image/svg\+xml;base64,[A-Za-z0-9+/=]+#view"')
        self.assertRegex(html, r"url\(data:image/svg\+xml;base64,[A-Za-z0-9+/=]+#frag\)")

    # --- symlink escapes -----------------------------------------------------------------

    def test_symlinked_file_pointing_outside_is_rejected(self) -> None:
        (self.dist / "link.png").symlink_to(self.outside / "secret.png")
        self.write_page('<img src="/link.png">')
        self.fails_naming("/link.png")

    def test_symlinked_directory_pointing_outside_is_rejected(self) -> None:
        (self.dist / "linked").symlink_to(self.outside, target_is_directory=True)
        self.write_page('<img src="/linked/secret.png">')
        self.fails_naming("/linked/secret.png")

    def test_public_symlinks_that_were_copied_into_dist_are_rejected(self) -> None:
        # Vite copies public/ into the build, following symlinks, so the escape has to be
        # detected against the project's public/ directory too.
        (self.project / "public" / "secret.png").symlink_to(self.outside / "secret.png")
        (self.project / "public" / "dir").symlink_to(self.outside, target_is_directory=True)
        (self.dist / "secret.png").write_bytes(b"TOP-SECRET")
        (self.dist / "dir").mkdir()
        (self.dist / "dir" / "secret.png").write_bytes(b"TOP-SECRET")
        for ref in ("/secret.png", "/dir/secret.png"):
            with self.subTest(ref=ref):
                self.write_page(f'<img src="{ref}">')
                self.fails_naming(ref)

    def test_parent_traversal_out_of_the_build_dir_is_rejected(self) -> None:
        (self.project / "package.json").write_text("{}")
        self.write_page('<img src="/../package.json">')
        self.fails_naming("package.json")

    def test_regular_files_and_internal_symlinks_still_work(self) -> None:
        (self.dist / "real.png").write_bytes(PNG)
        (self.dist / "alias.png").symlink_to(self.dist / "real.png")
        self.write_page('<img src="/real.png"><img src="/alias.png">')
        self.assertEqual(self.ok().count("data:image/png;base64,"), 2)


if __name__ == "__main__":
    unittest.main()
