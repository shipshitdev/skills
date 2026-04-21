#!/usr/bin/env python3
"""
shadcn/ui Setup with Tailwind v4

Sets up shadcn/ui with proper Tailwind CSS v4 configuration.
Ensures CSS-first configuration, no deprecated tailwind.config.js files.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Theme configurations (light mode)
THEMES = {
    'default': {
        'background': '0 0% 100%',
        'foreground': '222.2 84% 4.9%',
        'card': '0 0% 100%',
        'card-foreground': '222.2 84% 4.9%',
        'popover': '0 0% 100%',
        'popover-foreground': '222.2 84% 4.9%',
        'primary': '222.2 47.4% 11.2%',
        'primary-foreground': '210 40% 98%',
        'secondary': '210 40% 96.1%',
        'secondary-foreground': '222.2 47.4% 11.2%',
        'muted': '210 40% 96.1%',
        'muted-foreground': '215.4 16.3% 46.9%',
        'accent': '210 40% 96.1%',
        'accent-foreground': '222.2 47.4% 11.2%',
        'destructive': '0 84.2% 60.2%',
        'destructive-foreground': '210 40% 98%',
        'border': '214.3 31.8% 91.4%',
        'input': '214.3 31.8% 91.4%',
        'ring': '222.2 84% 4.9%',
    },
    'zinc': {
        'background': '0 0% 100%',
        'foreground': '240 10% 3.9%',
        'card': '0 0% 100%',
        'card-foreground': '240 10% 3.9%',
        'popover': '0 0% 100%',
        'popover-foreground': '240 10% 3.9%',
        'primary': '240 5.9% 10%',
        'primary-foreground': '0 0% 98%',
        'secondary': '240 4.8% 95.9%',
        'secondary-foreground': '240 5.9% 10%',
        'muted': '240 4.8% 95.9%',
        'muted-foreground': '240 3.8% 46.1%',
        'accent': '240 4.8% 95.9%',
        'accent-foreground': '240 5.9% 10%',
        'destructive': '0 84.2% 60.2%',
        'destructive-foreground': '0 0% 98%',
        'border': '240 5.9% 90%',
        'input': '240 5.9% 90%',
        'ring': '240 5.9% 10%',
    },
    'slate': {
        'background': '0 0% 100%',
        'foreground': '222.2 84% 4.9%',
        'card': '0 0% 100%',
        'card-foreground': '222.2 84% 4.9%',
        'popover': '0 0% 100%',
        'popover-foreground': '222.2 84% 4.9%',
        'primary': '222.2 47.4% 11.2%',
        'primary-foreground': '210 40% 98%',
        'secondary': '210 40% 96.1%',
        'secondary-foreground': '222.2 47.4% 11.2%',
        'muted': '210 40% 96.1%',
        'muted-foreground': '215.4 16.3% 46.9%',
        'accent': '210 40% 96.1%',
        'accent-foreground': '222.2 47.4% 11.2%',
        'destructive': '0 84.2% 60.2%',
        'destructive-foreground': '210 40% 98%',
        'border': '214.3 31.8% 91.4%',
        'input': '214.3 31.8% 91.4%',
        'ring': '222.2 84% 4.9%',
    },
    'blue': {
        'background': '0 0% 100%',
        'foreground': '222.2 84% 4.9%',
        'card': '0 0% 100%',
        'card-foreground': '222.2 84% 4.9%',
        'popover': '0 0% 100%',
        'popover-foreground': '222.2 84% 4.9%',
        'primary': '221.2 83.2% 53.3%',
        'primary-foreground': '210 40% 98%',
        'secondary': '210 40% 96.1%',
        'secondary-foreground': '222.2 47.4% 11.2%',
        'muted': '210 40% 96.1%',
        'muted-foreground': '215.4 16.3% 46.9%',
        'accent': '210 40% 96.1%',
        'accent-foreground': '222.2 47.4% 11.2%',
        'destructive': '0 84.2% 60.2%',
        'destructive-foreground': '210 40% 98%',
        'border': '214.3 31.8% 91.4%',
        'input': '214.3 31.8% 91.4%',
        'ring': '221.2 83.2% 53.3%',
    },
    'green': {
        'background': '0 0% 100%',
        'foreground': '240 10% 3.9%',
        'card': '0 0% 100%',
        'card-foreground': '240 10% 3.9%',
        'popover': '0 0% 100%',
        'popover-foreground': '240 10% 3.9%',
        'primary': '142.1 76.2% 36.3%',
        'primary-foreground': '355.7 100% 97.3%',
        'secondary': '240 4.8% 95.9%',
        'secondary-foreground': '240 5.9% 10%',
        'muted': '240 4.8% 95.9%',
        'muted-foreground': '240 3.8% 46.1%',
        'accent': '240 4.8% 95.9%',
        'accent-foreground': '240 5.9% 10%',
        'destructive': '0 84.2% 60.2%',
        'destructive-foreground': '0 0% 98%',
        'border': '240 5.9% 90%',
        'input': '240 5.9% 90%',
        'ring': '142.1 76.2% 36.3%',
    },
    'violet': {
        'background': '0 0% 100%',
        'foreground': '224 71.4% 4.1%',
        'card': '0 0% 100%',
        'card-foreground': '224 71.4% 4.1%',
        'popover': '0 0% 100%',
        'popover-foreground': '224 71.4% 4.1%',
        'primary': '262.1 83.3% 57.8%',
        'primary-foreground': '210 20% 98%',
        'secondary': '220 14.3% 95.9%',
        'secondary-foreground': '220.9 39.3% 11%',
        'muted': '220 14.3% 95.9%',
        'muted-foreground': '220 8.9% 46.1%',
        'accent': '220 14.3% 95.9%',
        'accent-foreground': '220.9 39.3% 11%',
        'destructive': '0 84.2% 60.2%',
        'destructive-foreground': '210 20% 98%',
        'border': '220 13% 91%',
        'input': '220 13% 91%',
        'ring': '262.1 83.3% 57.8%',
    },
}

# Dark theme overrides
DARK_THEMES = {
    'default': {
        'background': '222.2 84% 4.9%',
        'foreground': '210 40% 98%',
        'card': '222.2 84% 4.9%',
        'card-foreground': '210 40% 98%',
        'popover': '222.2 84% 4.9%',
        'popover-foreground': '210 40% 98%',
        'primary': '210 40% 98%',
        'primary-foreground': '222.2 47.4% 11.2%',
        'secondary': '217.2 32.6% 17.5%',
        'secondary-foreground': '210 40% 98%',
        'muted': '217.2 32.6% 17.5%',
        'muted-foreground': '215 20.2% 65.1%',
        'accent': '217.2 32.6% 17.5%',
        'accent-foreground': '210 40% 98%',
        'destructive': '0 62.8% 30.6%',
        'destructive-foreground': '210 40% 98%',
        'border': '217.2 32.6% 17.5%',
        'input': '217.2 32.6% 17.5%',
        'ring': '212.7 26.8% 83.9%',
    },
    'zinc': {
        'background': '240 10% 3.9%',
        'foreground': '0 0% 98%',
        'card': '240 10% 3.9%',
        'card-foreground': '0 0% 98%',
        'popover': '240 10% 3.9%',
        'popover-foreground': '0 0% 98%',
        'primary': '0 0% 98%',
        'primary-foreground': '240 5.9% 10%',
        'secondary': '240 3.7% 15.9%',
        'secondary-foreground': '0 0% 98%',
        'muted': '240 3.7% 15.9%',
        'muted-foreground': '240 5% 64.9%',
        'accent': '240 3.7% 15.9%',
        'accent-foreground': '0 0% 98%',
        'destructive': '0 62.8% 30.6%',
        'destructive-foreground': '0 0% 98%',
        'border': '240 3.7% 15.9%',
        'input': '240 3.7% 15.9%',
        'ring': '240 4.9% 83.9%',
    },
}


def generate_css(theme_name: str, use_class_dark_mode: bool = False) -> str:
    """Generate the CSS content with Tailwind v4 @theme block."""
    theme = THEMES.get(theme_name, THEMES['default'])
    dark_theme = DARK_THEMES.get(theme_name, DARK_THEMES['default'])

    # Generate light theme variables
    light_vars = '\n'.join([
        f'  --color-{name}: hsl({value});'
        for name, value in theme.items()
    ])

    # Generate dark theme variables
    dark_vars = '\n'.join([
        f'    --color-{name}: hsl({value});'
        for name, value in dark_theme.items()
    ])

    dark_selector = '.dark' if use_class_dark_mode else '@media (prefers-color-scheme: dark)'
    dark_block = f'''
{dark_selector} {{
  @theme {{
{dark_vars}
  }}
}}'''

    return f'''@import "tailwindcss";

@theme {{
  /* Colors - {theme_name} theme */
{light_vars}

  /* Chart colors */
  --color-chart-1: hsl(12 76% 61%);
  --color-chart-2: hsl(173 58% 39%);
  --color-chart-3: hsl(197 37% 24%);
  --color-chart-4: hsl(43 74% 66%);
  --color-chart-5: hsl(27 87% 67%);

  /* Border radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
  --radius-2xl: 1rem;
  --radius-full: 9999px;

  /* Sidebar (optional) */
  --color-sidebar: hsl(0 0% 98%);
  --color-sidebar-foreground: hsl(240 5.3% 26.1%);
  --color-sidebar-primary: hsl(240 5.9% 10%);
  --color-sidebar-primary-foreground: hsl(0 0% 98%);
  --color-sidebar-accent: hsl(240 4.8% 95.9%);
  --color-sidebar-accent-foreground: hsl(240 5.9% 10%);
  --color-sidebar-border: hsl(220 13% 91%);
  --color-sidebar-ring: hsl(217.2 91.2% 59.8%);
}}

/* Dark mode */
{dark_block}

/* Base styles */
* {{
  border-color: var(--color-border);
}}

body {{
  background-color: var(--color-background);
  color: var(--color-foreground);
}}
'''


def generate_utils_ts() -> str:
    """Generate the cn() utility file."""
    return '''import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
'''


def generate_components_json(
    root: Path,
    theme: str = 'zinc',
    css_path: str = 'src/app/globals.css',
    rsc: bool = True
) -> dict:
    """Generate components.json configuration."""
    return {
        "$schema": "https://ui.shadcn.com/schema.json",
        "style": "default",
        "rsc": rsc,
        "tsx": True,
        "tailwind": {
            "config": "",  # Empty - we use CSS-first config
            "css": css_path,
            "baseColor": theme,
            "cssVariables": True,
            "prefix": ""
        },
        "aliases": {
            "components": "@/components",
            "utils": "@/lib/utils",
            "ui": "@/components/ui",
            "lib": "@/lib",
            "hooks": "@/hooks"
        },
        "iconLibrary": "lucide"
    }


def generate_postcss_config() -> str:
    """Generate PostCSS config for Tailwind v4."""
    return '''export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
};
'''


def install_dependencies(root: Path):
    """Install required dependencies using bun."""
    print("Installing dependencies...")

    deps = [
        'class-variance-authority',
        'clsx',
        'tailwind-merge',
        'lucide-react',
    ]

    dev_deps = [
        'tailwindcss@latest',
        '@tailwindcss/postcss@latest',
    ]

    try:
        # Install production dependencies
        subprocess.run(
            ['bun', 'add'] + deps,
            cwd=root,
            check=True,
            capture_output=True
        )
        print(f"  Installed: {', '.join(deps)}")

        # Install dev dependencies
        subprocess.run(
            ['bun', 'add', '-D'] + dev_deps,
            cwd=root,
            check=True,
            capture_output=True
        )
        print(f"  Installed (dev): {', '.join(dev_deps)}")

    except subprocess.CalledProcessError as e:
        print(f"  Warning: Failed to install some dependencies: {e}")
        print("  You may need to run: bun add class-variance-authority clsx tailwind-merge lucide-react")
        print("  And: bun add -D tailwindcss@latest @tailwindcss/postcss@latest")


def remove_v3_configs(root: Path):
    """Remove deprecated Tailwind v3 config files."""
    v3_configs = [
        'tailwind.config.js',
        'tailwind.config.ts',
        'tailwind.config.mjs',
        'tailwind.config.cjs',
    ]

    for config in v3_configs:
        config_path = root / config
        if config_path.exists():
            config_path.unlink()
            print(f"  Removed deprecated: {config}")


def setup_project(
    root: Path,
    theme: str = 'default',
    app_router: bool = True,
    components: list[str] | None = None,
    use_class_dark_mode: bool = False,
    skip_install: bool = False
):
    """Set up shadcn/ui with Tailwind v4."""
    print(f"\nSetting up shadcn/ui with Tailwind v4...")
    print(f"  Theme: {theme}")
    print(f"  Router: {'App Router' if app_router else 'Pages Router'}")
    print()

    # Determine paths based on router type
    if app_router:
        css_path = 'src/app/globals.css'
        css_dir = root / 'src' / 'app'
    else:
        css_path = 'src/styles/globals.css'
        css_dir = root / 'src' / 'styles'

    lib_dir = root / 'src' / 'lib'
    ui_dir = root / 'src' / 'components' / 'ui'

    # Create directories
    for dir_path in [css_dir, lib_dir, ui_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {dir_path.relative_to(root)}")

    # Remove v3 configs
    print("\nRemoving v3 configs...")
    remove_v3_configs(root)

    # Generate CSS
    print("\nGenerating CSS...")
    css_content = generate_css(theme, use_class_dark_mode)
    css_file = root / css_path
    css_file.write_text(css_content)
    print(f"  Created: {css_path}")

    # Generate utils.ts
    utils_file = lib_dir / 'utils.ts'
    utils_file.write_text(generate_utils_ts())
    print(f"  Created: src/lib/utils.ts")

    # Generate components.json
    components_json = generate_components_json(root, theme, css_path, rsc=app_router)
    (root / 'components.json').write_text(json.dumps(components_json, indent=2))
    print(f"  Created: components.json")

    # Generate PostCSS config
    postcss_file = root / 'postcss.config.mjs'
    postcss_file.write_text(generate_postcss_config())
    print(f"  Created: postcss.config.mjs")

    # Install dependencies
    if not skip_install:
        print()
        install_dependencies(root)

    # Install components if specified
    if components:
        print(f"\nInstalling components: {', '.join(components)}")
        try:
            subprocess.run(
                ['bunx', 'shadcn@latest', 'add'] + components + ['--yes'],
                cwd=root,
                check=True
            )
        except subprocess.CalledProcessError:
            print("  Warning: Failed to install components. Run manually:")
            print(f"  bunx shadcn@latest add {' '.join(components)}")

    print("\n" + "=" * 50)
    print("  Setup complete!")
    print("=" * 50)
    print(f"""
