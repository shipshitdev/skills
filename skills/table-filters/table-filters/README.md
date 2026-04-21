# table-filters

Design optimal filtering UX for data tables.

## When to Use

- Building a table that needs user-controlled filters
- Claude struggles with filter UX patterns

## What It Does

1. Analyzes each column's data type
2. Assigns filter type (text, checkbox, range, date)
3. Designs chip-based filter UI
4. Outputs semantic HTML with class names

## Filter Types

| Data | Filter |
|------|--------|
| Free text | Contains search |
| Fixed values | Checkboxes |
| Numbers | Range slider |
| Dates | Date range picker |

## Styling

For visual styling, invoke `html-style` after generating filter HTML.
