#!/usr/bin/env python3
"""
Bun Workspace Validator

Validates Bun workspace configuration and detects common monorepo issues.
Ensures Bun 1.3+ patterns and proper workspace isolation.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


class Issue(NamedTuple):
    severity: str
    file: str
    line: int | None
    message: str
    fix: str | None


class ValidationResult:
    def __init__(self):
        self.issues: list[Issue] = []
        self.passed: list[str] = []
        self.bun_version: str | None = None

    def add_issue(self, severity: str, file: str, message: str, line: int | None = None, fix: str | None = None):
        self.issues.append(Issue(severity, file, line, message, fix))

    def add_passed(self, message: str):
        self.passed.append(message)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == 'error' for i in self.issues)


def check_bun_version(result: ValidationResult) -> bool:
    """Check if Bun 1.3+ is installed."""
    try:
        output = subprocess.run(['bun', '--version'], capture_output=True, text=True)
        if output.returncode != 0:
            result.add_issue('error', 'bun', 'Bun not installed',
                           fix='Install Bun: curl -fsSL https://bun.sh/install | bash')
            return False

        version = output.stdout.strip()
        result.bun_version = version

        # Parse version
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


def check_root_package_json(root: Path, result: ValidationResult) -> dict | None:
    """Check root package.json configuration."""
    pkg_path = root / 'package.json'
    if not pkg_path.exists():
        result.add_issue('error', 'package.json', 'Root package.json not found',
                        fix='bun init')
        return None

    try:
        with open(pkg_path) as f:
            pkg = json.load(f)
    except json.JSONDecodeError:
        result.add_issue('error', 'package.json', 'Invalid JSON')
        return None

    # Check private
    if not pkg.get('private'):
        result.add_issue('error', 'package.json',
                        'Root package.json should have "private": true',
                        fix='Add "private": true to package.json')

    # Check workspaces
    workspaces = pkg.get('workspaces')
    if not workspaces:
        result.add_issue('warning', 'package.json',
                        'No workspaces defined (not a monorepo?)')
    else:
        if isinstance(workspaces, list):
            result.add_passed(f'Workspaces defined: {workspaces}')
        elif isinstance(workspaces, dict) and 'packages' in workspaces:
            result.add_passed(f'Workspaces defined: {workspaces["packages"]}')

    # Check for dependencies in root (usually bad practice)
    if pkg.get('dependencies'):
        result.add_issue('warning', 'package.json',
                        'Root package.json has dependencies (consider moving to workspaces)',
                        fix='Move dependencies to individual workspace package.json files')

    # Check for catalog (Bun 1.3+)
    if pkg.get('catalog'):
        catalog = pkg['catalog']
        result.add_passed(f'Dependency catalog found with {len(catalog)} entries')
    else:
        result.add_issue('warning', 'package.json',
                        'No dependency catalog found (recommended for Bun 1.3+)',
                        fix='Add "catalog": {} with shared dependency versions')

    return pkg


def find_workspaces(root: Path, pkg: dict) -> list[Path]:
    """Find all workspace directories."""
    workspaces = pkg.get('workspaces', [])
    if isinstance(workspaces, dict):
        workspaces = workspaces.get('packages', [])

    workspace_paths = []
    for pattern in workspaces:
        # Convert glob to actual paths
        if pattern.endswith('/*'):
            base = pattern[:-2]
            base_path = root / base
            if base_path.exists():
                for child in base_path.iterdir():
                    if child.is_dir() and (child / 'package.json').exists():
                        workspace_paths.append(child)
        else:
            ws_path = root / pattern
            if ws_path.exists() and (ws_path / 'package.json').exists():
                workspace_paths.append(ws_path)

    return workspace_paths


def check_workspace_structure(root: Path, workspaces: list[Path], result: ValidationResult):
    """Check workspace structure and configurations."""
    for ws_path in workspaces:
        rel_path = ws_path.relative_to(root)

        # Check for lockfile in workspace (bad)
        if (ws_path / 'bun.lockb').exists():
            result.add_issue('error', str(rel_path / 'bun.lockb'),
                           'Lockfile found in workspace - should only be at root',
                           fix=f'rm {rel_path}/bun.lockb && bun install (from root)')
        else:
            result.add_passed(f'{rel_path} - no lockfile (correct)')

        # Check workspace package.json
        pkg_path = ws_path / 'package.json'
        try:
            with open(pkg_path) as f:
                pkg = json.load(f)

            # Check for name
            if not pkg.get('name'):
                result.add_issue('error', str(rel_path / 'package.json'),
                               'Workspace package.json missing name')

            # Check dependencies for workspace protocol
            check_workspace_dependencies(root, rel_path, pkg, result)

        except json.JSONDecodeError:
            result.add_issue('error', str(rel_path / 'package.json'), 'Invalid JSON')


def check_workspace_dependencies(root: Path, rel_path: Path, pkg: dict, result: ValidationResult):
    """Check if workspace dependencies use workspace: protocol."""
    # Get all local package names
    root_pkg_path = root / 'package.json'
    local_packages = set()

    if root_pkg_path.exists():
        try:
            with open(root_pkg_path) as f:
                root_pkg = json.load(f)

            workspaces = root_pkg.get('workspaces', [])
            if isinstance(workspaces, dict):
                workspaces = workspaces.get('packages', [])

            for pattern in workspaces:
                if pattern.endswith('/*'):
                    base_path = root / pattern[:-2]
                    if base_path.exists():
                        for child in base_path.iterdir():
                            child_pkg = child / 'package.json'
                            if child_pkg.exists():
                                try:
                                    with open(child_pkg) as f:
                                        cp = json.load(f)
                                        if cp.get('name'):
                                            local_packages.add(cp['name'])
                                except:
                                    pass
        except:
            pass

    # Check dependencies
    all_deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}

    for dep_name, dep_version in all_deps.items():
        if dep_name in local_packages:
            if not dep_version.startswith('workspace:'):
                result.add_issue('error', str(rel_path / 'package.json'),
                               f'Local package {dep_name} should use workspace: protocol',
                               fix=f'Change "{dep_name}": "{dep_version}" to "{dep_name}": "workspace:*"')

        # Check for catalog: usage (Bun 1.3+)
        if dep_version == 'catalog:':
            result.add_passed(f'{rel_path}: {dep_name} uses catalog')


def check_single_lockfile(root: Path, result: ValidationResult):
    """Ensure there's only one lockfile at root."""
    root_lockfile = root / 'bun.lockb'

    if not root_lockfile.exists():
        result.add_issue('warning', 'bun.lockb',
                        'No bun.lockb at root (run bun install)',
                        fix='bun install')
        return

    result.add_passed('Single lockfile at root')

    # Check for other lockfiles
    other_lockfiles = []
    for lockfile in root.rglob('bun.lockb'):
        if lockfile != root_lockfile and 'node_modules' not in str(lockfile):
            other_lockfiles.append(lockfile)

    if other_lockfiles:
        for lf in other_lockfiles:
            rel_path = lf.relative_to(root)
            result.add_issue('error', str(rel_path),
                           'Extra lockfile found - should only be at root',
                           fix=f'rm {rel_path}')


