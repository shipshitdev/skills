---
name: cto-advisor
description: "Advises engineering leadership: ADRs, technology and vendor evaluation, team scaling, DORA targets. Org-level, not a repo scan. Use for CTO or tech strategy questions."
license: MIT
metadata:
  version: "2.2.3"
  tags: "leadership, engineering, architecture, strategy, metrics"
when_to_use: "hiring plan, build vs buy"
---

# CTO Advisor

## When This Activates

- User mentions CTO, technical leadership, or engineering leadership
- User asks how much of the engineering budget to spend paying debt down —
  the portfolio-level call, not the codebase inventory (`tech-debt` owns that)
- User needs team scaling or hiring plans
- User wants architecture decisions or ADRs
- User asks about engineering metrics or DORA metrics
- User needs technology evaluation or vendor selection

## Quick Start

### Tech Debt Assessment

```bash
python scripts/tech_debt_analyzer.py
```

### Team Scaling Planning

```bash
python scripts/team_scaling_calculator.py
```

### Architecture Decisions

See `references/architecture_decision_records.md`

### Technology Evaluation

See `references/technology_evaluation_framework.md`

### Engineering Metrics

See `references/engineering_metrics.md`

## Core Responsibilities

| Area | Focus |
|------|-------|
| Technology Strategy | Vision, roadmaps, innovation, tech debt |
| Team Leadership | Scaling, performance, culture |
| Architecture Governance | Decisions, standards, reviews |
| Vendor Management | Evaluation, relationships, SLAs |
| Engineering Excellence | Metrics, quality, reliability |

## Key Ratios

| Metric | Target |
|--------|--------|
| Manager:Engineer | 1:8 |
| Senior:Mid:Junior | 3:4:2 |
| Product:Engineering | 1:10 |
| QA:Engineering | 1.5:10 |

## DORA Metrics Targets

| Metric | Elite | High |
|--------|-------|------|
| Deployment Frequency | On-demand | 1/day - 1/week |
| Lead Time | <1 hour | 1 day - 1 week |
| MTTR | <1 hour | <1 day |
| Change Failure Rate | <15% | <30% |

## Success Indicators

| Area | Target |
|------|--------|
| System uptime | >99.9% |
| Tech debt capacity | <10% |
| Team satisfaction | >8/10 |
| Attrition rate | <10% |
| Features on-time | >80% |

## Red Flags

- Increasing technical debt
- Rising attrition rate
- Slowing velocity
- Growing incidents
- Team morale declining
- Budget overruns

## Integration

| Skill | When to Use |
|-------|-------------|
| `performance-expert` | Optimize system performance |
| `security-expert` | Security architecture |
| `testing-expert` | Testing strategy |

## Related

- `tech-debt` — scan a real codebase and rank its debt into a register; this skill sets the investment level, that one finds the items.

---

**For detailed operational guidance, cadences, crisis management, and templates:** `references/full-guide.md`
