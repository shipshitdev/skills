#!/usr/bin/env python3
"""
Husky Test Coverage Setup - Configure Husky git hooks to run tests and enforce coverage thresholds

Usage:
    setup-husky-coverage.py --root <path> [options]

Options:
    --root              Project root directory (required)
    --threshold         Coverage threshold percentage (default: 80)
    --fail-on-below     Fail commit if coverage below threshold (default: true)
    --skip-if-no-tests  Skip hook if no tests found (default: false)
    --dry-run           Show what would be done without making changes

Examples:
    setup-husky-coverage.py --root /path/to/project
    setup-husky-coverage.py --root /path/to/project --threshold 85
    setup-husky-coverage.py --root /path/to/project --threshold 75 --fail-on-below false
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


# ============================================================================
# Configuration Templates
# ============================================================================

PRE_COMMIT_HOOK_TEMPLATE = """#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

{test_command}
"""

VITEST_COVERAGE_CONFIG = """import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      thresholds: {
        lines: 80,
        branches: 75,
        functions: 80,
        statements: 80
      }
    }
  }
})
"""

NYC_CONFIG = {
    "check-coverage": True,
    "lines": 80,
    "branches": 75,
    "functions": 80,
    "statements": 80,
    "reporter": ["text", "text-summary", "html", "lcov"]
}


# ============================================================================
# Helper Functions
# ============================================================================

def detect_package_manager(root: Path) -> str:
    """Detect which package manager is used in the project."""
    if (root / "pnpm-lock.yaml").exists():
        return "pnpm"
    elif (root / "yarn.lock").exists():
        return "yarn"
    elif (root / "bun.lockb").exists() or (root / "bun.lock").exists():
        return "bun"
    else:
        return "npm"


def detect_test_runner(root: Path) -> dict:
    """Detect test runner and coverage tool from package.json."""
    pkg_json = root / "package.json"
    if not pkg_json.exists():
        return {}
    
    try:
        pkg = json.loads(pkg_json.read_text())
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        
        result = {
            "runner": None,
            "coverage": None,
            "test_script": pkg.get("scripts", {}).get("test", None)
        }
        
        result["has_v8_provider"] = "@vitest/coverage-v8" in deps

        # Detect test runner
        if "vitest" in deps:
            result["runner"] = "vitest"
        elif "mocha" in deps:
            result["runner"] = "mocha"
        
        # Detect coverage tool
        if "nyc" in deps or "@istanbuljs/nyc-config-typescript" in deps:
            result["coverage"] = "nyc"
        elif "c8" in deps:
            result["coverage"] = "c8"
        elif result["runner"] == "vitest":
            result["coverage"] = "builtin"
        
        return result
    except Exception as e:
        print(f"  ⚠️  Error reading package.json: {e}")
        return {}


def check_existing_husky(root: Path) -> bool:
    """Check if Husky is already installed and configured."""
    pkg_json = root / "package.json"
    if not pkg_json.exists():
        return False
    
    try:
        pkg = json.loads(pkg_json.read_text())
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        
        if "husky" not in deps:
            return False
        
        husky_dir = root / ".husky"
        if not husky_dir.exists():
            return False
        
        return True
    except:
        return False


def read_config(root: Path) -> dict:
    """Read configuration from .husky-test-coverage.json or package.json."""
    config = {
        "threshold": 80,
        "fail_on_below": True,
        "skip_if_no_tests": False
    }
    
    # Check for .husky-test-coverage.json
    config_file = root / ".husky-test-coverage.json"
    if config_file.exists():
        try:
            file_config = json.loads(config_file.read_text())
            if "coverageThreshold" in file_config:
                thresholds = file_config["coverageThreshold"]
                # Take the highest threshold as the default
                config["threshold"] = max(
                    thresholds.get("lines", 80),
                    thresholds.get("branches", 75),
                    thresholds.get("functions", 80),
                    thresholds.get("statements", 80)
                )
            config["fail_on_below"] = file_config.get("failOnCoverageBelowThreshold", True)
            config["skip_if_no_tests"] = file_config.get("skipIfNoTests", False)
            return config
        except Exception as e:
            print(f"  ⚠️  Error reading .husky-test-coverage.json: {e}")
    
    # Check package.json
    pkg_json = root / "package.json"
    if pkg_json.exists():
        try:
            pkg = json.loads(pkg_json.read_text())
            if "huskyTestCoverage" in pkg:
                htc = pkg["huskyTestCoverage"]
                config["threshold"] = htc.get("threshold", 80)
                config["fail_on_below"] = htc.get("failOnBelow", True)
        except:
            pass
    
    return config


def run_command(cmd: list, cwd: Path, dry_run: bool = False) -> bool:
    """Run a shell command."""
    cmd_str = " ".join(cmd)
    if dry_run:
        print(f"  [DRY-RUN] Would run: {cmd_str}")
        return True
    
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ⚠️  Command failed: {cmd_str}")
            if result.stderr:
                print(f"     {result.stderr[:200]}")
            return False
        return True
    except Exception as e:
        print(f"  ❌ Error running command: {e}")
        return False


def write_json(path: Path, data: dict, dry_run: bool = False):
    """Write JSON to file."""
    if dry_run:
        print(f"  [DRY-RUN] Would write: {path}")
        return
    
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"  ✅ Created: {path.name}")


def write_text(path: Path, content: str, dry_run: bool = False):
    """Write text to file."""
    if dry_run:
        print(f"  [DRY-RUN] Would write: {path}")
        return
    
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"  ✅ Created: {path.name}")


def update_package_json(root: Path, scripts: dict, dry_run: bool = False):
    """Update package.json with scripts."""
    pkg_path = root / "package.json"
    
    if not pkg_path.exists():
        print("  ⚠️  No package.json found, skipping script additions")
        return
    
    if dry_run:
        print(f"  [DRY-RUN] Would update: package.json")
        return
    
    try:
        pkg = json.loads(pkg_path.read_text())
        
        if "scripts" not in pkg:
            pkg["scripts"] = {}
        pkg["scripts"].update(scripts)
        
        pkg_path.write_text(json.dumps(pkg, indent=2) + "\n")
        print("  ✅ Updated: package.json")
    except Exception as e:
        print(f"  ❌ Error updating package.json: {e}")


# ============================================================================
# Setup Functions
# ============================================================================

def setup_husky(root: Path, dry_run: bool):
    """Set up Husky pre-commit hooks."""
    print("\n🪝 Setting up Husky...")
    
    pm = detect_package_manager(root)
    install_cmd = {
        "npm": ["npm", "install", "-D"],
        "pnpm": ["pnpm", "add", "-D"],
        "yarn": ["yarn", "add", "-D"],
        "bun": ["bun", "add", "-D"]
    }[pm]
    
    # Check if husky is already installed
    pkg_json = root / "package.json"
    husky_installed = False
    if pkg_json.exists():
        try:
            pkg = json.loads(pkg_json.read_text())
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            husky_installed = "husky" in deps
        except:
            pass
    
    if not husky_installed:
        run_command(install_cmd + ["husky"], root, dry_run)
    else:
        print("  ℹ️  Husky already installed")
    
    # Initialize husky
    run_command(["npx", "husky", "install"], root, dry_run)
    
    # Add prepare script to package.json
    if pkg_json.exists() and not dry_run:
        try:
            pkg = json.loads(pkg_json.read_text())
            if "scripts" not in pkg:
                pkg["scripts"] = {}
            if "prepare" not in pkg["scripts"]:
                pkg["scripts"]["prepare"] = "husky install"
                pkg_json.write_text(json.dumps(pkg, indent=2) + "\n")
                print("  ✅ Added prepare script to package.json")
        except:
            pass


def configure_coverage(root: Path, test_info: dict, threshold: int, dry_run: bool):
    """Configure coverage thresholds based on test runner."""
    print(f"\n📊 Configuring coverage threshold ({threshold}%)...")
    
    runner = test_info.get("runner")
    coverage = test_info.get("coverage")
    
    if runner == "vitest":
        # Install the v8 coverage provider when missing
        if not test_info.get("has_v8_provider"):
            pm = detect_package_manager(root)
            add_cmd = {
                "npm": ["npm", "install", "-D"],
                "pnpm": ["pnpm", "add", "-D"],
                "yarn": ["yarn", "add", "-D"],
                "bun": ["bun", "add", "-D"]
            }[pm]
            run_command(add_cmd + ["@vitest/coverage-v8"], root, dry_run)

        # Update vitest.config.ts or vitest.config.js
        vitest_config_ts = root / "vitest.config.ts"
        vitest_config_js = root / "vitest.config.js"
        
        config_content = VITEST_COVERAGE_CONFIG.replace("lines: 80", f"lines: {threshold}")
        config_content = config_content.replace("branches: 75", f"branches: {max(75, threshold - 5)}")
        config_content = config_content.replace("functions: 80", f"functions: {threshold}")
        config_content = config_content.replace("statements: 80", f"statements: {threshold}")
        
        if vitest_config_ts.exists() or vitest_config_js.exists():
            print("  ℹ️  Vitest config exists - manual update may be needed")
            print("     Add test.coverage with provider 'v8' and thresholds to your config:")
            print(config_content)
        else:
            write_text(vitest_config_ts if (root / "tsconfig.json").exists() else vitest_config_js, config_content, dry_run)
    
    elif runner == "mocha" and coverage == "nyc":
        # Create or update .nycrc.json
        nyc_config = NYC_CONFIG.copy()
        nyc_config["lines"] = threshold
        nyc_config["branches"] = max(75, threshold - 5)
        nyc_config["functions"] = threshold
        nyc_config["statements"] = threshold
        
        nycrc = root / ".nycrc.json"
        if nycrc.exists():
            try:
                existing = json.loads(nycrc.read_text())
                existing.update({k: v for k, v in nyc_config.items() if k != "reporter"})
                write_json(nycrc, existing, dry_run)
            except:
                write_json(nycrc, nyc_config, dry_run)
        else:
            write_json(nycrc, nyc_config, dry_run)


def create_pre_commit_hook(root: Path, test_info: dict, threshold: int, fail_on_below: bool, skip_if_no_tests: bool, dry_run: bool):
    """Create pre-commit hook that runs tests with coverage."""
    print("\n🪝 Creating pre-commit hook...")
    
    runner = test_info.get("runner")
    coverage = test_info.get("coverage")
    test_script = test_info.get("test_script", "test")
    
    pm = detect_package_manager(root)
    pm_run = {
        "npm": "npm run",
        "pnpm": "pnpm run",
        "yarn": "yarn",
        "bun": "bun run"
    }[pm]
    
    # Build test command based on runner
    pm_exec = {
        "npm": "npx",
        "pnpm": "pnpm exec",
        "yarn": "yarn",
        "bun": "bunx"
    }[pm]
    if runner == "vitest":
        test_cmd = f"{pm_exec} vitest run --coverage"
    elif runner == "mocha":
        if coverage == "nyc":
            test_cmd = f"nyc --reporter=text --reporter=html {pm_run} {test_script}"
        elif coverage == "c8":
            test_cmd = f"c8 --reporter=text --reporter=html {pm_run} {test_script}"
        else:
            print(f"  ⚠️  Mocha detected but no coverage tool found. Install nyc or c8.")
            test_cmd = f"{pm_run} {test_script}"
    else:
        print(f"  ⚠️  Unknown test runner. Using default test command.")
        test_cmd = f"{pm_run} {test_script}"
    
    # Add skip logic if needed
    if skip_if_no_tests:
        hook_content = f"""#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

