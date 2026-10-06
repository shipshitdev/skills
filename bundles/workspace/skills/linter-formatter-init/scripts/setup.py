#!/usr/bin/env python3
"""
Linter Formatter Setup - Initialize Biome (default) or ESLint + Prettier, and pre-commit hooks

Usage:
    setup.py --root <path> [options]

Options:
    --root          Project root directory (required)
    --typescript    Enable TypeScript support (only for ESLint mode)
    --eslint        Use ESLint + Prettier instead of Biome (legacy)
    --no-hooks      Skip pre-commit hook setup
    --monorepo      Configure for monorepo root
    --dry-run       Show what would be done without making changes

Examples:
    setup.py --root /path/to/project                    # Biome (default)
    setup.py --root /path/to/project --eslint           # ESLint + Prettier
    setup.py --root /path/to/project --eslint --typescript
    setup.py --root /path/to/project --no-hooks
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

BIOME_CONFIG = {
    "$schema": "https://biomejs.dev/schemas/2.5.15/schema.json",
    "assist": {
        "actions": {
            "source": {
                "organizeImports": "on"
            }
        }
    },
    "linter": {
        "enabled": True,
        "rules": {
            "preset": "recommended",
            "complexity": {
                "noForEach": "off"
            },
            "style": {
                "noNonNullAssertion": "off"
            },
            "suspicious": {
                "noArrayIndexKey": "off",
                "noExplicitAny": "warn"
            }
        }
    },
    "formatter": {
        "enabled": True,
        "indentStyle": "space",
        "indentWidth": 2,
        "lineWidth": 100
    },
    "javascript": {
        "formatter": {
            "quoteStyle": "single",
            "trailingCommas": "es5",
            "semicolons": "always"
        }
    },
    "files": {
        # Biome 2 replaced files.ignore with files.includes plus "!" exclusions
        "includes": [
            "**",
            "!**/node_modules",
            "!**/dist",
            "!**/build",
            "!**/.next",
            "!**/out",
            "!**/.cache",
            "!**/.turbo",
            "!**/coverage",
            "!**/*.min.js",
            "!**/*.min.css"
        ]
    }
}

ESLINT_CONFIG = {
    "env": {
        "browser": True,
        "es2021": True,
        "node": True
    },
    "extends": [
        "eslint:recommended",
        "plugin:prettier/recommended"
    ],
    "parserOptions": {
        "ecmaVersion": "latest",
        "sourceType": "module"
    },
    "rules": {
        "no-console": ["warn", {"allow": ["warn", "error"]}],
        "no-unused-vars": ["error", {"argsIgnorePattern": "^_"}],
        "prefer-const": "error",
        "no-var": "error",
        "eqeqeq": ["error", "always"],
        "curly": ["error", "all"]
    }
}

ESLINT_CONFIG_TS = {
    "env": {
        "browser": True,
        "es2021": True,
        "node": True
    },
    "extends": [
        "eslint:recommended",
        "plugin:@typescript-eslint/recommended",
        "plugin:prettier/recommended"
    ],
    "parser": "@typescript-eslint/parser",
    "parserOptions": {
        "ecmaVersion": "latest",
        "sourceType": "module"
    },
    "plugins": ["@typescript-eslint"],
    "rules": {
        "no-console": ["warn", {"allow": ["warn", "error"]}],
        "@typescript-eslint/no-unused-vars": ["error", {"argsIgnorePattern": "^_"}],
        "@typescript-eslint/explicit-function-return-type": "off",
        "@typescript-eslint/no-explicit-any": "warn",
        "prefer-const": "error",
        "no-var": "error",
        "eqeqeq": ["error", "always"],
        "curly": ["error", "all"]
    }
}

PRETTIER_CONFIG = {
    "semi": True,
    "singleQuote": True,
    "tabWidth": 2,
    "trailingComma": "es5",
    "printWidth": 100,
    "bracketSpacing": True,
    "arrowParens": "always",
    "endOfLine": "lf"
}

PRETTIER_IGNORE = """# Dependencies
node_modules/

# Build outputs
dist/
build/
.next/
out/

# Cache
.cache/
.turbo/

# Coverage
coverage/

# Lock files
package-lock.json
pnpm-lock.yaml
yarn.lock
bun.lock
bun.lockb

# Generated
*.min.js
*.min.css
"""

ESLINT_IGNORE = """# Dependencies
node_modules/

# Build outputs
dist/
build/
.next/
out/

# Cache
.cache/
.turbo/

