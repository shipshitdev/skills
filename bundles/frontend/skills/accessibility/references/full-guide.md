
# Accessibility (a11y) Skill

You are an expert in web accessibility (a11y), specializing in WCAG 2.1 AA compliance for React/Next.js applications. Your mission is to ensure all projects are usable by everyone, including people with disabilities.

## When to Use This Skill

This skill activates automatically when you're:

- Creating or reviewing UI components
- Implementing interactive elements (buttons, forms, modals)
- Adding keyboard navigation
- Reviewing color contrast and visual design
- Testing with screen readers
- Auditing existing pages for accessibility issues
- Implementing ARIA attributes

---

## WCAG 2.1 AA Compliance Goals

Projects should target **WCAG 2.1 Level AA** compliance for all public-facing apps. Discover project-specific accessibility requirements from documentation.

### Success Criteria Overview

| Principle          | Focus Areas                                          |
| ------------------ | ---------------------------------------------------- |
| **Perceivable**    | Text alternatives, color contrast, responsive design |
| **Operable**       | Keyboard navigation, focus management, timing        |
| **Understandable** | Clear language, predictable behavior, error handling |
| **Robust**         | Valid HTML, ARIA usage, compatibility                |

---

## 1. Perceivable Content

### 1.1 Text Alternatives

**Images**:

```typescript
// ✅ Good: Descriptive alt text
<Image
  src="/product.jpg"
  alt="Blue wireless headphones with noise cancellation"
  width={300}
  height={300}
/>

// ❌ Bad: Generic or missing alt
<Image src="/product.jpg" alt="image" />
<img src="/product.jpg" /> // Missing alt
```

**Icons**:

```typescript
// ✅ Good: ARIA label for icon-only buttons
<button aria-label="Close modal" onClick={onClose}>
  <XIcon aria-hidden="true" />
</button>

// ✅ Good: Icon with visible text
<button onClick={onSave}>
  <SaveIcon aria-hidden="true" />
  Save
</button>

// ❌ Bad: No label
<button onClick={onClose}>
  <XIcon />
</button>
```

**Decorative Images**:

```typescript
// ✅ Good: Empty alt for decorative images
<img src="/decoration.svg" alt="" role="presentation" />

// Or hide from screen readers
<div aria-hidden="true">
  <img src="/decoration.svg" />
</div>
```

### 1.2 Color Contrast (WCAG AA)

**Requirements**:

- Normal text (< 24px): **4.5:1** contrast ratio
- Large text (≥ 24px): **3:1** contrast ratio
- UI components & graphics: **3:1** contrast ratio

**Tools**:

- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Chrome DevTools: Inspect → Accessibility pane

**Examples**:

```typescript
// ✅ Good: High contrast text
<p className="text-base-content">
  This text has sufficient contrast
</p>

// ❌ Bad: Low contrast (text-gray-400 on white)
<p className="text-gray-400">
  This text may not have enough contrast
</p>

// ✅ Good: Test with @agenticindiedev/ui theme tokens
<p className="text-base-content/80">
  Uses semantic color with opacity
</p>
```

### 1.3 Responsive & Zoom Support

```typescript
// ✅ Good: Responsive text sizing
<h1 className="text-2xl md:text-4xl lg:text-6xl">
  Scales across devices
</h1>

// ✅ Good: Support 200% zoom
<meta name="viewport" content="width=device-width, initial-scale=1.0" />

// ❌ Bad: Fixed font sizes in pixels without scaling
<p style={{ fontSize: '12px' }}>
  Too small and doesn't scale
</p>
```

### 1.4 Text Spacing & Readability

```typescript
// ✅ Good: Proper line height and spacing
<p className="leading-relaxed tracking-normal max-w-prose">
  Content with good readability
</p>

// ❌ Bad: Cramped text
<p className="leading-tight tracking-tighter">
  Hard to read for users with dyslexia
</p>
```

---

## 2. Operable Interface

### 2.1 Keyboard Navigation

**All interactive elements must be keyboard accessible.**

**Focus Management**:

```typescript
// ✅ Good: Proper tab order
<nav>
  <a href="/" tabIndex={0}>Home</a>
  <a href="/about" tabIndex={0}>About</a>
  <a href="/pricing" tabIndex={0}>Pricing</a>
</nav>

// ✅ Good: Skip to main content link
<a href="#main-content" className="sr-only focus:not-sr-only">
  Skip to main content
</a>
<main id="main-content">...</main>

// ❌ Bad: Positive tabIndex (breaks natural order)
<button tabIndex={5}>Don't do this</button>
```

**Keyboard Event Handlers**:

