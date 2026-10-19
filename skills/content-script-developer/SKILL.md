---
name: content-script-developer
description: "Builds browser-extension content scripts: DOM integration, injecting UI into third-party pages, SPA navigation, dynamic DOM changes. Use when writing or updating a content script."
metadata:
  version: "2.2.4"
  tags: "browser-extension, content-script, dom"
when_to_use: "isolated world, page scraping"
---

# Content Script Developer

## Core constraints

- Content scripts run in an isolated world; page JS scope is not shared.
- Avoid polluting the host page (global styles, conflicting IDs/classes).
- Be idempotent: injection must not duplicate on re-run.
- Prefer robust selectors over brittle class chains.
- Never block the main thread; throttle observers and event handlers.

## Workflow

1. **Understand the target page.**
   - Identify stable anchors (data attributes, IDs, landmark roles).
   - Note SPA navigation patterns (URL changes, DOM root swaps).
   - Decide what you need: read-only scrape or UI injection.

2. **Plan injection safely.**
   - Create a single root container for your UI.
   - Use a shadow root if CSS conflicts are likely.
   - Scope styles to your root or give them a unique prefix.
   - Add cleanup hooks for when the page swaps roots.

3. **Handle dynamic pages.**
   - Use a MutationObserver for DOM changes.
   - Throttle work with `requestAnimationFrame` or debouncing.
   - Re-check anchors on navigation events.

4. **Message and store data.**
   - Use `chrome.runtime.sendMessage` for background/service-worker calls.
   - Use `chrome.storage` for persistent state.
   - Keep tokens and sensitive data in extension storage, not in the DOM.

5. **Accessibility and UX.** Keyboard-focusable elements, visible focus styles, ARIA labels for controls.

## Patterns and snippets

### Idempotent UI injection

```ts
const ROOT_ID = 'ext-root';

export function ensureRoot() {
  let root = document.getElementById(ROOT_ID);
  if (root) return root;

  root = document.createElement('div');
  root.id = ROOT_ID;
  root.setAttribute('data-ext-root', 'true');
  document.body.appendChild(root);
  return root;
}
```

### Safe styling (scoped)

```ts
const styleId = 'ext-style';

function injectStyles(css: string) {
  if (document.getElementById(styleId)) return;
  const style = document.createElement('style');
  style.id = styleId;
  style.textContent = css;
  document.head.appendChild(style);
}
```

### MutationObserver with throttle

```ts
let scheduled = false;
const observer = new MutationObserver(() => {
  if (scheduled) return;
  scheduled = true;
  requestAnimationFrame(() => {
    scheduled = false;
    // re-check anchors or update UI
  });
});

observer.observe(document.body, { childList: true, subtree: true });
```

### Messaging to background

```ts
async function fetchData(payload: Record<string, unknown>) {
  return await chrome.runtime.sendMessage({ type: 'FETCH_DATA', payload });
}
```

## Reliability checklist

- UI injection is idempotent
- Styles are scoped or shadow-rooted
- Observers are throttled and cleaned up
- Messaging uses explicit message types
- Host page performance stays stable

## Common pitfalls

- Injecting the same UI multiple times on SPA navigation
- Brittle selectors that break on minor DOM changes
- Global CSS that overrides host styles
- Heavy MutationObserver handlers without throttling

## Notes

- Prefer small, composable helpers over large one-off scripts.
- Prefix extension logging and keep it easy to disable in production.
