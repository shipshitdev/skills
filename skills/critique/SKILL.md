---
name: critique
description: "Critiques design from a UX view: hierarchy, IA, cognitive load, with scoring, persona testing, and actionable feedback. Use when asked to review or critique a design."
user-invocable: true
argument-hint: "[area (feature, page, component...)]"
metadata:
  version: "2.2.5"
  tags: "critique, ux, design"
  source: https://github.com/pbakaus/impeccable/blob/main/skill/reference/critique.md
  upstream_version: skill-v4.5.0
  upstream_latest: skill-v4.5.0
  last_synced: "2026-10-06"
  license: Apache-2.0
when_to_use: "give feedback on a component"
---

## STEPS

### Step 1: Preparation

Gather context about the interface under review: what it is trying to accomplish, who uses it, and where to find the relevant source files. If a `.impeccable.md` or a `## Design Context` block in `.github/copilot-instructions.md` exists, read it now for brand and audience. Read the existing design system (CSS / tokens / theme and a representative component) so the critique judges against the project's own conventions rather than generic defaults.

### Step 2: Gather Assessments

Launch two independent assessments. **Neither must see the other's output** to avoid bias.

Delegate each assessment to a separate sub-agent only when authorized and available. Use the current environment's sub-agent or delegation mechanism when available. Sub-agents should return their findings as structured text. Do NOT output findings to the user yet.

Otherwise complete each assessment sequentially, recording the design review
before reading scan output. Declare whether the report used isolated agents or
a sequential single-context review; never imply independence that did not occur.
Stop any server started solely for this review before reporting, unless the user
asks to keep it running.

**Tab isolation**: When browser automation is available, each assessment MUST create its own new tab. Never reuse an existing tab, even if one is already open at the correct URL. This prevents the two assessments from interfering with each other's page state.

#### Assessment A: LLM Design Review

Read the relevant source files (HTML, CSS, JS/TS) and, if browser automation is available, visually inspect the live page. **Create a new tab** for this; do not reuse existing tabs. After navigation, label the tab by setting the document title:

```javascript
document.title = '[LLM] ' + document.title;
```

Evaluate these dimensions:

**Design specificity**: Is the composition, interaction and visual language
grounded in this product, or could an unrelated product use it unchanged?
Make this judgment before seeing scan output; a visual pattern alone is not a defect.

**Holistic Design Review**: visual hierarchy (eye flow, primary action clarity), information architecture (structure, grouping, cognitive load), emotional resonance (does it match brand and audience?), discoverability (are interactive elements obvious?), composition (balance, whitespace, rhythm), typography (hierarchy, readability, font choices), color (purposeful use, cohesion, accessibility), states & edge cases (empty, loading, error, success), microcopy (clarity, tone, helpfulness).

**Cognitive Load** (consult [cognitive-load](references/cognitive-load.md)):

- Run the 8-item cognitive load checklist. Report failure count: 0-1 = low (good), 2-3 = moderate, 4+ = critical.
- Count visible options at each decision point. If >4, flag it.
- Check for progressive disclosure: is complexity revealed only when needed?

**Emotional Journey**:

- What emotion does this interface evoke? Is that intentional?
- **Peak-end rule**: Is the most intense moment positive? Does the experience end well?
- **Emotional valleys**: Check for anxiety spikes at high-stakes moments (payment, delete, commit). Are there design interventions (progress indicators, reassurance copy, undo options)?

**Nielsen's Heuristics** (consult [heuristics-scoring](references/heuristics-scoring.md)):
Score applicable heuristics 0-4. Mark genuinely inapplicable ones `n/a` with
a reason, such as expert accelerators on a simple marketing page. The maximum
is four times the number scored; never treat `n/a` as a zero or a perfect score.

Return structured findings covering: design-specificity verdict, heuristic scores, cognitive load assessment, what's working (2-3 items), priority issues (3-5 with what/why/fix), minor observations, and provocative questions.

#### Assessment B: Automated Pattern Scan

Perform a deterministic scan for AI slop tells and general design quality issues using the tools available.

**Static file scan** (when source files are accessible):

Read HTML, JSX, TSX, Vue, or Svelte files and grep for the following patterns:

- Gradient text (`bg-gradient` + `bg-clip-text`, `WebkitBackgroundClip`)
- Glassmorphism (`backdrop-blur`, `bg-white/10`, `bg-opacity` on overlays)
- Hero metric layouts (large isolated numbers, `text-6xl`+ standalone stats)
- Generic AI color palettes (`#6366f1`, `#8b5cf6`, `#f59e0b` as primary colors without customization)
- Identical card grids (`grid-cols-3` with identical card structure repeated 3+ times)
- Redundant copy (alt text restating visible text, label + placeholder with same content)
- Bounce easing (`bounce`, `elastic` in animation classes)
- Gray text on colored backgrounds
- Nested cards (card inside card)

**Browser visualization** (when browser automation tools are available AND the target is a viewable page):

If the project has a linting or design-check tool configured (check `package.json` scripts), run it. Otherwise, use browser devtools to inspect the live page visually. Create a new tab; do not reuse existing tabs. Label the tab:

```javascript
document.title = '[Human] ' + document.title;
```

Return: scan findings with file locations and counts, and any false positives noted.

### Step 3: Generate Combined Critique Report

Synthesize both assessments into a single report. Do NOT simply concatenate. Weave the findings together, noting where the LLM review and detector agree, where the detector caught issues the LLM missed, and where detector findings are false positives.

Structure your feedback as a design director would. Be direct and don't soften criticism — developers need honest feedback to ship great design, and vague or hedged notes waste everyone's time.