```typescript
// ✅ Good: Support Enter and Space for custom buttons
const handleKeyDown = (e: React.KeyboardEvent) => {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    handleAction();
  }
};

<div
  role="button"
  tabIndex={0}
  onClick={handleAction}
  onKeyDown={handleKeyDown}
>
  Custom Button
</div>

// ✅ Better: Use native button element
<button onClick={handleAction}>
  Native Button
</button>
```

**Modal Keyboard Trapping**:

```typescript
// ✅ Good: Trap focus in modal, close on Escape
import { useEffect, useRef } from "react";
import { trapFocus } from "@/lib/accessibility";

export default function Modal({ isOpen, onClose, children }: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };

    document.addEventListener("keydown", handleEscape);
    const cleanup = trapFocus(modalRef.current);

    return () => {
      document.removeEventListener("keydown", handleEscape);
      cleanup();
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div role="dialog" aria-modal="true" ref={modalRef}>
      <button aria-label="Close" onClick={onClose}>
        ×
      </button>
      {children}
    </div>
  );
}
```

### 2.2 Focus Indicators

```typescript
// ✅ Good: Visible focus styles
<button className="focus:ring-2 focus:ring-primary focus:ring-offset-2">
  Clear focus indicator
</button>

// ✅ Good: Custom focus styles
<a
  href="/link"
  className="focus:outline-none focus:underline focus:text-primary"
>
  Link with focus
</a>

// ❌ Bad: Removing focus without replacement
<button className="focus:outline-none">
  No focus indicator
</button>
```

### 2.3 Interactive Element States

```typescript
// ✅ Good: All states defined
<button
  disabled={isDisabled}
  aria-pressed={isPressed}
  aria-expanded={isExpanded}
  className={cn(
    "btn",
    isDisabled && "opacity-50 cursor-not-allowed",
    isPressed && "btn-active"
  )}
>
  Toggle Button
</button>
```

---

## 3. Understandable Content

### 3.1 Form Labels & Instructions

```typescript
// ✅ Good: Proper labels and error messages
<div>
  <label htmlFor="email" className="label">
    <span className="label-text">Email Address</span>
    <span className="label-text-alt">Required</span>
  </label>

  <input
    id="email"
    type="email"
    aria-required="true"
    aria-invalid={!!emailError}
    aria-describedby={emailError ? 'email-error' : undefined}
    className={emailError ? 'input-error' : ''}
  />

  {emailError && (
    <span id="email-error" className="label-text-alt text-error" role="alert">
      {emailError}
    </span>
  )}
</div>

// ❌ Bad: No label, vague error
<input type="email" placeholder="Email" />
{error && <span>Error</span>}
```

### 3.2 Error Handling

```typescript
// ✅ Good: Clear error messages with recovery steps
<div role="alert" className="alert alert-error">
  <AlertIcon aria-hidden="true" />
  <div>
    <h3 className="font-bold">Upload failed</h3>
    <p>File size exceeds 10MB limit. Compress your file and try again.</p>
  </div>
  <button onClick={handleRetry}>Retry</button>
</div>

// ❌ Bad: Vague error
<div>Error occurred</div>
```

### 3.3 Consistent Navigation

```typescript
// ✅ Good: Consistent header across all pages
<header role="banner">
  <nav aria-label="Main navigation">
    <Link href="/">Home</Link>
    <Link href="/studio">Studio</Link>
    <Link href="/analytics">Analytics</Link>
  </nav>
</header>

// ✅ Good: Breadcrumbs for context
<nav aria-label="Breadcrumb">
  <ol className="breadcrumbs">
    <li><Link href="/">Home</Link></li>
    <li><Link href="/studio">Studio</Link></li>
    <li aria-current="page">Video Editor</li>
  </ol>
</nav>
```

### 3.4 Clear Language

```typescript
// ✅ Good: Clear, specific button text
<button onClick={handleDelete}>Delete Video</button>
<button onClick={handleSave}>Save</button>

// ❌ Bad: Vague button text
<button onClick={handleAction}>Submit</button>
<button onClick={handleClose}>OK</button>
```

---

## 4. Robust & Semantic HTML

### 4.1 Semantic Elements

```typescript
// ✅ Good: Semantic HTML
<header>...</header>
<nav>...</nav>
<main>...</main>
<article>...</article>
<aside>...</aside>
<footer>...</footer>

// ❌ Bad: Div soup
<div class="header">...</div>
<div class="nav">...</div>
<div class="content">...</div>
```

### 4.2 ARIA Roles & Attributes

**When to use ARIA**:

- Only when semantic HTML isn't enough
- "No ARIA is better than bad ARIA"

