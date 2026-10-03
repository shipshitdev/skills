# Engineering coverage compared with Anthropic

Inspected actual source bodies on 2026-10-02, not just directory names. These are
two different official distributions:

- [Knowledge-work engineering](https://github.com/anthropics/knowledge-work-plugins/tree/8444efcd48f7012f09797778a36a33e73d0861f4/engineering),
  pinned at `8444efcd48f7012f09797778a36a33e73d0861f4`: ten skills, oriented toward
  standalone briefs and optional connected workplace evidence.
- [Official coding plugins](https://github.com/anthropics/claude-plugins-official/tree/ab024cdcfa7ca80be204acd4907656ba5a968589/plugins),
  pinned at `ab024cdcfa7ca80be204acd4907656ba5a968589`: inspected `code-review`,
  `pr-review-toolkit`, `feature-dev`, `code-simplifier`, and `commit-commands`,
  including command and agent bodies. This is not a comparison of every plugin
  in that repository.

Shipshit already covers most engineering jobs with deeper execution contracts.
The largest missing cohesive workflow is incident response. ADR and system-design
coverage exists across several skills but is harder to discover. Test strategy,
debugging, scoped debt inventory, retrospective review, and delivery gates are
already well represented. These are source-based judgments, not benchmark results
or claims of superior live model behavior.

## Ten knowledge-work engineering skills

Each source link points to the inspected commit.

| Anthropic source and concrete behavior | Shipshit coverage and strength | Gap / useful transfer without duplication |
|----------------------------------------|--------------------------------|------------------------------------------|
| [architecture][kw-architecture]: ADR output with options, constraints, costs, consequences; connector lookup of prior decisions | [architect](../../skills/architect/SKILL.md) owns code-shape alternatives and sketch/implementation; [cto-advisor](../../skills/cto-advisor/SKILL.md) already has an ADR template/lifecycle | Improve discoverability of the existing ADR owner from architecture entry points. Do not add a duplicate ADR template or automatically create implementation tickets from a design brief. |
| [code-review][kw-review]: security/performance/correctness/maintainability rubric and actionable file/line findings | [code-review](../../skills/code-review/SKILL.md) separates spec fidelity from standards; [full-code-review](../../skills/full-code-review/SKILL.md) adds structure/security/devex and verified cross-commit findings | Coverage is substantial. Consider a concise generic-performance checklist for non-TS code rather than another review skill. Keep explicit frozen scope and advisory reports. |
| [debug][kw-debug]: reproduce, isolate, diagnose, fix, optionally correlate logs and recent deploys | [debug](../../skills/debug/SKILL.md) requires a deterministic loop, falsifiable hypotheses and narrow instrumentation; `systematic-debugging` escalates repeated/cross-component failures | Stronger diagnosis/verification already exists. Make an optional recent-deploy/log correlation field easier to find; it must not imply production access or ticket-write authority. |
| [deploy-checklist][kw-deploy]: pre/deploy/post checklist, migration/flag steps, rollback thresholds and monitoring | [deployment-composer](../../skills/deployment-composer/SKILL.md), [deploy-dispatch](../../skills/deploy-dispatch/SKILL.md), [release-pr-gates](../../skills/release-pr-gates/SKILL.md), and `production-audit` cover routing, evidence, and authorization | A compact evidence-linked rollback/readiness report could improve usability. Preserve exact-head independent review and CI discovery; notifications, watches, deploys, and ticket closure remain separate writes. |
| [documentation][kw-docs]: document types and reader-first guidance for README/API/runbook/architecture/onboarding | [docs](../../skills/docs/SKILL.md) follows nearby conventions and real scripts; `technical-writing` adds document taxonomy and language standards | Reuse a small audience/document-type map in docs if needed; no new documentation skill. Require actual examples and avoid connector-only assumptions. |
| [incident-response][kw-incident]: severity, roles, communication, mitigation timeline, blameless postmortem with actions/owners | `debug`, `production-audit`, and `deploy` cover pieces, but no dedicated incident coordination owner exists | Real gap: propose one report-first incident workflow, with drafts/timeline/postmortem and explicit gates for paging, chat, war rooms, rollback, and tracker writes. Do not implement it as an implicit extension of this audit. |
| [standup][kw-standup]: yesterday/today/blockers from notes or commits/PRs/tickets/chat, optional CI context | [standup](../../skills/standup/SKILL.md) keeps personal diff-backed reporting; new `all` / trailing `audit` modes add integration scope and shared retrospective evidence | Added the requested all-author mode instead of a competing skill. Notes/ticket/chat enrichment remains a possible opt-in extension; never infer deployment from activity or send updates automatically. |
| [system-design][kw-system]: functional/nonfunctional requirements, APIs/data/queues, capacity/reliability, explicit tradeoffs and revisit points | `architect`/`codebase-design` cover module shape; `domain-modeling`, `api-design-expert`, `performance-expert`, and `cto-advisor` cover related decisions | A discoverable system-design brief assembled from existing owners could add quantified scale, SLO/failure/cost assumptions and revisit triggers. Module-design vocabulary alone is not a full distributed-system design. |
| [tech-debt][kw-debt]: six debt classes, impact/risk/effort scoring and phased remediation | [tech-debt](../../skills/tech-debt/SKILL.md) inventories concrete file/metric evidence and churn, ranks interest/principal, and gates issue filing; `roadmap-analyzer` weighs business priorities | Add explicit documentation/infrastructure categories to the existing register when those blind spots matter. Keep one scoring owner rather than importing a second incompatible formula. |
| [testing-strategy][kw-testing]: pyramid, component-specific test types, critical paths, plan/coverage gaps | [testing-expert](../../skills/testing-expert/SKILL.md) already owns level/coverage/behavior/data/flakes and specialist routing; [test-runner](../../skills/test-runner/SKILL.md) separates execution from repair | No missing strategy engine. A concise requirement-to-risk-to-test plan output could be easier to consume. Keep host limits and execution/repair boundaries; coverage numbers do not prove behavior. |

## Five official coding plugins

| Inspected plugin / mechanism | Existing Shipshit owner | Transfer or limitation |
|-----------------------------|--------------------------|------------------------|
| [code-review][official-review]: multiple bug/guideline/history/previous-review lenses, confidence filtering, full-SHA citations, eligibility recheck, PR comment output | `code-review`, `full-code-review`, `pr-comments`, `review-dispatch` | Prior-review/history context and SHA citations are useful. The upstream eligibility filter skips closed/draft/already-reviewed and some automation PRs; a merged audit must include their integrated changes. Do not inherit automatic comment publication, fixed model selection, or assumptions that CI evidence can be ignored. |
| [pr-review-toolkit][official-toolkit]: selected code/comment/test/error/type lenses; behavioral coverage, hidden failures, type invariants, comment accuracy; optional parallelism and a simplifier | `full-code-review`, `testing-expert`, `error-handling-expert`, `typescript-expert`, `no-comments`, `structural-review` | Useful future additions to existing rubrics: catches/fallbacks that conceal failures, invariant enforcement at construction/mutation, and comment claims checked against code. Do not silently run the mutating simplifier from a report-only review. Specific upstream logging/Sentry conventions are not universal requirements. |
| [feature-dev][official-feature]: discovery, code-path exploration, explicit architecture alternatives, implementation and focused review | `feature-intake`, `interview`, `writing-plans`, `architect`, `executing-plans` | Preserve the exploration-to-key-files handoff. Existing preparation/readiness/delivery gates are more explicit about complete acceptance and independent current-head review. Avoid copying repeated confirmations for already settled scope or fixed fan-out/provider choices. |
| [code-simplifier][official-simplifier]: recent-change scope, functionality preservation, clarity over clever brevity, autonomous refinements | `deslop`, `refactor-code`, `structural-review` | Reinforce behavior preservation and the smaller changed scope in existing cleanup work. Do not inherit unsolicited mutation or a provider-specific model field; an audit only reports. |
| [commit-commands][official-commit]: single commit, commit/push/PR, and forced deletion of gone branches/worktrees | `commit-summary`, `github-pr-publish`, `git-safety`, `git-cleanup` | Existing owners already add scoped staging, secrets checks, delivery evidence and preservation of active work. Do not treat remote branch disappearance as proof of safe deletion or import force-removal recipes. No changes to git-cleanup here; that surface is separately claimed. |

## Prioritized proposals

1. Add a cohesive incident-response owner with explicit read/report versus external
   action boundaries. This is the clearest coverage gap.
2. Surface existing ADR and system-design companions through an advisory map or
   architecture mode; keep ADR content canonical in `cto-advisor` and execution
   shape canonical in `architect`.
3. Extend existing review references with targeted silent-failure, type-invariant,
   and comment-accuracy questions. Route only relevant lenses and preserve
   behavioral test review already present.
4. Improve compact outputs for rollback readiness, debt categories, and test plans
   before creating more skills.

Only standup all/audit and its necessary shared-history/distribution integration
are implemented in this change. Broader proposals are not repairs, scheduled
work, or authorization to write into connected systems. The audit does not change
auto-merge policy.

## License and attribution inspection

The inspected [knowledge-work root license][kw-license], [official root
license][official-license], and each of the five selected plugin-local licenses
contain Apache License 2.0 terms. All five plugin-local license files matched at
inspection. Retain source attribution and check notices/license conditions before
any future adaptation or redistribution. No Anthropic skill body, agent prompt,
or script is copied into this change: the comparison is original analysis, and
the shared-history procedure is an in-house extraction/extension of weekly-review.
Consequently this change introduces no vendored or adapted Anthropic skill and
no upstream-sync metadata. Source comparisons are pinned so future drift is visible.

[kw-architecture]: https://github.com/anthropics/knowledge-work-plugins/blob/8444efcd48f7012f09797778a36a33e73d0861f4/engineering/skills/architecture/SKILL.md
[kw-review]: https://github.com/anthropics/knowledge-work-plugins/blob/8444efcd48f7012f09797778a36a33e73d0861f4/engineering/skills/code-review/SKILL.md
[kw-debug]: https://github.com/anthropics/knowledge-work-plugins/blob/8444efcd48f7012f09797778a36a33e73d0861f4/engineering/skills/debug/SKILL.md
[kw-deploy]: https://github.com/anthropics/knowledge-work-plugins/blob/8444efcd48f7012f09797778a36a33e73d0861f4/engineering/skills/deploy-checklist/SKILL.md
[kw-docs]: https://github.com/anthropics/knowledge-work-plugins/blob/8444efcd48f7012f09797778a36a33e73d0861f4/engineering/skills/documentation/SKILL.md
[kw-incident]: https://github.com/anthropics/knowledge-work-plugins/blob/8444efcd48f7012f09797778a36a33e73d0861f4/engineering/skills/incident-response/SKILL.md
[kw-standup]: https://github.com/anthropics/knowledge-work-plugins/blob/8444efcd48f7012f09797778a36a33e73d0861f4/engineering/skills/standup/SKILL.md
[kw-system]: https://github.com/anthropics/knowledge-work-plugins/blob/8444efcd48f7012f09797778a36a33e73d0861f4/engineering/skills/system-design/SKILL.md
[kw-debt]: https://github.com/anthropics/knowledge-work-plugins/blob/8444efcd48f7012f09797778a36a33e73d0861f4/engineering/skills/tech-debt/SKILL.md
[kw-testing]: https://github.com/anthropics/knowledge-work-plugins/blob/8444efcd48f7012f09797778a36a33e73d0861f4/engineering/skills/testing-strategy/SKILL.md
[official-review]: https://github.com/anthropics/claude-plugins-official/blob/ab024cdcfa7ca80be204acd4907656ba5a968589/plugins/code-review/commands/code-review.md
[official-toolkit]: https://github.com/anthropics/claude-plugins-official/tree/ab024cdcfa7ca80be204acd4907656ba5a968589/plugins/pr-review-toolkit
[official-feature]: https://github.com/anthropics/claude-plugins-official/blob/ab024cdcfa7ca80be204acd4907656ba5a968589/plugins/feature-dev/commands/feature-dev.md
[official-simplifier]: https://github.com/anthropics/claude-plugins-official/blob/ab024cdcfa7ca80be204acd4907656ba5a968589/plugins/code-simplifier/agents/code-simplifier.md
[official-commit]: https://github.com/anthropics/claude-plugins-official/tree/ab024cdcfa7ca80be204acd4907656ba5a968589/plugins/commit-commands
[kw-license]: https://github.com/anthropics/knowledge-work-plugins/blob/8444efcd48f7012f09797778a36a33e73d0861f4/LICENSE
[official-license]: https://github.com/anthropics/claude-plugins-official/blob/ab024cdcfa7ca80be204acd4907656ba5a968589/LICENSE
