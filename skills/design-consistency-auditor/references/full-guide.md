# Design Consistency Auditor - Full Guide

## Design System Overview

### Technology Stack

**Frontend Framework**: Next.js 16 with App Router
**Styling**: Tailwind CSS v4 (CSS-first, tokens in `@theme`) + @agenticindiedev/ui
**Typography**: Inter font family
**Themes**: Light and Dark mode support
**State**: React Context API

### Color Palette

#### Light Theme

```css
--color-primary: #000000; /* Black */
--color-primary-content: #ffffff; /* White */
--color-base-100: #fafafa; /* Cards/menu background */
--color-base-200: #ffffff; /* App background */
--color-base-300: #e5e7eb; /* Borders */
--color-base-content: #111111; /* Dark gray text */
--color-muted: #9ca3af; /* Muted text */
--color-muted-content: #f9fafb; /* Muted background */
```

#### Dark Theme

```css
--color-primary: #ffffff; /* White */
--color-primary-content: #000000; /* Black */
--color-base-100: #0f0f0f; /* Cards/menu background */
--color-base-200: #020202; /* App background */
--color-base-300: #1a1a1a; /* Dividers */
--color-base-content: #e5e7eb; /* Off-white text */
--color-muted: #6b7280; /* Muted text */
--color-muted-content: #f3f4f6; /* Muted background */
```

### Custom Theme Classes

#### Layout

- `.gf-app` - Main app shell with background and transitions
- `.gf-card` - Card component with hover effects
- `.glass-modal` - Glass morphism modal backdrop
- `.glass-input` - Glass morphism input fields

#### Buttons

- `.btn-secondary` - Soft ghost style with primary tint

#### Forms

- `.form-focus` - Consistent focus ring styling

## Audit Checklist

### 1. Color Consistency

**DO:**

- Use @agenticindiedev/ui semantic tokens/classes (e.g. primary/surface/border)
- Use custom theme classes: `.gf-app`, `.gf-card`, `.btn-secondary`
- Apply colors through Tailwind utilities: `bg-primary`, `text-base-content`
- Use opacity modifiers for subtle effects: `bg-primary/5`, `bg-primary/20`

**DON'T:**

- Hardcode hex colors in components (`#000000`, `#ffffff`)
- Use arbitrary color values: `bg-[#123456]`
- Mix custom CSS colors with Tailwind classes
- Use inline styles for colors
- Skip theme-aware color tokens

**Example Violations:**

```tsx
// BAD - Hardcoded colors
<div style={{ backgroundColor: '#000000' }}>
<div className="bg-[#fafafa]">

// GOOD - Theme-aware classes
<div className="bg-primary">
<div className="bg-base-100">
```

### 2. Typography Consistency

**DO:**

- Use Tailwind typography utilities: `text-sm`, `text-lg`, `font-bold`
- Apply Inter font family (applied in the base layer of `globals.css`)
- Use consistent heading hierarchy: `text-3xl sm:text-4xl` for h2
- Apply consistent line heights and letter spacing

**DON'T:**

- Set custom font families (Inter is default)
- Use arbitrary font sizes: `text-[14px]`
- Skip responsive typography modifiers
- Mix different type scales across components

**Example Violations:**

```tsx
// BAD - Custom fonts and sizes
<h2 style={{ fontFamily: 'Arial', fontSize: '32px' }}>

// GOOD - Consistent Tailwind classes
<h2 className="text-3xl sm:text-4xl font-bold mb-4 text-primary">
```

### 3. Spacing Consistency

**DO:**

- Use Tailwind spacing scale: `p-4`, `m-8`, `gap-6`, `space-y-4`
- Apply shared UI utilities for radius, spacing, and shadows from @agenticindiedev/ui
- Use consistent container padding: `px-4 md:px-8`
- Apply grid/flex gaps consistently

**DON'T:**

- Use arbitrary spacing values: `p-[17px]`
- Mix different spacing patterns
- Skip responsive spacing modifiers
- Use inline margin/padding styles

**Example Violations:**

```tsx
// BAD - Arbitrary spacing
<div className="p-[17px] m-[23px]">

// GOOD - Consistent spacing scale
<div className="p-4 m-6">
```

### 4. Component Patterns

**DO:**

- Use `.gf-card` for card components
- Apply `.gf-app` to app shells
- Use `.glass-modal` for modals with backdrop
- Apply `.glass-input` for input fields
- Use `.btn-secondary` for secondary actions
- Apply `.form-focus` for form inputs

**DON'T:**

- Create duplicate card styles
- Skip custom theme classes
- Build modals without glass effects
- Ignore established button variants

