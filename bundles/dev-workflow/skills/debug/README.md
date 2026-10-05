# Debugging Best Practices

The front door for a reported failure, and the lookup library behind it. Based on research from Andreas Zeller's "Why Programs Fail" and academic debugging curricula.

## Overview

This skill provides 54 rules across 10 categories to help developers debug systematically instead of randomly. Rules are prioritized by impact, from critical problem definition techniques to prevention practices.

It owns every entry: first contact (build a deterministic feedback loop, reproduce, rank falsifiable hypotheses, instrument, fix with a regression test), escalation after a failed fix (the four-phase loop in `references/systematic-debugging.md`), and scoped mode for a test or build breaking mid-task.

| Category | Rules | Impact |
|----------|-------|--------|
| Problem Definition | 6 | CRITICAL |
| Hypothesis-Driven Search | 6 | CRITICAL |
| Observation Techniques | 6 | HIGH |
| Root Cause Analysis | 5 | HIGH |
| Tool Mastery | 6 | MEDIUM-HIGH |
| Bug Triage and Classification | 5 | MEDIUM |
| Common Bug Patterns | 7 | MEDIUM |
| Fix Verification | 4 | MEDIUM |
| Anti-Patterns | 5 | MEDIUM |
| Prevention & Learning | 4 | LOW-MEDIUM |

## Structure

```
debugging/
├── SKILL.md              # Entry point with quick reference
├── AGENTS.md             # Compiled comprehensive guide
├── metadata.json         # Version, references, metadata
├── README.md             # This file
├── scripts/
│   └── hitl-loop.template.sh  # Human-in-the-loop repro template
├── references/
│   ├── _sections.md      # Category definitions
│   ├── prob-*.md         # Problem definition rules (6)
│   ├── hypo-*.md         # Hypothesis-driven search rules (6)
│   ├── obs-*.md          # Observation technique rules (6)
│   ├── rca-*.md          # Root cause analysis rules (5)
│   ├── tool-*.md         # Tool mastery rules (6)
│   ├── triage-*.md       # Bug triage rules (5)
│   ├── pattern-*.md      # Common bug pattern rules (7)
│   ├── verify-*.md       # Fix verification rules (4)
│   ├── anti-*.md         # Anti-pattern rules (5)
│   └── prev-*.md         # Prevention rules (4)
└── assets/
    └── templates/
        └── _template.md  # Rule template
```

## Getting Started

### Using in Claude Code

This skill automatically activates when you're working on:

- First contact with a bug, crash, or unexpected behavior
- Choosing a reproduction strategy or feedback loop
- Placing logging, breakpoints, or a profiler baseline
- Looking up a bug pattern, observation technique, or anti-pattern
- Bug triage and prioritization

### Manual Commands

```bash
# Install dependencies (if contributing)
pnpm install

# Build AGENTS.md from rules
pnpm build

# Validate skill structure
pnpm validate
```

## Creating a New Rule

1. Determine the category based on the rule's primary concern
2. Use the appropriate prefix from the table below
3. Copy `assets/templates/_template.md` as your starting point
4. Fill in frontmatter and content

### Prefix Reference

| Prefix | Category | Impact |
|--------|----------|--------|
| `prob-` | Problem Definition | CRITICAL |
| `hypo-` | Hypothesis-Driven Search | CRITICAL |
| `obs-` | Observation Techniques | HIGH |
| `rca-` | Root Cause Analysis | HIGH |
| `tool-` | Tool Mastery | MEDIUM-HIGH |
| `triage-` | Bug Triage and Classification | MEDIUM |
| `pattern-` | Common Bug Patterns | MEDIUM |
| `verify-` | Fix Verification | MEDIUM |
| `anti-` | Anti-Patterns | MEDIUM |
| `prev-` | Prevention & Learning | LOW-MEDIUM |

## Rule File Structure

Each rule follows this template:

```markdown
---
title: Rule Title Here
impact: CRITICAL|HIGH|MEDIUM-HIGH|MEDIUM|LOW-MEDIUM|LOW
impactDescription: Quantified impact (e.g., "2-10× faster localization")
tags: prefix, technique, related-concepts
---

## Rule Title Here

1-3 sentences explaining WHY this matters for debugging effectiveness.

**Incorrect (what's wrong):**

```language
// Bad example with comments explaining the cost
```

**Correct (what's right):**

```language
// Good example with comments explaining the benefit
```

Reference: [Link](https://example.com)

```

## File Naming Convention

Rule files follow the pattern: `{prefix}-{description}.md`

Examples:

