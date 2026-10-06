# Analysis Report

The `report` mode's output format. Read this when the ask is **understanding** (onboard a developer, document the architecture, assess project health) rather than **execution** (plans another agent runs).

Same recon and audit as any other run — only the artifact changes. Findings still need `file:line` evidence; the report is a survey, not a vibes summary.

---

## Discovery pass

Before writing, take the measurements the report cites. Skip any command whose tool is absent rather than installing it.

```bash
# Structure
tree -L 3 -I 'node_modules|.next|dist|build|coverage|target|vendor'

# Scale, per dominant language
find . -path ./node_modules -prune -o -name '*.ts' -print | wc -l
find . -path ./node_modules -prune -o -name '*.tsx' -print | wc -l

# Layer shape — adapt the suffixes to the framework in play
find . -name '*.controller.ts' | wc -l
find . -name '*.service.ts' | wc -l
```

Counts are context, not conclusions. "412 components, 3 of which own all routing state" is the sentence worth writing.

---

## Report sections

Write to `.agents/memory/codebase-analysis.md` (create the directory if absent), or to a path the user names. If a prior report exists there, read it first and note what changed since — a diff against last time is more useful than a fresh restatement.

1. **Executive Summary** — 3–5 sentences. What the system is, its architectural style, its health in one honest line.
2. **Project Overview** — purpose, tech stack with versions, package manager, deployment target.
3. **Directory Structure** — module layout, entry points, what lives where, what is generated.
4. **Architecture Patterns** — backend and frontend patterns actually in use, with an exemplar `file:line` for each. Name the convention a new contributor must copy.
5. **Security Posture** — auth flow, data isolation (tenancy, soft delete), input validation, secret handling. Reference credential locations by `file:line` and type only; never reproduce a value.
6. **Performance Characteristics** — query patterns, caching layers, background jobs, known hot paths.
7. **Code Quality** — strengths first, then improvement areas and tech debt, each with evidence.
8. **Dependencies** — critical packages, version currency, external services the system cannot run without.
9. **Testing Strategy** — what exists, the exact commands to run it, and where coverage stops.
10. **Recommendations** — immediate / short-term / long-term, ordered by leverage.

Close with a **Not audited** line naming what the run skipped. On a monorepo, say which packages were in scope.

---

## Quick mode

`quick report` produces sections 1–4 plus 10, sized for an onboarding doc rather than an audit. One discovery pass, no subagents:

```bash
tree -L 3 -I 'node_modules|.next|dist'
echo "TypeScript files: $(find . -path ./node_modules -prune -o -name '*.ts' -print -o -name '*.tsx' -print | wc -l)"
```

---

## Handing off

The report ends where plans begin. When it surfaces work worth doing, offer the planning path rather than expanding the report into one: `codebase-design survey` turns vetted findings into self-contained plan files under `plans/`. The report itself stays a document — it never becomes an executor's input.