**Example Violations:**

```tsx
// BAD - Duplicate card styling
<div className="bg-white border border-gray-200 shadow rounded-lg">

// GOOD - Theme class
<div className="gf-card">
```

### 5. Accessibility (a11y)

**DO:**

- Use semantic HTML: `<button>`, `<nav>`, `<main>`, `<article>`
- Add ARIA labels to interactive elements
- Ensure 4.5:1 color contrast ratio (text)
- Ensure 3:1 color contrast ratio (UI elements)
- Support keyboard navigation
- Apply focus states: `focus:outline-none focus:ring-2 focus:ring-primary`
- Use `sr-only` for screen reader text

**DON'T:**

- Use `<div>` for buttons/links
- Skip ARIA labels on icons
- Use low-contrast colors
- Remove focus outlines without replacement
- Ignore keyboard navigation

**Example Violations:**

```tsx
// BAD - No semantics or a11y
<div onClick={handleClick}>Click me</div>

// GOOD - Semantic button with focus
<button
  onClick={handleClick}
  className="btn btn-primary focus:outline-none focus:ring-2 focus:ring-primary"
  aria-label="Submit form"
>
  Click me
</button>
```

### 6. Responsive Design

**DO:**

- Use Tailwind responsive modifiers: `sm:`, `md:`, `lg:`, `xl:`
- Apply mobile-first design
- Test all breakpoints: 640px, 768px, 1024px, 1280px
- Use responsive typography: `text-3xl sm:text-4xl`
- Apply responsive spacing: `px-4 md:px-8`

**DON'T:**

- Use fixed widths without responsive alternatives
- Skip mobile testing
- Use `max-w-` without responsive variants
- Ignore tablet/desktop breakpoints

**Example Violations:**

```tsx
// BAD - Fixed width
<div className="w-[800px]">

// GOOD - Responsive width
<div className="w-full max-w-3xl mx-auto">
```

### 7. Animation & Transitions

**DO:**

- Use consistent transition durations: `duration-300`, `duration-500`
- Apply smooth transitions: `transition-all`, `transition-colors`
- Use hover states: `hover:shadow-md`, `hover:bg-primary/20`
- Apply ease timing: `ease-in-out`

**DON'T:**

- Skip transitions on interactive elements
- Use arbitrary durations: `duration-[247ms]`
- Mix different timing functions
- Overuse animations

**Example Violations:**

```tsx
// BAD - No transition
<button className="bg-primary">

// GOOD - Smooth transition
<button className="bg-primary transition-all duration-300 hover:bg-primary/80">
```

### 8. Dark Mode Support

**DO:**

- Test all components in both light and dark themes
- Use theme-aware color tokens
- Avoid hardcoded colors that don't adapt
- Apply `data-theme` attribute correctly

**DON'T:**

- Hardcode theme-specific colors
- Skip dark mode testing
- Use colors that don't have theme variants

**Example Violations:**

```tsx
// BAD - Hardcoded white background
<div className="bg-white text-black">

// GOOD - Theme-aware
<div className="bg-base-100 text-base-content">
```

## Audit Process

### Phase 1: Color Palette Audit

1. **Scan for hardcoded colors**

   - Search: `#[0-9a-fA-F]{3,6}` in TSX/JSX files
   - Search: `style={{.*color.*}}` for inline styles
   - Search: `bg-\[#`, `text-\[#` for arbitrary values

2. **Verify theme tokens**

   - Ensure all colors use @agenticindiedev/ui tokens
   - Check custom classes are applied correctly
   - Validate light/dark theme consistency

3. **Generate report**

   ```
   Color Violations Found: X
   - File: path/to/component.tsx:42
     Issue: Hardcoded hex color #000000
     Fix: Use bg-primary instead
   ```

### Phase 2: Component Pattern Audit

1. **Check card components**

   - Verify `.gf-card` usage
   - Validate hover states
   - Check border and shadow consistency

2. **Check button variants**

   - Primary buttons: `btn btn-primary`
   - Secondary buttons: `btn-secondary`
   - Ghost buttons: `btn-ghost`

3. **Check form elements**
   - Verify `.form-focus` on inputs
   - Check `.glass-input` for special inputs
   - Validate label associations

### Phase 3: Spacing & Layout Audit

1. **Verify container spacing**

   - Check `container mx-auto px-4 md:px-8` pattern
   - Validate consistent padding
   - Check responsive spacing

2. **Check component spacing**
   - Verify `space-y-*` for vertical stacks
   - Check `gap-*` for grids/flex
   - Validate margin/padding scale usage

### Phase 4: Typography Audit

