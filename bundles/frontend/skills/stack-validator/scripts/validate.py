#!/usr/bin/env python3
"""
Stack Validator

One validator for the Shipshit.dev stack: Biome 2.3+, Bun 1.3+ workspaces, Clerk,
Next.js 16 and Tailwind v4. Each stack keeps its own checks; the Issue and
ValidationResult scaffolding, report format, flags and exit codes are shared.

Usage:
    python3 scripts/validate.py --root .                     # auto-detect stacks
    python3 scripts/validate.py --root . --stack nextjs      # one stack
    python3 scripts/validate.py --root . --stack biome --stack tailwind --strict
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import NamedTuple


class Issue(NamedTuple):
    severity: str  # 'error' | 'warning'
    file: str
    line: int | None
    message: str
    fix: str | None


class ValidationResult:
    def __init__(self) -> None:
        self.issues: list[Issue] = []
        self.passed: list[str] = []
        self.meta: dict[str, str | None] = {}

    def add_issue(
        self,
        severity: str,
        file: str,
        message: str,
        line: int | None = None,
        fix: str | None = None,
    ) -> None:
        self.issues.append(Issue(severity, file, line, message, fix))

    def add_passed(self, message: str) -> None:
        self.passed.append(message)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == 'error' for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == 'warning' for i in self.issues)


SOURCE_EXTENSIONS = ('*.tsx', '*.ts', '*.jsx', '*.js')


def load_package_json(root: Path, result: ValidationResult) -> dict | None:
    """Read package.json, recording an error when missing or invalid."""
    pkg_path = root / 'package.json'
    if not pkg_path.exists():
        result.add_issue('error', 'package.json', 'package.json not found')
        return None
    try:
        with open(pkg_path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        result.add_issue('error', 'package.json', 'Invalid JSON')
        return None


def all_dependencies(pkg: dict) -> dict:
    return {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}


def read_package_deps(root: Path) -> dict:
    """Dependencies of package.json, or {} when unreadable (used for detection)."""
    try:
        with open(root / 'package.json') as f:
            return all_dependencies(json.load(f))
    except (OSError, json.JSONDecodeError):
        return {}


def source_files(root: Path, directories: list[str], patterns: tuple[str, ...] = SOURCE_EXTENSIONS):
    """Yield source files below the given directories, skipping node_modules."""
    for dir_name in directories:
        dir_path = root / dir_name
        if not dir_path.exists():
            continue
        for pattern in patterns:
            for file_path in dir_path.rglob(pattern):
                if 'node_modules' in str(file_path):
                    continue
                yield file_path


def read_text(path: Path) -> str | None:
    try:
        return path.read_text()
    except (OSError, UnicodeDecodeError):
        return None


def first_line_with(content: str, needle: str) -> int | None:
    for number, line in enumerate(content.split('\n'), 1):
        if needle in line:
            return number
    return None


# --------------------------------------------------------------------------- #
# Biome
# --------------------------------------------------------------------------- #

def check_biome_package_version(root: Path, result: ValidationResult) -> bool:
    """Check if Biome 2.3+ is installed."""
    pkg = load_package_json(root, result)
    if pkg is None:
        return False

    deps = all_dependencies(pkg)

    if '@biomejs/biome' not in deps:
        result.add_issue('error', 'package.json',
                         '@biomejs/biome not found in dependencies',
                         fix='bun add -D @biomejs/biome@latest')
        return False

    version = deps['@biomejs/biome']
    result.meta['biome_version'] = version

    match = re.search(r'(\d+)\.(\d+)', version)
    if match:
        major, minor = int(match.group(1)), int(match.group(2))
        if major < 2:
            result.add_issue('error', 'package.json',
                             f'Biome 1.x detected ({version}). Must use v2.3+',
                             fix='bun add -D @biomejs/biome@latest')
            return False
        if major == 2 and minor < 3:
            result.add_issue('warning', 'package.json',
                             f'Biome {version} detected. Consider upgrading to 2.3+',
                             fix='bun add -D @biomejs/biome@latest')
        else:
            result.add_passed(f'Biome version: {version}')
        return True

    result.add_issue('warning', 'package.json', f'Could not parse Biome version: {version}')
    return True


def load_biome_config(root: Path, result: ValidationResult) -> dict | None:
    """Load biome.json (or biome.jsonc, with comments removed)."""
    config_path = root / 'biome.json'
    if not config_path.exists():
        config_path = root / 'biome.jsonc'

    if not config_path.exists():
        result.add_issue('error', 'biome.json', 'biome.json not found', fix='bunx biome init')
        return None

    try:
        with open(config_path) as f:
            content = f.read()
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return json.loads(content)
    except json.JSONDecodeError as e:
        result.add_issue('error', config_path.name, f'Invalid JSON: {e}')
        return None


def check_biome_schema_version(config: dict, result: ValidationResult) -> None:
    schema = config.get('$schema', '')

    if not schema:
        result.add_issue('warning', 'biome.json', 'No $schema defined',
                         fix='Add "$schema": "https://biomejs.dev/schemas/2.3.12/schema.json"')
        return

    match = re.search(r'/schemas/(\d+\.\d+\.\d+)/', schema)
    if not match:
        result.add_issue('warning', 'biome.json', f'Could not parse schema version from: {schema}')
        return

    version = match.group(1)
    result.meta['schema_version'] = version
    major, minor = (int(part) for part in version.split('.')[:2])

    if major < 2:
        result.add_issue('error', 'biome.json', f'Schema version {version} is outdated. Use 2.3+',
                         fix='Update $schema to "https://biomejs.dev/schemas/2.3.12/schema.json"')
    elif major == 2 and minor < 3:
        result.add_issue('warning', 'biome.json',
                         f'Schema version {version}. Consider upgrading to 2.3+',
                         fix='Update $schema to "https://biomejs.dev/schemas/2.3.12/schema.json"')
    else:
        result.add_passed(f'Schema version: {version}')


def check_biome_linter(config: dict, result: ValidationResult) -> None:
    linter = config.get('linter', {})

    if not linter.get('enabled', True):
        result.add_issue('warning', 'biome.json', 'Linter is disabled', fix='Set linter.enabled: true')
        return

    result.add_passed('Linter enabled')

    rules = linter.get('rules', {})
    if rules.get('recommended'):
        result.add_passed('Using recommended rules')
    else:
        result.add_issue('warning', 'biome.json', 'Recommended rules not enabled',
                         fix='Add "recommended": true to linter.rules')

    correctness = rules.get('correctness', {})
    if correctness.get('useAwaitThenable'):
        result.add_passed('useAwaitThenable rule enabled')
    else:
        result.add_issue('warning', 'biome.json',
                         'useAwaitThenable not enabled (catches await on non-Promise)',
                         fix='Add correctness.useAwaitThenable: "error"')

    if correctness.get('noLeakedRender'):
        result.add_passed('noLeakedRender rule enabled')

    domains = linter.get('domains', {})
    if domains:
        enabled_domains = [k for k, v in domains.items() if v == 'on']
        if enabled_domains:
            result.add_passed(f'Domains enabled: {", ".join(enabled_domains)}')
    else:
        result.add_issue('warning', 'biome.json',
                         'No domains configured (consider enabling react, next, test)',
                         fix='Add linter.domains: { "react": "on", "next": "on" }')


def check_biome_assist(config: dict, result: ValidationResult) -> None:
    if 'organizeImports' in config:
        result.add_issue('error', 'biome.json', 'organizeImports at root level is deprecated',
                         fix='Move to assist.actions.source.organizeImports')
        return

    source = config.get('assist', {}).get('actions', {}).get('source', {})

    if source.get('organizeImports') == 'on':
        result.add_passed('Using assist.actions for import organization')
    else:
        result.add_issue('warning', 'biome.json', 'Import organization not configured',
                         fix='Add assist.actions.source.organizeImports: "on"')


def check_biome_formatter(config: dict, result: ValidationResult) -> None:
    formatter = config.get('formatter', {})

    if not formatter.get('enabled', True):
        result.add_issue('warning', 'biome.json', 'Formatter is disabled',
                         fix='Set formatter.enabled: true')
        return

    result.add_passed('Formatter enabled')

    if formatter.get('indentStyle'):
        result.add_passed(f'Indent style: {formatter["indentStyle"]}')


BIOME_OLD_CONFIGS = [
    '.eslintrc', '.eslintrc.js', '.eslintrc.json', '.eslintrc.yml', '.eslintrc.yaml',
    '.prettierrc', '.prettierrc.js', '.prettierrc.json', '.prettierrc.yml', '.prettierrc.yaml',
    'prettier.config.js', '.eslintignore', '.prettierignore',
]


def check_biome_old_configs(root: Path, result: ValidationResult) -> None:
    """Flag ESLint/Prettier configs that Biome replaces."""
    for old_file in BIOME_OLD_CONFIGS:
        if (root / old_file).exists():
            result.add_issue('warning', old_file,
                             'Old config file found - Biome replaces ESLint/Prettier',
                             fix=f'rm {old_file}')


def validate_biome(root: Path, result: ValidationResult) -> None:
    check_biome_package_version(root, result)
    config = load_biome_config(root, result)
    if config:
        check_biome_schema_version(config, result)
        check_biome_linter(config, result)
        check_biome_assist(config, result)
        check_biome_formatter(config, result)
    check_biome_old_configs(root, result)


# --------------------------------------------------------------------------- #
# Bun
# --------------------------------------------------------------------------- #

def check_bun_version(result: ValidationResult) -> bool:
    """Check if Bun 1.3+ is installed."""
    try:
        output = subprocess.run(['bun', '--version'], capture_output=True, text=True)
        if output.returncode != 0:
            result.add_issue('error', 'bun', 'Bun not installed',
                             fix='Install Bun: curl -fsSL https://bun.sh/install | bash')
            return False

        version = output.stdout.strip()
        result.meta['bun_version'] = version

        match = re.match(r'(\d+)\.(\d+)', version)
        if match:
            major, minor = int(match.group(1)), int(match.group(2))
            if major < 1 or (major == 1 and minor < 3):
                result.add_issue('warning', 'bun',
                                 f'Bun {version} detected. Consider upgrading to 1.3+ for catalogs and isolated installs',
                                 fix='bun upgrade')
            else:
                result.add_passed(f'Bun version: {version}')
            return True
    except FileNotFoundError:
        result.add_issue('error', 'bun', 'Bun not found',
                         fix='Install Bun: curl -fsSL https://bun.sh/install | bash')
        return False

    return True


def check_bun_root_package(root: Path, result: ValidationResult) -> dict | None:
    pkg_path = root / 'package.json'
    if not pkg_path.exists():
        result.add_issue('error', 'package.json', 'Root package.json not found', fix='bun init')
        return None

    try:
        with open(pkg_path) as f:
            pkg = json.load(f)
    except json.JSONDecodeError:
        result.add_issue('error', 'package.json', 'Invalid JSON')
        return None

    if not pkg.get('private'):
        result.add_issue('error', 'package.json',
                         'Root package.json should have "private": true',
                         fix='Add "private": true to package.json')

    workspaces = pkg.get('workspaces')
    if not workspaces:
        result.add_issue('warning', 'package.json', 'No workspaces defined (not a monorepo?)')
    elif isinstance(workspaces, list):
        result.add_passed(f'Workspaces defined: {workspaces}')
    elif isinstance(workspaces, dict) and 'packages' in workspaces:
        result.add_passed(f'Workspaces defined: {workspaces["packages"]}')

    if pkg.get('dependencies'):
        result.add_issue('warning', 'package.json',
                         'Root package.json has dependencies (consider moving to workspaces)',
                         fix='Move dependencies to individual workspace package.json files')

    if pkg.get('catalog'):
        result.add_passed(f'Dependency catalog found with {len(pkg["catalog"])} entries')
    else:
        result.add_issue('warning', 'package.json',
                         'No dependency catalog found (recommended for Bun 1.3+)',
                         fix='Add "catalog": {} with shared dependency versions')

    return pkg


def workspace_patterns(pkg: dict) -> list[str]:
    workspaces = pkg.get('workspaces', [])
    if isinstance(workspaces, dict):
        workspaces = workspaces.get('packages', [])
    return workspaces


def find_bun_workspaces(root: Path, pkg: dict) -> list[Path]:
    workspace_paths = []
    for pattern in workspace_patterns(pkg):
        if pattern.endswith('/*'):
            base_path = root / pattern[:-2]
            if base_path.exists():
                for child in base_path.iterdir():
                    if child.is_dir() and (child / 'package.json').exists():
                        workspace_paths.append(child)
        else:
            ws_path = root / pattern
            if ws_path.exists() and (ws_path / 'package.json').exists():
                workspace_paths.append(ws_path)
    return workspace_paths


def local_package_names(root: Path) -> set[str]:
    """Names of every workspace package declared under the root's glob patterns."""
    names: set[str] = set()
    try:
        with open(root / 'package.json') as f:
            root_pkg = json.load(f)
    except (OSError, json.JSONDecodeError):
        return names

    for pattern in workspace_patterns(root_pkg):
        if not pattern.endswith('/*'):
            continue
        base_path = root / pattern[:-2]
        if not base_path.exists():
            continue
        for child in base_path.iterdir():
            child_pkg = child / 'package.json'
            if not child_pkg.exists():
                continue
            try:
                with open(child_pkg) as f:
                    name = json.load(f).get('name')
            except (OSError, json.JSONDecodeError):
                continue
            if name:
                names.add(name)
    return names