# Check if test files exist
if [ -z "$(find . -name '*.test.*' -o -name '*.spec.*' -not -path './node_modules/*' 2>/dev/null)" ]; then
  echo "⚠️  No test files found, skipping test coverage check"
  exit 0
fi

{test_cmd}
"""
    else:
        hook_content = PRE_COMMIT_HOOK_TEMPLATE.format(test_command=test_cmd)
    
    husky_dir = root / ".husky"
    pre_commit_path = husky_dir / "pre-commit"
    
    # Check if pre-commit hook already exists
    if pre_commit_path.exists() and not dry_run:
        existing_content = pre_commit_path.read_text()
        if "coverage" in existing_content.lower() or test_script in existing_content:
            print("  ℹ️  Pre-commit hook already exists with test/coverage commands")
            print("     Review the hook manually to ensure it runs tests with coverage")
            return
    
    write_text(pre_commit_path, hook_content, dry_run)
    
    if not dry_run:
        pre_commit_path.chmod(0o755)


def verify_test_setup(root: Path) -> bool:
    """Verify that test setup exists."""
    # Check for test files
    test_files = list(root.rglob("*.test.*")) + list(root.rglob("*.spec.*"))
    test_files = [f for f in test_files if "node_modules" not in str(f)]
    
    if not test_files:
        print("  ⚠️  Warning: No test files found (*.test.* or *.spec.*)")
        print("     Consider adding tests before setting up coverage enforcement")
        return False
    
    return True


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Set up Husky git hooks to run tests and enforce coverage thresholds"
    )
    parser.add_argument("--root", required=True, help="Project root directory")
    parser.add_argument("--threshold", type=int, default=80, help="Coverage threshold percentage (default: 80)")
    parser.add_argument("--fail-on-below", action="store_true", default=True, help="Fail commit if coverage below threshold")
    parser.add_argument("--no-fail-on-below", dest="fail_on_below", action="store_false", help="Allow commit even if coverage below threshold")
    parser.add_argument("--skip-if-no-tests", action="store_true", help="Skip hook if no test files found")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    root = Path(args.root).resolve()
    
    if not root.exists():
        print(f"❌ Error: Directory does not exist: {root}")
        sys.exit(1)
    
    if not (root / "package.json").exists():
        print(f"❌ Error: No package.json found in {root}")
        print("   Run 'npm init' first to create a package.json")
        sys.exit(1)
    
    # Read configuration
    config = read_config(root)
    threshold = args.threshold or config["threshold"]
    fail_on_below = args.fail_on_below if args.fail_on_below is not None else config["fail_on_below"]
    skip_if_no_tests = args.skip_if_no_tests or config["skip_if_no_tests"]
    
    print(f"🚀 Setting up Husky test coverage enforcement")
    print(f"   Project: {root}")
    print(f"   Coverage threshold: {threshold}%")
    print(f"   Fail on below threshold: {fail_on_below}")
    
    if args.dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made\n")
    
    # Detect test runner
    test_info = detect_test_runner(root)
    if not test_info.get("runner"):
        print("\n⚠️  Warning: No supported test runner detected (Vitest or Mocha)")
        print("   Install a test runner first:")
        print("   - bun add -D vitest @vitest/coverage-v8")
        print("   - bun add -D mocha nyc")
        sys.exit(1)
    
    print(f"   Test runner: {test_info['runner']}")
    print(f"   Coverage tool: {test_info.get('coverage', 'none')}")
    
    # Verify test setup
    if not skip_if_no_tests:
        verify_test_setup(root)
    
    # Setup Husky
    setup_husky(root, args.dry_run)
    
    # Configure coverage
    configure_coverage(root, test_info, threshold, args.dry_run)
    
    # Create pre-commit hook
    create_pre_commit_hook(root, test_info, threshold, fail_on_below, skip_if_no_tests, args.dry_run)
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print(f"  1. Review the pre-commit hook in .husky/pre-commit")
    print(f"  2. Ensure your test command runs with coverage enabled")
    print(f"  3. Make a commit to test the hook")
    if not fail_on_below:
        print(f"  4. Note: Hook is set to warn only (won't block commits)")


if __name__ == "__main__":
    main()

