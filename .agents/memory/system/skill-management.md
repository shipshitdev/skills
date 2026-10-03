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
└── plugin.json        # Distribution manifest; keep synced with SKILL.md
```

## Writing Rules

See [PLATFORM-ADAPTATIONS.md](PLATFORM-ADAPTATIONS.md) for the full writing guide. Key rules:

1. **No tool names** — write "Read the file", not "Use the Read tool"
2. **No platform-name coupling in universal instructions** — keep shared instructions neutral, and isolate Claude-only notes when needed
3. **Shared frontmatter baseline** — keep `version`, `tags`, and custom metadata inside `metadata`; keep official Claude extension fields top-level when intentionally used
4. **No hardcoded paths** — use relative paths for bundled resources
5. **Imperative style** — "Use when...", "Run the command...", "Check for..."
6. **Rewrite imported skills before shipping** — upstream skills may be used as references, but the shipped `SKILL.md` must be reviewed, rewritten, and made consistent with this repo's security posture, naming, and cross-skill conventions
7. **Use contract blocks for composable skills** — action skills, orchestrators, and skills with side effects declare inputs, outputs, file changes, external side effects, confirmation gates, and delegated skills
8. **Honor invocation composition** — user-invoked skills (`disable-model-invocation: true`) may invoke model-invoked primitives, never another user-invoked skill. Shared interview/design language lives in a model-invoked primitive.
9. **Apply writing craft** — leading words, checkable completion criteria, prune no-ops, prompt the positive. See [skill-standards.md](skill-standards.md) "Writing craft" and "Invocation architecture"

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
3. Update the skill's `plugin.json` if name, version, or description changed
4. Regenerate bundles and marketplace catalog: `bun run marketplace:generate`

## Consolidation Policy

Use consolidation to reduce routing ambiguity, not to make broad skills that hide
side effects. Split or merge based on contracts:

- **Keep separate** when skills have different side-effect boundaries
- **Compose** when one skill selects an execution route and delegates to focused skills
- **Merge** when two skills have the same inputs, outputs, and confirmation gates
- **Deprecate** when another skill or `npx @shipshitdev/v0` fully owns the workflow

Current consolidation backlog:

| Cluster | Direction |
|---------|-----------|
| Init/scaffold | `project-init-orchestrator` owns route selection; new Shipshit.dev products route to `npx @shipshitdev/v0`; setup skills become repair/customization helpers |
| Deployment/release | `release` is the single release path (gate the trunk SHA, cut via release-please, guarded workflow, or tag); `deployment-composer` routes deploys; `deploy` and provider skills stay separate by side-effect boundary |
| Agent config | Split read-only audit from write/sync if `fix` mode grows further |
| Landing pages | Keep scaffold and deploy/domain attach as separate contracts; route full products through v0 |
| Session learning | Keep `rules-capture` and `skill-capture` separate; promotion to permanent skills/rules must remain explicit |
| Frontend review/design | Keep `critique`, `audit`, `polish`, `layout`, `quieter`, and `clarify` separate while their outputs differ; consider a future UI-review orchestrator if routing becomes confusing |

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
npx skills add shipshitdev/skills -g --agent claude-code codex cursor --skill '*' -y

# Install specific skill
npx skills add shipshitdev/skills --skill stripe-implementer -y
```

Default behavior is cross-platform. If a skill genuinely cannot work on a platform,
explain that requirement in `compatibility` while keeping canonical content portable;
put any harness entry adapter outside the skill body. Do not add unsupported
frontmatter fields or inert platform-marker blocks.

The retired `scripts/install-skills.sh` path must not be restored. It duplicated
catalog membership, installed project bundles only into Claude paths, and included
recursive replacement/restore operations. Use only the catalog-backed skills CLI
commands above for global or project installation. Migrate existing installs by
installing first, verifying each selected agent, and reviewing obsolete links one at
a time; never recursively remove an agent skills directory.

## Bundle Management

Bundles group skills by category for marketplace distribution:

```bash
bun run marketplace:generate  # Regenerate bundle snapshots and marketplace catalog
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
