#!/usr/bin/env python3
"""
Batch create multiple landing pages from a template or CSV/JSON file.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


# Same rule as scaffold.py: one path segment, lowercase letters, digits and hyphens.
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")


# Color validation is shared with scaffold.py (and mirrored in lib/theme.ts): exactly
# #rgb, #rgba, #rrggbb or #rrggbbaa, no surrounding whitespace, no empty strings.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scaffold import COLOR_PATTERN, THEME_MODES, validate_theme  # noqa: E402

THEME_FIELDS = ("primary", "accent", "background")


def parse_theme(project: dict[str, Any]) -> dict[str, str] | None:
    """Validated optional theme fields of a project, or None when any of them is invalid.

    Values are validated exactly as supplied (no stripping). A missing key or JSON null means
    "not set"; an empty or whitespace-padded string is invalid.
    """
    theme: dict[str, str] = {}
    for field in THEME_FIELDS:
        value = project.get(field)
        if value is None:
            continue
        if not isinstance(value, str) or not COLOR_PATTERN.fullmatch(value):
            return None
        theme[field] = value
    mode = project.get("theme_mode")
    if mode is not None:
        if not isinstance(mode, str) or mode not in THEME_MODES:
            return None
        theme["mode"] = mode
    return theme


def theme_args(theme: dict[str, str]) -> list[str]:
    args: list[str] = []
    for field in THEME_FIELDS:
        if field in theme:
            args += [f"--{field}", theme[field]]
    if "mode" in theme:
        args += ["--theme-mode", theme["mode"]]
    return args


def apply_theme(config_theme: dict[str, Any], theme: dict[str, str]) -> None:
    """Apply validated per-project theme fields to a cloned template's app.json theme.

    Inherited foreground, mode and accent were chosen for the template's background, so a new
    background clears them (unless given) and lib/theme.ts derives matching ones."""
    for field in THEME_FIELDS:
        if field in theme:
            config_theme[field] = theme[field]
    if "background" in theme:
        # Contrast and mode must follow the new background unless a mode was requested.
        config_theme.pop("foreground", None)
        if "accent" not in theme:
            config_theme.pop("accent", None)  # lib/theme.ts picks an accent that fits the background
        if "mode" in theme:
            config_theme["mode"] = theme["mode"]
        else:
            config_theme.pop("mode", None)
    elif "mode" in theme:
        defaults = THEME_MODES[theme["mode"]]
        config_theme["mode"] = theme["mode"]
        config_theme["background"] = defaults["background"]
        config_theme["foreground"] = defaults["foreground"]
        if "accent" not in theme:
            config_theme["accent"] = defaults["accent"]


def destination_for(root: Path, slug: str) -> Path | None:
    """Return root/slug, or None when the slug is unsafe or resolves outside the root."""
    if not SLUG_PATTERN.fullmatch(slug):
        return None
    target = root / slug
    real_root = Path(os.path.realpath(root))
    if Path(os.path.realpath(target)).parent != real_root or target.is_symlink():
        return None
    return target


CSV_COLUMNS = ("slug", "name", "domain", "concept", *THEME_FIELDS, "theme_mode")


def load_projects_from_csv(csv_path: Path) -> list[dict[str, Any]]:
    """Load project definitions from CSV file.

    The file is read as UTF-8 with an optional BOM. Header names are trimmed and matched
    case-insensitively against the documented columns; unknown or duplicate headers are an
    error. Theme cell values are kept exactly as written (an empty cell means "not set").
    """
    projects: list[dict[str, Any]] = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            return projects
        columns = [name.strip().lower() for name in header]
        unknown = [raw for raw, name in zip(header, columns) if name not in CSV_COLUMNS]
        if unknown:
            raise ValueError(
                f"unknown CSV header(s) {unknown}; allowed: {', '.join(CSV_COLUMNS)}"
            )
        duplicates = sorted({name for name in columns if columns.count(name) > 1})
        if duplicates:
            raise ValueError(f"duplicate CSV header(s) {duplicates}")
        for line_number, cells in enumerate(reader, start=2):
            if not any(cell.strip() for cell in cells):
                continue
            if len(cells) != len(columns):
                raise ValueError(f"CSV row {line_number}: expected {len(columns)} cells, got {len(cells)}")
            row = dict(zip(columns, cells))
            project: dict[str, Any] = {
                key: row.get(key, "").strip() for key in ("slug", "name", "domain", "concept")
            }
            for column in (*THEME_FIELDS, "theme_mode"):
                cell = row.get(column)
                if cell:
                    project[column] = cell
            projects.append(project)
    return projects


def load_projects_from_json(json_path: Path) -> list[dict[str, Any]]:
    """Load project definitions from JSON file."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "projects" in data:
            return data["projects"]
        else:
            raise ValueError("JSON must be an array or object with 'projects' key")


