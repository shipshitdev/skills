---
name: evaluation
description: Builds evaluation frameworks for agent systems, including LLM-as-judge design. Use when testing agent performance, comparing model outputs, or debugging inconsistent evals.
metadata:
  version: "2.2.4"
  source: https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/evaluation/SKILL.md
  upstream_repo: muratcankoylan/Agent-Skills-for-Context-Engineering
  upstream_ref: main
  upstream_commit: 58b55a8921758d13453b440704fb1b5b208c0b0e
  last_synced: "2026-10-06"
  license: MIT
  tags: "evaluation, agents, testing, llm-as-judge, bias-mitigation"
when_to_use: "regression tests for agents, rubrics, LLM judge, pairwise, bias mitigation, A/B test prompts"
---

# Evaluation Methods for Agent Systems

Evaluate agent systems differently from traditional software: agents make dynamic decisions, are non-deterministic between runs, and often lack a single correct answer. Build frameworks that account for this, give actionable feedback, catch regressions, and validate that context-engineering choices have their intended effect.

## When to use

- Testing agent performance systematically; measuring improvement over time
- Validating context engineering choices; comparing agent configurations
- Catching regressions before deployment; building quality gates for agent pipelines
- Evaluating production systems continuously
- Building an LLM judge: direct scoring, pairwise comparison, rubric generation, calibration against human ratings, bias mitigation

Not for: diagnosing a specific context-failure mode before measuring it (use a context-optimization skill), or tool API contracts for evaluation tools (use a tool-design skill), if available.

## Modes

| Mode | Use when | Read |
|------|----------|------|
| Default | Outcome measurement, rubrics, test sets, deterministic gates, continuous monitoring | This file, then [references/metrics.md](./references/metrics.md) |
| LLM-as-judge | Designing or debugging a model-based judge: direct vs pairwise, rubric generation, confidence calibration, human agreement, bias mitigation, panel or hierarchical judging | [references/llm-as-judge.md](./references/llm-as-judge.md) first, then the judge references below |

Run default mode first. Move to LLM-as-judge mode only after deterministic checks and rubrics are stable and the open question is how a model should judge.

LLM-as-judge references:

- [Implementation Patterns](./references/judge-patterns.md): building an evaluation pipeline from scratch or wiring judges into CI/CD
- [Bias Mitigation Techniques](./references/judge-bias-mitigation.md): inconsistent or suspicious scoring patterns
- [Judge Metric Selection](./references/judge-metrics.md): statistical metrics to validate judge reliability (rubric and outcome metrics live in [references/metrics.md](./references/metrics.md))
- [Pipeline Diagram](./references/judge-pipeline.md): architecture of a multi-stage evaluation system
- [Prompt Templates & Worked Examples](./references/judge-prompts.md): direct scoring or pairwise prompts and full worked examples

## Core concepts

- **Outcomes over paths.** Agents may find alternative valid routes. Judge whether the agent reached the right outcome via a reasonable process, not whether it followed specific steps.
- **Multi-dimensional rubrics.** One number hides failures. Score factual accuracy, completeness, citation accuracy, source quality and tool efficiency separately, then weight them for the use case.
- **Deterministic checks first.** Run machine-checkable validation (schema validity, duplicate keys, rubric math, manifest sync, retrieval status, required evidence paths) before spending tokens on an LLM judge, so invalid artifacts cannot be laundered by a favorable score.
- **Budgets matter.** In browsing-agent research, token usage is the primary driver of performance variance, tool calls secondary, model choice secondary but multiplicative. So: evaluate with production-realistic token limits, compare model upgrades against token increases, and compare multi-agent setups to single-agent baselines.

## Detailed topics

### Evaluation challenges

- **Non-determinism and multiple valid paths:** define outcome criteria (correctness, completeness, quality) and treat the path as informational, not evaluative.
- **Context-dependent failures:** test simple, medium, complex and very complex cases and varied interaction lengths; agents can succeed on simple queries, fail on complex ones, or degrade as context accumulates.
- **Composite quality:** score dimensions independently (accuracy, completeness, coherence, tool efficiency, process quality), then compute weighted aggregates.

### Rubric design

Define rubrics with descriptive levels from excellent to failed. Core dimensions (adapt weights per use case):

- Factual accuracy: claims match ground truth (heavy for knowledge tasks)
- Completeness: covers requested aspects (heavy for research tasks)
- Citation accuracy: citations match claimed sources (trust-sensitive contexts)
- Source quality: appropriate primary sources (authoritative outputs)
- Tool efficiency: right tools, reasonable number of calls (cost-sensitive systems)

Map assessments to 0.0-1.0, apply per-dimension weights, and compute a weighted overall. Typical passing thresholds: 0.7 general, 0.9 high-stakes. Store per-dimension scores alongside the aggregate.

### Methodologies

