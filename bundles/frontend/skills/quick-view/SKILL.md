---
name: quick-view
description: >-
  Generates minimal HTML pages to review structured data in a browser with
  maximum readability. Triggers on: "show me", "view this", "make reviewable",
  "open as webpage", or any request to review lists, tables, drafts, or
  summaries that are hard to read in the terminal.
metadata:
  version: "2.2.2"
  tags: "html, review, preview"
---

# Quick View

Generate minimal HTML to review structured data in a browser. Minimal styling, maximum readability.

## When to Use

- User wants to review output that's hard to read in terminal
- Lists, tables, drafts, summaries that benefit from visual layout
- User says: "show me", "view this", "make reviewable", "open as webpage"

## Output Rules

**DO:**

- Semantic HTML: `<table>`, `<ul>`, `<details>`, `<pre>`, `<h1-3>`
- Use the base template with CSS variables
- Write to `_private/views/`
- Open with `open _private/views/{filename}`

**DO NOT:**

- Add decorative styling beyond the base template
- Use CSS frameworks
- Over-engineer or "make it nice"

## File Naming

Views have a lifecycle: temporary → keeper → archived.

| Stage | Filename | When |
|-------|----------|------|
| Temporary | `name-temp.html` | Default for new views |
| Keeper | `name.html` | User says "keep this", "this is good" |
| Archived | `name.2025-01-01.html` | Previous keeper when promoting new one |

**Rules:**

1. **Always create with `-temp` suffix** — Every new view starts as `name-temp.html`
2. **Promote on approval** — When user approves, rename to `name.html`
3. **Archive before replacing** — If `name.html` exists, rename to `name.DATE.html` before promoting
4. **Never regenerate keepers** — Only regenerate `-temp` files

**Workflow:** See `references/full-guide.md` (§ File Naming Lifecycle Example) for a walkthrough of temp → keeper → archived across iterations.

**Trigger phrases for promotion:**

- "keep this", "this is good", "save this"
- "make this the default", "lock this in"
- "I like this one"

## Base Template

Every quick-view HTML file uses the base template at `${CLAUDE_SKILL_DIR}/assets/base-template.html`. Load it to get the full HTML structure with CSS variables, dark-mode support, truncation toggle script, and type-border classes. Replace `{title}`, `{timestamp}`, `{count}`, and `{content}` placeholders when generating output.

## Patterns

### List of items

```html
<h1>Title</h1>
<ul>
  <li><strong>@username</strong> — action item</li>
</ul>
```

### Table

```html
<table>
  <tr><th>Contact</th><th>Action</th><th>Draft</th></tr>
  <tr><td>@name</td><td>Follow up</td><td>Hey...</td></tr>
</table>
```

### Expandable sections (for long content)

```html
<details>
  <summary><strong>@username</strong> — action</summary>
  <div class="truncate">
    <pre>Long content here that may need truncation...</pre>
  </div>
</details>
```

### Type-differentiated items

```html
<div class="type-user">User message or input</div>
<div class="type-draft">Draft content</div>
<div class="type-done">Completed item</div>
```

### With actions

```html
<p>
  <a href="tg://resolve?domain=username">Open Telegram</a> ·
  <button onclick="navigator.clipboard.writeText('draft text')">Copy</button>
</p>
```

### Sourced data (citations & drill-down)

When displaying data gathered from external sources, always include attribution links for drill-down.

**Add to base template CSS:**

```css
.source { color: var(--muted); font-size: 0.75rem; }
.source a { color: var(--muted); }
.source a:hover { color: var(--accent); }
```

**Inline attribution (preferred for lists):**

```html
<div class="tip">
  <strong>Tip title</strong> — Description of the tip.
  <span class="source">— <a href="https://x.com/user/status/123">@username</a></span>
</div>
```

**Table with source column:**

```html
<table>
  <tr><th>Tip</th><th>Source</th></tr>
  <tr>
    <td>Description here</td>
    <td class="source"><a href="https://x.com/user/status/123">@user</a></td>
  </tr>
</table>
```

**Expandable with source in summary:**

```html
<details>
  <summary><strong>Tip title</strong> <span class="source">— <a href="URL">@source</a></span></summary>
  <p>Full content...</p>
</details>
```

**Meta header with main source:**

```html
<p class="meta">
  Generated: {timestamp} · {count} items ·
  Source: <a href="https://x.com/user/status/123">Original thread</a>
</p>
```

**Principles:**

- Always link to original when data comes from external sources
- Use `@username` for social media, domain for articles
- Source links should be muted/subtle, not prominent
- Include main source in meta header for collections from single source

### Editable drafts (with diff tracking)

For drafts that user may edit before sending. Tracks original vs edited for later analysis.

See `references/full-guide.md` (§ Editable Drafts Markup, § Editable Drafts Script) for the `<details>` markup and the `saveDraft`/`copyDraft`/`restoreEdits`/`exportEdits` script to include before the closing `</body>` tag.

Add export button in header when using editable drafts:

```html
<p class="meta">Generated: {timestamp} · {count} drafts · <button onclick="exportEdits()">Export Edits</button></p>
```

## Workflow

1. Identify the data to display (file, variable, recent output)
2. Choose pattern: list, table, or expandable sections
3. Generate HTML using template above
4. Write to `_private/views/{name}-temp.html`
5. Run `open _private/views/{name}-temp.html`
6. If user approves, promote to `{name}.html`

## Example

User: "show me the drafts"

Agent:

1. Reads `_private/drafts/outreach_drafts.md`
2. Parses each draft (heading = contact, body = draft)
3. Generates HTML with `<details>` for each draft
4. Writes to `_private/views/drafts-temp.html`
5. Runs `open _private/views/drafts-temp.html`

Result: Browser opens, user sees expandable list of drafts with auto dark/light mode, long content truncated with "Show more", can copy each one.

User: "this looks good, keep it"

Agent:

1. Renames `drafts-temp.html` → `drafts.html`
2. Confirms: "Saved as drafts.html"

## Styling Handoff

This skill produces functional HTML with minimal styling. For full visual styling, invoke the `html-style` skill after generating.

**Classes used by quick-view (compatible with html-style):**

| Class | Purpose |
|-------|---------|
| `.type-user` | User input/message |
| `.type-draft` | Draft content |
| `.type-done` | Completed item |
| `.source` | Attribution links |
| `.meta` | Metadata header |
| `.truncate` | Long content container |
| `.actions` | Action button container |

**Data attributes for JS hooks:**

- `data-username` — Identifier for drafts
- `data-original` — Original text for diff tracking

## Attribution

Truncation pattern and CSS variables approach inspired by [simon willison's claude-code-transcripts](https://github.com/simonw/claude-code-transcripts).
