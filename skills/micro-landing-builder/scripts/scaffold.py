#!/usr/bin/env python3
"""
Scaffold a config-driven NextJS landing page.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from textwrap import dedent


SKILL_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = SKILL_DIR / "assets" / "templates" / "landing"

# Looked up with `npm view <pkg> version` on 2026-10-06; the Next/React/TypeScript/Tailwind pins
# match project-init-orchestrator. The shadcn runtime set (shadcn, radix-ui, cva, cn, lucide-react,
# tw-animate-css) is what `bunx --bun shadcn@latest init` installs today.
PINS = {
    "next": "16.3.8",
    "react": "19.3.0",
    "types-node": "26.6.4",
    "types-react": "19.3.0",
    "typescript": "6.0.3",
    "tailwindcss": "4.3.3",
    "shadcn": "4.21.3",
    "radix-ui": "1.7.0",
    "class-variance-authority": "0.7.1",
    "cn": "0.4.0",
    "lucide-react": "1.52.0",
    "tw-animate-css": "1.4.0",
}


SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")

# Per-mode theme defaults written to app.json; layout.tsx applies them as shadcn CSS variables.
# Every default pair (including the primary below and the accent on its background) is at least
# WCAG AA 4.5:1; tests/test_scaffold.py enforces it.
DEFAULT_PRIMARY = "#4f46e5"
THEME_MODES = {
    "dark": {"background": "#0a0a0a", "foreground": "#fafafa", "accent": "#f59e0b"},
    "light": {"background": "#ffffff", "foreground": "#0a0a0a", "accent": "#b45309"},
}


COLOR_PATTERN = re.compile(r"^#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


def validate_color(flag: str, value: str) -> str:
    """Theme colors must be #rgb, #rgba, #rrggbb or #rrggbbaa (lib/theme.ts parses nothing else)."""
    if not COLOR_PATTERN.fullmatch(value):
        print(
            f"Error: invalid color {value!r} for {flag}. "
            "Use #rgb, #rgba, #rrggbb or #rrggbbaa."
        )
        sys.exit(1)
    return value


def validate_slug(slug: str) -> None:
    """Reject anything but a single path segment of lowercase letters, digits and hyphens."""
    if not SLUG_PATTERN.fullmatch(slug):
        print(
            f"Error: invalid slug {slug!r}. Use one segment of lowercase letters, digits and "
            "hyphens, starting with a letter or digit (for example 'mystartup')."
        )
        sys.exit(1)


def resolve_destination(root: Path, slug: str) -> Path:
    """Return root/slug and require its real path to stay strictly under the real root."""
    validate_slug(slug)
    real_root = Path(os.path.realpath(root))
    destination = root / slug
    real_destination = Path(os.path.realpath(destination))
    if real_destination.parent != real_root or destination.is_symlink():
        print(f"Error: {destination} resolves outside {root}.")
        sys.exit(1)
    return destination


def create_package_json(name: str) -> str:
    return json.dumps({
        "name": name.lower().replace(" ", "-"),
        "version": "0.1.0",
        "private": True,
        "scripts": {
            "dev": "next dev",
            "build": "next build",
            "start": "next start",
            "typecheck": "tsc --noEmit"
        },
        "dependencies": {
            "next": PINS["next"],
            "react": PINS["react"],
            "react-dom": PINS["react"],
            "shadcn": PINS["shadcn"],
            "radix-ui": PINS["radix-ui"],
            "class-variance-authority": PINS["class-variance-authority"],
            "cn": PINS["cn"],
            "lucide-react": PINS["lucide-react"],
            "tw-animate-css": PINS["tw-animate-css"]
        },
        "devDependencies": {
            "@types/node": PINS["types-node"],
            "@types/react": PINS["types-react"],
            "@types/react-dom": PINS["types-react"],
            "typescript": PINS["typescript"],
            "tailwindcss": PINS["tailwindcss"],
            "@tailwindcss/postcss": PINS["tailwindcss"]
        }
    }, indent=2)


def create_next_config() -> str:
    return dedent("""\
        import type { NextConfig } from "next";

        const nextConfig: NextConfig = {
          reactStrictMode: true,
        };

        export default nextConfig;
    """)


def create_postcss_config() -> str:
    return dedent("""\
        const config = {
          plugins: {
            "@tailwindcss/postcss": {},
          },
        };

        export default config;
    """)


def create_tsconfig() -> str:
    return json.dumps({
        "compilerOptions": {
            "target": "ES2017",
            "lib": ["dom", "dom.iterable", "esnext"],
            "allowJs": True,
            "skipLibCheck": True,
            "strict": True,
            "noEmit": True,
            "esModuleInterop": True,
            "module": "esnext",
            "moduleResolution": "bundler",
            "resolveJsonModule": True,
            "isolatedModules": True,
            "jsx": "react-jsx",
            "incremental": True,
            "plugins": [{"name": "next"}],
            "paths": {
                "@/*": ["./*"]
            }
        },
        "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts", ".next/dev/types/**/*.ts"],
        "exclude": ["node_modules"]
    }, indent=2)


