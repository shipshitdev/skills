---
name: shadcn
description: "Applies shadcn/ui best practices when writing, reviewing or refactoring components: Radix primitives, React Hook Form, data tables, theming, composition."
metadata:
  version: "2.2.2"
  source: https://github.com/pproenca/dot-skills/blob/master/skills/.curated/shadcn/SKILL.md
  upstream_repo: pproenca/dot-skills
  upstream_ref: master
  upstream_commit: b94ecb3dae52
  last_synced: "2026-06-12"
  license: MIT
  tags: "shadcn, ui, react"
when_to_use: "shadcn components, dark mode"
---
# shadcn/ui Community Best Practices

58 rules across 10 categories for shadcn/ui, prioritized by impact to guide automated refactoring and code generation.

## Stack baseline

Rules target current shadcn/ui: Tailwind CSS v4 (CSS-first, no `tailwind.config.*`, tokens in `@theme inline`), React 19 (`ref` as a prop, `data-slot` attributes), the unified `radix-ui` package, OKLCH color tokens, `tw-animate-css`, `Field` + React Hook Form `Controller` forms, and Bun (`bunx --bun shadcn@latest ...`). Examples use the Radix base (`--base radix`); the CLI also supports a Base UI base (`--base base`), where triggers take a `render` prop instead of `asChild`. For a Tailwind v3 project, keep the existing config and follow the shadcn upgrade guide first.

## When to Apply

- Installing and configuring shadcn/ui in a project
- Writing new shadcn/ui components or composing primitives
- Implementing forms with React Hook Form and Zod validation
- Building data tables or handling large dataset displays
- Customizing themes or adding dark mode support
- Reviewing code for accessibility compliance

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | CLI & Project Setup | CRITICAL | `setup-` |
| 2 | Component Architecture | CRITICAL | `arch-` |
| 3 | Accessibility Preservation | CRITICAL | `ally-` |
| 4 | Styling & Theming | HIGH | `style-` |
| 5 | Form Patterns | HIGH | `form-` |
| 6 | Data Display | MEDIUM-HIGH | `data-` |
| 7 | Layout & Navigation | MEDIUM | `layout-` |
| 8 | Component Composition | MEDIUM | `comp-` |
| 9 | Performance Optimization | MEDIUM | `perf-` |
| 10 | State Management | LOW-MEDIUM | `state-` |

## Quick Reference

### 1. CLI & Project Setup (CRITICAL)

- [`setup-components-json`](references/setup-components-json.md) - Configure components.json (empty tailwind.config for v4) before adding components
- [`setup-path-aliases`](references/setup-path-aliases.md) - Configure TypeScript path aliases to match components.json
- [`setup-cn-utility`](references/setup-cn-utility.md) - Create the cn utility (re-export from `cn`) before using components
- [`setup-use-cli-not-copy`](references/setup-use-cli-not-copy.md) - Use CLI to add components instead of copy-paste
- [`setup-css-variables-theme`](references/setup-css-variables-theme.md) - Enable CSS variables for consistent theming
- [`setup-rsc-configuration`](references/setup-rsc-configuration.md) - Set RSC flag based on framework support

### 2. Component Architecture (CRITICAL)

- [`arch-use-asChild-for-custom-triggers`](references/arch-use-asChild-for-custom-triggers.md) - Use asChild prop for custom trigger elements
- [`arch-preserve-radix-primitive-structure`](references/arch-preserve-radix-primitive-structure.md) - Maintain Radix compound component hierarchy
- [`arch-extend-variants-with-cva`](references/arch-extend-variants-with-cva.md) - Use Class Variance Authority for type-safe variants
- [`arch-use-cn-for-class-merging`](references/arch-use-cn-for-class-merging.md) - Use cn() utility for safe Tailwind class merging
- [`arch-forward-refs-for-composable-components`](references/arch-forward-refs-for-composable-components.md) - Pass refs through to the underlying element (React 19 ref prop)
- [`arch-isolate-component-variants`](references/arch-isolate-component-variants.md) - Separate base styles from variant-specific styles

### 3. Accessibility Preservation (CRITICAL)

- [`ally-preserve-aria-attributes`](references/ally-preserve-aria-attributes.md) - Keep Radix ARIA attributes intact
- [`ally-provide-sr-only-labels`](references/ally-provide-sr-only-labels.md) - Add screen reader labels for icon buttons
- [`ally-maintain-focus-management`](references/ally-maintain-focus-management.md) - Preserve focus trapping in modals
- [`ally-preserve-keyboard-navigation`](references/ally-preserve-keyboard-navigation.md) - Keep WAI-ARIA keyboard patterns
- [`ally-ensure-color-contrast`](references/ally-ensure-color-contrast.md) - Maintain WCAG color contrast ratios
- [`ally-dialog-title-required`](references/ally-dialog-title-required.md) - Always include DialogTitle for screen readers
- [`ally-form-field-labels`](references/ally-form-field-labels.md) - Associate labels with form controls
- [`ally-aria-invalid-errors`](references/ally-aria-invalid-errors.md) - Use aria-invalid for form error states
- [`ally-checkbox-label-association`](references/ally-checkbox-label-association.md) - Wrap Checkbox with Label for click target
- [`ally-focus-visible-styles`](references/ally-focus-visible-styles.md) - Preserve focus visible styles for keyboard navigation