```typescript
// ✅ Good: Semantic HTML (no ARIA needed)
<button onClick={handleClick}>Click me</button>
<nav>...</nav>

// ✅ Good: ARIA when needed for custom components
<div
  role="button"
  tabIndex={0}
  aria-pressed={isPressed}
  onClick={handleClick}
  onKeyDown={handleKeyDown}
>
  Custom Toggle
</div>

// ✅ Good: ARIA for dynamic content
<div role="status" aria-live="polite">
  {message}
</div>

// ❌ Bad: Redundant ARIA
<button role="button">Click me</button>
<nav role="navigation">...</nav>
```

### 4.3 Live Regions

```typescript
// ✅ Good: Announce dynamic updates
<div role="status" aria-live="polite" aria-atomic="true">
  {uploadProgress}% uploaded
</div>

<div role="alert" aria-live="assertive">
  {errorMessage}
</div>

// Politeness levels:
// - off: No announcement
// - polite: Announce when user is idle
// - assertive: Announce immediately (use sparingly)
```

### 4.4 Headings Hierarchy

```typescript
// ✅ Good: Proper heading structure
<h1>Page Title</h1>
<section>
  <h2>Section 1</h2>
  <h3>Subsection 1.1</h3>
  <h3>Subsection 1.2</h3>
</section>
<section>
  <h2>Section 2</h2>
  <h3>Subsection 2.1</h3>
</section>

// ❌ Bad: Skipping levels
<h1>Page Title</h1>
<h4>Subsection</h4> // Skipped h2 and h3
```

---

## 5. Common Patterns & Components

### 5.1 Accessible Buttons

```typescript
// ✅ Icon button with label
<button aria-label="Delete video" onClick={onDelete}>
  <TrashIcon aria-hidden="true" />
</button>

// ✅ Toggle button
<button
  aria-pressed={isMuted}
  onClick={toggleMute}
>
  {isMuted ? 'Unmute' : 'Mute'}
</button>

// ✅ Disabled button with reason
<button disabled={!hasChanges} title="No changes to save">
  Save
</button>
```

### 5.2 Accessible Forms

```typescript
// ✅ Complete accessible form field
<fieldset>
  <legend>Personal Information</legend>

  <div className="form-control">
    <label htmlFor="name" className="label">
      <span className="label-text">Full Name</span>
    </label>
    <input
      id="name"
      type="text"
      className="input input-bordered"
      aria-required="true"
      aria-describedby="name-help"
    />
    <span id="name-help" className="label-text-alt">
      Enter your first and last name
    </span>
  </div>

  <div className="form-control">
    <label htmlFor="email" className="label">
      <span className="label-text">Email</span>
    </label>
    <input
      id="email"
      type="email"
      className="input input-bordered"
      aria-required="true"
      aria-invalid={!!emailError}
      aria-describedby={emailError ? "email-error" : undefined}
    />
    {emailError && (
      <span id="email-error" className="label-text-alt text-error" role="alert">
        {emailError}
      </span>
    )}
  </div>
</fieldset>
```

### 5.3 Accessible Modals

```typescript
export default function Modal({
  isOpen,
  onClose,
  title,
  children,
}: ModalProps) {
  const titleId = useId();

  useEffect(() => {
    if (!isOpen) return;

    // Prevent body scroll
    document.body.style.overflow = "hidden";

    // Focus first focusable element
    const firstFocusable = modalRef.current?.querySelector<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    firstFocusable?.focus();

    return () => {
      document.body.style.overflow = "";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      className="modal modal-open"
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
    >
      <div className="modal-box" ref={modalRef}>
        <h2 id={titleId} className="text-xl font-bold">
          {title}
        </h2>

        <button
          className="btn btn-sm btn-circle absolute right-2 top-2"
          aria-label="Close"
          onClick={onClose}
        >
          ✕
        </button>

        <div className="py-4">{children}</div>

        <div className="modal-action">
          <button className="btn" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
```

### 5.4 Accessible Tabs

```typescript
export default function Tabs({ tabs, activeTab, onChange }: TabsProps) {
  return (
    <div>
      <div role="tablist" aria-label="Content tabs">
        {tabs.map((tab, index) => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={activeTab === tab.id}
            aria-controls={`panel-${tab.id}`}
            id={`tab-${tab.id}`}
            tabIndex={activeTab === tab.id ? 0 : -1}
            onClick={() => onChange(tab.id)}
            className={cn("tab", activeTab === tab.id && "tab-active")}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {tabs.map((tab) => (
        <div
          key={tab.id}
          role="tabpanel"
          id={`panel-${tab.id}`}
          aria-labelledby={`tab-${tab.id}`}
          hidden={activeTab !== tab.id}
        >
          {tab.content}
        </div>
      ))}
    </div>
  );
}
```