def check_bun_workspace_dependencies(root: Path, rel_path: Path, pkg: dict, result: ValidationResult) -> None:
    local_packages = local_package_names(root)

    for dep_name, dep_version in all_dependencies(pkg).items():
        if dep_name in local_packages and not dep_version.startswith('workspace:'):
            result.add_issue('error', str(rel_path / 'package.json'),
                             f'Local package {dep_name} should use workspace: protocol',
                             fix=f'Change "{dep_name}": "{dep_version}" to "{dep_name}": "workspace:*"')

        if dep_version == 'catalog:':
            result.add_passed(f'{rel_path}: {dep_name} uses catalog')


BUN_LOCKFILES = ('bun.lock', 'bun.lockb')  # text lockfile (Bun 1.2+ default) and legacy binary


def check_bun_workspace_structure(root: Path, workspaces: list[Path], result: ValidationResult) -> None:
    for ws_path in workspaces:
        rel_path = ws_path.relative_to(root)

        stray = [name for name in BUN_LOCKFILES if (ws_path / name).exists()]
        for name in stray:
            result.add_issue('error', str(rel_path / name),
                             'Lockfile found in workspace - should only be at root',
                             fix=f'rm {rel_path}/{name} && bun install (from root)')
        if not stray:
            result.add_passed(f'{rel_path} - no lockfile (correct)')

        try:
            with open(ws_path / 'package.json') as f:
                pkg = json.load(f)
        except json.JSONDecodeError:
            result.add_issue('error', str(rel_path / 'package.json'), 'Invalid JSON')
            continue

        if not pkg.get('name'):
            result.add_issue('error', str(rel_path / 'package.json'),
                             'Workspace package.json missing name')

        check_bun_workspace_dependencies(root, rel_path, pkg, result)


