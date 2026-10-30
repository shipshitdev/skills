import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "validate-codex.mjs"
VALID = "policy:\n  allow_implicit_invocation: false\n"


class CodexPolicyTest(unittest.TestCase):
    def run_on(self, policies):
        scratch = ROOT / ".tmp"
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as tmp:
            skills = Path(tmp) / "skills"
            for name, policy in policies.items():
                agents = skills / name / "agents"
                agents.mkdir(parents=True)
                if policy is not None:
                    (agents / "openai.yaml").write_text(policy)
            return subprocess.run(
                ["bun", str(SCRIPT), str(skills)],
                capture_output=True, text=True, check=False,
            )

    def test_explicit_only_policy_with_optional_metadata_passes(self):
        result = self.run_on({"sample": 'interface:\n  display_name: "Sample"\n' + VALID})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_file_fails(self):
        result = self.run_on({"sample": None})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sample/agents/openai.yaml", result.stderr)

    def test_missing_enabled_or_wrongly_typed_policy_fails(self):
        for policy in ["", "{}", "policy: {}", "policy: false", "policy: []"] + [
            f"policy:\n  allow_implicit_invocation: {value}\n"
            for value in ["true", '"false"', "null", "0", "[]"]
        ]:
            with self.subTest(policy=policy):
                result = self.run_on({"sample": policy})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("boolean false", result.stderr)

    def test_malformed_yaml_fails(self):
        result = self.run_on({"sample": "policy: [\n"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sample/agents/openai.yaml", result.stderr)

    def test_every_skill_is_checked(self):
        result = self.run_on({"first": VALID, "second": None, "third": "policy: {}\n"})
        self.assertEqual(result.returncode, 1)
        self.assertIn("second/agents/openai.yaml", result.stderr)
        self.assertIn("third/agents/openai.yaml", result.stderr)
        self.assertIn("3 Codex invocation policies checked, 2 errors", result.stdout)


if __name__ == "__main__":
    unittest.main()