def print_report(result: ValidationResult, verbose: bool = False):
    """Print validation report."""
    print("\n" + "=" * 50)
    print("  Bun Workspace Validation Report")
    print("=" * 50 + "\n")

    if result.bun_version:
        print(f"Bun Version: {result.bun_version}")
        print()

    if verbose and result.passed:
        print("Passed Checks:")
        for msg in result.passed:
            print(f"  [PASS] {msg}")
        print()

    if result.issues:
        errors = [i for i in result.issues if i.severity == 'error']
        warnings = [i for i in result.issues if i.severity == 'warning']

        if errors:
            print("Errors:")
            for issue in errors:
                print(f"  [ERROR] {issue.file}")
                print(f"          {issue.message}")
                if issue.fix:
                    print(f"          Fix: {issue.fix}")
            print()

        if warnings:
            print("Warnings:")
            for issue in warnings:
                print(f"  [WARN] {issue.file}")
                print(f"         {issue.message}")
                if issue.fix:
                    print(f"         Fix: {issue.fix}")
            print()

    print("-" * 50)
    error_count = len([i for i in result.issues if i.severity == 'error'])
    warning_count = len([i for i in result.issues if i.severity == 'warning'])

    if error_count == 0 and warning_count == 0:
        print("Result: All checks passed! Bun workspace configured correctly.")
    else:
        print(f"Result: {error_count} error(s), {warning_count} warning(s)")

    print()


def main():
    parser = argparse.ArgumentParser(description='Validate Bun workspace configuration')
    parser.add_argument('--root', '-r', type=str, default='.', help='Project root directory')
    parser.add_argument('--strict', action='store_true', help='Treat warnings as errors')
    parser.add_argument('--ci', action='store_true', help='CI mode: exit with non-zero on errors')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show passed checks')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()
    root = Path(args.root).resolve()

    if not root.exists():
        print(f"Error: Directory not found: {root}")
        sys.exit(1)

    result = ValidationResult()

    # Run all checks
    check_bun_version(result)
    pkg = check_root_package_json(root, result)

    if pkg:
        workspaces = find_workspaces(root, pkg)
        if workspaces:
            check_workspace_structure(root, workspaces, result)
        check_single_lockfile(root, result)

    # Output
    if args.json:
        output = {
            'bun_version': result.bun_version,
            'passed': result.passed,
            'issues': [
                {
                    'severity': i.severity,
                    'file': i.file,
                    'message': i.message,
                    'fix': i.fix
                }
                for i in result.issues
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        print_report(result, verbose=args.verbose)

    # Exit code
    if args.ci or args.strict:
        if result.has_errors:
            sys.exit(1)
        if args.strict and any(i.severity == 'warning' for i in result.issues):
            sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