def check_bun_single_lockfile(root: Path, result: ValidationResult) -> None:
    root_lockfiles = [root / name for name in BUN_LOCKFILES if (root / name).exists()]

    if not root_lockfiles:
        result.add_issue('warning', 'bun.lock', 'No bun.lock or bun.lockb at root (run bun install)',
                         fix='bun install')
        return

    result.add_passed('Single lockfile at root')

    for name in BUN_LOCKFILES:
        for lockfile in root.rglob(name):
            if lockfile not in root_lockfiles and 'node_modules' not in str(lockfile):
                rel_path = lockfile.relative_to(root)
                result.add_issue('error', str(rel_path),
                                 'Extra lockfile found - should only be at root',
                                 fix=f'rm {rel_path}')


def validate_bun(root: Path, result: ValidationResult) -> None:
    check_bun_version(result)
    pkg = check_bun_root_package(root, result)
    if pkg:
        workspaces = find_bun_workspaces(root, pkg)
        if workspaces:
            check_bun_workspace_structure(root, workspaces, result)
        check_bun_single_lockfile(root, result)


# --------------------------------------------------------------------------- #
# Clerk
# --------------------------------------------------------------------------- #

CLERK_SOURCE_DIRS = ['app', 'src', 'pages', 'components', 'lib', 'server']
CLERK_ENV_FILES = ['.env.example', '.env.local', '.env', '.env.development', '.env.production']
CLERK_REQUIRED_ENV = ['NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY', 'CLERK_SECRET_KEY']