1. **Check heading hierarchy**

   ```tsx
   h1: text-4xl sm:text-5xl font-bold
   h2: text-3xl sm:text-4xl font-bold
   h3: text-2xl sm:text-3xl font-semibold
   h4: text-xl sm:text-2xl font-semibold
   ```

2. **Verify body text**
   - Default: `text-base-content`
   - Large: `text-lg`
   - Small: `text-sm`
   - Muted: `text-muted`

### Phase 5: Accessibility Audit

1. **Run automated checks**

   - Use axe-core or similar tool
   - Check color contrast ratios
   - Verify semantic HTML

2. **Manual keyboard testing**

   - Tab through all interactive elements
   - Verify focus states visible
   - Check modal trap behavior

3. **Screen reader testing**
   - Verify ARIA labels
   - Check heading structure
   - Validate form labels

## Reporting Format

### Design Audit Report Template

```markdown
# Design Consistency Audit Report

**Date**: [Date]
**Scope**: [App/Component names]
**Auditor**: [Name/Agent]

## Summary

- Total Issues: X
- Critical: X
- Major: X
- Minor: X

## Issues by Category

### Color Consistency (X issues)

- [ ] `apps/studio/app/page.tsx:42` - Hardcoded #000000, use bg-primary
- [ ] `apps/dashboard/components/Card.tsx:15` - Arbitrary bg-[#fafafa], use bg-base-100

### Typography (X issues)

- [ ] `apps/website/components/Hero.tsx:23` - Custom font-size, use text-4xl

### Spacing (X issues)

- [ ] `apps/publisher/components/Editor.tsx:56` - Arbitrary p-[17px], use p-4

### Accessibility (X issues)

- [ ] `apps/manager/components/Button.tsx:12` - Missing aria-label
- [ ] `apps/analytics/pages/dashboard.tsx:78` - Low contrast ratio 2.8:1

## Best Practice Violations

### Component Patterns

- [ ] 5 card components not using `.gf-card`
- [ ] 3 modals missing `.glass-modal`

### Responsive Design

- [ ] 8 components without responsive modifiers

## Recommendations

1. **High Priority**

   - Fix all color contrast violations
   - Replace hardcoded colors with theme tokens
   - Add missing ARIA labels

2. **Medium Priority**

   - Consolidate card components to use `.gf-card`
   - Add responsive modifiers to fixed-width components

3. **Low Priority**
   - Standardize spacing scale usage
   - Optimize transition durations

## Files Analyzed

- [List of files]

## Next Steps

- [ ] Address critical issues
- [ ] Update component library documentation
- [ ] Create design system guidelines
```

## Design Best Practices

### Avoid "AI Slop" Aesthetic (CRITICAL)

**Source:** Anthropic prompt-engineering best practices (platform.claude.com/docs).

AI-generated frontends tend to converge on generic, "on distribution" outputs that create what users call the "AI slop" aesthetic. This skill audits for and prevents this pattern.

**AI SLOP WARNING SIGNS:**

- Generic fonts (Inter, Roboto, Arial, system fonts) used everywhere
- Clichéd purple gradients on white backgrounds
- Predictable component layouts with no character
- Cookie-cutter designs lacking context-specific style
- Overuse of the same patterns across all pages
- Safe, boring color choices that "just work"
- Space Grotesk and other trending AI-default fonts

**DESIGN FOR DELIGHT:**

- **Typography**: Choose fonts that are beautiful, unique, and interesting. Opt for distinctive choices that elevate the frontend's aesthetics over safe defaults
- **Color & Theme**: Commit to a cohesive aesthetic. Dominant colors with sharp accents outperform timid, evenly-distributed palettes. Draw from IDE themes and cultural aesthetics for inspiration
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions. Focus on high-impact moments: one well-orchestrated page load with staggered reveals creates more delight than scattered micro-interactions
- **Backgrounds**: Create atmosphere and depth rather than defaulting to solid colors. Layer CSS gradients, use geometric patterns, or add contextual effects

**AUDIT FOR DISTINCTIVENESS:**

When reviewing frontend code, ask:

- Does this look like it was designed specifically for THIS product?
- Would a user recognize this app from its visual style?
- Are we using the same fonts/colors as every other AI-generated app?
- Does the design have personality and character?
- Vary between light and dark themes across contexts
- Think outside the box - avoid converging on common AI choices

### Visual Hierarchy

**DO:**

- Use size and weight to establish hierarchy
- Apply consistent heading scales
- Use whitespace to group related content
- Apply contrast to draw attention

**Example:**

