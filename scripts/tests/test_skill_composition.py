from __future__ import annotations

import importlib.util
import subprocess
import shutil
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "skill_composition", ROOT / "scripts/check-skill-composition.py"
)
assert SPEC and SPEC.loader
composition = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(composition)


class SkillCompositionTests(unittest.TestCase):
    def setUp(self) -> None:
        scratch = ROOT / ".tmp"
        scratch.mkdir(exist_ok=True)
        self.directory = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.directory.cleanup)
        self.skills = Path(self.directory.name)

    def add_skill(self, name: str, body: str = "", explicit: bool = False) -> Path:
        directory = self.skills / name
        directory.mkdir()
        restriction = "disable-model-invocation: true\n" if explicit else ""
        (directory / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Fixture.\n{restriction}---\n{body}\n"
        )
        return directory

    def test_installed_dependency_docs_do_not_become_skill_routes(self) -> None:
        caller = self.add_skill("caller")
        dependency = caller / "scripts/node_modules/example/README.md"
        dependency.parent.mkdir(parents=True)
        dependency.write_text("Run the `missing-engine` skill.\n")
        self.assertEqual(composition.findings(caller, self.skills), [])

    def test_retired_provider_family_is_rejected(self) -> None:
        caller = self.add_skill("gh-inbox")
        self.assertIn("Retired gh-* skill family", composition.findings(caller, self.skills)[0])

    def test_catalog_adapters_reject_retired_routes_but_preserve_upstream_urls(self) -> None:
        commands = self.skills / "commands"
        commands.mkdir()
        path = commands / "board.md"
        path.write_text("Run the `gh-board-sync` skill.\n")
        self.assertIn("Retired skill reference", composition.catalog_findings(self.skills / "skills")[0])
        path.write_text("Run the `board-sync` skill.\nSource: https://example.com/gh-board-sync\nUse `gh-ost` and the `gh-pages` branch.\n")
        self.assertEqual(composition.catalog_findings(self.skills / "skills"), [])

    def test_catalog_rejects_stale_published_sources_and_bundled_identities(self) -> None:
        root = self.skills
        marketplace = root / ".claude-plugin"
        marketplace.mkdir()
        manifest = marketplace / "marketplace.json"
        manifest.write_text(json.dumps({"plugins": [{"name": "board-sync", "source": "./skills/gh-board-sync"}]}))
        self.assertIn("Missing local plugin source", composition.catalog_findings(root / "skills")[0])
        source = root / "skills/board-sync"
        source.mkdir(parents=True)
        manifest.write_text(json.dumps({"plugins": [{"name": "board-sync", "source": "./skills/board-sync"}]}))
        self.assertEqual(composition.catalog_findings(root / "skills"), [])
        (root / "bundles/example/skills/gh-board-sync").mkdir(parents=True)
        self.assertIn("Retired bundled skill identity", composition.catalog_findings(root / "skills")[0])

    def test_direct_route_rejects_hidden_engine(self) -> None:
        caller = self.add_skill("caller", "1. Run the `engine` skill.")
        self.add_skill("engine", explicit=True)
        self.assertEqual(len(composition.findings(caller, self.skills)), 1)
        self.assertIn("user-only skill: engine", composition.findings(caller, self.skills)[0])

    def test_negative_condition_still_executes_its_route(self) -> None:
        caller = self.add_skill("caller", "If not configured, run the `engine` skill.")
        self.add_skill("engine", explicit=True)
        self.assertIn("user-only skill: engine", composition.findings(caller, self.skills)[0])

    def test_callable_engine_can_be_composed(self) -> None:
        caller = self.add_skill("caller", "- **run →** apply the `engine` skill.", explicit=True)
        self.add_skill("engine", "Apply only within the authorized task.")
        self.assertEqual(composition.findings(caller, self.skills), [])

    def test_recommendations_and_prohibitions_do_not_execute(self) -> None:
        caller = self.add_skill("caller", "Recommend: run the `engine` skill.\nDo not invoke `engine`.\nForce mode does not run `engine`.")
        self.add_skill("engine", explicit=True)
        self.assertEqual(composition.findings(caller, self.skills), [])

    def test_related_workflow_is_advice_not_composition(self) -> None:
        caller = self.add_skill("caller", "## When NOT to Use\nUse the `engine` skill for other work.")
        self.add_skill("engine", explicit=True)
        self.assertEqual(composition.findings(caller, self.skills), [])

    def test_code_examples_are_not_routes(self) -> None:
        caller = self.add_skill("caller", "```markdown\nRun the `engine` skill.\n```\n~~~md\nApply `engine`.\n~~~")
        self.add_skill("engine", explicit=True)
        self.assertEqual(composition.findings(caller, self.skills), [])

    def test_shorter_fence_does_not_end_a_code_example(self) -> None:
        caller = self.add_skill("caller", "````markdown\n```\nRun the `engine` skill.\n```\n````")
        self.add_skill("engine", explicit=True)
        self.assertEqual(composition.findings(caller, self.skills), [])

    def test_actual_missing_skill_differs_from_cli_command(self) -> None:
        caller = self.add_skill("caller", "Run the `missing-engine` skill.\nRun `git-status`.")
        findings = composition.findings(caller, self.skills)
        self.assertEqual(len(findings), 1)
        self.assertIn("Missing execution skill: missing-engine", findings[0])

    def test_local_resources_resolve_from_the_installed_skill(self) -> None:
        caller = self.add_skill("caller", "Read [guide](references/guide.md).")
        findings = composition.findings(caller, self.skills)
        self.assertIn("Missing local resource", findings[0])
        (caller / "references").mkdir()
        (caller / "references/guide.md").write_text("Instructions.\n")
        self.assertEqual(composition.findings(caller, self.skills), [])

    def test_remote_links_and_template_placeholders_are_not_local_files(self) -> None:
        caller = self.add_skill("caller", "[docs](https://example.com/docs) [section](#usage)\n[reference](URL) [reference]({Reference URL}) [site](/docs/concepts/resources)")
        self.assertEqual(composition.findings(caller, self.skills), [])

    def test_declared_lists_check_every_target_across_wrapped_lines(self) -> None:
        caller = self.add_skill("caller", "## Contract\nDelegates To:\n\n- `visible`, `hidden`,\n  and `missing-engine` for investigation.")
        self.add_skill("visible")
        self.add_skill("hidden", explicit=True)
        findings = composition.findings(caller, self.skills)
        self.assertEqual(len(findings), 2)
        self.assertIn("user-only skill: hidden", findings[0])
        self.assertIn("Missing execution skill: missing-engine", findings[1])

    def test_declared_recommendation_and_mode_names_are_not_execution(self) -> None:
        caller = self.add_skill("caller", "Delegates To:\n\n- Recommend `hidden`, `absent` for other work.\n- `visible` for `hidden` mode.\n\n## Examples\n- `hidden` for a later workflow.")
        self.add_skill("visible")
        self.add_skill("hidden", explicit=True)
        self.assertEqual(composition.findings(caller, self.skills), [])

    def test_ordinary_prose_example_does_not_hide_an_execution_route(self) -> None:
        caller = self.add_skill("caller", "For example, if setup is missing, run the `hidden` skill.\nRecommend a report first; run the `hidden` skill.")
        self.add_skill("hidden", explicit=True)
        self.assertEqual(len(composition.findings(caller, self.skills)), 2)

    def test_missing_or_unclosed_target_frontmatter_is_a_finding(self) -> None:
        caller = self.add_skill("caller", "Run the `engine` skill.")
        target = self.add_skill("engine") / "SKILL.md"
        for text in ["# No frontmatter\n", "---\nname: engine\n"]:
            with self.subTest(text=text):
                target.write_text(text)
                self.assertIn("missing or unclosed frontmatter", composition.findings(caller, self.skills)[0])

    def test_trailing_space_frontmatter_delimiters_do_not_hide_routes(self) -> None:
        caller = self.add_skill("caller", "Run the `hidden` skill.")
        target = self.add_skill("hidden", explicit=True)
        for directory in [caller, target]:
            path = directory / "SKILL.md"
            path.write_text(path.read_text().replace("---\n", "---  \n"))
        self.assertIn("user-only skill: hidden", composition.findings(caller, self.skills)[0])

    def test_review_dispatch_is_callable_in_the_public_catalog(self) -> None:
        header = composition.frontmatter((ROOT / "skills/review-dispatch/SKILL.md").read_text())
        self.assertIsNotNone(header)
        self.assertNotIn("disable-model-invocation: true", header)

    def test_default_merge_preserves_cleanup_selection_boundary(self) -> None:
        """Static contract guard; this does not simulate a merge or an agent run."""
        body = (ROOT / "skills/merge-open-prs/SKILL.md").read_text()
        command = (ROOT / "commands/merge.md").read_text()
        self.assertNotIn("--delete-branch", body)
        self.assertNotIn("--delete-branch", command)
        for text in (body, command):
            normalized = " ".join(text.split())
            self.assertIn("Merge confirmation authorizes merges only", normalized)
            self.assertIn("Preserve local branches and worktrees", normalized)
        self.assertIn("Cleanup Inventory (Read-Only)", body)
        self.assertIn("Recommend `git-cleanup`", body)
        self.assertIn("With `--no-prune`, stop after Phase 4", body)

    def test_public_pstack_routes_are_discoverable(self) -> None:
        self.assertEqual(composition.findings(ROOT / "skills/pstack", ROOT / "skills"), [])

    def test_board_packages_resolve_when_installed_outside_the_repository(self) -> None:
        for name in ("board-sync", "project-board", "github-inbox", "github-review-suggestions"):
            shutil.copytree(ROOT / "skills" / name, self.skills / name)
        for name, helper in (("board-sync", "github-board-report.mjs"),
                             ("project-board", "setup-github-board.mjs"),
                             ("github-inbox", "github-inbox-report.mjs"),
                             ("github-review-suggestions", "diff-line-position.mjs")):
            installed = self.skills / name
            if name in ("board-sync", "project-board"):
                self.assertEqual(composition.findings(installed, self.skills), [])
            result = subprocess.run(["node", str(installed / "scripts" / helper), "--help"],
                                    cwd=self.skills, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_system_bash_parses_the_repository_validator(self) -> None:
        result = subprocess.run(
            ["/bin/bash", "-n", str(ROOT / "scripts/validate-skill-sync.sh")],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_provenance_workflow_uses_explicit_targets_and_harness_model(self) -> None:
        script = r'''
import { readFileSync } from "node:fs";
import assert from "node:assert/strict";
const source = readFileSync("scripts/classify-provenance.workflow.js", "utf8")
  .replace("export const meta", "const meta");
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const execute = new AsyncFunction("agent", "parallel", "phase", "SKILLS_ROOT", "SKILL_NAMES", source);
const missingNames = new AsyncFunction("agent", "parallel", "phase", "SKILLS_ROOT", source);
await assert.rejects(missingNames(null, null, null, "/installed/skills"), /Supply SKILLS_ROOT/);
let calls = 0;
const agent = async (prompt, options) => {
  assert.equal(Object.hasOwn(options, "model"), false);
  assert.match(prompt, /installed\/skills\/board-sync\/SKILL.md/);
  calls++;
  return { skill: options.label };
};
const parallel = (tasks) => Promise.all(tasks.map((task) => task()));
await assert.rejects(execute(agent, parallel, () => {}, "", []), /Supply SKILLS_ROOT/);
const result = await execute(agent, parallel, () => {}, "/installed/skills", ["board-sync", "board-sync"]);
assert.equal(calls, 1);
assert.deepEqual(result.results, [{ skill: "board-sync" }]);
'''
        result = subprocess.run(["bun", "-e", script], cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_review_workflow_leaves_model_selection_with_harness(self) -> None:
        script = r'''
import { readFileSync } from "node:fs";
import assert from "node:assert/strict";
const source = readFileSync("skills/full-code-review/scripts/full-code-review.js", "utf8")
  .replace("export const meta", "const meta");
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const execute = new AsyncFunction("agent", "parallel", "log", "DIFF", "CHANGED_FILES", "COMMIT_LOG", source);
for (const retro of [false, true]) {
  const labels = [];
  const agent = async (_prompt, options) => {
    assert.equal(Object.hasOwn(options, "model"), false);
    assert.equal(Object.hasOwn(options, "effort"), false);
    labels.push(options.label);
    if (options.label === "adversarial-verifier") return { verified_findings: [] };
    if (options.label.endsWith("synthesis")) return { mode: retro ? "retro" : "pr", verdict: retro ? "retro-backlog" : "approve", rationale: "Fixture", stats: {} };
    return { findings: [] };
  };
  const result = await execute(agent, (tasks) => Promise.all(tasks.map((task) => task())), () => {}, "diff", "file.ts", retro ? "commit" : "");
  assert.equal(labels.length, retro ? 6 : 5);
  assert.equal(result.mode, retro ? "retro" : "pr");
}
'''
        result = subprocess.run(["bun", "-e", script], cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
