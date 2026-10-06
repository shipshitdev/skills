# artifacts-builder

Build elaborate multi-component claude.ai HTML artifacts with shared UI and state management.

## Upstream

Derived from **[anthropics/skills](https://github.com/anthropics/skills)** (Apache-2.0).

| Field | Value |
|-------|-------|
| Source | [`skills/web-artifacts-builder/SKILL.md`](https://github.com/anthropics/skills/blob/main/skills/web-artifacts-builder/SKILL.md) |
| Upstream ref | `main` |
| Synced at commit | `ef740771ac90` |
| Last synced | 2026-06-12 |
| License | Apache-2.0 |

**Local modifications:** Vendored from Anthropic's `web-artifacts-builder` (renamed locally to `artifacts-builder`). Moved the scaffold to Bun, Vite and Tailwind CSS v4 (CSS-first); the shared UI is now the shadcn/ui components added with `bunx shadcn@latest` (replacing the bundled v3-era component archive and an unpublished package); bundling uses `vite-plugin-singlefile` plus a parser-based asset inliner (parse5, css-tree) instead of Parcel and html-inline; Node 20.19+ or 22.12+ is enforced. Otherwise tracks upstream.

**Checking for upstream changes:** when upstream has moved ahead of the synced marker above, diff [`skills/web-artifacts-builder/SKILL.md`](https://github.com/anthropics/skills/blob/main/skills/web-artifacts-builder/SKILL.md) on `main` since commit `ef740771ac90`, port anything worth bringing home, then bump `metadata.upstream_commit` (or `metadata.upstream_version`) and `metadata.last_synced` in `SKILL.md` and this table.