def clone_from_template(
    template_dir: Path,
    target_dir: Path,
    slug: str,
    name: str,
    domain: str,
    concept: str,
    theme: dict[str, str] | None = None,
) -> None:
    """Clone a landing page from template and update config."""
    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory not found: {template_dir}")

    # Copy template
    shutil.copytree(template_dir, target_dir, ignore=shutil.ignore_patterns(
        "node_modules", ".next", ".vercel", ".git"
    ))

    # Update app.json
    app_json_path = target_dir / "app.json"
    if app_json_path.exists():
        with open(app_json_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        config["name"] = name
        config["slug"] = slug
        config["domain"] = domain
        config["meta"]["title"] = f"{name} - {concept}"
        config["meta"]["description"] = f"{name}: {concept}. Join thousands of users."
        if theme:
            apply_theme(config.setdefault("theme", {}), theme)

        validate_theme(config.get("theme", {}))
        with open(app_json_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    # Update package.json name
    package_json_path = target_dir / "package.json"
    if package_json_path.exists():
        with open(package_json_path, "r", encoding="utf-8") as f:
            package = json.load(f)
        package["name"] = slug
        with open(package_json_path, "w", encoding="utf-8") as f:
            json.dump(package, f, indent=2)

    print(f"✅ Cloned and configured: {target_dir}")


def create_from_scaffold(
    root: Path,
    slug: str,
    name: str,
    domain: str,
    concept: str,
    scaffold_script: Path,
    extra_args: list[str] | None = None,
) -> None:
    """Create a new landing page using scaffold script."""
    cmd = [
        "python3",
        str(scaffold_script),
        "--root", str(root),
        "--slug", slug,
        "--name", name,
        "--domain", domain,
        "--concept", concept,
        "--allow-outside",
        *(extra_args or []),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Failed to create {slug}: {result.stderr}", file=sys.stderr)
        raise RuntimeError(f"Scaffold failed for {slug}: {result.stdout.strip()} {result.stderr.strip()}")
    print(result.stdout)


def batch_create(
    root: Path,
    projects: list[dict[str, Any]],
    template_dir: Path | None,
    scaffold_script: Path,
    allow_outside: bool,
) -> None:
    """Create multiple landing pages."""
    cwd = Path.cwd()
    if not allow_outside and not root.is_relative_to(cwd):
        print(f"Error: Target path {root} is outside current directory.")
        print("Use --allow-outside to confirm this is intentional.")
        sys.exit(1)

    root.mkdir(parents=True, exist_ok=True)

    created = []
    failed = []

    for project in projects:
        label = project.get("slug", "unknown") if isinstance(project, dict) else "unknown"
        target_dir = None
        owns_target = False
        try:
            # Everything about one project, including malformed JSON values, stays inside this
            # handler so a bad entry can never abort the rest of the batch.
            if not isinstance(project, dict):
                raise ValueError(f"project entry must be an object, got {type(project).__name__}")
            fields = {}
            for key, default in (("slug", ""), ("name", ""), ("domain", ""), ("concept", "innovative solution")):
                value = project.get(key, default)
                if not isinstance(value, str):
                    raise ValueError(f"{key} must be a string")
                fields[key] = value.strip()
            slug, name = fields["slug"], fields["name"]
            domain, concept = fields["domain"], fields["concept"]

            if not slug or not name:
                raise ValueError("slug and name are required")

            theme = parse_theme(project)
            if theme is None:
                raise ValueError(
                    "primary, accent and background must be #rgb, #rgba, #rrggbb or #rrggbbaa "
                    "and theme_mode must be dark or light"
                )

            target_dir = destination_for(root, slug)
            if target_dir is None:
                raise ValueError("slug must be one segment of [a-z0-9-] inside the root")

            if target_dir.exists():
                print(f"⚠️  Skipping {slug}: already exists")
                continue

            owns_target = True
            if template_dir and template_dir.exists():
                clone_from_template(template_dir, target_dir, slug, name, domain, concept, theme)
            else:
                create_from_scaffold(
                    root, slug, name, domain, concept, scaffold_script, theme_args(theme)
                )
            created.append(slug)
        except Exception as e:
            if owns_target and target_dir is not None and target_dir.exists():
                shutil.rmtree(target_dir)
            print(f"❌ Skipping {label!r}: {e}", file=sys.stderr)
            failed.append(project)

    print(f"\n📊 Summary:")
    print(f"✅ Created: {len(created)}")
    print(f"❌ Failed: {len(failed)}")
    if created:
        print(f"\nCreated projects: {', '.join(created)}")
    if failed:
        print(
            "\nFailed projects: "
            f"{[p.get('slug', 'unknown') if isinstance(p, dict) else 'unknown' for p in failed]}"
        )
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch create multiple landing pages from template or CSV/JSON."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Parent directory for landings (default: current directory)",
    )
    parser.add_argument(
        "--template",
        type=Path,
        help="Template landing page directory to clone from",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        help="CSV file with columns: slug,name,domain,concept[,primary,accent,background,theme_mode]",
    )
    parser.add_argument(
        "--json",
        type=Path,
        help="JSON file with array of {slug, name, domain, concept[, primary, accent, background, theme_mode]} objects",
    )
    parser.add_argument(
        "--allow-outside",
        action="store_true",
        help="Allow creating files outside current directory",
    )

    args = parser.parse_args()

    # Determine projects source
    if args.csv:
        try:
            projects = load_projects_from_csv(args.csv)
        except ValueError as e:
            print(f"Error: {args.csv}: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.json:
        projects = load_projects_from_json(args.json)
    else:
        print("Error: Must provide --csv or --json file", file=sys.stderr)
        sys.exit(1)

    if not projects:
        print("Error: No projects found in input file", file=sys.stderr)
        sys.exit(1)

    # Get scaffold script path
    skill_dir = Path(__file__).parent.parent
    scaffold_script = skill_dir / "scripts" / "scaffold.py"

    batch_create(
        root=args.root.resolve(),
        projects=projects,
        template_dir=args.template.resolve() if args.template else None,
        scaffold_script=scaffold_script,
        allow_outside=args.allow_outside,
    )


if __name__ == "__main__":
    main()

