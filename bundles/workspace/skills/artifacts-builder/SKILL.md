---
name: artifacts-builder
description: Builds multi-component claude.ai HTML artifacts with React, Tailwind, and shared UI. Use for complex artifacts needing state management, not simple single-file HTML.
license: Complete terms in LICENSE.txt
metadata:
  version: "2.2.2"
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

To build claude.ai artifacts, follow these steps:

1. Initialize the frontend repo using `scripts/init-artifact.sh`
2. Develop your artifact by editing the generated code
3. Bundle all code into a single HTML file using `scripts/bundle-artifact.sh`
4. Display artifact to user
5. (Optional) Test the artifact

**Stack**: React 19 + TypeScript + Vite + Tailwind CSS v4 + shadcn/ui (Radix), installed and run with Bun. Bundling: `vite-plugin-singlefile`.

**Requirements**: [Bun](https://bun.sh) and Node.js 20.19+ or 22.12+ (the Vite minimum; the init script rejects anything older).

## Design & Style Guidelines

VERY IMPORTANT: To avoid what is often referred to as "AI slop", avoid using excessive centered layouts, purple gradients, uniform rounded corners, and Inter font.

## Quick Start

### Step 1: Initialize Project

Run the initialization script to create a new React project (it refuses a project name that already exists and is not an empty directory):

```bash
bash scripts/init-artifact.sh <project-name>
cd <project-name>
```

This creates a fully configured project with:

- ✅ React + TypeScript (via `bun create vite`)
- ✅ Tailwind CSS v4, CSS-first: `@import "tailwindcss"` in `src/index.css`, tokens in `@theme inline`, the `@tailwindcss/vite` plugin, no `tailwind.config.*`
- ✅ shadcn/ui initialized (`components.json`, OKLCH theme variables, `cn` utility, `tw-animate-css`) with the full component set in `src/components/ui`
- ✅ Path alias (`@/`) configured in tsconfig and Vite
- ✅ A starter `src/App.tsx` using `Button` and `Card`

Add or refresh components later with `bunx shadcn@latest add <component>`.

### Step 2: Develop Your Artifact

To build the artifact, edit the generated files.

### Step 3: Bundle to Single HTML File

To bundle the React app into a single HTML artifact:

```bash
bash scripts/bundle-artifact.sh
```

This creates `bundle.html` - a self-contained artifact with all JavaScript, CSS, and dependencies inlined. This file can be directly shared in Claude conversations as an artifact.

**Requirements**: Your project must have an `index.html` in the root directory.

**What the script does**:

- Installs `vite-plugin-singlefile` as a dev dependency
- Writes `vite.singlefile.config.ts`, which extends your `vite.config.*` and inlines all JS, CSS, fonts and assets into `index.html`
- Runs `bunx vite build` with that config (object, promise or function-style `vite.config.*` all work)
- Inlines the files that the HTML or CSS reference (images, fonts, icons, linked stylesheets and their own `url()` dependencies) as data URIs, keeping `#fragments`, and fails with the list of any local reference it cannot inline or that escapes the project through a symlink
- Decodes HTML character references (`&amp;`, `&#47;`, `&#x2F;`, ...) in attribute values before resolving them, so an entity-encoded reference is inlined or rejected, never skipped; an unrecognized `&name;` in a resolved attribute fails the bundle
- Builds in a private temporary work directory per run, so concurrent runs do not collide
- Replaces `bundle.html` only after every step succeeded, so a failed build never destroys the previous bundle

Files referenced only by hard-coded path strings inside JavaScript are not detected: import them from code (Vite inlines those) or reference them from the HTML or CSS.

### Step 4: Share Artifact with User

Finally, share the bundled HTML file in conversation with the user so they can view it as an artifact.

### Step 5: Testing/Visualizing the Artifact (Optional)

To test/visualize the artifact, use available tools (including other Skills or built-in tools like Playwright or Puppeteer). In general, avoid testing the artifact upfront as it adds latency between the request and when the finished artifact can be seen. Test later, after presenting the artifact, if requested or if issues arise.

## Reference

- **shadcn/ui**: https://ui.shadcn.com/docs (see also the `shadcn` and `tailwind` skills in this marketplace)
