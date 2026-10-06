---
name: micro-landing-builder
description: Scaffolds, clones, and deploys config-driven NextJS landing pages built on shadcn/ui and Tailwind v4. Use when creating single or multiple startup landing pages with email capture, analytics, and modern design. Supports batch creation from templates or CSV/JSON files and Vercel deployment with custom domains. Each landing is a standalone NextJS app driven by an app.json config file.
disable-model-invocation: true
metadata:
  version: "2.2.2"
  tags: "landing-page, nextjs, vercel"
---

# Micro Landing Builder

Create config-driven NextJS landing pages for startups.

## Contract

Inputs:

- One or more landing definitions: slug, name, domain, concept, and config
- Destination root
- Slugs: one path segment of lowercase letters, digits and hyphens; anything else is rejected
- Optional domain mapping

Outputs:

- Generated landing app directories
- `app.json` config files
- Deployment plan or deployed URLs when deploy is explicitly requested

Creates/Modifies:

- Local landing app directories
- Vercel config files
- Does not deploy production by default

External Side Effects:

- May deploy to Vercel and attach custom domains only after explicit deploy request

Confirmation Required:

- Before batch creation outside the current workspace
- Before production deploys
- Before attaching custom domains
- Before overwriting an existing landing directory

Delegates To:

- Recommend `landing-page-vercel` for single static landing pages
- `project-init-orchestrator` / `npx @shipshitdev/v0` for full product repos
- `deployment-composer` or `deploy-app` for Vercel deployment

## Concept

Each landing page is a standalone NextJS app where:

- Content is defined in `app.json` config file
- UI is shadcn/ui: `components.json`, `components/ui` (Button, Card, Badge, Accordion, Input) and the landing sections in `components/sections`, all copied into the app so it owns its code
- Theme tokens are shadcn CSS variables in `app/globals.css` (`@theme inline`); `app.json` `theme` overrides `--primary`, `--background` and the extra `--brand` accent
- Deploy independently to any domain via Vercel

## Prerequisites

Nothing to publish or install first: the scaffold writes the shadcn/ui setup itself and depends only on live npm packages (Next.js 16, React 19, Tailwind v4, `shadcn`, `radix-ui`, `class-variance-authority`, `cn`, `lucide-react`, `tw-animate-css`). Versions are pinned in `scripts/scaffold.py`; re-check them with `npm view <pkg> version` before changing pins. Needs Bun and network access for `bun install`.

## Usage

```bash
# Show help
python3 scripts/scaffold.py --help

# Create a new landing
python3 scripts/scaffold.py \
  --slug mystartup \
  --name "My Startup" \
  --domain "mystartup.com" \
  --concept "AI-powered analytics"

# Light theme (app.json theme.mode "light" with a white background and dark text)
python3 scripts/scaffold.py \
  --slug mystartup \
  --name "My Startup" \
  --theme-mode light

# Custom colors (#rgb, #rgba, #rrggbb or #rrggbbaa); text colors are picked for contrast
python3 scripts/scaffold.py \
  --slug mystartup \
  --name "My Startup" \
  --primary "#00ff00" \
  --background "#f4f4f5"

# Allow outside current directory
python3 scripts/scaffold.py \
  --root ~/www/landings \
  --slug mystartup \
  --allow-outside
```

## Generated Structure

```
mystartup/
├── app.json              # All content/config here
├── package.json          # Next 16, React 19, Tailwind v4, shadcn/ui runtime deps
├── components.json       # shadcn config ("config": "" for Tailwind v4)
├── next.config.ts
├── postcss.config.mjs    # @tailwindcss/postcss (Tailwind v4)
├── tsconfig.json
├── vercel.json           # Vercel deployment config
├── public/
│   └── (images go here)
├── lib/
│   ├── utils.ts          # cn() helper
│   └── theme.ts          # app.json theme -> mode and CSS variable overrides
├── components/
│   ├── ui/               # shadcn: button, card, badge, accordion, input
│   └── sections/         # header, hero, stats, features, pricing, testimonials, faq, cta, footer
└── app/
    ├── layout.tsx        # Applies app.json theme to the shadcn CSS variables
    ├── page.tsx          # Renders sections from app.json
    ├── globals.css       # Tailwind v4 + shadcn tokens: :root, .dark, @theme inline
    └── api/subscribe/    # Waitlist endpoint stub (returns 501 until a provider is wired)
```

The email capture form posts to `app/api/subscribe/route.ts`. It validates the address and answers 501 until you connect an email provider there, so the form never claims to have stored an email it did not.

## app.json Config

The landing is entirely driven by `app.json`. See `references/config-schema.md` for full schema.