def create_vercel_json(domain: str) -> str:
    return json.dumps({
        "rewrites": [],
        "headers": [
            {
                "source": "/(.*)",
                "headers": [
                    {"key": "X-Frame-Options", "value": "DENY"},
                    {"key": "X-Content-Type-Options", "value": "nosniff"}
                ]
            }
        ]
    }, indent=2)


def create_theme(
    mode: str | None = None,
    primary: str | None = None,
    accent: str | None = None,
    background: str | None = None,
) -> dict:
    """Theme block for app.json.

    With no overrides the file carries the full dark (or --theme-mode) defaults. When a
    background is given, `foreground` is left out so lib/theme.ts picks the higher-contrast
    text color, and `mode` is left out unless requested so it follows the background.
    """
    theme: dict = {"primary": primary or DEFAULT_PRIMARY}
    if accent:
        theme["accent"] = accent
    if background:
        # accent (when not given) and foreground are derived from the background by lib/theme.ts
        theme["background"] = background
        if mode:
            theme["mode"] = mode
    else:
        chosen = mode or "dark"
        if not accent:
            theme["accent"] = THEME_MODES[chosen]["accent"]
        theme["background"] = THEME_MODES[chosen]["background"]
        theme["foreground"] = THEME_MODES[chosen]["foreground"]
        theme["mode"] = chosen
    theme["font"] = {"heading": "Fraunces", "body": "Space Grotesk"}
    return theme


def create_app_json(name: str, slug: str, domain: str, concept: str, theme: dict | None = None) -> str:
    return json.dumps({
        "name": name,
        "slug": slug,
        "domain": domain,
        "meta": {
            "title": f"{name} - {concept}",
            "description": f"{name}: {concept}. Join thousands of users.",
            "ogImage": "/og.png"
        },
        "theme": theme or create_theme(),
        "analytics": {
            "plausible": domain if domain else None,
            "ga": None
        },
        "header": {
            "logo": {
                "mark": name[:2].upper(),
                "text": name
            },
            "nav": [
                {"label": "Features", "href": "#features"},
                {"label": "Pricing", "href": "#pricing"},
                {"label": "FAQ", "href": "#faq"}
            ],
            "cta": {"label": "Get Started", "href": "#signup"}
        },
        "sections": [
            {
                "type": "hero",
                "eyebrow": "Now in beta",
                "headline": f"The future of {concept.lower()}",
                "subheadline": f"Join thousands of users who are already using {name} to transform their workflow.",
                "badges": [],
                "primaryCta": {"label": "Request Access", "href": "#signup"},
                "secondaryCta": {"label": "Learn More", "href": "#features"},
                "image": None
            },
            {
                "type": "stats",
                "items": [
                    {"value": "10K+", "label": "Users"},
                    {"value": "99.9%", "label": "Uptime"},
                    {"value": "4.9", "label": "Rating"}
                ]
            },
            {
                "type": "features",
                "title": "Everything you need",
                "subtitle": f"Powerful features to supercharge your {concept.lower()}.",
                "items": [
                    {
                        "icon": "zap",
                        "title": "Lightning Fast",
                        "description": "Built for speed from the ground up."
                    },
                    {
                        "icon": "shield",
                        "title": "Secure by Default",
                        "description": "Enterprise-grade security out of the box."
                    },
                    {
                        "icon": "trending-up",
                        "title": "Analytics",
                        "description": "Deep insights into your performance."
                    }
                ]
            },
            {
                "type": "pricing",
                "title": "Simple, transparent pricing",
                "subtitle": "No hidden fees. Cancel anytime.",
                "plans": [
                    {
                        "name": "Starter",
                        "price": {"monthly": 0, "yearly": 0},
                        "description": "Perfect for getting started",
                        "features": ["Up to 1,000 requests", "Basic analytics", "Email support"],
                        "cta": {"label": "Start Free", "href": "#signup"}
                    },
                    {
                        "name": "Pro",
                        "price": {"monthly": 29, "yearly": 290},
                        "description": "For growing teams",
                        "features": ["Unlimited requests", "Advanced analytics", "Priority support", "Custom integrations"],
                        "cta": {"label": "Get Started", "href": "#signup"},
                        "highlighted": True
                    }
                ]
            },
            {
                "type": "testimonials",
                "title": "Loved by teams worldwide",
                "items": [
                    {
                        "quote": f"{name} has completely transformed how we work. Can't imagine going back.",
                        "author": "Jane Doe",
                        "role": "CEO at TechCorp",
                        "avatar": None
                    }
                ]
            },
            {
                "type": "faq",
                "title": "Frequently asked questions",
                "items": [
                    {
                        "q": f"What is {name}?",
                        "a": f"{name} is a platform for {concept.lower()}. We help teams work faster and smarter."
                    },
                    {
                        "q": "How do I get started?",
                        "a": "Sign up for a free account and you'll be up and running in minutes."
                    },
                    {
                        "q": "Is there a free trial?",
                        "a": "Yes! Our Starter plan is free forever. No credit card required."
                    }
                ]
            },
            {
                "type": "cta",
                "headline": "Ready to get started?",
                "subheadline": f"Join thousands of users already using {name}.",
                "emailCapture": {
                    "enabled": True,
                    "provider": "resend",
                    "placeholder": "Enter your email",
                    "buttonText": "Join Waitlist"
                }
            }
        ],
        "footer": {
            "links": [
                {"label": "Privacy", "href": "/privacy"},
                {"label": "Terms", "href": "/terms"}
            ],
            "social": [
                {"platform": "twitter", "href": "#"},
                {"platform": "github", "href": "#"}
            ],
            "copyright": f"2024 {name}. All rights reserved."
        }
    }, indent=2)


