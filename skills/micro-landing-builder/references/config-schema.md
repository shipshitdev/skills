# app.json Config Schema

Complete schema for the landing page configuration file.

---

## Root Schema

```typescript
interface AppConfig {
  name: string;              // Display name
  slug: string;              // URL-friendly identifier
  domain: string;            // Domain for analytics/SEO
  meta: MetaConfig;
  theme: ThemeConfig;
  analytics: AnalyticsConfig;
  header: HeaderConfig;
  sections: Section[];
  footer: FooterConfig;
}
```

---

## Meta Config

```typescript
interface MetaConfig {
  title: string;             // Page title
  description: string;       // Meta description for SEO
  ogImage?: string;          // Open Graph image path
}
```

---

## Theme Config

`app/layout.tsx` writes these values onto `<html>` as shadcn CSS variables, overriding the defaults in `app/globals.css`.

```typescript
interface ThemeConfig {
  primary: string;           // --primary and --ring (bg-primary, text-primary)
  accent: string;            // --brand (text-brand), the extra brand accent
  background: string;        // --background (bg-background)
  foreground?: string;       // --foreground; derived from background brightness when omitted
  mode?: "dark" | "light";   // Token set in globals.css (default "dark"); toggles the .dark class
  font: {
    heading: string;         // Informational: set in layout.tsx <link> and --font-heading in globals.css
    body: string;            // Informational: set in layout.tsx <link> and --font-sans in globals.css
  };
}
```

Card, popover and muted-text colors are derived from `background` and `foreground`, so a light background never gets light text. Text on `bg-primary` uses `--primary-foreground`, which `layout.tsx` sets to white (or near-black when `primary` is light).

**Recommended fonts:**

- Headings: `Fraunces`, `Playfair Display`, `Clash Display`
- Body: `Space Grotesk`, `Inter`, `DM Sans`

---

## Analytics Config

```typescript
interface AnalyticsConfig {
  plausible?: string;        // Plausible domain
  ga?: string;               // Google Analytics ID (G-XXXXX)
}
```

---

## Header Config

```typescript
interface HeaderConfig {
  logo: {
    mark: string;            // Short text/initials (e.g., "MS")
    text: string;            // Full name
    image?: string;          // Optional logo image path
  };
  nav: NavItem[];
  cta: CTAButton;
}

interface NavItem {
  label: string;
  href: string;
}

interface CTAButton {
  label: string;
  href: string;
}
```

---

## Sections

Array of section objects. Each has a `type` field.

### Hero Section

```typescript
interface HeroSection {
  type: "hero";
  eyebrow?: string;          // Small text above headline
  headline: string;
  subheadline: string;
  badges?: string[];         // e.g., ["YC W24", "Product Hunt #1"]
  primaryCta: CTAButton;
  secondaryCta?: CTAButton;
  image?: string;            // Hero image path
  note?: string;             // Small note below CTAs
}
```

### Stats Section

```typescript
interface StatsSection {
  type: "stats";
  items: StatItem[];
}

interface StatItem {
  value: string;             // e.g., "10K+"
  label: string;             // e.g., "Users"
}
```

### Features Section

```typescript
interface FeaturesSection {
  type: "features";
  title: string;
  subtitle?: string;
  items: FeatureItem[];
}

interface FeatureItem {
  icon: string;              // Icon name (e.g., "zap", "shield")
  title: string;
  description: string;
}
```

**Available icons:** `zap`, `shield`, `trending-up`, `users`, `lock`, `globe`, `check`, `star`, `heart`, `settings`

### Pricing Section

```typescript
interface PricingSection {
  type: "pricing";
  title: string;
  subtitle?: string;
  plans: PricingPlan[];
}

interface PricingPlan {
  name: string;
  price: {
    monthly: number;
    yearly: number;
  };
  description?: string;
  features: string[];
  cta: CTAButton;
  highlighted?: boolean;     // Visual emphasis
}
```

### Testimonials Section

```typescript
interface TestimonialsSection {
  type: "testimonials";
  title: string;
  items: Testimonial[];
}

interface Testimonial {
  quote: string;
  author: string;
  role: string;              // e.g., "CEO at Company"
  avatar?: string;           // Avatar image path
}
```

### FAQ Section

```typescript
interface FAQSection {
  type: "faq";
  title: string;
  items: FAQItem[];
}

interface FAQItem {
  q: string;                 // Question
  a: string;                 // Answer
}
```

### CTA Section

```typescript
interface CTASection {
  type: "cta";
  headline: string;
  subheadline?: string;
  emailCapture?: {
    enabled: boolean;
    provider: "resend" | "mailchimp";
    placeholder?: string;
    buttonText?: string;
  };
  cta?: CTAButton;           // Alternative to email capture
}
```

---

## Footer Config

```typescript
interface FooterConfig {
  links: FooterLink[];
  social: SocialLink[];
  copyright: string;
}

interface FooterLink {
  label: string;
  href: string;
}

interface SocialLink {
  platform: "twitter" | "github" | "linkedin" | "instagram";
  href: string;
}
```

---

## Complete Example

```json
{
  "name": "My Startup",
  "slug": "mystartup",
  "domain": "mystartup.com",
  "meta": {
    "title": "My Startup - AI Analytics",
    "description": "Transform your analytics with AI",
    "ogImage": "/og.png"
  },
  "theme": {
    "primary": "#6366f1",
    "accent": "#f59e0b",
    "background": "#0a0a0a",
    "font": {
      "heading": "Fraunces",
      "body": "Space Grotesk"
    }
  },
  "analytics": {
    "plausible": "mystartup.com"
  },
  "header": {
    "logo": { "mark": "MS", "text": "My Startup" },
    "nav": [
      { "label": "Features", "href": "#features" },
      { "label": "Pricing", "href": "#pricing" }
    ],
    "cta": { "label": "Get Started", "href": "#signup" }
  },
  "sections": [
    {
      "type": "hero",
      "headline": "Analytics, reimagined",
      "subheadline": "AI-powered insights for modern teams",
      "primaryCta": { "label": "Start Free", "href": "#signup" }
    },
    {
      "type": "features",
      "title": "Features",
      "items": [
        { "icon": "zap", "title": "Fast", "description": "Lightning speed" }
      ]
    }
  ],
  "footer": {
    "links": [{ "label": "Privacy", "href": "/privacy" }],
    "social": [{ "platform": "twitter", "href": "https://twitter.com/..." }],
    "copyright": "2024 My Startup"
  }
}
```
