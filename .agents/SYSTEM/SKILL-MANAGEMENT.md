# Skill Management Guidelines

> **Standards reference:** For the complete frontmatter spec, valid fields, common mistakes, and versioning rules, see [SKILL-STANDARDS.md](SKILL-STANDARDS.md).

## Core Principle

**One source, two primary CLIs.** Each skill has a single SKILL.md that must work in both Claude Code and Codex. The Agent Skills spec is the shared baseline; Claude-specific extensions are allowed on top.

No per-platform copies. No sync workflows. No platform-specific forks.

## Skill Structure

```
skills/{skill-name}/
├── SKILL.md           # Single source of truth
├── references/        # Detailed docs, loaded on demand
├── scripts/           # Executable code (Python, bash, Node)
├── assets/            # Templates, boilerplate, resources
└── plugin.json        # Generated manifest (do not edit manually)
```

## Writing Rules

See [PLATFORM-ADAPTATIONS.md](PLATFORM-ADAPTATIONS.md) for the full writing guide. Key rules:

1. **No tool names** — write "Read the file", not "Use the Read tool"
2. **No platform-name coupling in universal instructions** — keep shared instructions neutral, and isolate Claude-only notes when needed
3. **Shared frontmatter baseline** — keep `version`, `tags`, and custom metadata inside `metadata`; keep official Claude extension fields top-level when intentionally used
4. **No hardcoded paths** — use relative paths for bundled resources
5. **Imperative style** — "Use when...", "Run the command...", "Check for..."

## When Platform-Specific Content Is Needed

Some skills legitimately need per-platform behavior (e.g., `agent-folder-init` scaffolds different config directories per agent). Use HTML comment markers:

```markdown
<!-- PLATFORM-SPECIFIC-START: claude -->
Platform-specific content here
<!-- PLATFORM-SPECIFIC-END: claude -->
```

This should be rare. If you find yourself adding many platform blocks, reconsider whether the skill should be split.

## Creating a New Skill

1. Create `skills/{skill-name}/SKILL.md` with Agent Skills frontmatter plus Claude extensions only if needed
2. Write shared Claude/Codex content following the writing rules
3. Add `references/` for detailed documentation
4. Add `scripts/` for executable code
5. Run the validator: `./scripts/validate-skill-sync.sh`
6. Add to README.md with install command

## Updating an Existing Skill

1. Edit the single SKILL.md
2. Run the validator to check for platform-specific language
3. Regenerate manifests if frontmatter changed: `bun run generate:plugin`
4. Regenerate bundles if skill is in a bundle: `bun run generate:bundle`

## Validation

Run the platform-agnostic validator:

```bash
./scripts/validate-skill-sync.sh
```

This checks for:

- Tool-name references (Skill tool, Read tool, etc.)
- Platform-name coupling outside marker blocks
- Hardcoded platform paths
- Unsupported top-level frontmatter fields
- SKILL.md line count (warn if >500)

## Distribution

Skills are distributed via `npx skills add`:

```bash
# Install for all platforms
npx skills add shipshitdev/skills -g --agent claude-code cursor codex openclaw --skill '*' -y

# Install specific skill
npx skills add shipshitdev/skills --skill stripe-implementer -y
```

The `generate-manifest.js` script sets compatibility for all platforms. If a skill genuinely cannot work on a platform, add `platforms` to frontmatter:

```yaml
platforms: [claude-code, cursor]  # only if restricted
```

Default (no field) = should work in both Claude Code and Codex.

## Bundle Management

Bundles group skills by category for marketplace distribution:

```bash
bun run generate:bundle    # Regenerate bundle directories
bun run generate:plugin    # Regenerate plugin.json files
bun run marketplace:generate  # Full marketplace sync
```

Bundle structure is already platform-neutral — no changes needed per platform.

## Decision Tree

```
Is this skill content platform-specific?
├─ No (95% of cases) → Write once, works everywhere
└─ Yes → Does it need different behavior per platform?
         ├─ Just different paths/configs → Use HTML markers
         └─ Fundamentally different → Consider separate skills
```