def create_gitignore() -> str:
    return dedent("""\
        # Dependencies
        node_modules/
        .pnp
        .pnp.js

        # Build
        .next/
        out/
        build/

        # Misc
        .DS_Store
        *.pem

        # Debug
        npm-debug.log*
        yarn-debug.log*
        yarn-error.log*

        # Local env
        .env*.local

        # Vercel
        .vercel

        # TypeScript
        *.tsbuildinfo
        next-env.d.ts
    """)


def scaffold_landing(
    root: Path,
    slug: str,
    name: str,
    domain: str,
    concept: str,
    allow_outside: bool,
    theme_mode: str | None = None,
    primary: str | None = None,
    accent: str | None = None,
    background: str | None = None,
) -> None:
    """Create a new landing page project."""

    project_dir = resolve_destination(root, slug)
    for flag, value in (("--primary", primary), ("--accent", accent), ("--background", background)):
        if value is not None:
            validate_color(flag, value)
    theme = create_theme(theme_mode, primary, accent, background)

    # Safety check
    cwd = Path.cwd()
    if not allow_outside and not root.is_relative_to(cwd):
        print(f"Error: Target path {root} is outside current directory.")
        print("Use --allow-outside to confirm this is intentional.")
        sys.exit(1)

    if project_dir.exists():
        print(f"Error: {project_dir} already exists.")
        sys.exit(1)

    # Create directories
    project_dir.mkdir(parents=True)
    (project_dir / "public").mkdir()

    # shadcn/ui kit and section components (components.json, components/ui, components/sections,
    # lib/utils.ts, app/*) are copied verbatim so the app has no private UI dependency.
    shutil.copytree(TEMPLATES_DIR, project_dir, dirs_exist_ok=True)

    # Create files
    files = {
        "package.json": create_package_json(name),
        "next.config.ts": create_next_config(),
        "postcss.config.mjs": create_postcss_config(),
        "tsconfig.json": create_tsconfig(),
        "vercel.json": create_vercel_json(domain),
        "app.json": create_app_json(name, slug, domain, concept, theme),
        ".gitignore": create_gitignore(),
    }

    for filename, content in files.items():
        filepath = project_dir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content)
        print(f"Created: {filepath}")

    print(f"\n✅ Landing page created at: {project_dir}")
    print(f"\nNext steps:")
    print(f"1. cd {project_dir}")
    print(f"2. Edit app.json with your content")
    print(f"3. Add images to public/")
    print(f"4. bun install")
    print(f"5. bun dev")
    print(f"\nAdd more shadcn/ui components with: bunx --bun shadcn@latest add <name>")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold a config-driven NextJS landing page."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Parent directory for the landing (default: current directory)",
    )
    parser.add_argument(
        "--slug",
        type=str,
        required=True,
        help="URL-friendly name (e.g., 'mystartup')",
    )
    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Display name (e.g., 'My Startup')",
    )
    parser.add_argument(
        "--domain",
        type=str,
        default="",
        help="Domain name (e.g., 'mystartup.com')",
    )
    parser.add_argument(
        "--concept",
        type=str,
        default="innovative solution",
        help="Product concept (e.g., 'AI-powered analytics')",
    )
    parser.add_argument(
        "--theme-mode",
        choices=sorted(THEME_MODES),
        default=None,
        help="Color mode written to app.json theme (default: dark, or inferred from --background)",
    )
    parser.add_argument("--primary", help="Primary color: #rgb, #rgba, #rrggbb or #rrggbbaa")
    parser.add_argument("--accent", help="Accent (brand) color: #rgb, #rgba, #rrggbb or #rrggbbaa")
    parser.add_argument("--background", help="Background color: #rgb, #rgba, #rrggbb or #rrggbbaa")
    parser.add_argument(
        "--allow-outside",
        action="store_true",
        help="Allow creating files outside current directory",
    )

    args = parser.parse_args()

    scaffold_landing(
        root=args.root.resolve(),
        slug=args.slug,
        name=args.name,
        domain=args.domain,
        concept=args.concept,
        allow_outside=args.allow_outside,
        theme_mode=args.theme_mode,
        primary=args.primary,
        accent=args.accent,
        background=args.background,
    )


if __name__ == "__main__":
    main()
