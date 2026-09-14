from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COMMANDS = ("commands/loop.md", "commands/codex-loop.md")
ENTRYPOINTS = COMMANDS + (
    ".agents/memory/system/ai-dev-loop.md",
    "skills/setup-agent-routing/SKILL.md",
    "skills/setup-agent-routing/references/triage-labels.md",
    "skills/setup-agent-routing/references/issue-tracker-github.md",
)


def content(path: str) -> str:
    return " ".join((ROOT / path).read_text().split())


class PreparedEntrypointTests(unittest.TestCase):
    """Catch contradictory published instructions; not a live dispatch evaluation."""

    def test_legacy_claim_expiry_and_automatic_closure_do_not_return(self) -> None:
        forbidden = (
            r"30[- ](?:minute|min)(?:s)?(?: claim)? (?:lock|takeover)",
            r"claims? (?:as )?stale and reclaimable",
            r"claim comment ages out",
            r"(?:closes|fixes|resolves)\s+#",
            r"same inlined contract",
        )
        for path in ENTRYPOINTS:
            with self.subTest(path=path):
                body = content(path)
                for pattern in forbidden:
                    self.assertNotRegex(body, re.compile(pattern, re.IGNORECASE))

    def test_recovery_requires_actual_run_state(self) -> None:
        for path in ENTRYPOINTS:
            with self.subTest(path=path):
                self.assertRegex(
                    content(path).lower(),
                    r"confirm the run ended before explicit claim recovery",
                )

    def test_publication_remains_review_pending(self) -> None:
        for path in ENTRYPOINTS:
            with self.subTest(path=path):
                body = content(path)
                self.assertIn("Refs #<issue>", body)
                self.assertIn("review_pending", body)
                self.assertIn("independent", body)
                self.assertIn("green required CI", body)
                self.assertIn("verified merge", body)
                self.assertIn("deployment", body)
                self.assertRegex(body.lower(), r"keep the epic open|keep an epic open")

    def test_commands_resolve_canonical_contracts_and_preserve_read_only_modes(self) -> None:
        for path in COMMANDS:
            with self.subTest(path=path):
                body = content(path)
                self.assertIn("Run the `executing-plans` skill", body)
                self.assertIn("active skill catalog", body)
                self.assertIn("references/delivery-gate.md", body)
                self.assertIn("references/execution-readiness.md", body)
                self.assertIn(".github/agent-dispatch.md", body)
                self.assertIn("For `--status` or `--list`, inspect only", body)
                self.assertIn("Missing required resources block execution", body)
                self.assertNotIn("source .github/agent-loop.env", body)
                self.assertNotIn("set_status()", body)
                self.assertNotIn("codex exec", body)

    def test_planner_identity_and_configuration_boundary_stay_explicit(self) -> None:
        for path in ENTRYPOINTS[:-1]:
            with self.subTest(path=path):
                body = content(path)
                self.assertIn("dispatch:plan", body)
                self.assertIn("OpenAI", body)
                self.assertIn("harness", body)
                self.assertIn("model", body.lower())
                self.assertIn("effort", body)
                self.assertNotRegex(body, r"(?:--model|--effort|model:|effort:)\s+\S+")

    def test_tracker_seed_treats_board_configuration_as_data(self) -> None:
        body = content("skills/setup-agent-routing/references/issue-tracker-github.md")
        self.assertIn("validated configuration data", body)
        self.assertIn("Paginate", body)
        self.assertIn("match repository identity", body)
        self.assertNotIn("source .github/agent-loop.env", body)


if __name__ == "__main__":
    unittest.main()
