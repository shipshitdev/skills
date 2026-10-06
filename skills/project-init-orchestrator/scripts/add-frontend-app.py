#!/usr/bin/env python3
"""
Add a new Next.js app next to the dashboard in the frontend project.

Each app is its own Bun workspace (frontend/apps/<name>) that reuses the dashboard's
Next.js, PostCSS, TypeScript and Vitest configuration and its Tailwind v4 theme.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from textwrap import dedent

# Files copied verbatim from the dashboard so every app shares one setup
SHARED_FILES = [
    "next.config.ts",
    "postcss.config.mjs",
    "tsconfig.json",
    "vitest.config.mts",
    "vitest.setup.ts",
]


def create_layout_tsx(name: str) -> str:
    title = name.replace("-", " ").title()
    return dedent(f"""\
        import type {{ Metadata }} from "next";
        import "./globals.css";

        export const metadata: Metadata = {{
          title: "{title}",
          description: "{title} application",
        }};

        export default function RootLayout({{
          children,
        }}: Readonly<{{
          children: React.ReactNode;
        }}>) {{
          return (
            <html lang="en">
              <body>{{children}}</body>
            </html>
          );
        }}
    """)


def create_page_tsx(name: str) -> str:
    title = name.replace("-", " ").title()
    return dedent(f"""\
        export default function Home() {{
          return (
            <main className="min-h-screen p-8">
              <h1 className="text-4xl font-bold">{title}</h1>
              <p className="mt-4 text-muted">Welcome to {title}.</p>
            </main>
          );
        }}
    """)


def create_page_spec(name: str) -> str:
    title = name.replace("-", " ").title()
    return dedent(f"""\
        import {{ render, screen }} from "@testing-library/react";
        import {{ describe, expect, it }} from "vitest";
        import Home from "./page";

        describe("Home", () => {{
          it("renders the app heading", () => {{
            render(<Home />);

            expect(screen.getByRole("heading", {{ name: "{title}" }})).toBeInTheDocument();
          }});
        }});
    """)


def create_package_json(dashboard_package: dict, name: str) -> str:
    scope = dashboard_package["name"].split("/")[0]  # e.g. "@myorg"
    package = dict(dashboard_package)
    package["name"] = f"{scope}/{name}"
    return json.dumps(package, indent=2) + "\n"


def add_frontend_app(root: Path, name: str) -> None:
    """Add a new app to the frontend project."""

    apps_dir = root / "apps"
    dashboard_dir = apps_dir / "dashboard"
    if not dashboard_dir.exists():
        print(f"Error: {dashboard_dir} does not exist. Is this a frontend project?")
        sys.exit(1)

    app_root = apps_dir / name
    if app_root.exists():
        print(f"Error: {app_root} already exists.")
        sys.exit(1)

    app_dir = app_root / "app"
    app_dir.mkdir(parents=True)

    dashboard_package = json.loads((dashboard_dir / "package.json").read_text())

    files = {
        app_root / "package.json": create_package_json(dashboard_package, name),
        app_dir / "layout.tsx": create_layout_tsx(name),
        app_dir / "page.tsx": create_page_tsx(name),
        app_dir / "page.spec.tsx": create_page_spec(name),
        app_dir / "globals.css": (dashboard_dir / "app" / "globals.css").read_text(),
    }
    for shared in SHARED_FILES:
        source = dashboard_dir / shared
        if source.exists():
            files[app_root / shared] = source.read_text()

    for filepath, content in files.items():
        filepath.write_text(content)
        print(f"Created: {filepath}")

    print(f"\n✅ Frontend app '{name}' created at: {app_root}")
    print("\nNext steps:")
    print("1. Run `bun install` at the workspace root (frontend/apps/* is already a workspace glob)")
    print(f"2. cd {app_root.relative_to(root)} && bun run dev -- -p 3002 (the dashboard uses 3000 and the API 3001)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add a new Next.js app to the frontend project."
    )
    parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Path to the frontend project root",
    )
    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="App name (e.g., 'admin', 'settings')",
    )

    args = parser.parse_args()

    add_frontend_app(
        root=args.root.resolve(),
        name=args.name.lower().replace(" ", "-"),
    )


if __name__ == "__main__":
    main()
