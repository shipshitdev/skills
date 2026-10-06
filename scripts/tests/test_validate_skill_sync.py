from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = REPO_ROOT / "scripts/fixtures/skill-validation"
VALIDATOR = REPO_ROOT / "scripts/validate-skill-sync.sh"


class SkillValidatorFixtureTests(unittest.TestCase):
    def run_fixture(
        self, name: str, manifest_overrides: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            skills_dir = Path(directory) / "skills"
            fixture_dir = skills_dir / name
            shutil.copytree(FIXTURES_DIR / name, fixture_dir)
            manifest = {
                "name": name,
                "version": "1.0.0",
                "description": f"Validation fixture for {name}.",
                "author": {"name": "Fixture"},
                "license": "MIT",
                "skills": ".",
                **(manifest_overrides or {}),
            }
            (fixture_dir / "plugin.json").write_text(json.dumps(manifest))
            environment = os.environ.copy()
            environment["SKILLS_DIR_OVERRIDE"] = str(skills_dir)
            # Isolate from the repo's real commands, which route to real skills.
            commands_dir = Path(directory) / "commands"
            commands_dir.mkdir()
            environment["COMMANDS_DIR_OVERRIDE"] = str(commands_dir)
            return subprocess.run(
                ["bash", str(VALIDATOR), name],
                cwd=REPO_ROOT,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )

    def assert_finding(
        self,
        fixture: str,
        finding: str,
        returncode: int,
        manifest_overrides: dict[str, str] | None = None,
    ) -> None:
        result = self.run_fixture(fixture, manifest_overrides)
        self.assertEqual(result.returncode, returncode, result.stdout + result.stderr)
        self.assertIn(finding, result.stdout)

    def test_valid_portable_fixture_passes(self) -> None:
        result = self.run_fixture("valid-portable")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("✗", result.stdout)

    def test_allowed_tools_list_is_rejected(self) -> None:
        self.assert_finding("invalid-allowed-tools", "allowed-tools must be", 1)

    def test_nested_trigger_metadata_is_rejected(self) -> None:
        self.assert_finding("invalid-triggers", "metadata.triggers is a no-op", 1)

    def test_execution_parameter_is_reported(self) -> None:
        self.assert_finding(
            "invalid-execution-parameter",
            "Harness-owned execution parameter",
            0,
        )

    def test_listing_budget_is_reported(self) -> None:
        result = self.run_fixture("invalid-listing-budget")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("(>200 listing budget)", result.stdout)
        self.assertIn("(>120 listing budget)", result.stdout)

    def test_missing_mutation_guard_is_reported(self) -> None:
        self.assert_finding(
            "invalid-side-effect",
            "side-effecting skill must declare an explicit Confirmation Required gate",
            0,
        )

    def test_callable_writer_uses_body_gate_without_hidden_invocation(self) -> None:
        result = self.run_fixture("valid-composable-writer")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("side-effecting skill", result.stdout)

    def test_platform_marker_is_rejected(self) -> None:
        self.assert_finding("invalid-platform-marker", "Inert platform marker", 1)

    def test_dangling_route_is_reported_outside_named_sections(self) -> None:
        self.assert_finding("invalid-route", "Missing local skill reference", 1)

    def test_library_and_example_names_are_not_skill_routes(self) -> None:
        result = self.run_fixture("valid-library-reference")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("Missing local skill reference", result.stdout)

    def test_concrete_model_is_rejected(self) -> None:
        self.assert_finding("invalid-model", "Concrete model name", 1)

    def test_unsupported_codex_path_claim_is_rejected(self) -> None:
        self.assert_finding(
            "invalid-codex-path-claim",
            "Unsupported Codex path claim",
            1,
        )

    def test_plugin_version_drift_is_rejected(self) -> None:
        # Fixture SKILL.md says 1.2.0; the harness manifest says 1.0.0.
        self.assert_finding(
            "invalid-plugin-version",
            "plugin.json version 1.0.0 != SKILL.md metadata.version 1.2.0",
            1,
        )

    def test_plugin_block_marker_description_is_rejected(self) -> None:
        self.assert_finding(
            "invalid-plugin-description",
            "plugin.json description is a YAML block marker",
            1,
            manifest_overrides={"description": "|"},
        )


COMMAND_TEMPLATE = """---
description: "Fixture command."
disable-model-invocation: true
---

# {name}

## Usage

`/{name} help` prints this Usage block and stops without running anything.

## Workflow

{body}
"""


class CommandRouteTests(unittest.TestCase):
    def run_commands(
        self,
        commands: dict[str, str],
        skills: dict[str, bool],
    ) -> subprocess.CompletedProcess[str]:
        """Validate fixture commands against fixture skills.

        `skills` maps skill name to whether it is user-only.
        """
        with tempfile.TemporaryDirectory() as directory:
            skills_dir = Path(directory) / "skills"
            commands_dir = Path(directory) / "commands"
            fixture_dir = skills_dir / "valid-portable"
            shutil.copytree(FIXTURES_DIR / "valid-portable", fixture_dir)
            (fixture_dir / "plugin.json").write_text(
                json.dumps(
                    {
                        "name": "valid-portable",
                        "version": "1.0.0",
                        "description": "Validation fixture for valid-portable.",
                        "author": {"name": "Fixture"},
                        "license": "MIT",
                        "skills": ".",
                    }
                )
            )
            for skill, user_only in skills.items():
                (skills_dir / skill).mkdir()
                invocation = "disable-model-invocation: true\n" if user_only else ""
                (skills_dir / skill / "SKILL.md").write_text(
                    f"---\nname: {skill}\ndescription: Fixture target.\n"
                    f"{invocation}---\n\n# {skill}\n"
                )
            commands_dir.mkdir()
            for name, body in commands.items():
                (commands_dir / f"{name}.md").write_text(
                    COMMAND_TEMPLATE.format(name=name, body=body)
                )
            environment = os.environ.copy()
            environment["SKILLS_DIR_OVERRIDE"] = str(skills_dir)
            environment["COMMANDS_DIR_OVERRIDE"] = str(commands_dir)
            return subprocess.run(
                ["bash", str(VALIDATOR), "valid-portable"],
                cwd=REPO_ROOT,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )

    def test_valid_target_passes(self) -> None:
        result = self.run_commands(
            {"go": "Use the `real-skill` skill."}, {"real-skill": False}
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("commands/go.md", result.stdout)

    def test_missing_target_names_command_and_target(self) -> None:
        result = self.run_commands({"go": "Use the `ghost-skill` skill."}, {})
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "commands/go.md: routes to missing skill ghost-skill", result.stdout
        )

    def test_missing_target_does_not_stop_later_targets(self) -> None:
        # `a-ghost` sorts before `z-user-only`, so a skipped scan would miss the latter.
        result = self.run_commands(
            {"go": "Use the `a-ghost` skill, then run the `z-user-only` skill."},
            {"z-user-only": True},
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("routes to missing skill a-ghost", result.stdout)
        self.assertIn("routes to user-only skill z-user-only", result.stdout)

    def test_user_only_route_exception_is_preserved(self) -> None:
        result = self.run_commands(
            {"go": "Use the `merge-open-prs` skill."}, {"merge-open-prs": True}
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("commands/go.md", result.stdout)

    def test_user_only_route_without_exception_still_fails(self) -> None:
        result = self.run_commands(
            {"go": "Use the `private-skill` skill."}, {"private-skill": True}
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("routes to user-only skill private-skill", result.stdout)


if __name__ == "__main__":
    unittest.main()
