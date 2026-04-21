---
name: analyze-codebase
description: Generate comprehensive codebase analysis covering architecture, security, performance, and code quality. Use when user says 'analyze codebase', 'code audit', 'architecture review', or 'project health check'.
metadata:
  version: 1.0.0
  tags: analysis, architecture, documentation, onboarding
---

# Analyze Codebase

Generate comprehensive analysis of the codebase structure, architecture, and organization.

## When to Use

- Onboarding new developers
- Architecture documentation
- Project health assessment
- Before major refactoring
- Understanding system complexity

## Analysis Process

### Step 1: Discovery

```bash
# Project structure
tree -L 3 -I 'node_modules|.next|dist|build|coverage'

# File counts
find . -type f -name "*.ts" | wc -l
find . -type f -name "*.tsx" | wc -l
```

### Step 2: Architecture Analysis

- Identify modules, entry points, API structure
- Map frontend components and routing
- Document service patterns and conventions

### Step 3: Patterns and Standards

- Check for established patterns in docs/examples
- Analyze type system organization
- Review security patterns (auth, multi-tenancy, soft delete)

### Step 4: Dependencies

- Catalog external services and libraries
- Check version currency
- Identify critical dependencies

### Step 5: Generate Report

Write to `.agents/SYSTEM/CODEBASE-ANALYSIS.md` with these sections:

1. **Executive Summary** — 3-5 sentence overview
2. **Project Overview** — Tech stack, purpose, architecture style
3. **Directory Structure** — Module layout and organization
4. **Architecture Patterns** — Backend and frontend patterns
5. **Security Analysis** — Auth, data isolation, validation
6. **Performance Insights** — Database, caching, background jobs
7. **Code Quality** — Strengths, improvements, tech debt
8. **Dependencies** — Critical packages and version matrix
9. **Testing Strategy** — Coverage, patterns, gaps
10. **Recommendations** — Immediate, short-term, long-term

## Quick Mode

For faster analysis (skip detailed metrics):

```bash
tree -L 3 -I 'node_modules|.next|dist'
echo "TypeScript: $(find . -name '*.ts' -o -name '*.tsx' | wc -l)"
echo "Controllers: $(find . -name '*.controller.ts' | wc -l)"
echo "Services: $(find . -name '*.service.ts' | wc -l)"
```
