from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_DIR / "scripts"


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


init_workspace = load("init_workspace", "init-workspace.py")

EXACT_VERSION = re.compile(r"^\d+\.\d+\.\d+$")
# Stack guidance the scaffold must never emit again
BANNED = [
    "clerk",
    "@agenticindiedev",
    ".scss",
    "sass",
    "tailwind.config",
    "middleware.ts",
    "mongo",
    "bun.lockb",
]


def run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True,
        text=True,
    )


class ScaffoldTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls._tmp.name) / "workspace"
        result = run(
            "init-workspace.py",
            "--root", str(cls.root),
            "--name", "Smoke App",
            "--org", "smoke",
            "--entities", "task,project",
            "--allow-outside",
        )
        assert result.returncode == 0, result.stdout + result.stderr

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def text_files(self) -> list[Path]:
        return [
            path
            for path in self.root.rglob("*")
            if path.is_file() and ".agents" not in path.parts
        ]

    def package(self, relative: str) -> dict:
        return json.loads((self.root / relative / "package.json").read_text())

    def test_no_stale_stack_guidance_is_emitted(self) -> None:
        for path in self.text_files():
            content = path.read_text().lower()
            for banned in BANNED:
                self.assertNotIn(banned, content, f"{banned!r} found in {path.relative_to(self.root)}")
        for pattern in ("tailwind.config.*", "*.scss", "middleware.ts", "biome.json"):
            matches = [p for p in self.root.rglob(pattern) if "node_modules" not in p.parts]
            if pattern == "biome.json":
                self.assertEqual([m.relative_to(self.root) for m in matches], [Path("biome.json")])
            else:
                self.assertEqual(matches, [], pattern)

    def test_every_pin_is_exact_and_shared_pins_agree(self) -> None:
        packages = {
            name: self.package(name)
            for name in ("api", "frontend/apps/dashboard", "frontend/packages", "mobile")
        }
        packages["root"] = json.loads((self.root / "package.json").read_text())
        seen: dict[str, set[str]] = {}
        for name, pkg in packages.items():
            for section in ("dependencies", "devDependencies", "peerDependencies"):
                for dep, version in pkg.get(section, {}).items():
                    self.assertRegex(version, EXACT_VERSION, f"{name}: {dep}")
                    seen.setdefault(dep, set()).add(version)
        # React is intentionally pinned differently for the Expo app only
        mobile_only = {"react", "@types/react"}
        for dep, versions in seen.items():
            if dep not in mobile_only:
                self.assertEqual(len(versions), 1, f"{dep} pinned to {versions}")

    def test_prisma_config_tolerates_a_missing_database_url(self) -> None:
        config = (self.root / "api" / "prisma.config.ts").read_text()
        self.assertIn("datasource: { url: process.env.DATABASE_URL }", config)
        self.assertNotIn("url: env(", config)
        self.assertNotIn("import { defineConfig, env }", config)
        # The generated Dockerfile builds without any .env
        dockerfile = (self.root / "api" / "Dockerfile").read_text()
        self.assertIn('--filter "@smoke/api"', dockerfile)
        self.assertNotIn("DATABASE_URL", dockerfile.replace("prisma generate needs no DATABASE_URL", ""))

    def test_frontend_is_tailwind_v4_css_first_with_proxy(self) -> None:
        dashboard = self.root / "frontend" / "apps" / "dashboard"
        css = (dashboard / "app" / "globals.css").read_text()
        self.assertTrue(css.startswith('@import "tailwindcss";'))
        self.assertIn("@theme inline", css)
        self.assertEqual(
            (dashboard / "postcss.config.mjs").read_text().count("@tailwindcss/postcss"), 1
        )
        self.assertTrue((dashboard / "proxy.ts").exists())
        deps = self.package("frontend/apps/dashboard")
        self.assertNotIn("sass", deps["devDependencies"])
        self.assertIn("better-auth", deps["dependencies"])

    def test_api_vitest_config_emits_decorator_metadata(self) -> None:
        config = (self.root / "api" / "vitest.config.mts").read_text()
        self.assertIn('import swc from "unplugin-swc"', config)
        self.assertIn("swc.vite(", config)

    def test_generated_json_is_valid_and_ends_with_newline(self) -> None:
        for path in self.text_files():
            if path.suffix == ".json":
                json.loads(path.read_text())
                self.assertTrue(path.read_text().endswith("\n"), path.name)

    def test_entities_get_guarded_controllers_and_specs(self) -> None:
        collections = self.root / "api" / "apps" / "api" / "src" / "collections" / "tasks"
        controller = (collections / "tasks.controller.ts").read_text()
        self.assertIn("@UseGuards(AuthGuard)", controller)
        for name in ("tasks.controller.spec.ts", "tasks.service.spec.ts"):
            self.assertTrue((collections / name).exists(), name)
        schema = (self.root / "api" / "prisma" / "schema" / "task.prisma").read_text()
        self.assertIn("model Task", schema)
        self.assertTrue((self.root / "api" / "prisma" / "schema" / "auth.prisma").exists())

    def test_reserved_entity_names_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run(
                "init-workspace.py",
                "--root", str(Path(tmp) / "ws"),
                "--name", "Clash",
                "--entities", "user",
                "--allow-outside",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Better Auth", result.stdout)

    def test_dump_json_matches_biome_formatting(self) -> None:
        self.assertEqual(
            init_workspace.dump_json({"a": ["x", "y"], "b": {"c": 1}, "d": []}),
            '{\n  "a": ["x", "y"],\n  "b": {\n    "c": 1\n  },\n  "d": []\n}',
        )
        long_list = [f"item-number-{i}" for i in range(10)]
        rendered = init_workspace.dump_json({"list": long_list})
        self.assertTrue(rendered.startswith('{\n  "list": [\n    "item-number-0",'))


class AddScriptsTest(unittest.TestCase):
    def test_add_frontend_app_creates_a_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "workspace"
            result = run(
                "init-workspace.py", "--root", str(root), "--name", "Demo", "--org", "demo",
                "--allow-outside",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            frontend = root / "frontend"
            added = run("add-frontend-app.py", "--root", str(frontend), "--name", "admin")
            self.assertEqual(added.returncode, 0, added.stdout + added.stderr)
            app = frontend / "apps" / "admin"
            package = json.loads((app / "package.json").read_text())
            self.assertEqual(package["name"], "@demo/admin")
            for relative in (
                "next.config.ts", "postcss.config.mjs", "tsconfig.json", "vitest.config.mts",
                "app/layout.tsx", "app/page.tsx", "app/page.spec.tsx", "app/globals.css",
            ):
                self.assertTrue((app / relative).exists(), relative)
            self.assertIn('import "./globals.css"', (app / "app" / "layout.tsx").read_text())

    def test_add_api_collection_writes_prisma_model_and_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            api = Path(tmp) / "api"
            (api / "apps" / "api" / "src" / "collections").mkdir(parents=True)
            result = run("add-api-collection.py", "--root", str(api), "--name", "comments")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((api / "prisma" / "schema" / "comments.prisma").exists())
            service = api / "apps/api/src/collections/comments/services/comments.service.ts"
            self.assertIn("../../../generated/prisma/client", service.read_text())


RELATIVE_IMPORT = re.compile(r"""from\s+["'](\.{1,2}/[^"']+)["']""")


def unresolved_relative_imports(src_root: Path) -> list[str]:
    """Relative imports in generated Nest sources that point at a missing file."""
    missing = []
    generated = (src_root / "generated").resolve()
    for path in src_root.rglob("*.ts"):
        if "generated" in path.parts:
            continue
        for target in RELATIVE_IMPORT.findall(path.read_text()):
            base = (path.parent / target).resolve()
            if not (
                Path(f"{base}.ts").exists()
                or (base / "index.ts").exists()
                or base.is_relative_to(generated)
            ):
                missing.append(f"{path.relative_to(src_root)} -> {target}")
    return missing


class ScaffoldSecurityTest(unittest.TestCase):
    """Regression tests for the independent review of the scaffold (issue 226)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls._tmp.name) / "workspace"
        result = run(
            "init-workspace.py", "--root", str(cls.root), "--name", "Smoke App",
            "--org", "smoke", "--entities", "task", "--allow-outside",
        )
        assert result.returncode == 0, result.stdout + result.stderr
        cls.api = cls.root / "api"
        cls.add = run("add-api-collection.py", "--root", str(cls.api), "--name", "comments")
        assert cls.add.returncode == 0, cls.add.stdout + cls.add.stderr
        cls.src = cls.api / "apps" / "api" / "src"
        cls.collection = cls.src / "collections" / "comments"

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def read(self, relative: str) -> str:
        return (self.root / relative).read_text()

    # P1: generated collections are guarded and scoped from the session
    def test_collection_controller_requires_the_auth_guard(self) -> None:
        controller = (self.collection / "controllers" / "comments.controller.ts").read_text()
        self.assertIn("@UseGuards(AuthGuard)", controller)
        self.assertIn("../../../auth/guards/auth.guard", controller)
        self.assertIn("../../../auth/decorators/current-user.decorator", controller)
        self.assertIn("@ApiCookieAuth()", controller)
        self.assertNotIn("ApiBearerAuth", controller)

    def test_collection_scope_never_comes_from_client_input(self) -> None:
        for path in self.collection.rglob("*"):
            if path.is_file():
                text = path.read_text()
                self.assertNotIn("organizationId", text, path.name)
                self.assertNotIn("@Query(", text, path.name)
        controller = (self.collection / "controllers" / "comments.controller.ts").read_text()
        self.assertEqual(controller.count("@CurrentUser()"), 5)
        dto = (self.collection / "dto" / "create-comments.dto.ts").read_text()
        self.assertNotIn("userId", dto)
        self.assertIn("userId", (self.api / "prisma" / "schema" / "comments.prisma").read_text())

    def test_collection_service_scopes_every_prisma_call(self) -> None:
        service = (self.collection / "services" / "comments.service.ts").read_text()
        calls = re.findall(r"this\.prisma\.comments?\.(\w+)\(", service)
        self.assertEqual(sorted(calls), ["create", "findFirst", "findMany", "updateMany", "updateMany"])
        for call in ("findMany", "findFirst", "updateMany"):
            for block in re.findall(rf"\.{call}\(\{{(.*?)\n\s*\}}\);", service, re.S):
                self.assertRegex(block, r"where:\s*\{[^}]*\buserId\b", f"{call} is not scoped")
        # A write outside the caller's scope finds nothing and answers 404
        self.assertIn("result.count === 0", service)
        self.assertIn("NotFoundException", service)
        self.assertNotIn("where: { id }", service)

    def test_collection_http_file_needs_a_session_not_a_tenant_id(self) -> None:
        http = (self.collection / "comments.http").read_text()
        self.assertNotIn("organizationId", http)
        self.assertIn("better-auth.session_token", http)

    def test_generated_imports_resolve(self) -> None:
        self.assertEqual(unresolved_relative_imports(self.src), [])

    def test_docs_do_not_teach_client_supplied_tenant_ids(self) -> None:
        for name in ("coding-standards.md", "architecture-guide.md"):
            text = (SKILL_DIR / "references" / name).read_text()
            self.assertNotIn('@Query("organizationId")', text, name)

    # P1: the Docker context must not leak api/.env
    def test_dockerignore_keeps_env_files_out_of_the_image(self) -> None:
        ignore = self.read(".dockerignore").splitlines()
        for pattern in (
            ".env*", "!.env.example", "**/.env*", "!**/.env.example",
            ".git", "**/node_modules", "**/dist", "**/coverage", "**/.next",
        ):
            self.assertIn(pattern, ignore)

    def test_runtime_image_copies_only_built_artifacts(self) -> None:
        dockerfile = self.read("api/Dockerfile")
        runner = dockerfile.split("AS runner", 1)[1]
        self.assertNotIn("COPY --from=builder /app/api ./api", runner)
        for artifact in (
            "/app/api/dist", "/app/api/package.json", "/app/node_modules", "/app/api/node_modules",
        ):
            self.assertIn(artifact, runner)
        self.assertIn("dist/generated", dockerfile)
        self.assertNotIn(".env", runner)

    # P2: the session cookie must reach the dashboard on a sibling subdomain
    def test_better_auth_cookies_can_span_subdomains(self) -> None:
        service = self.read("api/apps/api/src/auth/auth.service.ts")
        self.assertIn("crossSubDomainCookies", service)
        self.assertIn("process.env.COOKIE_DOMAIN", service)
        self.assertIn("trustedOrigins", service)
        self.assertIn("COOKIE_DOMAIN", self.read(".env.example"))
        guide = (SKILL_DIR / "references" / "deployment-guide.md").read_text()
        self.assertIn("COOKIE_DOMAIN", guide)
        self.assertIn("crossSubDomainCookies", guide)

    # P2: prisma generate is part of setup and of the add-collection flow
    def test_prisma_generate_is_in_setup_docs_and_output(self) -> None:
        self.assertIn("prisma:generate", self.read("README.md"))
        self.assertIn("prisma:generate", json.loads(self.read("package.json"))["scripts"])
        self.assertIn("prisma:generate", self.add.stdout)
        self.assertIn("prisma:generate", (SKILL_DIR / "SKILL.md").read_text())

    # P2: refreshed session cookies reach the client
    def test_guard_forwards_refreshed_session_cookies(self) -> None:
        guard = self.read("api/apps/api/src/auth/guards/auth.guard.ts")
        template = (SKILL_DIR / "references/templates/auth-guard.template.ts").read_text()
        for text in (guard, template):
            self.assertIn("returnHeaders: true", text)
            self.assertIn("getSetCookie()", text)
            self.assertIn("getResponse", text)
        spec = self.read("api/apps/api/src/auth/guards/auth.guard.spec.ts")
        self.assertIn("set-cookie", spec.lower())

    # P2: Tailwind must scan the shared workspace package
    def test_tailwind_scans_the_shared_packages(self) -> None:
        dashboard = self.root / "frontend" / "apps" / "dashboard" / "app"
        css = (dashboard / "globals.css").read_text()
        self.assertIn('@source "../../../packages";', css)
        self.assertTrue((dashboard / "../../../packages").resolve().samefile(
            self.root / "frontend" / "packages"))

    # P2: the controller template matches the generator's import depth
    def test_controller_template_imports_match_the_generator(self) -> None:
        template = (SKILL_DIR / "references/templates/controller.template.ts").read_text()
        self.assertIn('"../../auth/guards/auth.guard"', template)
        self.assertIn('"../../auth/decorators/current-user.decorator"', template)
        self.assertNotIn('"../auth/', template)

    # P3: the API owns 3001
    def test_extra_frontend_apps_do_not_suggest_the_api_port(self) -> None:
        added = run("add-frontend-app.py", "--root", str(self.root / "frontend"), "--name", "admin")
        self.assertEqual(added.returncode, 0, added.stdout + added.stderr)
        self.assertIn("-p 3002", added.stdout)
        self.assertNotIn("-p 3001", added.stdout)
        # A new app's origin is a one-line env change
        self.assertIn("FRONTEND_URLS=http://localhost:3000,http://localhost:3002", added.stdout)

    # Follow-up: several frontend origins for CORS and trustedOrigins
    def test_cors_and_trusted_origins_share_a_comma_separated_origin_list(self) -> None:
        origins = self.read("api/apps/api/src/config/origins.ts")
        self.assertIn("process.env", origins)
        self.assertIn("env.FRONTEND_URLS", origins)
        self.assertIn("env.FRONTEND_URL ||", origins)
        self.assertIn('.split(",")', origins)
        self.assertTrue((self.src / "config" / "origins.spec.ts").exists())
        main = self.read("api/apps/api/src/main.ts")
        self.assertIn("origin: allowedOrigins()", main)
        self.assertNotIn("process.env.FRONTEND_URL", main)
        service = self.read("api/apps/api/src/auth/auth.service.ts")
        template = (SKILL_DIR / "references/templates/auth-service.template.ts").read_text()
        for text in (service, template):
            self.assertIn("trustedOrigins: allowedOrigins()", text)
            self.assertNotIn("process.env.FRONTEND_URL", text)
        self.assertIn("FRONTEND_URLS=", self.read(".env.example"))
        guide = (SKILL_DIR / "references" / "deployment-guide.md").read_text()
        self.assertIn("FRONTEND_URLS", guide)

    # Review follow-up: only exact http(s) origins, validated at startup
    def test_origin_list_rejects_wildcards_and_non_origins_at_startup(self) -> None:
        origins = self.read("api/apps/api/src/config/origins.ts")
        self.assertIn("Invalid origin", origins)
        self.assertIn('includes("*")', origins)
        self.assertIn("new URL(", origins)
        self.assertIn(".origin !==", origins)
        self.assertIn("throw new Error", origins)
        self.assertNotIn(".replace(", origins)  # no silent normalisation
        spec = self.read("api/apps/api/src/config/origins.spec.ts")
        self.assertIn("https://*.example.com", spec)
        self.assertIn("rejects the wildcard origin", spec)
        # Both consumers take the validated list; nothing parses the env var on its own
        for relative in ("api/apps/api/src/main.ts", "api/apps/api/src/auth/auth.service.ts"):
            text = self.read(relative)
            self.assertIn("allowedOrigins()", text)
            self.assertNotIn("FRONTEND_URL", text)
        template = (SKILL_DIR / "references/templates/auth-service.template.ts").read_text()
        self.assertNotIn("FRONTEND_URL", template)
        for text in (
            self.read(".env.example"),
            (SKILL_DIR / "references" / "deployment-guide.md").read_text(),
        ):
            self.assertIn("wildcard", text.lower())
            self.assertIn("exact", text.lower())

    def test_docker_workflow_inspects_the_builder_stage_too(self) -> None:
        workflow = (SKILL_DIR.parents[1] / ".github/workflows/project-init-docker.yml").read_text()
        self.assertIn("docker build --target builder", workflow)
        builder_check = workflow.split("docker build --target builder", 1)[1]
        self.assertIn("test ! -e /app/api/.env", builder_check)
        self.assertIn("api/.env", workflow.split("docker build --target builder", 1)[0])


if __name__ == "__main__":
    unittest.main()
