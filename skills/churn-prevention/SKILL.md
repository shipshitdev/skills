---
name: churn-prevention
description: "Reduce voluntary and involuntary churn with cancel flows, dynamic save offers, dunning, and win-back tactics. Use when users are cancelling, failed payments are rising, or subscription retention needs improvement."
license: MIT
metadata:
  version: "1.1.0"
  tags: "churn, retention, saas, cancel-flow, dunning, subscriptions"
  author: "antigravity-awesome-skills"
---

# Churn Prevention

Expert in SaaS retention and churn prevention. Reduces both voluntary churn (customers choosing to cancel) and involuntary churn (failed payments) through cancel flows, dynamic save offers, proactive retention, and dunning strategies.

## When to Use

- Churn is rising or cancellation behavior needs intervention
- Designing cancel flows, save offers, dunning, or retention programs
- Reducing voluntary or involuntary churn

## Before Starting

Check for `.agents/product-marketing-context.md` first. If it exists, use that context and only ask for missing specifics.

Gather this context if not provided:

1. **Current Churn**: Monthly churn rate, active subscribers, avg MRR per customer, existing cancel flow?
2. **Billing Platform**: Stripe, Chargebee, Paddle, Recurly? Monthly/annual/both? Pause/downgrade support?
3. **Product Data**: Feature usage tracking? Engagement data? Cancellation reason history?
4. **Constraints**: B2B or B2C? Self-serve cancellation required? Brand tone for offboarding?

## Churn Types

| Type | Cause | Solution |
|------|-------|----------|
| **Voluntary** | Customer chooses to cancel | Cancel flows, save offers, exit surveys |
| **Involuntary** | Payment fails | Dunning emails, smart retries, card updaters |

Voluntary churn is typically 50-70% of total. Involuntary is 30-50% but easier to fix.

## Cancel Flow Design

```
Trigger → Survey → Dynamic Offer → Confirmation → Post-Cancel
```

### Exit Survey

5-8 reason options, single-select with optional free text. Common reasons:

| Reason | Implication |
|--------|-------------|
| Too expensive | Price sensitivity → discount or downgrade |
| Not using it enough | Low engagement → pause or onboarding |
| Missing a feature | Product gap → roadmap preview |
| Switching to competitor | Competitive pressure → comparison + discount |
| Technical issues / bugs | Escalate to support immediately |
| Temporary / seasonal | Usage pattern → pause |
| Business closed | Unavoidable — let go gracefully |

### Dynamic Save Offers

Match the offer to the cancellation reason:

| Cancel Reason | Primary Offer | Fallback |
|---------------|--------------|----------|
| Too expensive | 20-30% discount for 2-3 months | Downgrade |
| Not using it enough | Pause (1-3 months) | Free onboarding session |
| Missing feature | Roadmap preview + timeline | Workaround guide |
| Technical issues | Escalate to support | Credit + priority fix |
| Seasonal | Pause | Downgrade temporarily |
| Business closed | Skip offer | — |

**Discount rules:**

- 20-30% off for 2-3 months is the sweet spot
- Avoid 50%+ (trains customers to cancel for deals)
- Time-limit the offer ("expires when you leave this page")
- Show dollar amount saved, not just percentage

**Pause rules:**

- 1-3 month pause maximum (longer pauses rarely reactivate)
- 60-80% of pausers eventually return
- Auto-reactivation with advance email notice

## Dunning (Involuntary Churn)

### Smart Retry Schedule

| Day | Action |
|-----|--------|
| 0 | First payment failure — email immediately |
| 1 | Smart retry (best day/time for card type) |
| 3 | Retry + "Update payment method" email |
| 7 | Final retry + urgent email |
| 14 | Suspension + final warning |
| 21 | Cancellation |

### Email Sequence

1. **Day 0:** "We couldn't process your payment" — link to update card
2. **Day 3:** "Action required" — emphasize what they'll lose
3. **Day 7:** "Your account will be paused" — urgency with countdown
4. **Day 14:** "Final notice" — last chance before cancellation

## Win-Back Tactics

For users who cancelled:

- **Day 7:** "We miss you" email — no offer yet, just check-in
- **Day 14:** Offer to return with 1-month free or discount
- **Day 30:** If no response, lower-touch "anything we can improve?" email
- **Day 90:** Final win-back with best offer

## Metrics to Track

| Metric | Target |
|--------|--------|
| Cancel flow completion rate | >90% |
| Save offer acceptance rate | 15-25% |
| Dunning recovery rate | 20-40% of failed payments |
| Pause-to-reactivation rate | 60-80% |
| Win-back rate (30 days) | 5-15% |

## Integration Notes

- **Stripe:** Use `customer.subscription.deleted` webhook for cancellations, `invoice.payment_failed` for dunning
- **Churnkey / ProsperStack / Raaft:** Off-the-shelf cancel flow tools — faster than building custom
- **Segment:** Track cancel flow funnel events for analysis

## Limitations

- Use only when task matches churn/retention scope.
- Save offer discounts affect unit economics — model LTV impact before implementing.
