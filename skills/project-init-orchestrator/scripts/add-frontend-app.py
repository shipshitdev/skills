#!/usr/bin/env python3
"""
Add a new NextJS app to the frontend project.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from textwrap import dedent


def create_layout_tsx(name: str) -> str:
    title = name.replace("-", " ").title()
    return dedent(f"""\
        import type {{ Metadata }} from "next";
        import "../../../apps/dashboard/app/globals.css";

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
            <html lang="en" data-theme="dark">
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
              <p className="mt-4 text-gray-500">Welcome to {title}.</p>
            </main>
          );
        }}
    """)


def add_frontend_app(root: Path, name: str) -> None:
    """Add a new app to the frontend project."""

    apps_dir = root / "apps"
    if not apps_dir.exists():
        print(f"Error: {apps_dir} does not exist. Is this a frontend project?")
        sys.exit(1)

    app_dir = apps_dir / name / "app"
    if app_dir.exists():
        print(f"Error: {app_dir} already exists.")
        sys.exit(1)

    app_dir.mkdir(parents=True)

    files = {
        app_dir / "layout.tsx": create_layout_tsx(name),
        app_dir / "page.tsx": create_page_tsx(name),
    }

    for filepath, content in files.items():
        filepath.write_text(content)
        print(f"Created: {filepath}")

    print(f"\n✅ Frontend app '{name}' created at: {apps_dir / name}")
    print(f"\nTo run: bun run dev --filter {name}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add a new NextJS app to the frontend project."
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
