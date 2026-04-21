#!/usr/bin/env python3
"""
Tailwind v4 Validator

Validates that a project uses Tailwind CSS v4 with proper CSS-first configuration.
Detects and flags Tailwind v3 patterns that should be migrated.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import NamedTuple


class Issue(NamedTuple):
    severity: str  # 'error' | 'warning'
    file: str
    line: int | None
    message: str
    fix: str | None


class ValidationResult:
    def __init__(self):
        self.issues: list[Issue] = []
        self.passed: list[str] = []
        self.tailwind_version: str | None = None

    def add_issue(self, severity: str, file: str, message: str, line: int | None = None, fix: str | None = None):
        self.issues.append(Issue(severity, file, line, message, fix))

    def add_passed(self, message: str):
        self.passed.append(message)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == 'error' for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == 'warning' for i in self.issues)


def find_package_json(root: Path) -> Path | None:
    """Find package.json in project root."""
    pkg = root / 'package.json'
    return pkg if pkg.exists() else None


def check_tailwind_version(root: Path, result: ValidationResult) -> bool:
    """Check if tailwindcss v4+ is installed."""
    pkg_path = find_package_json(root)
    if not pkg_path:
        result.add_issue('error', 'package.json', 'package.json not found')
        return False

    try:
        with open(pkg_path) as f:
            pkg = json.load(f)
    except json.JSONDecodeError:
        result.add_issue('error', 'package.json', 'Invalid JSON in package.json')
        return False

    # Check dependencies and devDependencies
    deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}

    if 'tailwindcss' not in deps:
        result.add_issue('error', 'package.json', 'tailwindcss not found in dependencies',
                        fix='bun add tailwindcss@latest @tailwindcss/postcss')
        return False

    version = deps['tailwindcss']
    result.tailwind_version = version

    # Parse version (handle ^, ~, >=, etc.)
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

    # If we can't parse, assume it might be okay but warn
    result.add_issue('warning', 'package.json', f'Could not parse Tailwind version: {version}')
    return True


def check_config_files(root: Path, result: ValidationResult):
    """Check for deprecated v3 config files."""
    v3_configs = [
        'tailwind.config.js',
        'tailwind.config.ts',
        'tailwind.config.mjs',
        'tailwind.config.cjs',
    ]

    for config in v3_configs:
        config_path = root / config
        if config_path.exists():
            result.add_issue('error', config,
                           f'Found {config} - this is a v3 pattern. Migrate to @theme in CSS',
                           fix=f'Delete {config} and move configuration to @theme block in your CSS')


def check_postcss_config(root: Path, result: ValidationResult):
    """Check PostCSS configuration for v4 compatibility."""
    postcss_files = [
        'postcss.config.js',
        'postcss.config.mjs',
        'postcss.config.cjs',
    ]

    for config_name in postcss_files:
        config_path = root / config_name
        if config_path.exists():
            with open(config_path) as f:
                content = f.read()

            # Check for v3 patterns
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
                result.add_passed(f'PostCSS config uses @tailwindcss/postcss')
            return

    # No PostCSS config found - might be using Vite or Next.js built-in
    result.add_passed('No PostCSS config (may be using framework built-in)')


def find_css_files(root: Path) -> list[Path]:
    """Find all CSS files in the project."""
    css_files = []

    # Common directories to search
    search_dirs = ['src', 'app', 'styles', 'css', 'public']

    for dir_name in search_dirs:
        dir_path = root / dir_name
        if dir_path.exists():
            css_files.extend(dir_path.rglob('*.css'))

    # Also check root level
    css_files.extend(root.glob('*.css'))

    # Filter out node_modules, dist, build, .next
    exclude_patterns = ['node_modules', 'dist', 'build', '.next', '.output', 'out']
    css_files = [f for f in css_files if not any(p in str(f) for p in exclude_patterns)]

    return css_files


def check_css_files(root: Path, result: ValidationResult):
    """Check CSS files for v3 vs v4 patterns."""
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
            # Check for v3 @tailwind directives
            if '@tailwind' in line and not line.strip().startswith('/*'):
                result.add_issue('error', str(rel_path),
                               f'Found @tailwind directive (v3 pattern)',
                               line=i,
                               fix='Replace @tailwind directives with @import "tailwindcss"')

            # Check for v4 @import
            if '@import' in line and 'tailwindcss' in line:
                found_v4_import = True
                result.add_passed(f'Found @import "tailwindcss" in {rel_path}')

            # Check for @theme block
            if '@theme' in line:
                found_theme_block = True

        # Check for @theme block content
        content = ''.join(lines)
        if '@theme' in content:
            theme_match = re.search(r'@theme\s*\{([^}]*)\}', content, re.DOTALL)
            if theme_match:
                theme_content = theme_match.group(1)
                css_vars = re.findall(r'--[\w-]+:', theme_content)
                result.add_passed(f'Found @theme block with {len(css_vars)} custom properties in {rel_path}')

    if not found_v4_import:
        result.add_issue('error', 'CSS',
                        'No @import "tailwindcss" found - required for v4',
                        fix='Add @import "tailwindcss"; to your main CSS file')

    if not found_theme_block:
        result.add_issue('warning', 'CSS',
                        'No @theme block found - consider adding custom theme configuration',
                        fix='Add @theme { } block after @import "tailwindcss" for custom properties')


def check_for_v3_class_patterns(root: Path, result: ValidationResult):
    """Check for class patterns that changed between v3 and v4."""
    # These are less critical but worth flagging
    # v4 changed some default behaviors
    pass  # Can be expanded for specific pattern checks


def print_report(result: ValidationResult, verbose: bool = False):
    """Print validation report."""
    print("\n" + "=" * 50)
    print("  Tailwind v4 Validation Report")
    print("=" * 50 + "\n")

    if result.tailwind_version:
        status = "v4+" if not result.has_errors else "v3 (needs upgrade)"
        print(f"Package Version: tailwindcss@{result.tailwind_version.lstrip('^~>=')}")
        print()

    # Print passed checks
    if verbose and result.passed:
        print("Passed Checks:")
        for msg in result.passed:
            print(f"  [PASS] {msg}")
        print()

    # Print issues
    if result.issues:
        errors = [i for i in result.issues if i.severity == 'error']
        warnings = [i for i in result.issues if i.severity == 'warning']

        if errors:
            print("Errors:")
            for issue in errors:
                line_info = f":{issue.line}" if issue.line else ""
                print(f"  [ERROR] {issue.file}{line_info}")
                print(f"          {issue.message}")
                if issue.fix:
                    print(f"          Fix: {issue.fix}")
            print()

        if warnings:
            print("Warnings:")
            for issue in warnings:
                line_info = f":{issue.line}" if issue.line else ""
                print(f"  [WARN] {issue.file}{line_info}")
                print(f"         {issue.message}")
                if issue.fix:
                    print(f"         Fix: {issue.fix}")
            print()

    # Summary
    print("-" * 50)
    error_count = len([i for i in result.issues if i.severity == 'error'])
    warning_count = len([i for i in result.issues if i.severity == 'warning'])

    if error_count == 0 and warning_count == 0:
        print("Result: All checks passed! Project is using Tailwind v4 correctly.")
    else:
        print(f"Result: {error_count} error(s), {warning_count} warning(s)")
        if error_count > 0:
            print("\nAction required: Fix errors before proceeding with Tailwind work.")

    print()


def main():
    parser = argparse.ArgumentParser(
        description='Validate Tailwind CSS v4 configuration'
    )
    parser.add_argument(
        '--root', '-r',
        type=str,
        default='.',
        help='Project root directory (default: current directory)'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat warnings as errors'
    )
    parser.add_argument(
        '--ci',
        action='store_true',
        help='CI mode: exit with non-zero code on errors'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show passed checks'
    )
    parser.add_argument(
        '--suggest-fixes',
        action='store_true',
        help='Show fix suggestions (default: true)',
        default=True
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )

    args = parser.parse_args()
    root = Path(args.root).resolve()

    if not root.exists():
        print(f"Error: Directory not found: {root}")
        sys.exit(1)

    result = ValidationResult()

    # Run all checks
    check_tailwind_version(root, result)
    check_config_files(root, result)
    check_postcss_config(root, result)
    check_css_files(root, result)

    # Output
    if args.json:
        output = {
            'tailwind_version': result.tailwind_version,
            'passed': result.passed,
            'issues': [
                {
                    'severity': i.severity,
                    'file': i.file,
                    'line': i.line,
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
        if args.strict and result.has_warnings:
            sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
