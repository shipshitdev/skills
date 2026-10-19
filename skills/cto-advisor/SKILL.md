---
name: cto-advisor
description: "Advises engineering leadership: ADRs, technology and vendor evaluation, team scaling, DORA targets. Org-level, not a repo scan. Use for CTO or tech strategy questions."
license: MIT
metadata:
  version: "2.2.4"
  tags: "leadership, engineering, architecture, strategy, metrics"
when_to_use: "hiring plan, build vs buy"
---

# CTO Advisor

Org-level engineering guidance. For a scan of a real codebase's debt, use a tech-debt skill instead; this one sets the investment level, that one finds the items.

## When to use

- CTO, technical-leadership or engineering-leadership questions
- How much of the engineering budget to spend paying down debt (portfolio-level call)
- Team scaling or hiring plans
- Architecture decisions or ADRs
- Engineering metrics or DORA targets
- Technology evaluation or vendor selection, build vs buy

## Quick start

| Need | Use |
|------|-----|
| Tech debt assessment | `python scripts/tech_debt_analyzer.py` |
| Team scaling plan | `python scripts/team_scaling_calculator.py` |
| Architecture decisions | `references/architecture_decision_records.md` |
| Technology evaluation | `references/technology_evaluation_framework.md` |
| Engineering metrics | `references/engineering_metrics.md` |

The scripts use only the Python standard library.

## Core responsibilities

| Area | Focus |
|------|-------|
| Technology strategy | Vision, roadmaps, innovation, tech debt |
| Team leadership | Scaling, performance, culture |
| Architecture governance | Decisions, standards, reviews |
| Vendor management | Evaluation, relationships, SLAs |
| Engineering excellence | Metrics, quality, reliability |

## Key ratios (rules of thumb)

| Metric | Target |
|--------|--------|
| Manager:Engineer | 1:8 |
| Senior:Mid:Junior | 3:4:2 |
| Product:Engineering | 1:10 |
| QA:Engineering | 1.5:10 |

## DORA targets

| Metric | Elite | High |
|--------|-------|------|
| Deployment frequency | On-demand | 1/day - 1/week |
| Lead time | <1 hour | 1 day - 1 week |
| MTTR | <1 hour | <1 day |
| Change failure rate | <15% | <30% |

## Success indicators

| Area | Target |
|------|--------|
| System uptime | >99.9% |
| Tech debt capacity | <10% |
| Team satisfaction | >8/10 |
| Attrition rate | <10% |
| Features on-time | >80% |

## Red flags

Increasing technical debt, rising attrition, slowing velocity, growing incidents, declining morale, budget overruns.

## Related skills (use if available)

`performance-expert` (system performance), `security-expert` (security architecture), `testing-expert` (testing strategy).

For cadences, crisis management and templates, read `references/full-guide.md`.