def major_version(spec: str) -> int | None:
    match = re.search(r'(\d+)\.', spec) or re.search(r'(\d+)$', spec)
    return int(match.group(1)) if match else None


def check_clerk_package_version(root: Path, result: ValidationResult) -> bool:
    """Check that a current Clerk SDK is installed. Returns True when @clerk/nextjs is present."""
    pkg = load_package_json(root, result)
    if pkg is None:
        return False

    deps = all_dependencies(pkg)
    clerk_packages = sorted(name for name in deps if name.startswith('@clerk/'))

    if not clerk_packages:
        result.add_issue('error', 'package.json', 'No @clerk/* package found in dependencies',
                         fix='bun add @clerk/nextjs@latest')
        return False

    if '@clerk/nextjs' not in deps:
        result.add_passed(f'Clerk packages: {", ".join(clerk_packages)} (Next.js checks skipped)')
        return False

    version = deps['@clerk/nextjs']
    result.meta['clerk_version'] = version
    major = major_version(version)

    if major is None:
        result.add_issue('warning', 'package.json', f'Could not parse @clerk/nextjs version: {version}')
    elif major < 5:
        result.add_issue('error', 'package.json',
                         f'@clerk/nextjs {major}.x detected. Use the latest major',
                         fix='bun add @clerk/nextjs@latest')
    elif major == 5:
        result.add_issue('warning', 'package.json',
                         f'@clerk/nextjs {version} detected. Consider upgrading to the latest major',
                         fix='bun add @clerk/nextjs@latest')
    else:
        result.add_passed(f'@clerk/nextjs version: {version}')
    return True


def next_major(root: Path) -> int | None:
    version = read_package_deps(root).get('next')
    return major_version(version) if version else None


def check_clerk_proxy(root: Path, result: ValidationResult) -> None:
    """middleware.ts is deprecated in Next.js 16; the Clerk handler belongs in proxy.ts."""
    major = next_major(root)
    locations = [root, root / 'src']
    proxy_found = False

    for loc in locations:
        if (loc / 'proxy.ts').exists():
            proxy_found = True
            result.add_passed(f'Found proxy.ts in {loc.relative_to(root) if loc != root else "root"}')

        for name in ('middleware.ts', 'middleware.js'):
            path = loc / name
            if not path.exists():
                continue
            content = read_text(path) or ''
            if 'clerk' not in content.lower() and 'authMiddleware' not in content:
                continue
            if major is not None and major >= 16:
                result.add_issue('error', str(path.relative_to(root)),
                                 f'{name} with Clerk is deprecated in Next.js 16',
                                 fix='Rename to proxy.ts and export clerkMiddleware()')
            else:
                result.add_issue('warning', str(path.relative_to(root)),
                                 f'{name} with Clerk: move to proxy.ts when upgrading to Next.js 16',
                                 fix='Rename to proxy.ts on Next.js 16')

    if not proxy_found:
        result.add_passed('No proxy.ts (add one to protect routes with clerkMiddleware)')


def check_clerk_provider(root: Path, result: ValidationResult) -> None:
    layouts = [root / 'app' / 'layout.tsx', root / 'src' / 'app' / 'layout.tsx']
    existing = [layout for layout in layouts if layout.exists()]

    for pages_app in (root / 'pages' / '_app.tsx', root / 'src' / 'pages' / '_app.tsx'):
        content = read_text(pages_app) if pages_app.exists() else None
        if content and 'ClerkProvider' in content:
            result.add_issue('error', str(pages_app.relative_to(root)),
                             'ClerkProvider in _app.tsx is a Pages Router pattern',
                             fix='Move <ClerkProvider> into app/layout.tsx')

    if not existing:
        return

    for layout in existing:
        content = read_text(layout) or ''
        if 'ClerkProvider' in content:
            result.add_passed(f'ClerkProvider wraps the app in {layout.relative_to(root)}')
            return

    result.add_issue('warning', str(existing[0].relative_to(root)),
                     'ClerkProvider not found in the root layout',
                     fix='Wrap the app in <ClerkProvider> inside app/layout.tsx')