#### Design Health Score
>
> *Consult [heuristics-scoring](references/heuristics-scoring.md)*

Present the Nielsen's 10 heuristics scores as a table:

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | ? | [specific finding or "n/a" if solid] |
| 2 | Match System / Real World | ? | |
| 3 | User Control and Freedom | ? | |
| 4 | Consistency and Standards | ? | |
| 5 | Error Prevention | ? | |
| 6 | Recognition Rather Than Recall | ? | |
| 7 | Flexibility and Efficiency | ? | |
| 8 | Aesthetic and Minimalist Design | ? | |
| 9 | Error Recovery | ? | |
| 10 | Help and Documentation | ? | |
| **Total** | | **??/[applicable maximum]** | **[Rating band]** |

Assign a score of 4 only when the interface has no material issue for that
heuristic. Use 20-32 as the normal range for production interfaces with
ordinary gaps.

#### Design Specificity Verdict

**Start here.** Does the result feel authored for this product?

**Design assessment**: Your evaluation before scan output. Cover coherence,
category-interchangeable structure and missed opportunities for product character.

**Deterministic scan**: Summarize what the automated detector found, with counts and file locations. Note any additional issues the detector caught that you missed, and flag any false positives.

**Browser evidence**: Describe the inspected pages and actual results. Claim
a visible overlay only if injection succeeded and the detector ran in the page.
If no overlay was created, report ordinary screenshots or manual inspection
instead, with any unavailable or untested steps.

#### Overall Impression

One paragraph: what works, what fails, and the single biggest opportunity.

#### What's Working

Highlight 2-3 things done well with element names, visible behavior, and why
they work.

#### Priority Issues

The 3-5 most impactful design problems, ordered by importance.

For each issue, tag with **P0-P3 severity** (consult [heuristics-scoring](references/heuristics-scoring.md) for severity definitions):

- **[P?] What**: Name the problem clearly
- **Why it matters**: How this hurts users or undermines goals
- **Fix**: What to do about it (be concrete)
- **Suggested command**: Which available skill or command could address this

#### Persona Red Flags
>
> *Consult [personas](references/personas.md)*

Auto-select 2-3 personas most relevant to this interface type (use the selection table in the reference). If `.github/copilot-instructions.md` contains a `## Design Context` section, also generate 1-2 project-specific personas from the audience/brand info.

For each selected persona, walk through the primary user action and list specific red flags found:

**Alex (Power User)**: No keyboard shortcuts detected. Form requires 8 clicks for primary action. Forced modal onboarding. High abandonment risk.

**Jordan (First-Timer)**: Icon-only nav in sidebar. Technical jargon in error messages ("404 Not Found"). No visible help. Will abandon at step 2.

Be specific. Name the exact elements and interactions that fail each persona. Don't write generic persona descriptions; write what broke for them.

#### Minor Observations

Quick notes on smaller issues worth addressing.

Each priority issue must name the element, user impact, and fix. Limit minor
observations to findings with a visible location or source reference.

#### Questions to Consider

Provocative questions that might unlock better solutions:

- "What if the primary action were more prominent?"
- "Does this need to feel this complex?"
- "What would a confident version of this look like?"

### Step 4: Ask the User

**After presenting findings**, use targeted questions based on what was actually found. ask the user directly to clarify what you cannot infer. These answers will shape the action plan.

Ask questions along these lines (adapt to the specific findings; do NOT ask generic questions):

1. **Priority direction**: Based on the issues found, ask which category matters most to the user right now. For example: "I found problems with visual hierarchy, color usage, and information overload. Which area should we tackle first?" Offer the top 2-3 issue categories as options.

2. **Design intent**: If the critique found a tonal mismatch, ask whether it was intentional. For example: "The interface feels clinical and corporate. Is that the intended tone, or should it feel warmer/bolder/more playful?" Offer 2-3 tonal directions as options based on what would fix the issues found.

3. **Scope**: Ask how much the user wants to take on. For example: "I found N issues. Want to address everything, or focus on the top 3?" Offer scope options like "Top 3 only", "All issues", "Critical issues only".

4. **Constraints** (optional; only ask if relevant): If the findings touch many areas, ask if anything is off-limits. For example: "Should any sections stay as-is?" This prevents the plan from touching things the user considers done.

**Rules for questions**:

- Every question must reference specific findings from the report. Never ask generic "who is your audience?" questions.
- Keep it to 1-3 questions maximum, using the harness's structured question mechanism when available. Ask only about consequential unresolved scope or intent; preserve existing authorization.
- Deliver the report before the questions so the user can assess the findings.
- Offer concrete options, not open-ended prompts.
- If findings are straightforward (e.g., only 1-2 clear issues), skip questions and go directly to Step 5.

### Step 5: Recommended Actions

**After receiving the user's answers**, present a prioritized action summary reflecting the user's priorities and scope from Step 4.

#### Action Summary

List recommended commands in priority order, based on the user's answers:

1. **`/command-name`**: Brief description of what to fix (specific context from critique findings)
2. **`/command-name`**: Brief description (specific context)
...

**Rules for recommendations**:

- Only recommend commands or skills that are actually available in the current environment
- Order by the user's stated priorities first, then by impact
- Each item's description should carry enough context that the command knows what to focus on
- Map each Priority Issue to the appropriate command
- Skip commands that would address zero issues
- If the user chose a limited scope, only include items within that scope
- If the user marked areas as off-limits, exclude commands that would touch those areas
- End with a polish/cleanup step as the final recommendation if any fixes were recommended

After presenting the summary, tell the user:

> You can ask me to run these one at a time, all at once, or in any order you prefer.
>
> Re-run `/critique` after fixes to see your score improve.
