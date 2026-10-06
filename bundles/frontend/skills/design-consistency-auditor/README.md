# Design Consistency Auditor Skill

A comprehensive Claude Code skill for auditing and maintaining design system consistency across frontend applications. Discovers project structure from documentation.

## Quick Start

### Running a Full Audit

```bash
# Audit a specific app
"Audit the Studio app for design consistency"

# Audit all apps
"Run a full design audit across all frontend apps" (discovers project structure)

# Focus on specific areas
"Check color palette consistency in Publisher app"
"Review accessibility compliance in Dashboard app"
```

### Running a Quick Audit

Use the quick audit checklist for rapid reviews:

```bash
# Copy the checklist template
cp examples/quick-audit-checklist.md my-audit.md

# Fill it out while reviewing components
# Takes about 30 minutes for a full app audit
```

## What This Skill Checks

### 1. Color Palette (20%)

- ✅ Theme token usage (bg-background, bg-primary, text-muted-foreground, etc.)
- ❌ Hardcoded hex colors
- ❌ Arbitrary Tailwind values
- ✅ Dark mode compatibility

### 2. Typography (10%)

- ✅ Consistent font hierarchy
- ✅ Responsive text sizes
- ❌ Custom font families
- ❌ Arbitrary text sizes

### 3. Spacing & Layout (10%)

- ✅ Tailwind spacing scale
- ❌ Arbitrary spacing values
- ✅ Responsive spacing modifiers
- ✅ Consistent container patterns

### 4. Component Patterns (15%)

- ✅ shadcn `Card` for cards
- ✅ shadcn `Dialog` for modals
- ✅ `Button` variants for actions
- ❌ Duplicate component styles

### 5. Accessibility (25%)

- ✅ Semantic HTML
- ✅ ARIA labels
- ✅ Color contrast ratios (4.5:1 text, 3:1 UI)
- ✅ Keyboard navigation
- ✅ Focus states

### 6. Responsive Design (10%)

- ✅ Mobile-first approach
- ✅ Responsive modifiers (sm:, md:, lg:)
- ❌ Fixed widths without alternatives
- ✅ All breakpoints tested

### 7. Animation (5%)

- ✅ Consistent transitions
- ✅ Standard durations (300ms, 500ms)
- ✅ Hover states

### 8. Dark Mode (5%)

- ✅ Theme-aware colors
- ✅ Both themes tested
- ❌ Hardcoded theme colors

## Files Included

```
design-consistency-auditor/
├── SKILL.md                          # Main skill instructions
├── README.md                         # This file
└── examples/
    ├── audit-report-template.md      # Full audit report template
    └── quick-audit-checklist.md      # 30-minute quick audit
```

## How to Use

### For Quick Reviews (30 min)

1. Open `examples/quick-audit-checklist.md`
2. Copy it to your workspace
3. Go through each section while reviewing the code
4. Score each category out of 10
5. Calculate total score
6. Address critical issues first

### For Comprehensive Audits (2-4 hours)

1. Use `examples/audit-report-template.md`
2. Run automated scans (grep commands in SKILL.md)
3. Manual testing for accessibility and responsiveness
4. Document all findings
5. Prioritize fixes (Critical → Major → Minor)
6. Create action items

## Example Commands

### Automated Scans

```bash
# Find hardcoded colors
grep -r "#[0-9a-fA-F]\{6\}" [frontend-project]/apps/[app-name] --include="*.tsx"  # Discover from project

# Find arbitrary Tailwind values
grep -r "bg-\[#\|text-\[#\|p-\[\|m-\[" [frontend-project]/apps --include="*.tsx"  # Discover from project

# Find inline styles
grep -r "style={{" [frontend-project]/apps --include="*.tsx"  # Discover from project

# Find non-semantic buttons
grep -r "<div.*onClick" [frontend-project]/apps --include="*.tsx"  # Discover from project
```

### Manual Testing

1. **Color Contrast**: Use browser DevTools or WebAIM Contrast Checker
2. **Keyboard Navigation**: Tab through all interactive elements
3. **Responsive Design**: Resize to 375px, 768px, 1280px
4. **Dark Mode**: Toggle theme and check all components