CLERK_DEPRECATED = [
    ('authMiddleware', 'error', 'authMiddleware() is deprecated', 'Use clerkMiddleware() in proxy.ts'),
    ('withClerkMiddleware', 'error', 'withClerkMiddleware is deprecated', 'Use clerkMiddleware() in proxy.ts'),
]


CLERK_ENTRY_FILES = ['middleware.ts', 'middleware.js', 'proxy.ts', 'src/middleware.ts', 'src/middleware.js', 'src/proxy.ts']


def check_clerk_deprecated_patterns(root: Path, result: ValidationResult) -> None:
    entry_files = (root / name for name in CLERK_ENTRY_FILES if (root / name).exists())
    for file_path in dict.fromkeys(chain(entry_files, source_files(root, CLERK_SOURCE_DIRS))):
        content = read_text(file_path)
        if content is None or 'clerk' not in content.lower():
            continue
        rel_path = str(file_path.relative_to(root))

        for needle, severity, message, fix in CLERK_DEPRECATED:
            if needle in content:
                result.add_issue(severity, rel_path, message,
                                 line=first_line_with(content, needle), fix=fix)

        if re.search(r'import\s*\{[^}]*\bgetAuth\b[^}]*\}\s*from\s*[\'"]@clerk/nextjs/server[\'"]', content):
            result.add_issue('warning', rel_path,
                             'getAuth() is the Pages Router helper',
                             line=first_line_with(content, 'getAuth'),
                             fix='Use await auth() from @clerk/nextjs/server in the App Router')

        if re.search(r'import\s*\{[^}]*\bcurrentUser\b[^}]*\}\s*from\s*[\'"]@clerk/nextjs[\'"]', content):
            result.add_issue('warning', rel_path,
                             'currentUser imported from @clerk/nextjs (server helper)',
                             line=first_line_with(content, 'currentUser'),
                             fix='Import currentUser from @clerk/nextjs/server')


def env_variable_names(root: Path) -> set[str]:
    """Names (never values) defined in the project's env files."""
    names: set[str] = set()
    for file_name in CLERK_ENV_FILES:
        path = root / file_name
        if not path.exists():
            continue
        content = read_text(path) or ''
        for line in content.split('\n'):
            match = re.match(r'\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=', line)
            if match:
                names.add(match.group(1))
    return names


def check_clerk_env(root: Path, result: ValidationResult) -> None:
    defined = env_variable_names(root)
    for name in CLERK_REQUIRED_ENV:
        if name in defined:
            result.add_passed(f'{name} is defined in an env file')
        else:
            result.add_issue('warning', '.env',
                             f'{name} not found in .env files (fine if the platform injects it)',
                             fix=f'Add {name}=... to .env.local and .env.example')


def validate_clerk(root: Path, result: ValidationResult) -> None:
    has_nextjs = check_clerk_package_version(root, result)
    if has_nextjs:
        check_clerk_proxy(root, result)
        check_clerk_provider(root, result)
        check_clerk_env(root, result)
    check_clerk_deprecated_patterns(root, result)


# --------------------------------------------------------------------------- #
# Next.js
# --------------------------------------------------------------------------- #

def check_next_version(root: Path, result: ValidationResult) -> bool:
    """Check if Next.js v16+ is installed."""
    pkg = load_package_json(root, result)
    if pkg is None:
        return False

    deps = all_dependencies(pkg)

    if 'next' not in deps:
        result.add_issue('error', 'package.json', 'next not found in dependencies',
                         fix='bun add next@latest')
        return False

    version = deps['next']
    result.meta['next_version'] = version

    version_match = re.search(r'(\d+)\.', version)
    if version_match:
        major = int(version_match.group(1))
        if major < 16:
            result.add_issue('error', 'package.json', f'Next.js {major} detected. Must use v16+',
                             fix='bun add next@latest')
            return False
        result.add_passed(f'Next.js version: {version}')
        return True

    result.add_issue('warning', 'package.json', f'Could not parse Next.js version: {version}')
    return True


def check_next_directory_structure(root: Path, result: ValidationResult) -> None:
    app_dir = root / 'app'
    src_app_dir = root / 'src' / 'app'
    pages_dir = root / 'pages'
    src_pages_dir = root / 'src' / 'pages'

    has_app = app_dir.exists() or src_app_dir.exists()
    has_pages = pages_dir.exists() or src_pages_dir.exists()

    if has_app:
        result.add_passed('Using app/ directory (App Router)')
    else:
        result.add_issue('error', 'Directory Structure',
                         'No app/ directory found - App Router required for Next.js 16',
                         fix='Create app/ directory with layout.tsx and page.tsx')

    if has_pages:
        # API routes alone are acceptable; page files are not.
        pages_path = pages_dir if pages_dir.exists() else src_pages_dir
        has_page_files = any(
            'api' not in str(f)
            for pattern in ('*.tsx', '*.jsx')
            for f in pages_path.rglob(pattern)
        )

        if has_page_files:
            result.add_issue('error', 'pages/',
                             'Found pages/ directory with page files - migrate to App Router',
                             fix='Move pages to app/ directory, use Server Components')
        else:
            result.add_passed('pages/ only contains API routes (acceptable)')