# Coverage
coverage/
"""

VSCODE_SETTINGS_BIOME = {
    "editor.formatOnSave": True,
    "editor.defaultFormatter": "biomejs.biome",
    "editor.codeActionsOnSave": {
        "source.organizeImports.biome": "explicit",
        "quickfix.biome": "explicit"
    },
    "[javascript]": {
        "editor.defaultFormatter": "biomejs.biome"
    },
    "[javascriptreact]": {
        "editor.defaultFormatter": "biomejs.biome"
    },
    "[typescript]": {
        "editor.defaultFormatter": "biomejs.biome"
    },
    "[typescriptreact]": {
        "editor.defaultFormatter": "biomejs.biome"
    },
    "[json]": {
        "editor.defaultFormatter": "biomejs.biome"
    },
    "[jsonc]": {
        "editor.defaultFormatter": "biomejs.biome"
    }
}

VSCODE_SETTINGS_ESLINT = {
    "editor.formatOnSave": True,
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.codeActionsOnSave": {
        "source.fixAll.eslint": "explicit"
    },
    "[javascript]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode"
    },
    "[javascriptreact]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode"
    },
    "[typescript]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode"
    },
    "[typescriptreact]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode"
    },
    "[json]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode"
    },
    "[jsonc]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode"
    },
    "[markdown]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode"
    }
}

LINT_STAGED_CONFIG_BIOME = {
    "*.{js,jsx,ts,tsx,json,css}": ["bunx biome check --write"]
}

LINT_STAGED_CONFIG_ESLINT = {
    "*.{js,jsx,ts,tsx}": [
        "eslint --fix",
        "prettier --write"
    ],
    "*.{json,md,yml,yaml,css,scss}": [
        "prettier --write"
    ]
}


# ============================================================================
# Helper Functions
# ============================================================================

def detect_package_manager(root: Path) -> str:
    """Detect which package manager is used. ALWAYS prefers bun."""
    # Check for bun first - it's the preferred package manager
    try:
        result = subprocess.run(["which", "bun"], capture_output=True, text=True)
        if result.returncode == 0:
            return "bun"
    except:
        pass

    # Fall back to checking lock files
    if (root / "bun.lock").exists() or (root / "bun.lockb").exists():
        return "bun"
    elif (root / "pnpm-lock.yaml").exists():
        return "pnpm"
    elif (root / "yarn.lock").exists():
        return "yarn"

    return "npm"


def detect_framework(root: Path) -> list:
    """Detect frameworks used in the project."""
    frameworks = []

    pkg_json = root / "package.json"
    if pkg_json.exists():
        try:
            pkg = json.loads(pkg_json.read_text())
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

            if "next" in deps:
                frameworks.append("nextjs")
            if "react" in deps:
                frameworks.append("react")
            if "@nestjs/core" in deps:
                frameworks.append("nestjs")
            if "express" in deps:
                frameworks.append("express")
            if "vue" in deps:
                frameworks.append("vue")
        except:
            pass

    return frameworks


def run_command(cmd: list, cwd: Path, dry_run: bool = False) -> bool:
    """Run a shell command."""
    cmd_str = " ".join(cmd)
    if dry_run:
        print(f"  [DRY-RUN] Would run: {cmd_str}")
        return True

    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  Warning: Command had issues: {cmd_str}")
            if result.stderr:
                print(f"     {result.stderr[:200]}")
            return False
        return True
    except Exception as e:
        print(f"  Error running command: {e}")
        return False


def write_json(path: Path, data: dict, dry_run: bool = False):
    """Write JSON to file."""
    if dry_run:
        print(f"  [DRY-RUN] Would write: {path}")
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"  Created: {path.name}")


def write_text(path: Path, content: str, dry_run: bool = False):
    """Write text to file."""
    if dry_run:
        print(f"  [DRY-RUN] Would write: {path}")
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"  Created: {path.name}")


def update_package_json(root: Path, scripts: dict, lint_staged: dict, dry_run: bool = False):
    """Update package.json with scripts and lint-staged config."""
    pkg_path = root / "package.json"

    if not pkg_path.exists():
        print("  No package.json found, skipping script additions")
        return

    if dry_run:
        print(f"  [DRY-RUN] Would update: package.json")
        return

    try:
        pkg = json.loads(pkg_path.read_text())

        # Add scripts
        if "scripts" not in pkg:
            pkg["scripts"] = {}
        pkg["scripts"].update(scripts)

        # Add lint-staged
        pkg["lint-staged"] = lint_staged

        pkg_path.write_text(json.dumps(pkg, indent=2) + "\n")
        print("  Updated: package.json")
    except Exception as e:
        print(f"  Error updating package.json: {e}")


# ============================================================================
# Setup Functions
# ============================================================================

def setup_biome(root: Path, dry_run: bool):
    """Set up Biome (default linter/formatter)."""
    print("\n Installing Biome...")

    pm = detect_package_manager(root)
    install_cmd = {
        "bun": ["bun", "add", "-D"],
        "pnpm": ["pnpm", "add", "-D"],
        "yarn": ["yarn", "add", "-D"],
        "npm": ["npm", "install", "-D"]
    }[pm]

    # Always install Biome 2.3+ (latest)
    run_command(install_cmd + ["@biomejs/biome@latest"], root, dry_run)

    print("\n Creating configuration files...")

    write_json(root / "biome.json", BIOME_CONFIG, dry_run)

    scripts = {
        "lint": "biome lint .",
        "lint:fix": "biome lint --write .",
        "format": "biome format --write .",
        "format:check": "biome format .",
        "check": "biome check .",
        "check:fix": "biome check --write ."
    }

    update_package_json(root, scripts, LINT_STAGED_CONFIG_BIOME, dry_run)


def setup_eslint_prettier(root: Path, typescript: bool, dry_run: bool):
    """Set up ESLint and Prettier (legacy mode)."""
    print("\n Installing ESLint + Prettier dependencies...")

    pm = detect_package_manager(root)
    install_cmd = {
        "bun": ["bun", "add", "-D"],
        "pnpm": ["pnpm", "add", "-D"],
        "yarn": ["yarn", "add", "-D"],
        "npm": ["npm", "install", "-D"]
    }[pm]

    # Base dependencies
    deps = [
        "eslint",
        "prettier",
        "eslint-config-prettier",
        "eslint-plugin-prettier"
    ]

    # TypeScript dependencies
    if typescript:
        deps.extend([
            "@typescript-eslint/parser",
            "@typescript-eslint/eslint-plugin"
        ])

    # Detect frameworks and add plugins
    frameworks = detect_framework(root)
    if "react" in frameworks or "nextjs" in frameworks:
        deps.extend(["eslint-plugin-react", "eslint-plugin-react-hooks"])
    if "nextjs" in frameworks:
        deps.append("@next/eslint-plugin-next")

    run_command(install_cmd + deps, root, dry_run)

    print("\n Creating configuration files...")

    # ESLint config
    eslint_config = ESLINT_CONFIG_TS if typescript else ESLINT_CONFIG

    # Add React config if detected
    if "react" in frameworks or "nextjs" in frameworks:
        eslint_config["extends"].insert(1, "plugin:react/recommended")
        eslint_config["extends"].insert(2, "plugin:react-hooks/recommended")
        eslint_config["plugins"] = eslint_config.get("plugins", []) + ["react", "react-hooks"]
        eslint_config["settings"] = {"react": {"version": "detect"}}
        eslint_config["rules"]["react/react-in-jsx-scope"] = "off"
        eslint_config["rules"]["react/prop-types"] = "off"

    if "nextjs" in frameworks:
        eslint_config["extends"].insert(1, "next/core-web-vitals")

    write_json(root / ".eslintrc.json", eslint_config, dry_run)
    write_json(root / ".prettierrc", PRETTIER_CONFIG, dry_run)
    write_text(root / ".prettierignore", PRETTIER_IGNORE, dry_run)
    write_text(root / ".eslintignore", ESLINT_IGNORE, dry_run)

    # npm scripts
    ext = ".js,.jsx,.ts,.tsx" if typescript else ".js,.jsx"
    scripts = {
        "lint": f"eslint . --ext {ext}",
        "lint:fix": f"eslint . --ext {ext} --fix",
        "format": "prettier --write .",
        "format:check": "prettier --check ."
    }

    update_package_json(root, scripts, LINT_STAGED_CONFIG_ESLINT, dry_run)


def setup_husky(root: Path, dry_run: bool):
    """Set up Husky pre-commit hooks."""
    print("\n Setting up pre-commit hooks...")

    pm = detect_package_manager(root)
    install_cmd = {
        "bun": ["bun", "add", "-D"],
        "pnpm": ["pnpm", "add", "-D"],
        "yarn": ["yarn", "add", "-D"],
        "npm": ["npm", "install", "-D"]
    }[pm]

    run_command(install_cmd + ["husky", "lint-staged"], root, dry_run)

    # Initialize husky (v9+ uses just "husky" not "husky install")
    exec_cmd = "bunx" if pm == "bun" else "npx"
    run_command([exec_cmd, "husky"], root, dry_run)

    # Create pre-commit hook with appropriate executor
    husky_dir = root / ".husky"
    if not dry_run:
        husky_dir.mkdir(exist_ok=True)

    pre_commit_path = husky_dir / "pre-commit"
    pre_commit_content = f"""#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