Next steps:
  1. Ensure globals.css is imported in your layout.tsx:
     import '@/app/globals.css'

  2. Add components:
     bunx shadcn@latest add button card input

  3. Validate setup:
     python3 ~/.claude/skills/tailwind4-validator/scripts/validate.py --root .

  4. Start development:
     bun dev
""")


def main():
    parser = argparse.ArgumentParser(
        description='Set up shadcn/ui with Tailwind CSS v4'
    )
    parser.add_argument(
        '--root', '-r',
        type=str,
        default='.',
        help='Project root directory (default: current directory)'
    )
    parser.add_argument(
        '--theme', '-t',
        type=str,
        default='default',
        choices=list(THEMES.keys()),
        help='Color theme (default: default)'
    )
    parser.add_argument(
        '--app-router',
        action='store_true',
        default=True,
        help='Use Next.js App Router structure (default)'
    )
    parser.add_argument(
        '--pages-router',
        action='store_true',
        help='Use Next.js Pages Router structure'
    )
    parser.add_argument(
        '--components', '-c',
        type=str,
        help='Comma-separated list of components to install'
    )
    parser.add_argument(
        '--class-dark-mode',
        action='store_true',
        help='Use class-based dark mode instead of prefers-color-scheme'
    )
    parser.add_argument(
        '--skip-install',
        action='store_true',
        help='Skip dependency installation'
    )

    args = parser.parse_args()
    root = Path(args.root).resolve()

    if not root.exists():
        print(f"Error: Directory not found: {root}")
        sys.exit(1)

    # Parse components
    components = None
    if args.components:
        components = [c.strip() for c in args.components.split(',')]

    # Determine router type
    app_router = not args.pages_router

    setup_project(
        root=root,
        theme=args.theme,
        app_router=app_router,
        components=components,
        use_class_dark_mode=args.class_dark_mode,
        skip_install=args.skip_install
    )


if __name__ == '__main__':
    main()
