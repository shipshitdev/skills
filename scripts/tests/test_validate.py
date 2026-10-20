import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import validate  # noqa: E402

VALID = """---
name: sample
description: Does one thing when the user asks for it.
disable-model-invocation: true
---

# Sample

See [the guide](references/guide.md).
"""


class ValidateTest(unittest.TestCase):
    def run_on(self, skill_md, extra=None, directory="sample"):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "skills" / directory
            (skill / "references").mkdir(parents=True)
            (skill / "references" / "guide.md").write_text("# Guide\n")
            (skill / "SKILL.md").write_text(skill_md)
            for name, text in (extra or {}).items():
                (skill / name).write_text(text)
            return validate.check_skill(skill)

    def test_valid_skill_passes(self):
        self.assertEqual(self.run_on(VALID), [])

    def test_model_invocable_skill_fails(self):
        errors = self.run_on(VALID.replace("disable-model-invocation: true\n", ""))
        self.assertTrue(any("disable-model-invocation" in e for e in errors))

    def test_hidden_from_user_fails(self):
        errors = self.run_on(VALID.replace("---\n\n", "user-invocable: false\n---\n\n", 1))
        self.assertTrue(any("user-invocable" in e for e in errors))

    def test_name_mismatch_fails(self):
        errors = self.run_on(VALID.replace("name: sample", "name: other"))
        self.assertTrue(any("does not match directory" in e for e in errors))

    def test_hyphenated_name_fails(self):
        errors = self.run_on(VALID.replace("name: sample", "name: run-qa"), directory="run-qa")
        self.assertTrue(any("one lowercase word" in e for e in errors))

    def test_broken_link_fails(self):
        errors = self.run_on(VALID.replace("references/guide.md", "references/missing.md"))
        self.assertTrue(any("broken link" in e for e in errors))

    def test_links_inside_code_fences_are_ignored(self):
        self.assertEqual(self.run_on(VALID + "\n```md\n[x](nowhere.md)\n```\n"), [])

    def test_concrete_model_id_fails(self):
        errors = self.run_on(VALID, {"notes.md": "Run on claude-sonnet-4-5.\n"})
        self.assertTrue(any("concrete model ID" in e for e in errors))

    def test_main_reports_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            skills = Path(tmp) / "skills"
            (skills / "empty").mkdir(parents=True)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(validate.main(skills), 1)


if __name__ == "__main__":
    unittest.main()
