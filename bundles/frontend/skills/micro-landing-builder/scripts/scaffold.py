#!/usr/bin/env python3
"""
Scaffold a config-driven NextJS landing page.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from textwrap import dedent


SKILL_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = SKILL_DIR / "assets" / "templates" / "landing"

DEFAULT_UI_PACKAGE = "@agenticindiedev/ui"


# Looked up with `npm view <pkg> version` on 2026-10-06; same pins as project-init-orchestrator.
PINS = {
    "next": "16.3.8",
    "react": "19.3.0",
    "types-node": "26.6.4",
    "types-react": "19.3.0",
    "typescript": "6.0.3",
    "tailwindcss": "4.3.3",
}


def create_package_json(name: str, ui_package: str) -> str:
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
            ui_package: "latest"
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
            "jsx": "preserve",
            "incremental": True,
            "plugins": [{"name": "next"}],
            "paths": {
                "@/*": ["./*"]
            }
        },
        "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
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


def create_app_json(name: str, slug: str, domain: str, concept: str) -> str:
    return json.dumps({
        "name": name,
        "slug": slug,
        "domain": domain,
        "meta": {
            "title": f"{name} - {concept}",
            "description": f"{name}: {concept}. Join thousands of users.",
            "ogImage": "/og.png"
        },
        "theme": {
            "primary": "#6366f1",
            "accent": "#f59e0b",
            "background": "#0a0a0a",
            "font": {
                "heading": "Fraunces",
                "body": "Space Grotesk"
            }
        },
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


def create_layout_tsx(name: str) -> str:
    return dedent(f"""\
        import type {{ Metadata }} from "next";
        import config from "../app.json";
        import "./globals.css";

        export const metadata: Metadata = {{
          title: config.meta.title,
          description: config.meta.description,
        }};

        export default function RootLayout({{
          children,
        }}: Readonly<{{
          children: React.ReactNode;
        }}>) {{
          return (
            <html lang="en">
              <head>
                <link rel="preconnect" href="https://fonts.googleapis.com" />
                <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
                <link
                  href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Space+Grotesk:wght@400;500;600;700&display=swap"
                  rel="stylesheet"
                />
              </head>
              <body>{{children}}</body>
            </html>
          );
        }}
    """)


def create_page_tsx(ui_package: str) -> str:
    return dedent(f"""\
        import config from "../app.json";
        import {{
          Hero,
          Stats,
          Features,
          Pricing,
          Testimonials,
          FAQ,
          CTA,
          Header,
          Footer,
        }} from "{ui_package}";

        const sectionComponents: Record<string, React.ComponentType<any>> = {{
          hero: Hero,
          stats: Stats,
          features: Features,
          pricing: Pricing,
          testimonials: Testimonials,
          faq: FAQ,
          cta: CTA,
        }};

        export default function Landing() {{
          return (
            <main
              style={{{{
                "--color-primary": config.theme.primary,
                "--color-accent": config.theme.accent,
                "--color-background": config.theme.background,
              }} as React.CSSProperties}}
            >
              <Header
                logo={{config.header.logo}}
                nav={{config.header.nav}}
                cta={{config.header.cta}}
              />

              {{config.sections.map((section, index) => {{
                const Component = sectionComponents[section.type];
                if (!Component) return null;
                return <Component key={{index}} {{...section}} />;
              }})}}

              <Footer
                links={{config.footer.links}}
                social={{config.footer.social}}
                copyright={{config.footer.copyright}}
              />
            </main>
          );
        }}
    """)


def create_globals_css(ui_package: str) -> str:
    """Tailwind v4 CSS-first entry: @import, @source for the UI package and an @theme block."""
    template = dedent("""\
        @import "tailwindcss";

        /* Packages in node_modules are not scanned automatically */
        @source "../node_modules/__UI_PACKAGE__";

        @theme {
          --color-primary: #6366f1;
          --color-accent: #f59e0b;
          --color-background: #0a0a0a;
          --font-sans: "Space Grotesk", sans-serif;
          --font-heading: "Fraunces", serif;
        }

        @layer base {
          body {
            @apply bg-background font-sans text-white;
          }

          h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-heading);
          }
        }
    """)
    return template.replace("__UI_PACKAGE__", ui_package)


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
    ui_package: str,
    allow_outside: bool,
) -> None:
    """Create a new landing page project."""

    project_dir = root / slug

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
    (project_dir / "app").mkdir()
    (project_dir / "public").mkdir()

    # Create files
    files = {
        "package.json": create_package_json(name, ui_package),
        "next.config.ts": create_next_config(),
        "postcss.config.mjs": create_postcss_config(),
        "tsconfig.json": create_tsconfig(),
        "vercel.json": create_vercel_json(domain),
        "app.json": create_app_json(name, slug, domain, concept),
        ".gitignore": create_gitignore(),
        "app/layout.tsx": create_layout_tsx(name),
        "app/page.tsx": create_page_tsx(ui_package),
        "app/globals.css": create_globals_css(ui_package),
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
    print(f"\nNote: Requires UI package '{ui_package}' to be published.")


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
        "--ui-package",
        type=str,
        default=DEFAULT_UI_PACKAGE,
        help=f"UI components package (default: {DEFAULT_UI_PACKAGE})",
    )
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
        ui_package=args.ui_package,
        allow_outside=args.allow_outside,
    )


if __name__ == "__main__":
    main()