def check_next_proxy_middleware(root: Path, result: ValidationResult) -> None:
    proxy_found = False
    middleware_found = False

    for loc in [root, root / 'src']:
        if (loc / 'proxy.ts').exists():
            proxy_found = True
            result.add_passed(f'Found proxy.ts in {loc.relative_to(root) if loc != root else "root"}')

        for name in ('middleware.ts', 'middleware.js'):
            if (loc / name).exists():
                middleware_found = True
                result.add_issue('error', str((loc / name).relative_to(root)),
                                 f'{name} is deprecated in Next.js 16',
                                 fix='Rename to proxy.ts and update to use createProxy()')

    if not proxy_found and not middleware_found:
        result.add_passed('No middleware/proxy (optional)')


NEXT_DEPRECATED_PATTERNS = {
    'getServerSideProps': 'Use Server Components with async/await',
    'getStaticProps': 'Use Server Components with generateStaticParams',
    'getInitialProps': 'Use Server Components',
    "from 'next/router'": 'Use next/navigation instead',
    'from "next/router"': 'Use next/navigation instead',
}


def check_next_deprecated_patterns(root: Path, result: ValidationResult) -> None:
    search_dirs = ['app', 'src/app', 'pages', 'src/pages', 'components', 'src/components']

    for file_path in source_files(root, search_dirs):
        content = read_text(file_path)
        if content is None:
            continue
        rel_path = file_path.relative_to(root)

        for pattern, fix in NEXT_DEPRECATED_PATTERNS.items():
            if pattern in content:
                result.add_issue('error', str(rel_path), f'Found deprecated pattern: {pattern}',
                                 line=first_line_with(content, pattern), fix=fix)


def check_next_config_file(root: Path, result: ValidationResult) -> None:
    if (root / 'next.config.ts').exists() or (root / 'next.config.mts').exists():
        result.add_passed('Using TypeScript config (next.config.ts)')
    elif (root / 'next.config.js').exists() or (root / 'next.config.mjs').exists():
        result.add_issue('warning', 'next.config.js',
                         'Consider using next.config.ts for type safety',
                         fix='Rename to next.config.ts and add types')
    else:
        result.add_passed('No next.config (using defaults)')


def check_next_use_cache(root: Path, result: ValidationResult) -> None:
    for file_path in source_files(root, ['app', 'src/app'], ('*.tsx',)):
        content = read_text(file_path)
        if content and ("'use cache'" in content or '"use cache"' in content):
            result.add_passed('Using Cache Components (use cache)')
            return

    result.add_issue('warning', 'Cache Components',
                     "Consider using 'use cache' for cacheable pages",
                     fix="Add 'use cache' directive to cacheable Server Components")


def validate_nextjs(root: Path, result: ValidationResult) -> None:
    check_next_version(root, result)
    check_next_directory_structure(root, result)
    check_next_proxy_middleware(root, result)
    check_next_deprecated_patterns(root, result)
    check_next_config_file(root, result)
    check_next_use_cache(root, result)


# --------------------------------------------------------------------------- #
# Tailwind
# --------------------------------------------------------------------------- #

def check_tailwind_version(root: Path, result: ValidationResult) -> bool:
    """Check if tailwindcss v4+ is installed."""
    pkg = load_package_json(root, result)
    if pkg is None:
        return False

    deps = all_dependencies(pkg)

    if 'tailwindcss' not in deps:
        result.add_issue('error', 'package.json', 'tailwindcss not found in dependencies',
                         fix='bun add tailwindcss@latest @tailwindcss/postcss')
        return False

    version = deps['tailwindcss']
    result.meta['tailwind_version'] = version

    version_match = re.search(r'(\d+)\.', version)
    if version_match:
        major = int(version_match.group(1))
        if major < 4:
            result.add_issue('error', 'package.json',
                             f'Tailwind v3 detected ({version}). Must use v4+',
                             fix='bun remove tailwindcss && bun add tailwindcss@latest @tailwindcss/postcss')
            return False
        result.add_passed(f'Tailwind version: {version}')
        return True

    result.add_issue('warning', 'package.json', f'Could not parse Tailwind version: {version}')
    return True


TAILWIND_V3_CONFIGS = [
    'tailwind.config.js', 'tailwind.config.ts', 'tailwind.config.mjs', 'tailwind.config.cjs',
]


def check_tailwind_config_files(root: Path, result: ValidationResult) -> None:
    for config in TAILWIND_V3_CONFIGS:
        if (root / config).exists():
            result.add_issue('error', config,
                             f'Found {config} - this is a v3 pattern. Migrate to @theme in CSS',
                             fix=f'Delete {config} and move configuration to @theme block in your CSS')


