---
name: stripe-implementer
description: Implements Stripe payments, subscriptions, webhooks and customer management in Next.js and NestJS. Use for checkout, payment intents, billing, Stripe Connect.
metadata:
  version: "2.2.2"
  tags: "stripe, payments, subscriptions"
when_to_use: "stripe webhook, subscription billing"
---

# Stripe Implementer

## When to Use

Use when you're:

- Integrating Stripe payments
- Implementing subscription billing
- Setting up Stripe webhooks
- Managing Stripe customers
- Handling payment intents or checkout sessions
- Implementing Stripe Connect or marketplace features

## Quick Setup

```bash
npm install stripe @stripe/stripe-js
```

```env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## Key Flows

### Payment Methods

- **Checkout Sessions**: Recommended for one-time payments
- **Payment Intents**: For custom payment flows
- **Subscriptions**: For recurring billing

### Webhook Events

- `payment_intent.succeeded` / `payment_intent.payment_failed`
- `customer.subscription.created/updated/deleted`
- `invoice.payment_succeeded/failed`

## Best Practices

- Never expose secret keys client-side
- Always verify webhook signatures
- Use idempotency keys for critical operations
- Test with Stripe CLI: `stripe listen --forward-to localhost:3000/api/webhooks/stripe`

## References

- [Full guide: Setup, payments, subscriptions, webhooks, NestJS](references/full-guide.md)
