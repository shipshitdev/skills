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

# Frontend Quality Audit

Run systematic **technical** quality checks and generate the report below. Do not fix issues in this skill. Optionally scope the audit to an area (feature, page, component) given by the user.

Before scanning, read the existing design system (CSS / tokens / theme and a representative component) so "correct" is measured against the project's own conventions, not generic defaults. If the repo carries design context (for example `PRODUCT.md`, `DESIGN.md`, or a design-context section in its instructions file), read it too.

This is a code-level audit, not a design critique. Check what is measurable and verifiable in the implementation.

## Diagnostic scan

Check 5 dimensions and score each 0-4 using the criteria below.

### 1. Accessibility

Check for:

- **Contrast issues:** text contrast ratios below 4.5:1 (or 7:1 for AAA)
- **Motion sensitivity:** reduced motion should preserve useful state feedback; flag flashing, motion that blocks tasks, and blanket animation kills that hide changes
- **Missing ARIA:** interactive elements without proper roles, labels, or states
- **Keyboard navigation:** missing focus indicators, illogical tab order, keyboard traps
- **Semantic HTML:** improper heading hierarchy, missing landmarks, divs instead of buttons
- **Alt text:** missing or poor image descriptions
- **Form issues:** inputs without labels, poor error messaging, missing required indicators

Score: 0=Inaccessible (fails WCAG A), 1=Major gaps (few ARIA labels, no keyboard nav), 2=Partial (some a11y effort, significant gaps), 3=Good (WCAG AA mostly met, minor gaps), 4=Excellent (WCAG AA fully met, approaches AAA)

### 2. Performance

Check for:

- **Layout thrashing:** reading/writing layout properties in loops
- **Expensive animations:** animating layout properties (width, height, top, left) instead of transform/opacity
- **Missing optimization:** offscreen images without lazy loading, unoptimized assets; keep eager loading for critical initial content
- **will-change overuse:** broad or permanent hints waste resources; use targeted hints only for demonstrated expensive animation
- **Bundle size:** unnecessary imports, unused dependencies
- **Render performance:** unnecessary re-renders, missing memoization

Score: 0=Severe issues (layout thrash, unoptimized everything), 1=Major problems (no lazy loading, expensive animations), 2=Partial (some optimization, gaps remain), 3=Good (mostly optimized, minor improvements possible), 4=Excellent (fast, lean, well-optimized)

### 3. Theming

Check for:

- **Hard-coded colors:** colors not using design tokens
- **Broken dark mode:** missing dark variants, poor contrast in dark theme
- **Inconsistent tokens:** wrong tokens, mixed token types
- **Theme switching issues:** values that do not update on theme change

Score: 0=No theming (hard-coded everything), 1=Minimal tokens (mostly hard-coded), 2=Partial (tokens exist but inconsistently used), 3=Good (tokens used, minor hard-coded values), 4=Excellent (full token system, dark mode works perfectly)

### 4. Responsive design

Check for:

- **Fixed widths:** hard-coded widths that break on mobile
- **Touch targets:** interactive elements under 44x44px
- **Broken touch interaction:** exercise sliders and drag surfaces under touch; check pointer cancellation, lost capture, blur, and page scrolling. A mobile viewport proves layout, not gestures. State whether evidence came from viewport emulation, synthesized touch, or a physical device, and what remains untested
- **Horizontal scroll:** content overflow on narrow viewports
- **Text scaling:** layouts that break when text size increases
- **Missing breakpoints:** no mobile/tablet variants

Score: 0=Desktop-only (breaks on mobile), 1=Major issues (some breakpoints, many failures), 2=Partial (works on mobile, rough edges), 3=Good (responsive, minor touch target or overflow issues), 4=Excellent (fluid, all viewports, proper touch targets and working touch gestures)

### 5. Implementation integrity (critical)

Verify repeated shortcuts, design-system drift, misleading content, and interchangeable structure against the product context. Keep measurable source findings separate from visual judgment; a palette or layout pattern alone is not a defect. Explain false positives.

Score: 0=Systemic drift, 1=Major repeated failures, 2=Several verified issues, 3=Minor isolated issues, 4=Coherent and intentional

## Generate the report

### Audit health score

| # | Dimension | Score | Key finding |
|---|-----------|-------|-------------|
| 1 | Accessibility | ? | [most critical a11y issue or "--"] |
| 2 | Performance | ? | |
| 3 | Responsive Design | ? | |
| 4 | Theming | ? | |
| 5 | Implementation Integrity | ? | |
| **Total** | | **??/20** | **[Rating band]** |

Rating bands: 18-20 Excellent (minor polish), 14-17 Good (address weak dimensions), 10-13 Acceptable (significant work needed), 6-9 Poor (major overhaul), 0-5 Critical (fundamental issues)

### Implementation integrity verdict

Start here. Does the implementation express a coherent product-specific system? Cite verified evidence.

### Executive summary

- Audit health score: **??/20** ([rating band])
- Total issues found (count by severity: P0/P1/P2/P3)
- Top 3-5 critical issues
- Recommended next steps

### Detailed findings by severity

Tag every issue with a severity:

- **P0 Blocking:** prevents task completion; fix immediately
- **P1 Major:** significant difficulty or WCAG AA violation; fix before release
- **P2 Minor:** annoyance, workaround exists; fix in the next pass
- **P3 Polish:** nice to fix, no real user impact; fix if time permits

For each issue document:

- **[P?] Issue name**
- **Location:** component, file, line
- **Category:** Accessibility / Performance / Theming / Responsive / Implementation Integrity
- **Impact:** how it affects users
- **WCAG/Standard:** which standard it violates (if applicable)
- **Recommendation:** how to fix it
- **Suggested command:** which command or skill to use to fix it

### Patterns and systemic issues

Identify recurring problems that indicate systemic gaps rather than one-off mistakes, for example:

- "Hard-coded colors appear in 15+ components, should use design tokens"
- "Touch targets consistently too small (<44px) throughout the mobile experience"

### Positive findings

List 1-3 implementation practices worth preserving, with file/component evidence. Omit this section when there is no concrete positive finding.

## Recommended actions

List recommended fixes in priority order (P0 first, then P1, then P2):

1. **[P?] `/command-name`**: brief description (specific context from the findings)
2. **[P?] `/command-name`**: brief description (specific context)

Map findings to the most appropriate available skill or command. If any fixes are recommended, end with a polish/cleanup step.

After presenting the summary, tell the user:

> You can ask me to run these one at a time, all at once, or in any order you prefer.
>
> Re-run this audit after fixes to see your score improve.

Limit P3 findings to the top five unless the user asks for a complete backlog.

## Never

- Report issues without explaining impact (why it matters).
- Give recommendations without file/component evidence and a fix path.
- Skip positive findings.
- Skip prioritizing (everything cannot be P0).
- Report false positives without verification.

## Related

- `accessibility`: go deeper than dimension 1 when the request is WCAG conformance, ARIA, keyboard access, or screen readers.