def check_tailwind_postcss(root: Path, result: ValidationResult) -> None:
    for config_name in ('postcss.config.js', 'postcss.config.mjs', 'postcss.config.cjs'):
        config_path = root / config_name
        if not config_path.exists():
            continue

        with open(config_path) as f:
            content = f.read()

        if 'tailwindcss:' in content or "'tailwindcss'" in content or '"tailwindcss"' in content:
            if '@tailwindcss/postcss' not in content:
                result.add_issue('warning', config_name,
                                 'Using old tailwindcss PostCSS plugin. Use @tailwindcss/postcss for v4',
                                 fix="Replace 'tailwindcss' with '@tailwindcss/postcss' in PostCSS config")

        if 'autoprefixer' in content:
            result.add_issue('warning', config_name,
                             'autoprefixer is not needed with @tailwindcss/postcss (built-in)',
                             fix='Remove autoprefixer from PostCSS plugins')

        if '@tailwindcss/postcss' in content:
            result.add_passed('PostCSS config uses @tailwindcss/postcss')
        return

    result.add_passed('No PostCSS config (may be using framework built-in)')


def find_css_files(root: Path) -> list[Path]:
    css_files: list[Path] = []

    for dir_name in ['src', 'app', 'styles', 'css', 'public']:
        dir_path = root / dir_name
        if dir_path.exists():
            css_files.extend(dir_path.rglob('*.css'))

    css_files.extend(root.glob('*.css'))

    exclude_patterns = ['node_modules', 'dist', 'build', '.next', '.output', 'out']
    return [f for f in css_files if not any(p in str(f) for p in exclude_patterns)]


def check_tailwind_css_files(root: Path, result: ValidationResult) -> None:
    css_files = find_css_files(root)

    if not css_files:
        result.add_issue('warning', 'CSS', 'No CSS files found in common locations')
        return

    found_v4_import = False
    found_theme_block = False

    for css_file in css_files:
        rel_path = css_file.relative_to(root)

        with open(css_file) as f:
            lines = f.readlines()

        for i, line in enumerate(lines, 1):
            if '@tailwind' in line and not line.strip().startswith('/*'):
                result.add_issue('error', str(rel_path), 'Found @tailwind directive (v3 pattern)',
                                 line=i,
                                 fix='Replace @tailwind directives with @import "tailwindcss"')

            if '@import' in line and 'tailwindcss' in line:
                found_v4_import = True
                result.add_passed(f'Found @import "tailwindcss" in {rel_path}')

            if '@theme' in line:
                found_theme_block = True

        content = ''.join(lines)
        if '@theme' in content:
            theme_match = re.search(r'@theme\s*\{([^}]*)\}', content, re.DOTALL)
            if theme_match:
                css_vars = re.findall(r'--[\w-]+:', theme_match.group(1))
                result.add_passed(
                    f'Found @theme block with {len(css_vars)} custom properties in {rel_path}'
                )

    if not found_v4_import:
        result.add_issue('error', 'CSS', 'No @import "tailwindcss" found - required for v4',
                         fix='Add @import "tailwindcss"; to your main CSS file')

    if not found_theme_block:
        result.add_issue('warning', 'CSS',
                         'No @theme block found - consider adding custom theme configuration',
                         fix='Add @theme { } block after @import "tailwindcss" for custom properties')


def validate_tailwind(root: Path, result: ValidationResult) -> None:
    check_tailwind_version(root, result)
    check_tailwind_config_files(root, result)
    check_tailwind_postcss(root, result)
    check_tailwind_css_files(root, result)


# --------------------------------------------------------------------------- #
# Stack registry, detection, reporting
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Stack:
    name: str
    title: str
    success: str
    run: Callable[[Path, ValidationResult], None]
    detect: Callable[[Path], bool]
    version_line: Callable[[ValidationResult], str | None]
    json_keys: tuple[str, ...]


def _strip_range(version: str) -> str:
    return version.lstrip('^~>=')


def _detect_biome(root: Path) -> bool:
    return (
        '@biomejs/biome' in read_package_deps(root)
        or (root / 'biome.json').exists()
        or (root / 'biome.jsonc').exists()
    )


def _detect_bun(root: Path) -> bool:
    return (
        (root / 'bun.lock').exists()
        or (root / 'bun.lockb').exists()
        or (root / 'bunfig.toml').exists()
    )


def _detect_clerk(root: Path) -> bool:
    return any(name.startswith('@clerk/') for name in read_package_deps(root))


def _detect_nextjs(root: Path) -> bool:
    return 'next' in read_package_deps(root)


def _detect_tailwind(root: Path) -> bool:
    return 'tailwindcss' in read_package_deps(root)


def _version_line(label: str, key: str) -> Callable[[ValidationResult], str | None]:
    def line(result: ValidationResult) -> str | None:
        value = result.meta.get(key)
        return f'{label}{_strip_range(value)}' if value else None
    return line