```json
{
  "name": "My Startup",
  "slug": "mystartup",
  "domain": "mystartup.com",
  "meta": {
    "title": "My Startup - Tagline",
    "description": "SEO description"
  },
  "theme": {
    "primary": "#4f46e5",
    "accent": "#f59e0b",
    "background": "#0a0a0a",
    "foreground": "#fafafa",
    "mode": "dark"
  },
  "analytics": {
    "plausible": "mystartup.com"
  },
  "sections": [
    { "type": "hero", "headline": "...", "subheadline": "..." },
    { "type": "features", "items": [...] },
    { "type": "pricing", "plans": [...] },
    { "type": "faq", "items": [...] },
    { "type": "cta", "emailCapture": { "enabled": true } }
  ]
}
```

## Section Types

- `hero` - Main hero with headline, CTA buttons
- `stats` - Key metrics/numbers
- `features` - Feature grid with icons
- `pricing` - Pricing plans
- `testimonials` - Customer quotes
- `faq` - Accordion FAQ
- `cta` - Call to action with email capture

## Batch Creation

Create multiple landing pages from a template or CSV/JSON file:

```bash
# From CSV file
python3 scripts/batch_create.py \
  --root ~/www/landings \
  --csv projects.csv \
  --allow-outside

# From JSON file
python3 scripts/batch_create.py \
  --root ~/www/landings \
  --json projects.json \
  --allow-outside

# Clone from existing template
python3 scripts/batch_create.py \
  --root ~/www/landings \
  --template ~/www/landings/template-landing \
  --json projects.json \
  --allow-outside
```

### CSV Format

```csv
slug,name,domain,concept
project1,Project One,project1.com,AI-powered analytics
project2,Project Two,project2.com,Cloud infrastructure
```

Optional theme columns (headers are trimmed and case-insensitive; unknown or duplicate headers abort with an error; the file may have a UTF-8 BOM): `primary`, `accent`, `background`, `theme_mode` (`dark` or `light`). Colors must be exactly `#rgb`, `#rgba`, `#rrggbb` or `#rrggbbaa` (no spaces, no empty strings in JSON; an empty CSV cell means "not set"). Invalid rows are skipped and the run exits nonzero. With `--template`, the colors and mode are applied to the cloned `app.json`, and an inherited `foreground`, `mode` and `accent` are cleared when a new `background` is given (the accent is re-derived unless you supply one).

### JSON Format

```json
[
  {
    "slug": "project1",
    "name": "Project One",
    "domain": "project1.com",
    "concept": "AI-powered analytics"
  },
  {
    "slug": "project2",
    "name": "Project Two",
    "domain": "project2.com",
    "concept": "Cloud infrastructure"
  }
]
```

## Deployment

### Single Project

Before running `vercel`, confirm `.vercel/project.json` exists in the landing directory. If it does not exist, stop and ask the user to run `vercel link` manually — do not run it unattended.

```bash
cd mystartup
vercel
```

### Batch Deployment with Domains

Deploy multiple projects to Vercel with custom domains:

```bash
# Deploy with domain mapping
python3 scripts/deploy_vercel.py \
  ~/www/landings/project1 \
  ~/www/landings/project2 \
  --domains-json domains.json \
  --prod \
  --yes

# Single domain
python3 scripts/deploy_vercel.py \
  ~/www/landings/project1 \
  --domain project1.com \
  --prod \
  --yes
```

### Domain Mapping JSON

```json
{
  "project1": "project1.com",
  "project2": "project2.com"
}
```

**Note:** Domains must be configured in your DNS before adding to Vercel. Vercel will provide DNS records to add.

## Workflow

### Single Landing Page

1. Run scaffold to create landing structure
2. Edit `app.json` with your content
3. Add images to `public/`
4. Deploy with `vercel` or use `deploy_vercel.py`

### Multiple Landing Pages

1. Create CSV/JSON file with project definitions
2. Run `batch_create.py` to generate all landing pages
3. Customize each `app.json` as needed
4. Run `deploy_vercel.py` to deploy all with domains

## Customization

Add more shadcn components with `bunx --bun shadcn@latest add <name>` (they land in `components/ui`).

To add custom sections:

1. Add a component to `components/sections/`
2. Import it in `app/page.tsx`
3. Register it in the `sectionComponents` map under its `type`

Change colors in `app.json` `theme` (`primary`, `accent`, `background`, `foreground`, `mode`): `app/layout.tsx` applies them inline through `lib/theme.ts`, which accepts `#rgb`, `#rgba`, `#rrggbb` and `#rrggbbaa` (`scaffold.py` and `batch_create.py` reject anything else; at runtime an invalid value is ignored with a build warning and the default is used; alpha is treated as opaque for contrast and warns) and picks each text color (`--foreground`, `--primary-foreground`, `--brand-foreground`) as near-black or near-white by WCAG contrast (pure black or white when neither near color reaches 4.5:1; your color is never changed), so they override the matching variables in `app/globals.css`. When `mode` is omitted it follows the `background` brightness (a light background gives the full light token set); an explicit `mode` always wins. Edit `app/globals.css` for the tokens `app.json` does not set (for example `--radius`, `--secondary`) instead of editing component classes. Use `bg-primary`, `text-muted-foreground` and the other token utilities rather than hex values.

## References

- `references/config-schema.md` - Full JSON schema
- `references/sections-reference.md` - Section types and props
