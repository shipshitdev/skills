---
name: audit
description: Sweeps frontend accessibility, performance, theming, responsive design and implementation integrity in one scored P0-P3 report. Use for a broad audit without code changes.
user-invocable: true
argument-hint: "[area (feature, page, component...)]"
metadata:
  version: "2.2.4"
  tags: "audit, quality, accessibility"
  source: https://github.com/pbakaus/impeccable/blob/main/skill/reference/audit.md
  upstream_version: skill-v4.5.0
  upstream_latest: skill-v4.5.0
  last_synced: "2026-10-06"
  license: Apache-2.0
when_to_use: "UI quality report, no code changes"
---

Run systematic **technical** quality checks and generate the report below. Do
not fix issues in this skill.

Before scanning, read the existing design system (CSS / tokens / theme and a representative component) so "correct" is measured against the project's own conventions, not generic defaults. If the repo carries design context (`PRODUCT.md`, `DESIGN.md`, `.impeccable.md`, or a `## Design Context` block in `.github/copilot-instructions.md`), read it too.

This is a code-level audit, not a design critique. Check what's measurable and verifiable in the implementation.

## Diagnostic Scan

Run checks across 5 dimensions. Score each dimension 0-4 using the criteria
below.

### 1. Accessibility (A11y)

**Check for**:

- **Contrast issues**: Text contrast ratios < 4.5:1 (or 7:1 for AAA)
- **Motion sensitivity**: Reduced motion preserves useful state feedback; flag flashing, motion that blocks tasks, and blanket animation kills that hide changes
- **Missing ARIA**: Interactive elements without proper roles, labels, or states
- **Keyboard navigation**: Missing focus indicators, illogical tab order, keyboard traps
- **Semantic HTML**: Improper heading hierarchy, missing landmarks, divs instead of buttons
- **Alt text**: Missing or poor image descriptions
- **Form issues**: Inputs without labels, poor error messaging, missing required indicators

**Score 0-4**: 0=Inaccessible (fails WCAG A), 1=Major gaps (few ARIA labels, no keyboard nav), 2=Partial (some a11y effort, significant gaps), 3=Good (WCAG AA mostly met, minor gaps), 4=Excellent (WCAG AA fully met, approaches AAA)

### 2. Performance

**Check for**:

- **Layout thrashing**: Reading/writing layout properties in loops
- **Expensive animations**: Animating layout properties (width, height, top, left) instead of transform/opacity
- **Missing optimization**: Offscreen images without lazy loading and unoptimized assets; preserve eager loading for critical initial content
- **will-change overuse**: Broad or permanent hints can waste resources; use targeted hints only for demonstrated expensive animation
- **Bundle size**: Unnecessary imports, unused dependencies
- **Render performance**: Unnecessary re-renders, missing memoization

**Score 0-4**: 0=Severe issues (layout thrash, unoptimized everything), 1=Major problems (no lazy loading, expensive animations), 2=Partial (some optimization, gaps remain), 3=Good (mostly optimized, minor improvements possible), 4=Excellent (fast, lean, well-optimized)

### 3. Theming

**Check for**:

- **Hard-coded colors**: Colors not using design tokens
- **Broken dark mode**: Missing dark mode variants, poor contrast in dark theme
- **Inconsistent tokens**: Using wrong tokens, mixing token types
- **Theme switching issues**: Values that don't update on theme change

**Score 0-4**: 0=No theming (hard-coded everything), 1=Minimal tokens (mostly hard-coded), 2=Partial (tokens exist but inconsistently used), 3=Good (tokens used, minor hard-coded values), 4=Excellent (full token system, dark mode works perfectly)

### 4. Responsive Design

**Check for**:

- **Fixed widths**: Hard-coded widths that break on mobile
- **Touch targets**: Interactive elements < 44x44px
- **Broken touch interaction**: Exercise sliders and drag surfaces under touch; check pointer cancellation, lost capture, blur and page scrolling. A mobile viewport proves layout, not gestures. State whether evidence came from viewport emulation, synthesized touch or a physical device, and what remains untested
- **Horizontal scroll**: Content overflow on narrow viewports
- **Text scaling**: Layouts that break when text size increases
- **Missing breakpoints**: No mobile/tablet variants

