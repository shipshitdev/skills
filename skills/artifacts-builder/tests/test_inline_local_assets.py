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


DEPENDENCIES = ["parse5@8.0.1", "css-tree@3.2.1"]


@unittest.skipUnless(shutil.which("bun"), "bun is required")
class InlineLocalAssetsTest(unittest.TestCase):
    deps_tmp: tempfile.TemporaryDirectory

    @classmethod
    def setUpClass(cls) -> None:
        # The inliner runs from inside a project, where bundle-artifact.sh has installed its parsers
        cls.deps_tmp = tempfile.TemporaryDirectory()
        deps = Path(cls.deps_tmp.name)
        (deps / "package.json").write_text('{"name":"inliner-deps","private":true,"type":"module"}\n')
        installed = subprocess.run(["bun", "add", *DEPENDENCIES], cwd=deps, capture_output=True, text=True)
        if installed.returncode != 0:
            raise unittest.SkipTest(f"cannot install parser dependencies: {installed.stderr[-300:]}")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.deps_tmp.cleanup()

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
        # Run a copy next to a node_modules symlink, as the bundle script does inside the project
        self.script = self.base / "inline-local-assets.mjs"
        shutil.copy(INLINER, self.script)
        shutil.copy(INLINER.parent.parent / "tests" / "dump-dom.mjs", self.base / "dump-dom.mjs")
        (self.base / "node_modules").symlink_to(Path(self.deps_tmp.name) / "node_modules")

    def write_page(self, body: str = "", head: str = "") -> None:
        (self.dist / "index.html").write_text(page(body, head))

    def inline(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bun", str(self.script), str(self.dist), str(self.out), str(self.project)],
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
        self.assertRegex(html, r'url\("data:image/svg\+xml;base64,[A-Za-z0-9+/=]+#frag"\)')

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

    # --- HTML character references in attribute values ------------------------------------

    def test_entity_encoded_references_are_decoded_and_inlined(self) -> None:
        (self.dist / "x.png").write_bytes(PNG)
        (self.dist / "a&b.png").write_bytes(PNG)
        self.write_page(
            '<img src="&#47;x.png"><img src="&#x2F;x.png"><img src="&sol;x.png"><img src=&#47;x.png>'
            '<img src="&#x2f;a&amp;b.png"><img src="/&#120;.png"><img src="&#47x.png">'
        )
        html = self.ok()
        self.assertEqual(html.count("data:image/png;base64,"), 7)
        self.assertNotIn("x.png", html)

    def test_entity_encoded_missing_references_fail_instead_of_being_skipped(self) -> None:
        for body in ('<img src="&#47;gone.png">', "<img src=&#47;gone.png>", '<img SRC = "&sol;gone.png">'):
            with self.subTest(body=body):
                self.write_page(body)
                self.fails_naming("/gone.png")

    def test_entity_encoded_parent_traversal_cannot_escape(self) -> None:
        (self.project / "package.json").write_text('{"secret": true}')
        for ref in (
            "&#46;&#46;/package.json",
            "/&#x2e;&#x2E;/package.json",
            "&period;&period;&sol;package.json",
            "/..&sol;package.json",
            "/.&Tab;./package.json",
            "/&#46;.&#47;package.json",
            "/..&bsol;package.json",
        ):
            with self.subTest(ref=ref):
                self.write_page(f'<img src="{ref}">')
                result = self.inline()
                self.assertNotEqual(result.returncode, 0, ref)
                self.assertFalse(self.out.exists())
                self.assertNotIn("secret", self.out.read_text() if self.out.exists() else "")

    def test_entity_encoded_symlink_escape_is_still_rejected_after_decoding(self) -> None:
        (self.dist / "link.png").symlink_to(self.outside / "secret.png")
        self.write_page('<img src="/lin&#107;.png">')
        self.fails_naming("/link.png")

    def test_unknown_named_references_stay_literal_like_in_browsers(self) -> None:
        # parse5 follows the HTML spec: an unknown `&name;` is literal text, so the file that
        # really has that name is the one inlined (and a missing one fails as a missing file)
        (self.dist / "x&notarealentity;.png").write_bytes(b"LITERAL-UNKNOWN-ENTITY")
        self.write_page('<img src="/x&notarealentity;.png">')
        self.assertEqual(self.inlined(self.ok()), [b"LITERAL-UNKNOWN-ENTITY"])
        (self.dist / "x&notarealentity;.png").unlink()
        self.out.unlink()
        self.fails_naming("&notarealentity;")

    def test_ambiguous_ampersand_rules_follow_the_html_spec_in_attributes(self) -> None:
        (self.dist / "a&ampb.png").write_bytes(PNG)  # "&ampb" is literal: next char is alphanumeric
        (self.dist / "a&.png").write_bytes(PNG)  # "&amp." decodes: legacy name followed by "."
        self.write_page('<img src="/a&ampb.png"><img src="/a&amp.png">')
        self.assertEqual(self.ok().count("data:image/png;base64,"), 2)

    def test_legacy_name_followed_by_equals_stays_literal(self) -> None:
        (self.dist / "x.png").write_bytes(PNG)
        self.write_page('<img src="/x.png?a=1&copy=2&amp=3">')
        self.assertEqual(self.ok().count("data:image/png;base64,"), 1)

    def test_rewritten_values_are_encoded_correctly(self) -> None:
        (self.dist / "icon.svg").write_bytes(SVG)
        (self.dist / "x.png").write_bytes(PNG)
        self.write_page(
            '<img src="/icon.svg#a&amp;b"><img src=\'/icon.svg#q&#39;z\'>'
            '<div style="background:url(&quot;/x.png&quot;)"></div><p title="a&amp;b">t</p>'
        )
        html = self.ok()
        self.assertRegex(html, r'src="data:image/svg\+xml;base64,[A-Za-z0-9+/=]+#a&amp;b"')
        self.assertRegex(html, r'src="data:image/svg\+xml;base64,[A-Za-z0-9+/=]+#q\'z"')
        self.assertRegex(html, r'style="background:url\(&quot;data:image/png;base64,[A-Za-z0-9+/=]+&quot;\)"')
        self.assertIn('title="a&amp;b"', html)

    def test_entities_in_srcset_and_rel_are_decoded(self) -> None:
        (self.dist / "x.png").write_bytes(PNG)
        (self.dist / "s.css").write_text(".a{color:red}")
        self.write_page(
            '<img srcset="&#47;x.png 1x, &sol;x.png 2x">', '<link rel="&#115;tylesheet" href="/s.css">'
        )
        html = self.ok()
        self.assertEqual(html.count("data:image/png;base64,"), 2)
        self.assertIn('href="data:text/css;base64,', html)

    # --- parser-grade HTML, srcset and CSS handling -------------------------------------------

    def test_empty_comment_close_does_not_hide_following_markup(self) -> None:
        self.write_page("<!--><img src=/missing.png>")
        self.fails_naming("/missing.png")

    def test_srcset_keeps_data_uris_with_commas_and_inlines_local_candidates(self) -> None:
        (self.dist / "x.png").write_bytes(PNG)
        (self.dist / "a,b.png").write_bytes(PNG)
        data = "data:image/png;base64,AAAA"
        self.write_page(f'<img srcset="{data} 1x, /x.png 2x, /a,b.png 3x">')
        html = self.ok()
        srcset = re.search(r'srcset="([^"]*)"', html).group(1)
        self.assertTrue(srcset.startswith(f"{data} 1x, data:image/png;base64,"), srcset)
        self.assertEqual(srcset.count("data:image/png;base64,"), 3)
        self.assertNotIn("/x.png", srcset)
        self.assertNotIn("a,b.png", srcset)

    def test_srcset_with_a_missing_local_candidate_fails(self) -> None:
        self.write_page('<img srcset="data:image/png;base64,AAAA 1x, /nope.png 2x">')
        self.fails_naming("/nope.png")

    def test_css_strings_that_look_like_urls_are_not_dependencies(self) -> None:
        self.write_page("", '<style>.a::after{content:"url(example)"}.b::after{content:\'url(/nope.png)\'}</style>')
        html = self.ok()
        self.assertIn('content:"url(example)"', html)

    def test_quoted_css_urls_may_contain_parentheses(self) -> None:
        (self.dist / "a)b.png").write_bytes(PNG)
        self.write_page("", '<style>.a{background:url("/a)b.png")}</style>')
        html = self.ok()
        self.assertIn("data:image/png;base64,", html)
        self.assertNotIn("a)b.png", html)

    def test_css_comments_and_image_set_are_handled_by_the_css_parser(self) -> None:
        (self.dist / "x.png").write_bytes(PNG)
        self.write_page(
            "",
            '<style>/* url(/commented.png) */.a{background:image-set("/x.png" 1x, url(/x.png) 2x)}'
            '@import "/imp.css";</style>',
        )
        (self.dist / "imp.css").write_text(".z{color:red}")
        html = self.ok()
        self.assertIn("/* url(/commented.png) */", html)
        self.assertEqual(html.count("data:image/png;base64,"), 2)
        self.assertIn("data:text/css;base64,", html)

    def test_stylesheet_urls_resolve_against_the_lexical_url_directory(self) -> None:
        (self.dist / "styles").mkdir()
        (self.dist / "css").mkdir()
        (self.dist / "styles" / "theme.css").write_text(".a{background:url(img.png)}")
        (self.dist / "css" / "img.png").write_bytes(PNG)  # next to the URL the page links
        (self.dist / "css" / "alias.css").symlink_to(self.dist / "styles" / "theme.css")
        self.write_page("", '<link rel="stylesheet" href="/css/alias.css">')
        html = self.ok()
        match = re.search(r'href="data:text/css;base64,([^"]+)"', html)
        self.assertIsNotNone(match, html)
        self.assertIn("data:image/png;base64,", base64.b64decode(match.group(1)).decode())

    # --- distinct-content fixtures: the right bytes must be inlined --------------------------

    def inlined(self, html: str) -> list[bytes]:
        return [base64.b64decode(m) for m in re.findall(r"data:[^;\"')]+;base64,([A-Za-z0-9+/=]+)", html)]

    def test_legacy_name_without_semicolon_decodes_but_stays_literal_before_equals(self) -> None:
        (self.dist / "\u00a9.png").write_bytes(b"COPYRIGHT-SIGN")
        (self.dist / "x&copy=y.png").write_bytes(b"LITERAL-COPY-EQUALS")
        (self.dist / "a&amp=b.png").write_bytes(b"LITERAL-AMP-EQUALS")
        self.write_page('<img src="/&copy.png"><img src="/x&copy=y.png"><img src="/a&amp=b.png">')
        self.assertEqual(
            self.inlined(self.ok()), [b"COPYRIGHT-SIGN", b"LITERAL-COPY-EQUALS", b"LITERAL-AMP-EQUALS"]
        )

    def test_windows_1252_c1_numeric_references_are_remapped(self) -> None:
        (self.dist / "\u20ac.png").write_bytes(b"EURO-SIGN")
        self.write_page('<img src="/&#128;.png"><img src="/&#x80;.png"><img src="/&#x20AC;.png">')
        self.assertEqual(self.inlined(self.ok()), [b"EURO-SIGN"] * 3)

    def test_srcset_candidates_are_parsed_from_the_decoded_value(self) -> None:
        (self.dist / "a,b.png").write_bytes(b"COMMA-FILE")
        (self.dist / "a\u00a0b.png").write_bytes(b"NBSP-FILE")
        (self.dist / "plain.png").write_bytes(b"PLAIN-FILE")
        for attr, extra in (("srcset", ""), ("imagesrcset", ' rel="preload" as="image"')):
            with self.subTest(attr=attr):
                if attr == "srcset":
                    self.write_page(
                        '<img srcset="/a&comma;b.png 1x"><img srcset="/a&nbsp;b.png 1x, /plain.png 2x">'
                    )
                else:
                    self.write_page(
                        "",
                        f'<link{extra} imagesrcset="/a&comma;b.png 1x">'
                        f'<link{extra} imagesrcset="/a&nbsp;b.png 1x, /plain.png 2x">',
                    )
                if self.out.exists():
                    self.out.unlink()
                html = self.ok()
                self.assertEqual(
                    self.inlined(html), [b"COMMA-FILE", b"NBSP-FILE", b"PLAIN-FILE"], attr
                )
                values = re.findall(rf'{attr}="([^"]*)"', html)
                self.assertEqual(len(values), 2)
                self.assertEqual(values[0].count("data:"), 1, "one candidate, not split on the comma")

    # --- stylesheet context, CSS identifiers and escapes -----------------------------------

    def css_uris(self, html: str) -> list[str]:
        return [b.decode() for b in self.inlined(html) if b.startswith(b".") or b.startswith(b"@")]

    def test_stylesheet_links_and_imports_are_css_regardless_of_extension(self) -> None:
        (self.dist / "i.png").write_bytes(PNG)
        (self.dist / "theme").write_text(".a{background:url(i.png)}")
        (self.dist / "other").write_text(".b{background:url(/i.png)}")
        self.write_page("", '<link rel="stylesheet" href="/theme"><style>@import "/other";</style>')
        html = self.ok()
        self.assertEqual(html.count("data:text/css;base64,"), 2)
        for css in self.css_uris(html):
            self.assertIn("data:image/png;base64,", css)

    def test_css_identifiers_are_case_insensitive_and_escape_decoded(self) -> None:
        (self.dist / "x.png").write_bytes(b"IMG-X")
        (self.dist / "s.css").write_text(".z{color:red}")
        values = [
            "URL(/x.png)",
            "UrL( /x.png )",
            "u\\72l(/x.png)",
            'u\\72l("/x.png")',
            "\\75rl(/x.png)",
            'url( "/x.png" )',
        ]
        css = "".join(f".c{i}{{background:{v}}}" for i, v in enumerate(values))
        css += '@IMPORT "/s.css";@im\\70ort url(/s.css);'
        self.write_page("", f"<style>{css}</style>")
        html = self.ok()
        self.assertEqual(self.inlined(html).count(b"IMG-X"), len(values))
        self.assertEqual(html.count("data:text/css;base64,"), 2)
        self.assertNotIn("/x.png", html)
        self.assertNotIn("/s.css", html)

    def test_malformed_url_tokens_fail_loudly(self) -> None:
        self.write_page("", "<style>.a{background:url(/a b.png)}</style>")
        self.fails_naming("url(/a b.png)")

    def test_css_escapes_follow_css_syntax_3(self) -> None:
        cases = {
            "\\61\u00a0.png": "a\u00a0.png",  # NBSP is not CSS whitespace: it is kept
            "\\61 b.png": "ab.png",  # one whitespace after a hex escape is consumed
            "\\000061.png": "a.png",
            "\\0q.png": "\ufffdq.png",  # zero
            "\\d800r.png": "\ufffdr.png",  # surrogate
            "\\110000s.png": "\ufffds.png",  # out of range
            "x\\\n.png": "x.png",  # string continuation
            "\\2f x.png": "/x.png".replace("/", "%2F"),  # placeholder, replaced below
        }
        cases.pop("\\2f x.png")
        for i, (written, name) in enumerate(cases.items()):
            (self.dist / name).write_bytes(f"BYTES-{i}".encode())
        css = "".join(f'.c{i}{{background:url("/{w}")}}' for i, w in enumerate(cases))
        self.write_page("", f"<style>{css}</style>")
        html = self.ok()
        self.assertEqual(self.inlined(html), [f"BYTES-{i}".encode() for i in range(len(cases))])

    # --- srcset descriptors -------------------------------------------------------------

    def test_invalid_srcset_candidates_are_discarded_without_failing(self) -> None:
        (self.dist / "ok.png").write_bytes(b"OK-FILE")
        (self.dist / "v.png").write_bytes(b"V-FILE")
        invalid = [
            "/dup.png 1x 2x",
            "/zero.png 0w",
            "/mixed.png 100w 2x",
            "/nan.png abcx",
            "/dots.png 1.2.3x",
            "/neg.png -1x",
            "/frac.png 1.5w",
            "/hw.png 5h 1x",
            "/unknown.png 3q",
        ]
        valid = ["/ok.png 100w", "/v.png 1.5x"]
        self.write_page(f'<img srcset="{", ".join(invalid + valid)}">')
        html = self.ok()
        self.assertEqual(self.inlined(html), [b"OK-FILE", b"V-FILE"])
        self.assertNotIn("dup.png", html)
        self.assertNotIn("zero.png", html)

    def test_a_valid_but_missing_srcset_candidate_still_fails(self) -> None:
        self.write_page('<img srcset="/zero.png 0w, /gone.png 2x">')
        self.fails_naming("/gone.png")

    # --- serialization keeps the DOM ----------------------------------------------------

    def dump(self, path: Path) -> str:
        result = subprocess.run(
            ["bun", str(self.base / "dump-dom.mjs"), str(path)], cwd=self.base, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_output_parses_to_the_same_dom(self) -> None:
        html = (
            '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">'
            "<!-- lead --><html><head><title>t</title></head><body>"
            "<pre>\n\nfirst line is blank</pre><pre>\nx</pre><pre>plain</pre>"
            "<textarea>\n\nbox</textarea><listing>\n\nlisting</listing>"
            '<p title="a&amp;b &quot;q&quot;">&lt;tag&gt; &amp; &nbsp;</p></body></html>'
        )
        (self.dist / "index.html").write_text(html)
        self.ok()
        self.assertEqual(self.dump(self.out), self.dump(self.dist / "index.html"))

    def test_doctype_identifiers_are_kept(self) -> None:
        (self.dist / "index.html").write_text(
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
            "<html><body>x</body></html>"
        )
        out = self.ok()
        self.assertIn('PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"', out)
        self.assertIn('"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"', out)

    # --- hard links and check-to-read swaps ---------------------------------------------

    def test_hard_linked_files_are_rejected(self) -> None:
        import os

        os.link(self.outside / "secret.png", self.dist / "hard.png")
        self.write_page('<img src="/hard.png">')
        self.fails_naming("/hard.png", "hard link")

    def test_hard_linked_public_sources_are_rejected(self) -> None:
        import os

        os.link(self.outside / "secret.png", self.project / "public" / "hard.png")
        (self.dist / "hard.png").write_bytes(b"TOP-SECRET")  # Vite's copy has a single link
        self.write_page('<img src="/hard.png">')
        self.fails_naming("/hard.png", "hard link")

    def swap_script(self, how: str) -> dict:
        script = self.base / "swap.mjs"
        script.write_text(
            'import { renameSync, symlinkSync, writeFileSync, rmSync } from "node:fs"\n'
            'import { createInliner } from "./inline-local-assets.mjs"\n'
            f"const inliner = createInliner({{ buildDir: {str(self.dist)!r}, projectRoot: {str(self.project)!r} }})\n"
            'const record = inliner.resolveRef("/a.png", inliner.root)\n'
            f"const target = {str(self.dist / 'a.png')!r}\n"
            f"const how = {how!r}\n"
            'if (how === "inode") { writeFileSync(target + ".new", "SWAPPED"); renameSync(target + ".new", target) }\n'
            f'if (how === "symlink") {{ rmSync(target); symlinkSync({str(self.outside / "secret.png")!r}, target) }}\n'
            "const bytes = inliner.readChecked(record)\n"
            "console.log(JSON.stringify({ bytes: bytes === null ? null : bytes.toString(), problems: inliner.problems }))\n"
        )
        result = subprocess.run(["bun", str(script)], cwd=self.base, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        import json

        return json.loads(result.stdout)

    def test_a_file_swapped_after_the_check_is_detected(self) -> None:
        for how in ("inode", "symlink"):
            with self.subTest(how=how):
                (self.dist / "a.png").unlink(missing_ok=True)
                (self.dist / "a.png").write_bytes(b"ORIGINAL")
                outcome = self.swap_script(how)
                self.assertIsNone(outcome["bytes"], outcome)
                self.assertTrue(any("changed" in p for p in outcome["problems"]), outcome)

    def test_an_unswapped_file_is_read_through_the_checked_descriptor(self) -> None:
        (self.dist / "a.png").write_bytes(b"ORIGINAL")
        outcome = self.swap_script("none")
        self.assertEqual(outcome["bytes"], "ORIGINAL")
        self.assertEqual(outcome["problems"], [])


if __name__ == "__main__":
    unittest.main()