STACKS: dict[str, Stack] = {
    'biome': Stack(
        'biome', 'Biome 2.3+ Validation Report',
        'Result: All checks passed! Biome configured correctly.',
        validate_biome, _detect_biome,
        _version_line('Package Version: @biomejs/biome@', 'biome_version'),
        ('biome_version', 'schema_version'),
    ),
    'bun': Stack(
        'bun', 'Bun Workspace Validation Report',
        'Result: All checks passed! Bun workspace configured correctly.',
        validate_bun, _detect_bun,
        lambda result: f'Bun Version: {result.meta["bun_version"]}' if result.meta.get('bun_version') else None,
        ('bun_version',),
    ),
    'clerk': Stack(
        'clerk', 'Clerk Validation Report',
        'Result: All checks passed! Clerk configured correctly.',
        validate_clerk, _detect_clerk,
        _version_line('Package Version: @clerk/nextjs@', 'clerk_version'),
        ('clerk_version',),
    ),
    'nextjs': Stack(
        'nextjs', 'Next.js 16 Validation Report',
        'Result: All checks passed! Project is using Next.js 16 correctly.',
        validate_nextjs, _detect_nextjs,
        _version_line('Package Version: next@', 'next_version'),
        ('next_version',),
    ),
    'tailwind': Stack(
        'tailwind', 'Tailwind v4 Validation Report',
        'Result: All checks passed! Project is using Tailwind v4 correctly.',
        validate_tailwind, _detect_tailwind,
        _version_line('Package Version: tailwindcss@', 'tailwind_version'),
        ('tailwind_version',),
    ),
}


def detect_stacks(root: Path) -> list[str]:
    return [name for name, stack in STACKS.items() if stack.detect(root)]


def print_report(stack: Stack, result: ValidationResult, verbose: bool = False) -> None:
    print('\n' + '=' * 50)
    print(f'  {stack.title}')
    print('=' * 50 + '\n')

    version_line = stack.version_line(result)
    if version_line:
        print(version_line)
    if stack.name == 'biome' and result.meta.get('schema_version'):
        print(f"Schema Version: {result.meta['schema_version']}")
    if version_line or (stack.name == 'biome' and result.meta.get('schema_version')):
        print()

    if verbose and result.passed:
        print('Passed Checks:')
        for msg in result.passed:
            print(f'  [PASS] {msg}')
        print()

    errors = [i for i in result.issues if i.severity == 'error']
    warnings = [i for i in result.issues if i.severity == 'warning']

    for heading, tag, group in (('Errors:', 'ERROR', errors), ('Warnings:', 'WARN', warnings)):
        if not group:
            continue
        print(heading)
        pad = ' ' * (len(tag) + 5)
        for issue in group:
            line_info = f':{issue.line}' if issue.line else ''
            print(f'  [{tag}] {issue.file}{line_info}')
            print(f'{pad}{issue.message}')
            if issue.fix:
                print(f'{pad}Fix: {issue.fix}')
        print()

    print('-' * 50)
    if not errors and not warnings:
        print(stack.success)
    else:
        print(f'Result: {len(errors)} error(s), {len(warnings)} warning(s)')
        if stack.name == 'tailwind' and errors:
            print('\nAction required: Fix errors before proceeding with Tailwind work.')
    print()


def result_to_dict(stack: Stack, result: ValidationResult) -> dict:
    output: dict = {key: result.meta.get(key) for key in stack.json_keys}
    output['passed'] = result.passed
    output['issues'] = [
        {
            'severity': i.severity,
            'file': i.file,
            'line': i.line,
            'message': i.message,
            'fix': i.fix,
        }
        for i in result.issues
    ]
    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Validate Biome, Bun, Clerk, Next.js 16 and Tailwind v4 configuration'
    )
    parser.add_argument('--root', '-r', type=str, default='.', help='Project root directory')
    parser.add_argument(
        '--stack', '-s', action='append', choices=[*STACKS, 'all'],
        help='Stack to validate (repeatable). Default: auto-detect from the project'
    )
    parser.add_argument('--strict', action='store_true', help='Treat warnings as errors')
    parser.add_argument('--ci', action='store_true', help='CI mode: exit with non-zero on errors')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show passed checks')
    parser.add_argument('--suggest-fixes', action='store_true', default=True,
                        help='Show fix suggestions (always on; accepted for compatibility)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()
    root = Path(args.root).resolve()

    if not root.exists():
        print(f'Error: Directory not found: {root}')
        sys.exit(1)

    if args.stack and 'all' in args.stack:
        selected = list(STACKS)
    elif args.stack:
        selected = list(dict.fromkeys(args.stack))
    else:
        selected = detect_stacks(root)
        if not selected:
            print('Error: no supported stack detected (Biome, Bun, Clerk, Next.js, Tailwind). '
                  'Pass --stack <name> to validate one explicitly.')
            sys.exit(1)

    results: dict[str, ValidationResult] = {}
    for name in selected:
        result = ValidationResult()
        STACKS[name].run(root, result)
        results[name] = result

    if args.json:
        if len(selected) == 1:
            output = result_to_dict(STACKS[selected[0]], results[selected[0]])
        else:
            output = {name: result_to_dict(STACKS[name], results[name]) for name in selected}
        print(json.dumps(output, indent=2))
    else:
        for name in selected:
            print_report(STACKS[name], results[name], verbose=args.verbose)

    if args.ci or args.strict:
        if any(r.has_errors for r in results.values()):
            sys.exit(1)
        if args.strict and any(r.has_warnings for r in results.values()):
            sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
