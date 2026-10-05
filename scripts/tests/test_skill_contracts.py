from __future__ import annotations

import importlib.util
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "skill_composition", ROOT / "scripts/check-skill-composition.py"
)
assert SPEC and SPEC.loader
composition = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(composition)


def skill(name: str) -> str:
    return re.sub(r"\s+", " ", (ROOT / "skills" / name / "SKILL.md").read_text())


class SkillContractTests(unittest.TestCase):
    """Static safeguards for published instructions, not an agent behavior eval."""

    def test_test_routes_do_not_grant_implicit_edits(self) -> None:
        for name in ("test-runner", "test-dispatch"):
            with self.subTest(skill=name):
                body = skill(name)
                self.assertIn("Before the first source or test edit", body)
                self.assertIn("Existing explicit authorization", body)
                self.assertIn("bare scope", body)
                self.assertNotIn("their tests without asking", body)
                self.assertNotIn("Only `status`, `qa`, and `--no-fix`", body)

    def test_command_preserves_engine_repair_gate(self) -> None:
        body = re.sub(r"\s+", " ", (ROOT / "commands/test.md").read_text())
        self.assertIn("Before the first source or test edit", body)
        self.assertIn("Existing explicit authorization", body)
        self.assertIn("report-only mode prohibits source and test edits", body)
        self.assertNotIn("auto-fix until green", body)
        self.assertNotIn("apply a minimal fix, and rerun until green or blocked", body)
        self.assertIn("when repair is authorized apply a minimal fix", body)

    def test_report_only_overrides_repair_authorization(self) -> None:
        for name in ("test-runner", "test-dispatch"):
            with self.subTest(skill=name):
                self.assertIn("`--no-fix` or report-only mode prohibits source and test edits", skill(name))

    def test_inlined_routers_are_explicit_entry_points_and_commands_name_engines(self) -> None:
        """Commands carry the routing table; their portable routers cost no listing space."""
        for name in ("agent", "deploy", "design", "prd", "skill", "test"):
            with self.subTest(command=name):
                router = f"{name}-dispatch"
                skill_text = (ROOT / "skills" / router / "SKILL.md").read_text()
                header = composition.frontmatter(skill_text)
                self.assertIsNotNone(header)
                self.assertIn("disable-model-invocation: true", header)
                self.assertNotIn("user-invocable: false", header)
                command = (ROOT / "commands" / f"{name}.md").read_text()
                self.assertNotIn(f"`{router}`", command)
                lines = list(composition.instruction_lines(skill_text))
                delegates = {target for _, target in composition.declared_delegates(lines)}
                self.assertTrue(delegates)
                for target in delegates:
                    self.assertIn(f"`{target}`", command)
                    target_header = composition.frontmatter(
                        (ROOT / "skills" / target / "SKILL.md").read_text()
                    )
                    self.assertNotIn("disable-model-invocation: true", target_header)

    def test_standup_has_no_session_write_exception(self) -> None:
        body = skill("standup")
        self.assertIn("Nothing. Keep the entire invocation read-only", body)
        self.assertNotIn("Only writes to a session log", body)
        self.assertNotIn("Nothing by default", body)

    def test_retired_skills_are_not_required_contracts(self) -> None:
        validator = (ROOT / "scripts/validate-skill-sync.sh").read_text()
        contract_list = validator.split('CONTRACT_REQUIRED_SKILLS="', 1)[1].split('"', 1)[0].split()
        for name in ("session-documenter", "session-start", "session-end"):
            self.assertNotIn(name, contract_list)
            self.assertFalse((ROOT / "skills" / name).exists())

    def test_monitor_contract_covers_restart_and_equal_timestamps(self) -> None:
        body = skill("qa-loop")
        for rule in ("last complete-record boundary", "make queue records durable before advancing the persisted cursor", "timestamp alone is not a cursor", "source identity", "persist", "tie-breaker", "rotation", "at-least-once", "restore the queue records", "never use it as the replay identity"):
            with self.subTest(rule=rule):
                self.assertIn(rule, body)
        outputs = body.split("Outputs:", 1)[1].split("Creates/Modifies:", 1)[0]
        self.assertIn("in progress", outputs)
        intake = body.split("For each incoming issue:", 1)[1].split("2.", 1)[0]
        for state in ("pending", "in progress", "fixed", "ignored", "observed", "blocked"):
            self.assertIn(f"`{state}`", intake)
        self.assertIn("Move the selected `pending` issue to `in progress`", body)
        self.assertIn("never commit checkpoints", body)

    def test_interception_requires_application_ownership(self) -> None:
        body = skill("qa-loop")
        self.assertIn("A 5xx status, failed job, or same-origin URL alone does not prove ownership", body)
        self.assertIn("Without that evidence, classify as `observed` or `blocked`", body)

    def test_deslop_preserves_precise_technical_terms(self) -> None:
        body = re.sub(r"\s+", " ", (ROOT / "skills/deslop/references/prose-slop.md").read_text())
        self.assertIn("Preserve established technical meanings", body)
        self.assertIn("API surface", body)
        self.assertIn("embedding vector", body)
        self.assertNotIn('"Vector" becomes "way" or "method"', body)


if __name__ == "__main__":
    unittest.main()