**Score 0-4**: 0=Desktop-only (breaks on mobile), 1=Major issues (some breakpoints, many failures), 2=Partial (works on mobile, rough edges), 3=Good (responsive, minor touch target or overflow issues), 4=Excellent (fluid, all viewports, proper touch targets and working touch gestures)

### 5. Implementation Integrity (CRITICAL)

Verify repeated shortcuts, design-system drift, misleading content and
interchangeable structure against the product context. Keep measurable source
findings separate from visual judgment; a palette or layout pattern alone is
not a defect. Explain false positives.

**Score 0-4**: 0=Systemic drift, 1=Major repeated failures, 2=Several verified issues, 3=Minor isolated issues, 4=Coherent and intentional

## Generate Report

### Audit Health Score

| # | Dimension | Score | Key Finding |
|---|-----------|-------|-------------|
| 1 | Accessibility | ? | [most critical a11y issue or "--"] |
| 2 | Performance | ? | |
| 3 | Responsive Design | ? | |
| 4 | Theming | ? | |
| 5 | Implementation Integrity | ? | |
| **Total** | | **??/20** | **[Rating band]** |

**Rating bands**: 18-20 Excellent (minor polish), 14-17 Good (address weak dimensions), 10-13 Acceptable (significant work needed), 6-9 Poor (major overhaul), 0-5 Critical (fundamental issues)

### Implementation Integrity Verdict

**Start here.** Does the implementation express a coherent product-specific
system? Cite verified evidence.

### Executive Summary

- Audit Health Score: **??/20** ([rating band])
- Total issues found (count by severity: P0/P1/P2/P3)
- Top 3-5 critical issues
- Recommended next steps

### Detailed Findings by Severity

Tag every issue with **P0-P3 severity**:

- **P0 Blocking**: Prevents task completion — fix immediately
- **P1 Major**: Significant difficulty or WCAG AA violation — fix before release
- **P2 Minor**: Annoyance, workaround exists — fix in next pass
- **P3 Polish**: Nice-to-fix, no real user impact — fix if time permits

For each issue, document:

- **[P?] Issue name**
- **Location**: Component, file, line
- **Category**: Accessibility / Performance / Theming / Responsive / Implementation Integrity
- **Impact**: How it affects users
- **WCAG/Standard**: Which standard it violates (if applicable)
- **Recommendation**: How to fix it
- **Suggested command**: Which command or skill to use to fix it

### Patterns & Systemic Issues

Identify recurring problems that indicate systemic gaps rather than one-off mistakes:

- "Hard-coded colors appear in 15+ components, should use design tokens"
- "Touch targets consistently too small (<44px) throughout mobile experience"

### Positive Findings

List 1-3 implementation practices worth preserving, with file/component
evidence. Omit this section when there is no concrete positive finding.

## Recommended Actions

List recommended commands in priority order (P0 first, then P1, then P2):

1. **[P?] `/command-name`** — Brief description (specific context from audit findings)
2. **[P?] `/command-name`** — Brief description (specific context)

**Rules**: Map findings to the most appropriate available skill or command. End with a polish/cleanup step as the final recommendation if any fixes were recommended.

After presenting the summary, tell the user:

> You can ask me to run these one at a time, all at once, or in any order you prefer.
>
> Re-run `/audit` after fixes to see your score improve.

Limit P3 findings to the top five unless the user asks for a complete backlog.

**NEVER**:

- Report issues without explaining impact (why does this matter?)
- Provide recommendations without file/component evidence and a fix path
- Skip positive findings (celebrate what works)
- Forget to prioritize (everything can't be P0)
- Report false positives without verification

## Related

- `accessibility` — go deeper than dimension 1 when the request is WCAG conformance, ARIA, keyboard access, or screen readers.
- `design-consistency-auditor` — go deeper than dimension 3 when the request is token drift, hardcoded colors, or design-system divergence.