### 5.5 Accessible Dropdowns

```typescript
export default function Dropdown({ trigger, items }: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const triggerId = useId();
  const menuId = useId();

  return (
    <div className="dropdown">
      <button
        id={triggerId}
        aria-haspopup="true"
        aria-expanded={isOpen}
        aria-controls={menuId}
        onClick={() => setIsOpen(!isOpen)}
      >
        {trigger}
      </button>

      {isOpen && (
        <ul
          id={menuId}
          role="menu"
          aria-labelledby={triggerId}
          className="dropdown-content menu"
        >
          {items.map((item, index) => (
            <li key={index}>
              <button
                role="menuitem"
                onClick={() => {
                  item.onClick();
                  setIsOpen(false);
                }}
              >
                {item.label}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

---

## 6. Testing & Tools

### 6.1 Automated Testing

**ESLint Plugin**:

```bash
pnpm add -D eslint-plugin-jsx-a11y
```

```javascript
// eslint.config.mjs
{
  plugins: ['jsx-a11y'],
  extends: ['plugin:jsx-a11y/recommended'],
}
```

**Axe DevTools** (Browser Extension):

- Install: Chrome/Firefox "axe DevTools"
- Run: F12 → axe DevTools tab → Scan

**Vitest a11y Tests**:

```typescript
import { render } from "@testing-library/react";
import { axe } from "vitest-axe";
import * as matchers from "vitest-axe/matchers";
import { describe, expect, it } from "vitest";
import Button from "./Button";

expect.extend(matchers);

describe("Button accessibility", () => {
  it("should have no a11y violations", async () => {
    const { container } = render(<Button>Click me</Button>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### 6.2 Manual Testing

**Keyboard Navigation**:

1. Tab through all interactive elements
2. Verify focus indicators visible
3. Test keyboard shortcuts (Enter, Space, Escape)
4. Ensure no keyboard traps

**Screen Reader Testing**:

- **macOS**: VoiceOver (Cmd+F5)
- **Windows**: NVDA (free)
- **Test**: Navigate page, fill forms, trigger actions

**Zoom Testing**:

1. Zoom to 200% (Cmd/Ctrl + "+")
2. Verify content still readable and functional
3. Check for horizontal scrolling issues

### 6.3 Accessibility Checklist

Before shipping:

- [ ] All images have alt text
- [ ] Color contrast meets WCAG AA (4.5:1 for text)
- [ ] All interactive elements keyboard accessible
- [ ] Focus indicators visible and clear
- [ ] Form labels properly associated
- [ ] Error messages are clear and helpful
- [ ] Headings follow proper hierarchy (h1 → h2 → h3)
- [ ] ARIA used correctly (or not at all)
- [ ] Modals trap focus and close on Escape
- [ ] Dynamic content announces to screen readers
- [ ] Page tested with keyboard only
- [ ] Page tested with screen reader
- [ ] Page tested at 200% zoom
- [ ] Automated tests pass (axe, ESLint)

---

## 7. Resources

### Official Guidelines

- **WCAG 2.1**: https://www.w3.org/WAI/WCAG21/quickref/
- **MDN Accessibility**: https://developer.mozilla.org/en-US/docs/Web/Accessibility
- **W3C ARIA**: https://www.w3.org/WAI/ARIA/apg/

### Tools

- **WebAIM Contrast Checker**: https://webaim.org/resources/contrastchecker/
- **axe DevTools**: https://www.deque.com/axe/devtools/
- **WAVE**: https://wave.webaim.org/
- **Lighthouse**: Built into Chrome DevTools

### Testing

- **VoiceOver Guide**: https://webaim.org/articles/voiceover/
- **NVDA Guide**: https://webaim.org/articles/nvda/
- **Keyboard Testing**: https://webaim.org/articles/keyboard/

---

## Summary

**The Golden Rules**:

1. **Semantic HTML first** - Use the right element for the job
2. **No ARIA is better than bad ARIA** - Only add when necessary
3. **Test with real users** - Automated tools catch ~40% of issues
4. **Keyboard navigation is mandatory** - Not optional
5. **Color is not the only indicator** - Use icons, text, patterns

**When in doubt**:

- Use semantic HTML
- Check WCAG guidelines
- Test with keyboard and screen reader
- Run automated tools (axe, Lighthouse)

---

**Questions?** Consult WCAG 2.1 guidelines or run accessibility audits with axe DevTools.
