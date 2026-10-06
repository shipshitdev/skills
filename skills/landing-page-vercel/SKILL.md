---
name: landing-page-vercel
description: Scaffolds a production-ready static landing page with working email capture form, analytics, and responsive design. Activates on "create landing page", "build a landing page", "launch page for product", or similar requests. Optionally deploys to Vercel on explicit request.
disable-model-invocation: true
metadata:
  version: "2.2.3"
  tags: "landing-page, vercel, frontend"
---

# Landing Page (Vercel)

Create a static landing page with:

## Contract

Inputs:

- Product name, tagline, audience, offer, and CTA
- Destination directory
- Form provider and analytics preference

Outputs:

- Static landing page files
- Form/analytics setup notes
- Deployment instructions

Creates/Modifies:

- Local landing page files and Vercel config
- Does not deploy production unless explicitly requested

External Side Effects:

- None during scaffolding
- May deploy to Vercel only after explicit deploy request

Confirmation Required:

- Before using external form/analytics identifiers
- Before running Vercel deploy commands
- Before overwriting an existing landing page directory

Delegates To:

- `project-init-orchestrator` / `npx @shipshitdev/v0` for full Shipshit.dev product repos
- `frontend-design` for custom visual design
- `deployment-composer` or `deploy-app` for deployment

- **Structure:** Semantic HTML5 + Modern CSS + Vanilla JS
- **Form:** Working email capture (Formspree or custom endpoint)
- **Analytics:** Plausible/Fathom ready
- **Design:** Responsive, accessible, performant
- **Deploy:** One-click Vercel deployment

## What Makes This Different

This skill generates **working landing pages**, not empty templates:

- Real email capture form that actually submits
- Analytics integration ready to activate
- Responsive design tested on mobile
- Accessibility basics (WCAG 2.1 AA)
- Content from your PRD brief

---

## Workflow

### Phase 1: PRD Brief Intake

Ask the user for product details, then extract and confirm: product name, tagline, hero headline/subheadline/CTA, 3-5 features with descriptions, CTA type (Waitlist/Sign Up/Demo Request/Contact), and social proof preference (Testimonials/Logos/Stats/None). See `references/full-guide.md` (§ PRD Brief Intake Template) for the confirmation message format.

### Phase 2: Content Generation

Generate complete landing page content across these sections:

1. **Hero** - Headline, subheadline, CTA button, optional hero image
2. **Features** - 3-5 feature cards with icons
3. **How It Works** - 3-step process (optional)
4. **Social Proof** - Testimonials or logos (optional)
5. **FAQ** - 4-6 common questions (optional)
6. **CTA** - Final call to action with form
7. **Footer** - Links, copyright, social icons

### Phase 3: Form Integration

Choose an email capture option:

1. **Formspree (Recommended - Free tier)** - no backend needed, instant setup, email notifications
2. **Custom Endpoint** - your own API, full control, requires backend
3. **Waitlist Service** - Waitlist.email, Loops.so, ConvertKit

### Phase 4: Quality Verification

Verify before handoff:

- HTML validates (W3C)
- Responsive on mobile
- Form submits successfully
- Analytics placeholders present
- Lighthouse score 90+

---

## Usage

```bash
# Create landing page with PRD
python3 scripts/scaffold.py \
  --out ./my-landing-page \
  --name "ProductName" \
  --tagline "Your compelling value proposition" \
  --features "Feature1,Feature2,Feature3"

# Interactive mode
python3 scripts/scaffold.py --out ./my-landing-page --interactive
```

Generates `index.html`, `styles.css`, `script.js`, `data.json`, `vercel.json`, and an `assets/` directory. See `references/full-guide.md` (§ Generated Structure) for the full file tree.

---

## Key Patterns

Form submission handles loading/success/error states via `fetch` against the form's action URL; content lives in `data.json` (hero, features, faq) so copy edits never touch markup. See `references/full-guide.md` (§ Form Handling (JavaScript), § Data Structure (data.json)) for the full implementations.

---

## Form Integration Guide

**Formspree (Recommended):** create a free account at [formspree.io](https://formspree.io), create a form, and replace `YOUR_FORM_ID` in the HTML with the generated form ID.

**Custom Endpoint:** post `{ email }` as JSON to a self-hosted API and handle the response. See `references/full-guide.md` (§ Option 2: Custom Endpoint) for the full snippet.

---

## Analytics Setup

Add one script tag to the page head: Plausible (`data-domain` + `plausible.io/js/script.js`) for privacy-friendly analytics, or Fathom (`cdn.usefathom.com/script.js` + `data-site`). See `references/full-guide.md` (§ Analytics Setup) for both tags.

---

## Deployment

```bash
cd my-landing-page
bunx vercel          # Deploy (no global install needed)
bunx vercel --prod   # Production deploy
```

`vercel.json` maps all static assets through `@vercel/static`, routes everything to `index.html`, and sets baseline security headers (`X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`). See `references/full-guide.md` (§ Vercel Configuration (vercel.json)) for the full config.

---

## CSS Variables

Theme tokens (`--color-primary`, `--color-bg`, `--font-sans`, `--spacing-*`, `--max-width`) drive the whole stylesheet — see `references/full-guide.md` (§ CSS Variables) for the full `:root` block.

---

## Accessibility Checklist

- [x] Semantic HTML structure
- [x] Proper heading hierarchy (h1 → h2 → h3)
- [x] Alt text for images
- [x] Focus states for interactive elements
- [x] Color contrast ratio 4.5:1 minimum
- [x] Form labels and error messages
- [x] Skip link for keyboard navigation
- [x] Responsive text sizing (no fixed px for body text)

---

## Performance Checklist

- [x] No external CSS frameworks
- [x] Minimal JavaScript
- [x] Optimized images (WebP with fallback)
- [x] System fonts (no web font loading)
- [x] Lazy loading for below-fold images
- [x] Preconnect for external resources

---

## References

- `scripts/scaffold.py` - Generation script (templates are inline)
- `references/full-guide.md` - Full PRD template, generated file tree, form/analytics/deploy config dumps, and CSS variable set
