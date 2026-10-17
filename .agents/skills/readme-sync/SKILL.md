---
name: readme-sync
description: |
  Regenerate catalog counts, layout claims, and README summaries from canonical sources.
  Run after adding, removing, or renaming skills, commands, or bundles.
metadata:
  internal: true
  version: "2.2.5"
  tags: "readme, sync, maintenance, automation"
---

# README and Catalog Sync

Regenerate `catalog.json` and every marked count/layout summary from the actual
skill, command, bundle, and tracked-path sources.

## When to Run

- After adding new skills
- After removing or renaming skills
- After adding or removing commands or bundles
- After importing skills from external repos
- When any catalog count or directory claim does not match the repository

## Process

### 1. Generate the Catalog and Documentation Blocks

```bash
bun run catalog:generate
```

The generator derives:

- skills from `skills/*/SKILL.md`;
- commands from `commands/*.md`;
- bundles from `scripts/plugin-categories.json`;
- plugins as skills plus bundles;
- top-level layout from `git ls-files`.

It writes the single generated source `catalog.json`, then updates marked blocks in
`README.md`, `AGENTS.md`, and memory/architecture docs plus the package description.
Do not edit text between `catalog-*:start` and `catalog-*:end` markers manually.

### 2. Validate Without Writing

```bash
bun run catalog:check
```

The lightweight repository validator also runs this check, and CI regenerates the
catalog and fails if any generated file changes.

## Safety

- Preserve prose outside generated markers.
- Never infer counts from README text.
- Never add a top-level path to the generated layout unless it is tracked.
- Review `catalog.json` and generated documentation diffs before committing.