- **LLM-as-judge for scale.** Prompts include the task, the output under test, ground truth if available, a scale with explicit level descriptions, and a request for structured judgment with reasoning. Use a different model family from the agent under test (avoids self-enhancement bias). Use direct scoring when objective criteria or ground truth exist, pairwise for subjective preference; in pairwise runs evaluate both orderings and treat disagreement as a tie. Require evidence before the score, and validate the judge against a human-rated sample before trusting it.
- **Human evaluation.** Route edge cases, unusual queries and a random production sample to humans; feed patterns back into automated criteria.
- **End-state evaluation** for stateful agents (files, databases, configs): assert on the final state programmatically after each run, not on how it got there.

### Test set design

- Start with 20-30 cases early; scale to 50+ for reliable signal. Sample from real usage, add known edge cases, cover all complexity levels.
- Stratify: simple (single tool call, factual lookup), medium (multiple calls, comparison), complex (many calls, ambiguity), very complex (extended interaction, synthesis). Report per-stratum scores next to the overall score.

### Context engineering evaluation

- Run different context strategies on the same test set and compare quality, token usage and efficiency, to isolate the effect from other variables.
- Run degradation tests at different context sizes to find performance cliffs and establish safe operating limits.

### Continuous evaluation

- Run evaluations automatically on agent changes; track results over time, compare versions, block deployments that regress on key metrics.
- Sample production interactions; alert below warning (0.85 pass rate) and critical (0.70 pass rate); keep trend dashboards to catch gradual degradation.

## Building a framework

1. Define quality dimensions for the use case before writing code (later choices drift toward what is easy to measure).
2. Write rubrics with clear level definitions.
3. Build test sets from real usage and edge cases, stratified, 50+ cases.
4. Automate evaluation to run on every significant change.
5. Establish baseline metrics before changing anything.
6. Compare each significant change to the baseline.
7. Track metrics over time.
8. Review with humans on a regular cadence.
9. Separate deterministic validation failures from quality judgments.

## Examples

```python
# Simple evaluation
def evaluate_agent_response(response, expected):
    rubric = load_rubric()
    scores = {}
    for dimension, config in rubric.items():
        scores[dimension] = assess_dimension(response, expected, dimension)
    overall = weighted_average(scores, config["weights"])
    return {"passed": overall >= 0.7, "scores": scores}
```

```python
# Test set spanning complexity levels
test_set = [
    {"name": "simple_lookup", "input": "What is the capital of France?",
     "expected": {"type": "fact", "answer": "Paris"}, "complexity": "simple"},
    {"name": "medium_query", "input": "Compare the revenue of Apple and Microsoft last quarter",
     "complexity": "medium"},
    {"name": "multi_step_reasoning",
     "input": "Analyze sales data from Q1-Q4 and create a summary report with trends",
     "complexity": "complex"},
    {"name": "research_synthesis",
     "input": "Research emerging AI technologies, evaluate impact, recommend adoption strategy",
     "complexity": "very_complex"},
]
```

```python
# Deterministic gate before model judgment
def evaluate_pr_candidate(candidate):
    structure = run_validate_repo(candidate)
    if not structure.ok:
        return {"passed": False, "reason": "deterministic validation failed", "details": structure.errors}
    quality = run_rubric_eval(candidate)
    return {"passed": quality.overall >= 0.8, "scores": quality.dimensions}
```

```yaml
# Quality gate dimensions
gate:
  deterministic: [schema_valid, required_files_present, no_duplicate_ids]
  quality:
    factual_accuracy: min 0.85
    completeness: min 0.80
    source_traceability: min 0.90
```

## Gotchas

1. **Overfitting evals to code paths:** tests pass but the agent fails on slight variations. Write criteria against outcomes and semantics; rotate test inputs.
2. **Judge self-enhancement bias:** models rate their own outputs higher. Judge with a different model family.
3. **Test set contamination:** eval examples leak into prompts or training data. Keep eval sets versioned and separate.
4. **Metric gaming:** optimizing the metric, not quality. Cross-validate against human judgments regularly.
5. **Single-dimension scoring:** always report per-dimension scores and fail if any dimension is below its minimum.
6. **Eval set too small:** under 50 cases is high-variance. Scale up and report confidence intervals.
7. **No stratification:** easy cases inflate scores. Report per stratum and weight to prevent easy-case dominance.
8. **Eval as one-time gate:** quality drifts as models, tools and usage change. Run on every change and on a production cadence.

## Related skills (if available)

context-optimization (measure token, cost, latency and quality effects; degradation), tool-design (evaluation tool schemas; tool selection and recovery), multi-agent-patterns (coordination quality), memory-systems (retrieval and retention quality).

## References

- [Metrics Reference](./references/metrics.md): evaluation metrics, scoring scales, weighted rubric calculations
- [LLM-as-Judge](./references/llm-as-judge.md): model-based judge design; lists the `judge-*` references and `scripts/llm_judge_example.py`