## Common Issues & Fixes

### Issue: Hardcoded Colors

```tsx
// ❌ BAD
<div className="bg-[#fafafa]">

// ✅ GOOD
<div className="bg-card">
```

### Issue: Non-Semantic HTML

```tsx
// ❌ BAD
<div onClick={handleClick}>Click me</div>

// ✅ GOOD
<button onClick={handleClick} aria-label="Action">Click me</button>
```

### Issue: Custom Card Styling

```tsx
// ❌ BAD
<div className="bg-white border border-gray-200 shadow rounded-lg">

// ✅ GOOD
<Card>
```

### Issue: Missing Responsive Modifiers

```tsx
// ❌ BAD
<div className="w-[800px]">

// ✅ GOOD
<div className="w-full max-w-3xl">
```

## Design System Reference

### Color Tokens

shadcn/ui themes are CSS variables (`:root` and `.dark`) mapped to utilities by `@theme inline`. Read the project's `globals.css` for the real values.

| Intent | Utility |
|--------|---------|
| App background / body text | `bg-background` / `text-foreground` |
| Card surface | `bg-card text-card-foreground` |
| Primary action | `bg-primary text-primary-foreground` |
| Quiet surface / secondary text | `bg-muted` / `text-muted-foreground` |
| Hover or selected row | `bg-accent text-accent-foreground` |
| Borders and focus ring | `border-border`, `ring-ring` |

### Components

Add components with `bunx --bun shadcn@latest add <name>`; they live in `components/ui` and merge classes with `cn()`.

- `Card` for card surfaces
- `Dialog` / `Sheet` for overlays
- `Button` variants (`default`, `secondary`, `outline`, `ghost`) for actions
- `Input` / `Textarea` / `Select` for form fields

### Typography Scale

```tsx
h1: text-4xl sm:text-5xl font-bold
h2: text-3xl sm:text-4xl font-bold
h3: text-2xl sm:text-3xl font-semibold
h4: text-xl sm:text-2xl font-semibold
body: text-base
large: text-lg
small: text-sm
```

### Spacing Scale

Use Tailwind's default scale:

- `p-4` = 1rem (16px)
- `p-6` = 1.5rem (24px)
- `p-8` = 2rem (32px)
- `m-4`, `m-6`, `m-8` (same values)
- `gap-4`, `gap-6`, `gap-8` (same values)

### Breakpoints

- `sm:` - 640px
- `md:` - 768px
- `lg:` - 1024px
- `xl:` - 1280px

## Success Metrics

### Target Scores

- **90-100**: Excellent - Production ready
- **75-89**: Good - Minor improvements needed
- **60-74**: Fair - Requires attention
- **Below 60**: Poor - Needs refactoring

### Health Indicators

Good design consistency when:

- ✅ No hardcoded colors found
- ✅ All accessibility violations fixed
- ✅ 100% dark mode compatibility
- ✅ All components use theme classes
- ✅ Semantic HTML throughout
- ✅ Keyboard navigation works everywhere

## Related Skills

This skill works well with:

- **Accessibility (a11y)** - For deeper accessibility audits
- **Component Library Standards** - For component architecture
- **Copywriter** - For content consistency

## Maintenance

### Update This Skill When

- New theme colors are added
- Custom classes are created
- Design patterns change
- New apps are added

### Regular Schedule

- **Weekly**: Quick audits of new features
- **Monthly**: Full audit of one app
- **Quarterly**: Complete design system review

## Resources

### Tools

- Chrome DevTools (Inspect elements)
- axe DevTools (Accessibility)
- WebAIM Contrast Checker
- Tailwind CSS IntelliSense (VSCode)

### Documentation

- [shadcn/ui](https://ui.shadcn.com/docs)
- [Tailwind CSS](https://tailwindcss.com/)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Material Design](https://material.io/design)

---

**Created**: 2025-10-22
**Version**: 1.0.0
**Maintained by**: Project Design Team

Need help? Ask Claude: "How do I use the Design Consistency Auditor skill?"