{exec_cmd} lint-staged
"""
    write_text(pre_commit_path, pre_commit_content, dry_run)

    if not dry_run:
        pre_commit_path.chmod(0o755)

    # Add prepare script to package.json (v9+ uses just "husky")
    pkg_path = root / "package.json"
    if pkg_path.exists() and not dry_run:
        pkg = json.loads(pkg_path.read_text())
        if "scripts" not in pkg:
            pkg["scripts"] = {}
        pkg["scripts"]["prepare"] = "husky"
        pkg_path.write_text(json.dumps(pkg, indent=2) + "\n")


def setup_vscode(root: Path, use_eslint: bool, dry_run: bool):
    """Set up VS Code / Cursor settings."""
    print("\n Setting up editor configuration...")

    vscode_dir = root / ".vscode"
    settings_path = vscode_dir / "settings.json"

    settings = VSCODE_SETTINGS_ESLINT.copy() if use_eslint else VSCODE_SETTINGS_BIOME.copy()

    # Merge with existing settings if present
    if settings_path.exists() and not dry_run:
        try:
            existing = json.loads(settings_path.read_text())
            existing.update(settings)
            settings = existing
        except:
            pass

    write_json(settings_path, settings, dry_run)


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Set up linting and formatting for JS/TS projects (Biome by default)"
    )
    parser.add_argument("--root", required=True, help="Project root directory")
    parser.add_argument("--typescript", action="store_true", help="Enable TypeScript support (ESLint mode only)")
    parser.add_argument("--eslint", action="store_true", help="Use ESLint + Prettier instead of Biome (legacy)")
    parser.add_argument("--no-hooks", action="store_true", help="Skip pre-commit hook setup")
    parser.add_argument("--monorepo", action="store_true", help="Configure for monorepo root")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    # Keep --biome for backwards compatibility (now a no-op since it's the default)
    parser.add_argument("--biome", action="store_true", help=argparse.SUPPRESS)

    args = parser.parse_args()

    root = Path(args.root).resolve()

    if not root.exists():
        print(f"Error: Directory does not exist: {root}")
        sys.exit(1)

    if not (root / "package.json").exists():
        print(f"Error: No package.json found in {root}")
        print("   Run 'bun init' first to create a package.json")
        sys.exit(1)

    use_eslint = args.eslint
    pm = detect_package_manager(root)

    print(f"Setting up linting and formatting")
    print(f"   Project: {root}")
    print(f"   Package manager: {pm}")
    print(f"   Tool: {'ESLint + Prettier (legacy)' if use_eslint else 'Biome'}")
    if use_eslint:
        print(f"   TypeScript: {'Yes' if args.typescript else 'No'}")
    print(f"   Pre-commit hooks: {'No' if args.no_hooks else 'Yes'}")

    if args.dry_run:
        print("\n DRY RUN MODE - No changes will be made\n")

    # Detect frameworks
    frameworks = detect_framework(root)
    if frameworks:
        print(f"   Detected: {', '.join(frameworks)}")

    # Run setup
    if use_eslint:
        setup_eslint_prettier(root, args.typescript, args.dry_run)
    else:
        setup_biome(root, args.dry_run)

    if not args.no_hooks:
        setup_husky(root, args.dry_run)

    setup_vscode(root, use_eslint, args.dry_run)

    print("\n Setup complete!")
    print("\nNext steps:")
    print(f"  1. Review the generated config files")
    print(f"  2. Run 'bun run lint' to check for issues")
    print(f"  3. Run 'bun run format' to format all files")
    if not args.no_hooks:
        print("  4. Make a commit to test the pre-commit hook")

    if use_eslint:
        print("\nRecommended VS Code extensions:")
        print("  - ESLint (dbaeumer.vscode-eslint)")
        print("  - Prettier (esbenp.prettier-vscode)")
    else:
        print("\nRecommended VS Code extension:")
        print("  - Biome (biomejs.biome)")


if __name__ == "__main__":
    main()