```tsx
<div className="space-y-6">
  <h1 className="text-4xl font-bold text-primary">Main Title</h1>
  <p className="text-lg text-base-content">Important description</p>
  <p className="text-sm text-muted">Secondary information</p>
</div>
```

### Consistency Over Innovation

**DO:**

- Follow established patterns
- Reuse existing components
- Apply design system classes
- Maintain visual rhythm

**DON'T:**

- Create one-off designs
- Reinvent common components
- Skip design system review

### Progressive Disclosure

**DO:**

- Show most important content first
- Use modals for secondary actions
- Apply tooltips for helper text
- Implement expand/collapse for details

### Feedback & Affordance

**DO:**

- Show hover states on interactive elements
- Display loading states for async actions
- Provide error/success feedback
- Use disabled states for unavailable actions

**Example:**

```tsx
<button
  className="btn btn-primary transition-all duration-300 hover:bg-primary/80 disabled:opacity-50"
  disabled={isLoading}
>
  {isLoading ? "Loading..." : "Submit"}
</button>
```

### Performance

**DO:**

- Minimize custom CSS
- Use Tailwind JIT mode
- Optimize image assets
- Lazy load non-critical components

**DON'T:**

- Add unused Tailwind classes
- Import entire icon libraries
- Skip image optimization

## Common Violations

### Button Inconsistency

**Common Issue:**

```tsx
// Different button styles across apps
<button className="px-4 py-2 bg-black text-white rounded">
<button className="bg-primary text-primary-content px-6 py-3 rounded-lg">
<a className="inline-block p-3 bg-gray-900 text-white">
```

**Fix:**

```tsx
// Consistent button pattern
<button className="btn btn-primary">Primary Action</button>
<button className="btn-secondary">Secondary Action</button>
<button className="btn btn-ghost">Tertiary Action</button>
```

### Card Duplication

**Common Issue:**

```tsx
// Duplicate card styling
<div className="bg-white border border-gray-200 shadow rounded-lg p-6">
<div className="bg-base-100 border-base-300 border rounded-box p-4 shadow-sm">
```

**Fix:**

```tsx
// Use theme class
<div className="gf-card p-6">
```

### Spacing Chaos

**Common Issue:**

```tsx
// Inconsistent spacing
<div className="p-[17px] mt-[23px] mb-[15px]">
```

**Fix:**

```tsx
// Consistent spacing scale
<div className="p-4 my-6">
```

## Tools & Resources

### Audit Tools

- **Chrome DevTools** - Inspect elements, check colors
- **axe DevTools** - Accessibility testing
- **Tailwind CSS IntelliSense** - VSCode extension for validation
- **Contrast Checker** - WebAIM contrast checker

### Design References

- **@agenticindiedev/ui**: Check the package README/docs
- **Tailwind Docs**: https://tailwindcss.com/
- **WCAG Guidelines**: https://www.w3.org/WAI/WCAG21/quickref/
- **Material Design**: https://material.io/design

### Codebase Locations

#### Design System Files

- `[frontend-project]/apps/[app]/app/globals.css` - Tailwind v4 entry: `@import "tailwindcss"`, `@theme` tokens, base layer (discover from project)
- Theme tokens live in `@theme` / `@theme inline` blocks in the CSS, not in a JS Tailwind config file
- Keyframes and animations are `@keyframes` rules plus `--animate-*` entries in `@theme`

#### Frontend Apps

- `[frontend-project]/apps/[app-1]/` - App 1 (discover from project structure)
- `[frontend-project]/apps/[app-2]/` - App 2
- `[frontend-project]/apps/[app-3]/` - App 3

## Audit Commands

### Quick Audit Scripts

```bash
# Find hardcoded hex colors
grep -r "#[0-9a-fA-F]\{6\}" [frontend-project]/apps --include="*.tsx" --include="*.jsx"

# Find arbitrary Tailwind values
grep -r "bg-\[#\|text-\[#\|p-\[\|m-\[" [frontend-project]/apps --include="*.tsx"

# Find inline styles
grep -r "style={{" [frontend-project]/apps --include="*.tsx"

# Find missing theme classes
grep -r "className=\".*card" [frontend-project]/apps --include="*.tsx" | grep -v "[project-prefix]-card"

# Check for non-semantic buttons
grep -r "<div.*onClick" [frontend-project]/apps --include="*.tsx"
```

## Maintenance

### Regular Audits

**Weekly**: Quick spot checks on new features
**Monthly**: Full design audit of one app
**Quarterly**: Complete design system review

### Documentation Updates

Keep this skill updated when:

- New theme colors are added
- Custom classes are created
- Design patterns change
- New apps are added to monorepo
