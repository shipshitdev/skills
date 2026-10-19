---
name: artifacts-builder
description: Builds multi-component claude.ai HTML artifacts with React, Tailwind, and shared UI. Use for complex artifacts needing state management, not simple single-file HTML.
license: Complete terms in LICENSE.txt
metadata:
  version: "2.2.4"
  source: https://github.com/anthropics/skills/blob/main/skills/web-artifacts-builder/SKILL.md
  upstream_repo: anthropics/skills
  upstream_ref: main
  upstream_commit: ef740771ac90
  last_synced: "2026-06-12"
  license: Apache-2.0
  tags: "artifacts, frontend, html"
when_to_use: "bundle artifact"
---

# Artifacts Builder

To build a claude.ai artifact:

1. Initialize the frontend project with `scripts/init-artifact.sh`.
2. Develop the artifact by editing the generated code.
3. Bundle everything into a single HTML file with `scripts/bundle-artifact.sh`.
4. Share the bundled file with the user.
5. (Optional) Test the artifact.

**Stack:** React 19 + TypeScript + Vite + Tailwind CSS v4 + shadcn/ui (Radix), installed and run with Bun. Bundling uses `vite-plugin-singlefile`.

**Requirements:** [Bun](https://bun.sh) and Node.js 20.19+ or 22.12+ (the Vite minimum; the init script rejects older versions). The scripts install packages and run builds, so they need a shell with network access to the package registry.

## Design and style

Avoid what is often called "AI slop": excessive centered layouts, purple gradients, uniform rounded corners, and the Inter font.

## Step 1: Initialize the project

The script refuses a project name that already exists and is not an empty directory:

```bash
bash scripts/init-artifact.sh <project-name>
cd <project-name>
```

This creates a configured project with:

- React + TypeScript (via `bun create vite`)
- Tailwind CSS v4, CSS-first: `@import "tailwindcss"` in `src/index.css`, tokens in `@theme inline`, the `@tailwindcss/vite` plugin, no `tailwind.config.*`
- shadcn/ui initialized (`components.json`, OKLCH theme variables, `cn` utility, `tw-animate-css`) with the full component set in `src/components/ui`
- Path alias `@/` configured in tsconfig and Vite
- A starter `src/App.tsx` using `Button` and `Card`

Add or refresh components later with `bunx shadcn@latest add <component>`.

## Step 2: Develop the artifact

Edit the generated files.

## Step 3: Bundle to a single HTML file

```bash
bash scripts/bundle-artifact.sh
```

This creates `bundle.html`, a self-contained artifact with all JavaScript, CSS, and dependencies inlined. The project must have an `index.html` in its root.

What the script does:

- Installs `vite-plugin-singlefile`, `parse5`, and `css-tree` (pinned) as dev dependencies when missing, under a lock so concurrent runs cannot race.
- Writes `vite.singlefile.config.ts`, which extends your `vite.config.*` and inlines all JS, CSS, fonts, and assets into `index.html`, then runs `bunx vite build` with a per-run `--outDir`.
- Inlines files referenced by the HTML or CSS (images, fonts, icons, `srcset` candidates, linked stylesheets, `@import` targets, and their `url()` dependencies) as data URIs, and fails with a list of any local reference it cannot inline.
- Parses HTML with `parse5` and CSS with `css-tree`, writes the HTML back so it parses to the same DOM, and verifies that by reparsing the output. Any difference fails the bundle instead of changing the page; a malformed `url()` token also fails it.
- Builds in a private temporary work directory per run and inlines only from a private snapshot that rejects symlinks, hard links, and non-regular files in the build and in `public/`.
- Replaces `bundle.html` only after every step succeeded, so a failed build never destroys the previous bundle.

Threat model: the confinement covers symlinks and hard links committed in the project and anything a malicious page, stylesheet, or `public/` tree can reference. It is not a defense against a concurrent local attacker racing the snapshot copy while the script runs.

Files referenced only by hard-coded path strings inside JavaScript are not detected. Import them from code (Vite inlines those) or reference them from the HTML or CSS.

## Step 4: Share the artifact

Share the bundled HTML file with the user so they can view it as an artifact.

## Step 5: Test (optional)

Test with available tools (other skills, or built-in tools such as Playwright or Puppeteer). Avoid testing upfront, since it delays the user seeing the finished artifact; test afterwards if requested or if issues arise.

## Reference

- shadcn/ui docs: https://ui.shadcn.com/docs
