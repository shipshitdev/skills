---
name: table-filters
description: "Designs filtering UX for data tables: picks a filter type per column and builds a unified filter field with inline header filters. Use when building a table that needs filters."
metadata:
  version: "2.2.2"
  tags: "tables, filters, ux"
when_to_use: "column filters, filter bar"
---

# Table Filters

When the user is building a table that needs filters, analyze the columns and design the filtering UX.

## Step 1: Analyze Each Column

For each column in the table, determine the filter type:

| Data Pattern | Filter Type | Example Columns |
|--------------|-------------|-----------------|
| Free text, names, descriptions | **Contains** | Product Name, Notes, Customer |
| Fixed set of values (<20 options) | **Checkboxes** | Status, Category, Priority, Type |
| Numeric values | **Range** | Price, Quantity, Age, Score |
| Dates | **Date Range** | Created, Updated, Due Date |
| Boolean | **Toggle** | Active, Verified, Published |

## Step 2: Implement the Filter Layout

```
┌─────────────────────────────────────────────────────────┐
│ [Filter chips go here...] [🔍 Filter or search...]  [✕] │  ← Unified filter field
└─────────────────────────────────────────────────────────┘
                                          Sort by: [Dropdown ▾]

┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Name       ▼ │ Status     ▼ │ Price      ▼ │ Created    ▼ │  ← Clickable headers with filter icon
├──────────────┼──────────────┼──────────────┼──────────────┤
│ ...          │ ...          │ ...          │ ...          │
```

**Key layout rules:**

- Filter field spans table width, contains chips + search input + clear button
- Sort dropdown next to filter field (not in headers)
- Each header is clickable and opens its filter menu
- Menu appears ABOVE field when filtering (inserts chip directly)

## Step 3: Build Each Filter Component

### Contains Filter (text)

```
┌─ Product Name ──────────── ✕ ─┐
│ ┌────────────────────────────┐│
│ │ Search...                  ││
│ └────────────────────────────┘│
└───────────────────────────────┘
```

Chip result: `Product Name: system`

### Checkbox Filter (categories)

```
┌─ Status ──────────────── ✕ ─┐
│ ☑ Active                     │
│ ☑ Pending                    │
│ ☐ Archived                   │
│ ☐ Deleted                    │
│            [Clear] [Apply]   │
└──────────────────────────────┘
```

Chip result: `Status: Active, Pending` or `Status: Active, +2`

### Range Filter (numeric)

```
┌─ Price ─────────────────── ✕ ─┐
│  Min         Max              │
│ ┌─────┐     ┌─────┐           │
│ │ 0   │  -  │ 100 │           │
│ └─────┘     └─────┘           │
│ ○───────────────●─────○       │  ← Optional slider
│              [Apply]          │
└───────────────────────────────┘
```

Chip result: `Price: $0 - $100`

### Date Range Filter

```
┌─ Created ─────────────────── ✕ ─┐
│  From           To              │
│ ┌──────────┐   ┌──────────┐     │
│ │ 01/01/25 │ - │ 12/31/25 │     │
│ └──────────┘   └──────────┘     │
│ [Today] [This week] [This month]│
│                [Apply]          │
└─────────────────────────────────┘
```

Chip result: `Created: Jan 1 - Dec 31, 2025`

## Chip Design Rules

- Dark background, light text, rounded pill shape
- X button on contrasting surface (clearly clickable)
- Truncate after 2 values: `Status: Active, Pending, +3`
- Clicking chip reopens its filter menu

## Empty State

When filters return no results:

```
     ┌─────────────┐
     │   (╯°□°)╯   │
     │   ︵ ┻━┻    │
     └─────────────┘
   No results found
   Try adjusting your filters

   [Clear all filters]
```

## Quick Checklist

When implementing, verify:

- [ ] Each column has appropriate filter type assigned
- [ ] Filter field contains chips (not separate row above)
- [ ] Sort is dropdown, not toggle icons in headers
- [ ] Chip shows max 2 values, then +N
- [ ] Clear all button at end of filter field
- [ ] Empty state has clear action

## HTML Class Reference

Use these classes for styling compatibility with `html-style`:

| Element | Class | Purpose |
|---------|-------|---------|
| Filter container | `.filter-bar` | Top-level filter row |
| Chip container | `.filter-chips` | Holds all active chips |
| Individual chip | `.chip` | Single filter chip |
| Chip remove | `.chip-remove` | X button on chip |
| Search input | `.filter-search` | Text search field |
| Clear all | `.filter-clear` | Clear all filters button |
| Sort control | `.sort-control` | Sort dropdown container |
| Filter menu | `.filter-menu` | Dropdown filter panel |
| Empty state | `.empty-state` | No results container |

**Data attributes:**

- `data-column` — Column identifier on chips
- `data-filter-type` — Filter type (contains/checkbox/range/date)

## Styling Handoff

This skill outputs semantic HTML with class names. For visual styling, invoke the `html-style` skill after generating filter HTML.