### 4. Styling & Theming (HIGH)

- [`style-use-css-variables-for-theming`](references/style-use-css-variables-for-theming.md) - Use CSS variables for theme colors
- [`style-avoid-important-overrides`](references/style-avoid-important-overrides.md) - Never use !important for style overrides
- [`style-use-tailwind-theme-extend`](references/style-use-tailwind-theme-extend.md) - Define design tokens in CSS with @theme inline
- [`style-consistent-spacing-scale`](references/style-consistent-spacing-scale.md) - Use consistent Tailwind spacing scale
- [`style-responsive-design-patterns`](references/style-responsive-design-patterns.md) - Apply mobile-first responsive design
- [`style-dark-mode-support`](references/style-dark-mode-support.md) - Support dark mode with CSS variables

### 5. Form Patterns (HIGH)

- [`form-use-react-hook-form-integration`](references/form-use-react-hook-form-integration.md) - Integrate React Hook Form with Field and Controller
- [`form-use-zod-for-schema-validation`](references/form-use-zod-for-schema-validation.md) - Use Zod for type-safe validation
- [`form-show-validation-errors-correctly`](references/form-show-validation-errors-correctly.md) - Show errors at appropriate times
- [`form-handle-async-validation`](references/form-handle-async-validation.md) - Debounce async validation calls
- [`form-reset-form-state-correctly`](references/form-reset-form-state-correctly.md) - Reset form state after submission

### 6. Data Display (MEDIUM-HIGH)

- [`data-use-tanstack-table-for-complex-tables`](references/data-use-tanstack-table-for-complex-tables.md) - Use TanStack Table for sorting/filtering
- [`data-virtualize-large-lists`](references/data-virtualize-large-lists.md) - Virtualize lists with 100+ items
- [`data-use-skeleton-loading-states`](references/data-use-skeleton-loading-states.md) - Use Skeleton for loading states
- [`data-paginate-server-side`](references/data-paginate-server-side.md) - Paginate large datasets server-side
- [`data-empty-states-with-guidance`](references/data-empty-states-with-guidance.md) - Provide actionable empty states

### 7. Layout & Navigation (MEDIUM)

- [`layout-sidebar-provider`](references/layout-sidebar-provider.md) - Wrap layout with SidebarProvider
- [`layout-sidebar-collapsible`](references/layout-sidebar-collapsible.md) - Configure sidebar collapsible behavior
- [`layout-sidebar-groups`](references/layout-sidebar-groups.md) - Organize sidebar navigation with groups
- [`layout-sheet-mobile-nav`](references/layout-sheet-mobile-nav.md) - Use Sheet for mobile navigation overlay
- [`layout-breadcrumb-navigation`](references/layout-breadcrumb-navigation.md) - Implement breadcrumbs for deep navigation

### 8. Component Composition (MEDIUM)

- [`comp-compose-with-compound-components`](references/comp-compose-with-compound-components.md) - Use compound component patterns
- [`comp-use-drawer-for-mobile-modals`](references/comp-use-drawer-for-mobile-modals.md) - Use Drawer on mobile devices
- [`comp-combine-command-with-popover`](references/comp-combine-command-with-popover.md) - Create searchable selects with Command
- [`comp-nest-dialogs-correctly`](references/comp-nest-dialogs-correctly.md) - Manage nested dialog focus correctly
- [`comp-create-reusable-form-fields`](references/comp-create-reusable-form-fields.md) - Extract reusable form field components
- [`comp-use-slot-pattern-for-flexibility`](references/comp-use-slot-pattern-for-flexibility.md) - Use slot pattern for flexible content

### 9. Performance Optimization (MEDIUM)

- [`perf-lazy-load-heavy-components`](references/perf-lazy-load-heavy-components.md) - Lazy load components over 50KB
- [`perf-memoize-expensive-renders`](references/perf-memoize-expensive-renders.md) - Memoize list items and expensive components
- [`perf-optimize-icon-imports`](references/perf-optimize-icon-imports.md) - Use direct imports for Lucide icons
- [`perf-avoid-unnecessary-rerenders-in-forms`](references/perf-avoid-unnecessary-rerenders-in-forms.md) - Isolate form field watching
- [`perf-debounce-search-inputs`](references/perf-debounce-search-inputs.md) - Debounce search and filter inputs

### 10. State Management (LOW-MEDIUM)

- [`state-prefer-uncontrolled-for-simple-inputs`](references/state-prefer-uncontrolled-for-simple-inputs.md) - Use uncontrolled for simple forms
- [`state-lift-state-to-appropriate-level`](references/state-lift-state-to-appropriate-level.md) - Lift state to lowest common ancestor
- [`state-use-controlled-dialog-state`](references/state-use-controlled-dialog-state.md) - Control dialogs for programmatic access
- [`state-colocate-state-with-components`](references/state-colocate-state-with-components.md) - Keep state close to where it's used

## How to Use

Read individual reference files for detailed explanations and code examples:

- [Section definitions](references/_sections.md) - Category structure and impact levels
- [Rule template](assets/templates/_template.md) - Template for adding new rules

## Reference Files

| File | Description |
|------|-------------|
| [references/_sections.md](references/_sections.md) | Category definitions and ordering |
| [assets/templates/_template.md](assets/templates/_template.md) | Template for new rules |
