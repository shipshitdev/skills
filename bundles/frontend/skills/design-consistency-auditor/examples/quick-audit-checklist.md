# Quick Design Audit Checklist

Use this checklist for rapid design audits of new features or components.

## Pre-Audit Setup

- [ ] Identify scope (app/component/page)
- [ ] Open in both light and dark themes
- [ ] Test on mobile, tablet, and desktop
- [ ] Have design system reference open

## 1. Color Audit (5 min)

### Check for violations

- [ ] No hardcoded hex colors (`#000000`, `#ffffff`, etc.)
- [ ] No arbitrary Tailwind values (`bg-[#fafafa]`)
- [ ] No inline color styles
- [ ] All colors use theme tokens (`bg-primary`, `bg-card`, `text-muted-foreground`, etc.)
- [ ] Dark mode works correctly

### Quick scan commands

```bash
# In the file/component directory
grep -n "#[0-9a-fA-F]\{6\}" *.tsx
grep -n "bg-\[#\|text-\[#" *.tsx
grep -n "style={{.*color" *.tsx
```

**Score**: ___/10

## 2. Typography Audit (3 min)

### Check for violations

- [ ] No custom font families (Inter is default)
- [ ] No arbitrary text sizes (`text-[18px]`)
- [ ] Proper heading hierarchy (h1 → h2 → h3)
- [ ] Responsive typography modifiers (`text-3xl sm:text-4xl`)
- [ ] Consistent font weights

### Quick checks

```bash
# Check for arbitrary sizes
grep -n "text-\[" *.tsx
# Check for custom fonts
grep -n "fontFamily" *.tsx
```

**Score**: ___/10

## 3. Spacing Audit (3 min)

### Check for violations

- [ ] No arbitrary spacing (`p-[17px]`, `m-[23px]`)
- [ ] Consistent padding/margin scale
- [ ] Proper container spacing (`px-4 md:px-8`)
- [ ] Responsive spacing modifiers
- [ ] No inline spacing styles

### Quick checks

```bash
# Check for arbitrary spacing
grep -n "p-\[\|m-\[\|gap-\[" *.tsx
```

**Score**: ___/10

## 4. Component Patterns Audit (5 min)

### Check for violations

- [ ] Cards use the shadcn `Card` component
- [ ] App shells use `bg-background text-foreground` tokens
- [ ] Modals use the shadcn `Dialog`
- [ ] Inputs use the shadcn `Input` (shared focus ring)
- [ ] Buttons use standard variants (`.btn-secondary`, etc.)

### Manual inspection

- [ ] Count custom card implementations
- [ ] Check modal consistency
- [ ] Verify button patterns

**Score**: ___/10

## 5. Accessibility Audit (7 min)

### Critical checks

- [ ] Semantic HTML (`<button>`, not `<div onClick>`)
- [ ] ARIA labels on icon buttons
- [ ] Color contrast ≥ 4.5:1 for text
- [ ] Color contrast ≥ 3:1 for UI elements
- [ ] Focus states visible
- [ ] Keyboard navigation works
- [ ] Screen reader tested (if critical feature)

### Quick checks

```bash
# Check for non-semantic buttons
grep -n "<div.*onClick" *.tsx
# Check for missing ARIA labels
grep -n "<button" *.tsx | grep -v "aria-label"
```

### Manual testing

- [ ] Tab through all interactive elements
- [ ] Check focus indicators visible
- [ ] Test with browser color contrast checker

**Score**: ___/10

## 6. Responsive Design Audit (4 min)

### Check for violations

- [ ] No fixed widths without responsive variants
- [ ] Responsive modifiers on key elements (`sm:`, `md:`, `lg:`)
- [ ] Mobile-first approach
- [ ] All breakpoints tested (640px, 768px, 1024px)

### Manual testing

- [ ] Resize browser to 375px (mobile)
- [ ] Resize browser to 768px (tablet)
- [ ] Resize browser to 1280px (desktop)

**Score**: ___/10

## 7. Animation Audit (2 min)

### Check for violations

- [ ] Transitions on interactive elements
- [ ] Consistent durations (`duration-300`, `duration-500`)
- [ ] No arbitrary durations (`duration-[247ms]`)
- [ ] Smooth hover states

### Quick checks

```bash
# Check for arbitrary durations
grep -n "duration-\[" *.tsx
```

**Score**: ___/10

## 8. Dark Mode Audit (3 min)

### Check for violations

- [ ] All components work in dark theme
- [ ] No hardcoded light/dark colors
- [ ] Images/icons adapt to theme
- [ ] Sufficient contrast in both themes

### Manual testing

- [ ] Toggle to dark mode
- [ ] Check all components render correctly
- [ ] Verify readability

**Score**: ___/10

## Total Score Calculation

```
Color:          ___/10 × 20% = ___
Typography:     ___/10 × 10% = ___
Spacing:        ___/10 × 10% = ___
Patterns:       ___/10 × 15% = ___
Accessibility:  ___/10 × 25% = ___
Responsive:     ___/10 × 10% = ___
Animation:      ___/10 × 5%  = ___
Dark Mode:      ___/10 × 5%  = ___
----------------------------------
Total:                       ___/100
```

## Rating Scale

- **90-100**: Excellent - Ready to ship
- **75-89**: Good - Minor tweaks needed
- **60-74**: Fair - Needs improvements
- **Below 60**: Poor - Requires major refactoring

## Quick Fixes

If score is below 75, prioritize these quick wins:

### 5-Minute Fixes

1. Replace hardcoded colors with theme tokens
2. Add missing `aria-label` attributes
3. Fix arbitrary spacing values
4. Add transitions to buttons

### 15-Minute Fixes

1. Use the shadcn `Card` for custom cards
2. Add responsive modifiers to fixed-width elements
3. Fix semantic HTML (divs → buttons)
4. Add focus states

### 30-Minute Fixes

1. Fix color contrast violations
2. Implement proper keyboard navigation
3. Refactor duplicate component patterns
4. Test and fix dark mode issues

## Notes

**Component/Page**: ___________________
**Audited By**: ___________________
**Date**: ___________________
**Time Taken**: ___ minutes

**Critical Issues:**

-
-
-

**Quick Wins:**

-
-
-

**Follow-up Required:**

-
-
-
