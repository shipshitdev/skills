---
name: growth-engine
description: "Growth engine for digital products: growth hacking, SEO, ASO, viral loops, email marketing, referral programs, and organic acquisition. Use when creating a growth strategy, planning SEO, building a referral program, or optimizing acquisition funnels."
license: MIT
metadata:
  version: "1.0.0"
  tags: "growth, seo, aso, viral, referral, acquisition, marketing"
  author: "antigravity-awesome-skills"
---

# Growth Engine

Growth engine for digital products covering growth hacking, SEO, ASO, viral loops, email marketing, CRM, referral programs, and organic acquisition.

## When to Use

- Creating a growth strategy or acquisition plan
- SEO for landing pages or blog content
- App Store Optimization (ASO)
- Designing viral loops or referral programs
- Email marketing sequences
- Product Hunt or launch campaigns
- Calculating viral coefficient (K-factor)

## Pirate Metrics (AARRR)

| Stage | Question | Key Metric |
|-------|----------|-----------|
| **Acquisition** | How do people discover you? | Visitors → Signups |
| **Activation** | When do users experience first value? | First Conversion Rate |
| **Retention** | Do people come back? | D7, D30, D90 rates |
| **Revenue** | Do people pay? | Trial→Paid conversion, MRR |
| **Referral** | Do people recommend? | NPS, K-factor, referrals/user |

## Viral Loops

**Three loop types:**

1. **Word-of-mouth organic:** User has impressive experience → shares with peers
2. **Share of insights:** Product generates shareable output → 1-click share button
3. **Referral program:** Reward-based ("Give 1 month, get 1 month")

### Viral Coefficient (K-factor)

```
K = (% who invite) × (invites per user) × (conversion rate)
K ≥ 1.0 → Viral growth
K ≥ 0.5 → Accelerated growth
K ≥ 0.2 → Supported growth
K < 0.2 → Slow growth
```

## SEO for Landing Pages

### Critical Tags

```html
<title>Product — Core Value Proposition | Use Case</title>
<meta name="description" content="Clear benefit statement, 150-160 chars">

<meta property="og:title" content="...">
<meta property="og:description" content="...">
<meta property="og:image" content="...">

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "...",
  "description": "...",
  "offers": { "@type": "Offer", "price": "0" }
}
</script>
```

### Keyword Strategy by Intent

| Stage | Modifiers | Example |
|-------|-----------|---------|
| Awareness | "what is", "how to", "guide" | "how to manage project sprints" |
| Consideration | "best", "vs", "alternatives", "top" | "best project management tools" |
| Decision | "pricing", "reviews", "demo" | "[product] pricing comparison" |

## Onboarding Email Sequence (7-Day)

| Day | Trigger | Goal |
|-----|---------|------|
| 0 | Signup | Welcome + quick-start tutorial |
| 1 | No activation | "Your account is waiting" |
| 3 | Activated | Feature education + hidden tip |
| 7 | Used 3+ times | Upsell with usage-based hook |
| 14 | Inactive | Re-engagement / feedback |

## Referral Program Design

```
Incentive: Give [X] → Get [Y] for both parties
Placement: Dashboard, post-activation, post-purchase
Tracking: Unique referral codes or links per user
Goal: 10% of paid users refer ≥1 person
```

## Product Hunt Launch Checklist

**1 week before:**

- Request hunters from influent PH community members
- Prepare: logo, tagline, screenshots, 60s demo video
- Warm up: posts about the problem you solve

**Launch day:**

- Post at 12:01 AM PT
- Email waitlist: "We're on Product Hunt today!"
- Post in relevant communities
- Respond to every comment

## App Store Optimization (ASO)

```
App Name:  [Brand] — [Core Value Proposition] (30 chars max)
Subtitle:  [Key Feature 1] + [Key Feature 2] (30 chars max)
Keywords:  High-intent terms (100 chars max, comma-separated)
Screenshots: Show value in first 2 screenshots — most users stop there
```

## Growth Audit Checklist

- [ ] Is there a clear acquisition channel with >20% of traffic?
- [ ] Is activation metric defined and measured?
- [ ] Is D7 retention above 20%?
- [ ] Is there a referral mechanism built into the product?
- [ ] Is there an email sequence for new signups?
- [ ] Are SEO fundamentals in place (title, meta, structured data)?
- [ ] Is there a win-back sequence for churned users?

## Limitations

- Use only when task matches growth/acquisition scope.
- Growth tactics should be validated with A/B tests before scaling spend.