- `prob-reproduce-before-debug.md` - Problem definition, about reproducing bugs first
- `hypo-binary-search.md` - Hypothesis-driven, about binary search localization
- `tool-conditional-breakpoints.md` - Tool mastery, about conditional breakpoints

## Impact Levels

| Level | Description |
|-------|-------------|
| CRITICAL | Core debugging methodology; skipping causes wasted hours |
| HIGH | Major improvement in debugging effectiveness |
| MEDIUM-HIGH | Significant impact on specific debugging workflows |
| MEDIUM | Noticeable improvement in debugging quality |
| LOW-MEDIUM | Incremental improvement and long-term benefits |
| LOW | Minor optimization |

## Scripts

| Command | Description |
|---------|-------------|
| `pnpm build` | Compiles rules into AGENTS.md |
| `pnpm validate` | Validates skill structure and rules |

## Contributing

1. Check existing rules to avoid duplication
2. Use the rule template (`assets/templates/_template.md`)
3. Include both incorrect and correct examples
4. Quantify impact where possible
5. Reference authoritative sources
6. Run validation before submitting

## Key Principles

1. **Reproduce Before Debugging** - Never debug until you can reliably trigger the bug
2. **Apply Scientific Method** - Form hypotheses, predict outcomes, test systematically
3. **Binary Search Localization** - Narrow down by 50% with each checkpoint
4. **Find WHERE Before WHAT** - Locate first, understand second
5. **One Change at a Time** - Isolate variables to avoid confounding
6. **Question Assumptions** - Many bugs hide behind unquestioned beliefs

## Upstream

### Matt Pocock skills

The front-door loop (tight red-capable loop, minimise, redaction, ranked
hypotheses shown to the user, seam-as-finding, hypothesis in the commit message)
and `scripts/hitl-loop.template.sh` are adapted from **[mattpocock/skills](https://github.com/mattpocock/skills)** (MIT).

| Field | Value |
|-------|-------|
| Source | [`skills/engineering/diagnosing-bugs/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/diagnosing-bugs/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `4588b32ecab9` |
| Last synced | 2026-10-05 |
| License | MIT |

**Local modifications:** Adapted to house style and merged with the rule library,
scoped mode and the escalation lane. The HITL script adds a `report` helper that
prints every captured variable. Attribution only; not a sync target. The skill was
earlier credited to the older `diagnose` name.

**Checking for upstream changes:** when upstream has moved ahead of the synced
marker above, diff
[`skills/engineering/diagnosing-bugs/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/diagnosing-bugs/SKILL.md)
on `main` since commit `4588b32ecab9`, port anything worth bringing home, then bump
`metadata.upstream_commit` and `metadata.last_synced` in `SKILL.md` and this table.

### systematic-debugging reference

Derived from **[obra/superpowers](https://github.com/obra/superpowers)** (MIT).

| Field | Value |
|-------|-------|
| Source | [`skills/systematic-debugging/SKILL.md`](https://github.com/obra/superpowers/blob/main/skills/systematic-debugging/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `030a222af19c` |
| Last synced | 2026-06-12 |
| License | MIT |

**Local modifications:** Adapted from obra/superpowers as a standalone, platform-neutral marketplace plugin. The four phases, the Iron Law, and the red flags are unchanged from upstream. Locally narrowed to the **escalation lane**: `description` and `when_to_use` now trigger on failed-fix and recurring-defect wording rather than on any bug, and an `## Entry Point` section names `debug` as the front door that hands cases here. That keeps the two skills' trigger phrases disjoint in this catalog — upstream ships no `debug` counterpart, so the split does not travel back.

**Checking for upstream changes:** when upstream has moved ahead of the synced marker above, diff [`skills/systematic-debugging/SKILL.md`](https://github.com/obra/superpowers/blob/main/skills/systematic-debugging/SKILL.md) on `main` since commit `030a222af19c`, port anything worth bringing home, then update the provenance comment at the top of `references/systematic-debugging.md` and this table. The merged `debug/SKILL.md` carries no obra provenance metadata.


Folded into `debug` as `references/systematic-debugging.md` on 2026-10-03 (#168). Rolling sync ended; port upstream changes by hand when worth it.

## Acknowledgments

This skill draws from:

- [Why Programs Fail](https://www.whyprogramsfail.com/) - Andreas Zeller
- [MIT 6.031 - Debugging](https://web.mit.edu/6.031/www/sp17/classes/11-debugging/)
- [Cornell CS312 - Debugging Techniques](https://www.cs.cornell.edu/courses/cs312/2006fa/lectures/lec26.html)
- [VS Code Debugging](https://code.visualstudio.com/docs/debugtest/debugging)

## License

MIT
