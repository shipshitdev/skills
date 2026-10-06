# Stripe Implementation Guide

Complete reference for implementing Stripe payment processing, subscriptions, webhooks, and customer management in Next.js and NestJS applications.

---

## 1. Setup and Configuration

### 1.1 Install Dependencies

```bash
# Core Stripe SDK (server-side)
npm install stripe

# React/Next.js client-side (optional, for Elements)
npm install @stripe/stripe-js @stripe/react-stripe-js
```

### 1.2 Environment Variables

```env
# .env.local (Next.js) or .env (NestJS)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Optional: Price IDs for subscriptions
STRIPE_PRICE_MONTHLY=price_...
STRIPE_PRICE_YEARLY=price_...
```

### 1.3 Client Initialization

#### Next.js Server-Side Client

```typescript
// lib/stripe.ts
import Stripe from 'stripe';

if (!process.env.STRIPE_SECRET_KEY) {
  throw new Error('STRIPE_SECRET_KEY is not set');
}

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
  apiVersion: '2024-12-18.acacia',
  typescript: true,
});
```

#### NestJS Module Configuration

```typescript
// stripe/stripe.module.ts
import { Module, Global } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import Stripe from 'stripe';
import { StripeService } from './stripe.service';
import { StripeController } from './stripe.controller';
import { StripeWebhookController } from './stripe-webhook.controller';

export const STRIPE_CLIENT = 'STRIPE_CLIENT';

@Global()
@Module({
  imports: [ConfigModule],
  controllers: [StripeController, StripeWebhookController],
  providers: [
    {
      provide: STRIPE_CLIENT,
      useFactory: (configService: ConfigService) => {
        const secretKey = configService.getOrThrow<string>('STRIPE_SECRET_KEY');
        return new Stripe(secretKey, {
          apiVersion: '2024-12-18.acacia',
          typescript: true,
        });
      },
      inject: [ConfigService],
    },
    StripeService,
  ],
  exports: [STRIPE_CLIENT, StripeService],
})
export class StripeModule {}
```

```typescript
// stripe/stripe.service.ts
import { Injectable, Inject } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import Stripe from 'stripe';
import { STRIPE_CLIENT } from './stripe.module';

@Injectable()
export class StripeService {
  constructor(
    @Inject(STRIPE_CLIENT) private readonly stripe: Stripe,
    private readonly configService: ConfigService,
  ) {}

  getClient(): Stripe {
    return this.stripe;
  }

  getWebhookSecret(): string {
    return this.configService.getOrThrow<string>('STRIPE_WEBHOOK_SECRET');
  }
}
```

#### Client-Side Initialization (React)

```typescript
// lib/stripe-client.ts
import { loadStripe } from '@stripe/stripe-js';

let stripePromise: ReturnType<typeof loadStripe> | null = null;

export const getStripe = () => {
  if (!stripePromise) {
    stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);
  }
  return stripePromise;
};
```

#### Session Helper (Better Auth)

The route handlers below read the signed-in user with one helper, so swapping the session
source touches a single file.

```typescript
// lib/session.ts
import { headers } from 'next/headers';
import { auth } from '@/lib/auth'; // Better Auth server instance

export async function getUserId(): Promise<string | null> {
  const session = await auth.api.getSession({ headers: await headers() });
  return session?.user.id ?? null;
}
```

If Better Auth runs in a separate API (the house layout), forward the incoming cookie to
that API instead. `getSession` on the client returns `{ data, error }`, not the session:

```typescript
// lib/session.ts (auth served by a separate API)
import { headers } from 'next/headers';
import { authClient } from '@/lib/auth-client';

export async function getUserId(): Promise<string | null> {
  const { data, error } = await authClient.getSession({
    fetchOptions: { headers: await headers() },
  });
  if (error) return null;
  return data?.user.id ?? null;
}
```

---

## 2. Payment Processing

### 2.1 Checkout Sessions (Recommended for Most Use Cases)

Checkout Sessions provide a Stripe-hosted payment page with built-in UI, validation, and compliance.

#### Next.js App Router - Create Checkout Session

```typescript
// app/api/checkout/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe';
import { getUserId } from '@/lib/session';

interface CheckoutRequestBody {
  priceId: string;
  quantity?: number;
  successUrl?: string;
  cancelUrl?: string;
}

export async function POST(request: NextRequest) {
  try {
    const userId = await getUserId();
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body: CheckoutRequestBody = await request.json();
    const { priceId, quantity = 1, successUrl, cancelUrl } = body;

    if (!priceId) {
      return NextResponse.json({ error: 'Price ID is required' }, { status: 400 });
    }

    const baseUrl = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000';

    const session = await stripe.checkout.sessions.create({
      mode: 'payment', // or 'subscription' for recurring
      payment_method_types: ['card'],
      line_items: [
        {
          price: priceId,
          quantity,
        },
      ],
      success_url: successUrl || `${baseUrl}/checkout/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: cancelUrl || `${baseUrl}/checkout/cancel`,
      client_reference_id: userId,
      metadata: {
        userId,
      },
    });

    return NextResponse.json({ sessionId: session.id, url: session.url });
  } catch (error) {
    console.error('Checkout session error:', error);

    if (error instanceof Stripe.errors.StripeError) {
      return NextResponse.json(
        { error: error.message },
        { status: error.statusCode || 500 }
      );
    }

    return NextResponse.json(
      { error: 'Failed to create checkout session' },
      { status: 500 }
    );
  }
}
```

#### NestJS - Create Checkout Session

```typescript
// stripe/dto/create-checkout.dto.ts
import { IsString, IsOptional, IsNumber, Min } from 'class-validator';

export class CreateCheckoutDto {
  @IsString()
  priceId: string;

  @IsOptional()
  @IsNumber()
  @Min(1)
  quantity?: number;

  @IsOptional()
  @IsString()
  successUrl?: string;

  @IsOptional()
  @IsString()
  cancelUrl?: string;
}
```

```typescript
// stripe/stripe.controller.ts
import { Controller, Post, Body, UseGuards, Req } from '@nestjs/common';
import { StripeService } from './stripe.service';
import { CreateCheckoutDto } from './dto/create-checkout.dto';
import { AuthGuard } from '@/auth/auth.guard';
import { CurrentUser } from '@/auth/current-user.decorator';

@Controller('stripe')
export class StripeController {
  constructor(private readonly stripeService: StripeService) {}

  @Post('checkout')
  @UseGuards(AuthGuard)
  async createCheckoutSession(
    @Body() dto: CreateCheckoutDto,
    @CurrentUser() user: { id: string },
  ) {
    const stripe = this.stripeService.getClient();
    const baseUrl = process.env.APP_URL || 'http://localhost:3000';

    const session = await stripe.checkout.sessions.create({
      mode: 'payment',
      payment_method_types: ['card'],
      line_items: [
        {
          price: dto.priceId,
          quantity: dto.quantity || 1,
        },
      ],
      success_url: dto.successUrl || `${baseUrl}/checkout/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: dto.cancelUrl || `${baseUrl}/checkout/cancel`,
      client_reference_id: user.id,
      metadata: {
        userId: user.id,
      },
    });

    return { sessionId: session.id, url: session.url };
  }
}
```

#### Client-Side Redirect to Checkout

```typescript
// components/CheckoutButton.tsx
'use client';

import { useState } from 'react';
import { getStripe } from '@/lib/stripe-client';

interface CheckoutButtonProps {
  priceId: string;
  quantity?: number;
}

export function CheckoutButton({ priceId, quantity = 1 }: CheckoutButtonProps) {
  const [loading, setLoading] = useState(false);

  const handleCheckout = async () => {
    setLoading(true);

    try {
      const response = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ priceId, quantity }),
      });

      const { sessionId, url } = await response.json();

      if (url) {
        // Redirect to Stripe Checkout
        window.location.href = url;
      } else {
        // Fallback: use Stripe.js redirect
        const stripe = await getStripe();
        await stripe?.redirectToCheckout({ sessionId });
      }
    } catch (error) {
      console.error('Checkout error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button onClick={handleCheckout} disabled={loading}>
      {loading ? 'Processing...' : 'Buy Now'}
    </button>
  );
}
```

### 2.2 Payment Intents (Custom Payment Flows)

Payment Intents provide full control over the payment UI using Stripe Elements.

#### Next.js - Create Payment Intent

```typescript
// app/api/payment-intent/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe';
import { getUserId } from '@/lib/session';

interface PaymentIntentRequestBody {
  amount: number; // in cents
  currency?: string;
  metadata?: Record<string, string>;
}

export async function POST(request: NextRequest) {
  try {
    const userId = await getUserId();
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body: PaymentIntentRequestBody = await request.json();
    const { amount, currency = 'usd', metadata = {} } = body;

    if (!amount || amount < 50) {
      return NextResponse.json(
        { error: 'Amount must be at least 50 cents' },
        { status: 400 }
      );
    }

    const paymentIntent = await stripe.paymentIntents.create({
      amount,
      currency,
      automatic_payment_methods: { enabled: true },
      // Caller metadata first, trusted userId last, so a request cannot rebind the payment.
      metadata: {
        ...metadata,
        userId,
      },
    });

    return NextResponse.json({
      clientSecret: paymentIntent.client_secret,
      paymentIntentId: paymentIntent.id,
    });
  } catch (error) {
    console.error('Payment intent error:', error);

    if (error instanceof Stripe.errors.StripeError) {
      return NextResponse.json(
        { error: error.message },
        { status: error.statusCode || 500 }
      );
    }

    return NextResponse.json(
      { error: 'Failed to create payment intent' },
      { status: 500 }
    );
  }
}
```

#### NestJS - Create Payment Intent

```typescript
// stripe/dto/create-payment-intent.dto.ts
import { IsNumber, Min, IsOptional, IsString } from 'class-validator';

export class CreatePaymentIntentDto {
  @IsNumber()
  @Min(50)
  amount: number; // in cents

  @IsOptional()
  @IsString()
  currency?: string;

  @IsOptional()
  metadata?: Record<string, string>;
}
```

```typescript
// stripe/stripe.controller.ts (add to existing controller)
@Post('payment-intent')
@UseGuards(AuthGuard)
async createPaymentIntent(
  @Body() dto: CreatePaymentIntentDto,
  @CurrentUser() user: { id: string },
) {
  const stripe = this.stripeService.getClient();

  const paymentIntent = await stripe.paymentIntents.create({
    amount: dto.amount,
    currency: dto.currency || 'usd',
    automatic_payment_methods: { enabled: true },
    // Caller metadata first, trusted userId last, so a request cannot rebind the payment.
    metadata: {
      ...dto.metadata,
      userId: user.id,
    },
  });

  return {
    clientSecret: paymentIntent.client_secret,
    paymentIntentId: paymentIntent.id,
  };
}
```

#### Client-Side Payment Form with Elements

```typescript
// components/PaymentForm.tsx
'use client';

import { useState, useEffect } from 'react';
import {
  Elements,
  PaymentElement,
  useStripe,
  useElements,
} from '@stripe/react-stripe-js';
import { getStripe } from '@/lib/stripe-client';

interface PaymentFormProps {
  amount: number; // in cents
  onSuccess?: (paymentIntentId: string) => void;
  onError?: (error: string) => void;
}

function PaymentFormInner({ onSuccess, onError }: Omit<PaymentFormProps, 'amount'>) {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setLoading(true);
    setErrorMessage(null);

    const { error, paymentIntent } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/payment/success`,
      },
      redirect: 'if_required',
    });

    if (error) {
      setErrorMessage(error.message || 'Payment failed');
      onError?.(error.message || 'Payment failed');
    } else if (paymentIntent?.status === 'succeeded') {
      onSuccess?.(paymentIntent.id);
    }

    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <PaymentElement />
      {errorMessage && <div className="text-red-500 mt-2">{errorMessage}</div>}
      <button
        type="submit"
        disabled={!stripe || loading}
        className="mt-4 w-full bg-blue-600 text-white py-2 rounded disabled:opacity-50"
      >
        {loading ? 'Processing...' : 'Pay Now'}
      </button>
    </form>
  );
}

export function PaymentForm({ amount, onSuccess, onError }: PaymentFormProps) {
  const [clientSecret, setClientSecret] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    fetch('/api/payment-intent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount }),
      signal: controller.signal,
    })
      .then((res) => res.json())
      .then((data) => setClientSecret(data.clientSecret))
      .catch((err) => {
        if (err.name !== 'AbortError') {
          onError?.(err.message);
        }
      });

    return () => controller.abort();
  }, [amount, onError]);

  if (!clientSecret) {
    return <div>Loading payment form...</div>;
  }

  return (
    <Elements
      stripe={getStripe()}
      options={{
        clientSecret,
        appearance: {
          theme: 'stripe',
          variables: {
            colorPrimary: '#0066ff',
          },
        },
      }}
    >
      <PaymentFormInner onSuccess={onSuccess} onError={onError} />
    </Elements>
  );
}
```

---

## 3. Subscription Management

### 3.1 Products and Prices

Products and prices should be created in the Stripe Dashboard or via API. Here's how to manage them programmatically.

#### Create Product and Price

```typescript
// scripts/create-products.ts (run once to set up)
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-12-18.acacia',
});

async function createProducts() {
  // Create product
  const product = await stripe.products.create({
    name: 'Pro Plan',
    description: 'Full access to all features',
    metadata: {
      tier: 'pro',
    },
  });

  // Create monthly price
  const monthlyPrice = await stripe.prices.create({
    product: product.id,
    unit_amount: 2900, // $29.00
    currency: 'usd',
    recurring: {
      interval: 'month',
    },
    metadata: {
      tier: 'pro',
      interval: 'monthly',
    },
  });

  // Create yearly price (with discount)
  const yearlyPrice = await stripe.prices.create({
    product: product.id,
    unit_amount: 29000, // $290.00 (2 months free)
    currency: 'usd',
    recurring: {
      interval: 'year',
    },
    metadata: {
      tier: 'pro',
      interval: 'yearly',
    },
  });

  console.log('Product:', product.id);
  console.log('Monthly Price:', monthlyPrice.id);
  console.log('Yearly Price:', yearlyPrice.id);
}

createProducts();
```

### 3.2 Create Subscription

#### Next.js - Create Subscription via Checkout

```typescript
// app/api/subscription/checkout/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe';
import { getUserId } from '@/lib/session';
import { db } from '@/lib/db';

interface SubscriptionCheckoutBody {
  priceId: string;
  trialDays?: number;
}

export async function POST(request: NextRequest) {
  try {
    const userId = await getUserId();
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body: SubscriptionCheckoutBody = await request.json();
    const { priceId, trialDays } = body;

    // Get or create Stripe customer
    let customerId: string;
    const user = await db.user.findUnique({
      where: { id: userId },
      select: { stripeCustomerId: true, email: true },
    });

    if (user?.stripeCustomerId) {
      customerId = user.stripeCustomerId;
    } else {
      const customer = await stripe.customers.create({
        email: user?.email,
        metadata: { userId },
      });
      customerId = customer.id;

      await db.user.update({
        where: { id: userId },
        data: { stripeCustomerId: customerId },
      });
    }

    const baseUrl = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000';

    const sessionParams: Stripe.Checkout.SessionCreateParams = {
      mode: 'subscription',
      customer: customerId,
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: `${baseUrl}/subscription/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${baseUrl}/pricing`,
      metadata: { userId },
    };

    // Add trial if specified
    if (trialDays && trialDays > 0) {
      sessionParams.subscription_data = {
        trial_period_days: trialDays,
      };
    }

    const session = await stripe.checkout.sessions.create(sessionParams);

    return NextResponse.json({ url: session.url });
  } catch (error) {
    console.error('Subscription checkout error:', error);
    return NextResponse.json(
      { error: 'Failed to create subscription checkout' },
      { status: 500 }
    );
  }
}
```

#### NestJS - Create Subscription Directly

```typescript
// stripe/dto/create-subscription.dto.ts
import { IsString, IsOptional, IsNumber, Min, Max } from 'class-validator';

export class CreateSubscriptionDto {
  @IsString()
  priceId: string;

  @IsOptional()
  @IsString()
  paymentMethodId?: string;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(30)
  trialDays?: number;
}
```

```typescript
// stripe/stripe.service.ts (add to existing service)
async createSubscription(
  userId: string,
  dto: CreateSubscriptionDto,
): Promise<Stripe.Subscription> {
  const user = await this.usersService.findById(userId);

  if (!user.stripeCustomerId) {
    throw new BadRequestException('User does not have a Stripe customer');
  }

  const subscriptionParams: Stripe.SubscriptionCreateParams = {
    customer: user.stripeCustomerId,
    items: [{ price: dto.priceId }],
    payment_behavior: 'default_incomplete',
    payment_settings: {
      save_default_payment_method: 'on_subscription',
    },
    expand: ['latest_invoice.payment_intent'],
    metadata: { userId },
  };

  // Add trial if specified
  if (dto.trialDays && dto.trialDays > 0) {
    subscriptionParams.trial_period_days = dto.trialDays;
  }

  // Attach payment method if provided
  if (dto.paymentMethodId) {
    await this.stripe.paymentMethods.attach(dto.paymentMethodId, {
      customer: user.stripeCustomerId,
    });
    subscriptionParams.default_payment_method = dto.paymentMethodId;
  }

  return this.stripe.subscriptions.create(subscriptionParams);
}
```

### 3.3 Update Subscription

```typescript
// Next.js - Update subscription plan
// app/api/subscription/update/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe';
import { getUserId } from '@/lib/session';
import { db } from '@/lib/db';

interface UpdateSubscriptionBody {
  newPriceId: string;
  prorationBehavior?: 'create_prorations' | 'none' | 'always_invoice';
}

export async function POST(request: NextRequest) {
  try {
    const userId = await getUserId();
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body: UpdateSubscriptionBody = await request.json();
    const { newPriceId, prorationBehavior = 'create_prorations' } = body;

    // Get user's active subscription
    const user = await db.user.findUnique({
      where: { id: userId },
      select: { stripeSubscriptionId: true },
    });

    if (!user?.stripeSubscriptionId) {
      return NextResponse.json({ error: 'No active subscription' }, { status: 400 });
    }

    // Get current subscription to find the item ID
    const subscription = await stripe.subscriptions.retrieve(user.stripeSubscriptionId);
    const subscriptionItemId = subscription.items.data[0].id;

    // Update subscription
    const updatedSubscription = await stripe.subscriptions.update(
      user.stripeSubscriptionId,
      {
        items: [
          {
            id: subscriptionItemId,
            price: newPriceId,
          },
        ],
        proration_behavior: prorationBehavior,
      }
    );

    return NextResponse.json({
      subscription: {
        id: updatedSubscription.id,
        status: updatedSubscription.status,
        currentPeriodEnd: updatedSubscription.current_period_end,
      },
    });
  } catch (error) {
    console.error('Update subscription error:', error);
    return NextResponse.json(
      { error: 'Failed to update subscription' },
      { status: 500 }
    );
  }
}
```

### 3.4 Cancel Subscription

```typescript
// Next.js - Cancel subscription
// app/api/subscription/cancel/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe';
import { getUserId } from '@/lib/session';
import { db } from '@/lib/db';

interface CancelSubscriptionBody {
  cancelImmediately?: boolean;
}

export async function POST(request: NextRequest) {
  try {
    const userId = await getUserId();
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body: CancelSubscriptionBody = await request.json();
    const { cancelImmediately = false } = body;

    const user = await db.user.findUnique({
      where: { id: userId },
      select: { stripeSubscriptionId: true },
    });

    if (!user?.stripeSubscriptionId) {
      return NextResponse.json({ error: 'No active subscription' }, { status: 400 });
    }

    let subscription: Stripe.Subscription;

    if (cancelImmediately) {
      // Cancel immediately
      subscription = await stripe.subscriptions.cancel(user.stripeSubscriptionId);
    } else {
      // Cancel at period end (recommended)
      subscription = await stripe.subscriptions.update(user.stripeSubscriptionId, {
        cancel_at_period_end: true,
      });
    }

    return NextResponse.json({
      subscription: {
        id: subscription.id,
        status: subscription.status,
        cancelAtPeriodEnd: subscription.cancel_at_period_end,
        currentPeriodEnd: subscription.current_period_end,
      },
    });
  } catch (error) {
    console.error('Cancel subscription error:', error);
    return NextResponse.json(
      { error: 'Failed to cancel subscription' },
      { status: 500 }
    );
  }
}
```

### 3.5 Reactivate Subscription

```typescript
// app/api/subscription/reactivate/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe';
import { getUserId } from '@/lib/session';
import { db } from '@/lib/db';

export async function POST(request: NextRequest) {
  try {
    const userId = await getUserId();
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const user = await db.user.findUnique({
      where: { id: userId },
      select: { stripeSubscriptionId: true },
    });

    if (!user?.stripeSubscriptionId) {
      return NextResponse.json({ error: 'No subscription found' }, { status: 400 });
    }

    // Remove cancellation
    const subscription = await stripe.subscriptions.update(user.stripeSubscriptionId, {
      cancel_at_period_end: false,
    });

    return NextResponse.json({
      subscription: {
        id: subscription.id,
        status: subscription.status,
        cancelAtPeriodEnd: subscription.cancel_at_period_end,
      },
    });
  } catch (error) {
    console.error('Reactivate subscription error:', error);
    return NextResponse.json(
      { error: 'Failed to reactivate subscription' },
      { status: 500 }
    );
  }
}
```

---

## 4. Customer Management

### 4.1 Create Customer

```typescript
// lib/stripe-customers.ts
import { stripe } from '@/lib/stripe';
import { db } from '@/lib/db';

interface CreateCustomerParams {
  userId: string;
  email: string;
  name?: string;
  metadata?: Record<string, string>;
}

export async function createStripeCustomer({
  userId,
  email,
  name,
  metadata = {},
}: CreateCustomerParams): Promise<string> {
  // Check if customer already exists
  const existingUser = await db.user.findUnique({
    where: { id: userId },
    select: { stripeCustomerId: true },
  });

  if (existingUser?.stripeCustomerId) {
    return existingUser.stripeCustomerId;
  }

  // Create new customer
  const customer = await stripe.customers.create({
    email,
    name,
    // Trusted userId last; the webhook resolves the user from this key.
    metadata: {
      ...metadata,
      userId,
    },
  });

  // Save to database
  await db.user.update({
    where: { id: userId },
    data: { stripeCustomerId: customer.id },
  });

  return customer.id;
}
```

### 4.2 Retrieve Customer

```typescript
// lib/stripe-customers.ts
export async function getStripeCustomer(customerId: string) {
  const customer = await stripe.customers.retrieve(customerId, {
    expand: ['subscriptions', 'default_source', 'invoice_settings.default_payment_method'],
  });

  if (customer.deleted) {
    return null;
  }

  return customer;
}

export async function getCustomerByUserId(userId: string) {
  const user = await db.user.findUnique({
    where: { id: userId },
    select: { stripeCustomerId: true },
  });

  if (!user?.stripeCustomerId) {
    return null;
  }

  return getStripeCustomer(user.stripeCustomerId);
}
```

### 4.3 Update Customer

```typescript
// lib/stripe-customers.ts
interface UpdateCustomerParams {
  customerId: string;
  email?: string;
  name?: string;
  metadata?: Record<string, string>;
  defaultPaymentMethodId?: string;
}

export async function updateStripeCustomer({
  customerId,
  email,
  name,
  metadata,
  defaultPaymentMethodId,
}: UpdateCustomerParams) {
  const updateParams: Stripe.CustomerUpdateParams = {};

  if (email) updateParams.email = email;
  if (name) updateParams.name = name;
  if (metadata) {
    // Never let an update rebind the customer to another user.
    const { userId: _ignored, ...safeMetadata } = metadata;
    updateParams.metadata = safeMetadata;
  }
  if (defaultPaymentMethodId) {
    updateParams.invoice_settings = {
      default_payment_method: defaultPaymentMethodId,
    };
  }

  return stripe.customers.update(customerId, updateParams);
}
```

### 4.4 Customer Portal

```typescript
// app/api/customer-portal/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe';
import { getUserId } from '@/lib/session';
import { db } from '@/lib/db';

export async function POST(request: NextRequest) {
  try {
    const userId = await getUserId();
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const user = await db.user.findUnique({
      where: { id: userId },
      select: { stripeCustomerId: true },
    });

    if (!user?.stripeCustomerId) {
      return NextResponse.json({ error: 'No Stripe customer found' }, { status: 400 });
    }

    const baseUrl = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000';

    const portalSession = await stripe.billingPortal.sessions.create({
      customer: user.stripeCustomerId,
      return_url: `${baseUrl}/settings/billing`,
    });

    return NextResponse.json({ url: portalSession.url });
  } catch (error) {
    console.error('Customer portal error:', error);
    return NextResponse.json(
      { error: 'Failed to create customer portal session' },
      { status: 500 }
    );
  }
}
```

---

## 5. Webhook Handling

### 5.1 Stripe CLI Setup (Development)

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login to Stripe
stripe login

# Listen for webhooks and forward to local server
stripe listen --forward-to localhost:3000/api/webhooks/stripe

# Copy the webhook signing secret (whsec_...) to your .env file
```

### 5.2 Next.js Webhook Endpoint

```typescript
// app/api/webhooks/stripe/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { headers } from 'next/headers';
import { stripe } from '@/lib/stripe';
import { db } from '@/lib/db';
import Stripe from 'stripe';

// Disable body parsing - Stripe requires raw body for signature verification
export const runtime = 'nodejs';

async function handleCheckoutSessionCompleted(session: Stripe.Checkout.Session) {
  const userId = session.metadata?.userId || session.client_reference_id;

  if (!userId) {
    console.error('No userId in checkout session');
    return;
  }

  if (session.mode === 'subscription') {
    const subscriptionId = session.subscription as string;
    const customerId = session.customer as string;

    await db.user.update({
      where: { id: userId },
      data: {
        stripeCustomerId: customerId,
        stripeSubscriptionId: subscriptionId,
        subscriptionStatus: 'active',
      },
    });
  } else if (session.mode === 'payment') {
    // Handle one-time payment
    await db.purchase.create({
      data: {
        userId,
        stripePaymentIntentId: session.payment_intent as string,
        amount: session.amount_total || 0,
        status: 'completed',
      },
    });
  }
}

async function handleSubscriptionUpdated(subscription: Stripe.Subscription) {
  const userId = subscription.metadata?.userId;

  if (!userId) {
    // Try to find user by customer ID
    const user = await db.user.findFirst({
      where: { stripeCustomerId: subscription.customer as string },
    });
    if (!user) return;
  }

  await db.user.updateMany({
    where: {
      OR: [
        { id: userId || '' },
        { stripeCustomerId: subscription.customer as string },
      ],
    },
    data: {
      stripeSubscriptionId: subscription.id,
      subscriptionStatus: subscription.status,
      subscriptionPriceId: subscription.items.data[0]?.price.id,
      currentPeriodEnd: new Date(subscription.current_period_end * 1000),
      cancelAtPeriodEnd: subscription.cancel_at_period_end,
    },
  });
}

async function handleSubscriptionDeleted(subscription: Stripe.Subscription) {
  await db.user.updateMany({
    where: { stripeSubscriptionId: subscription.id },
    data: {
      subscriptionStatus: 'canceled',
      stripeSubscriptionId: null,
      currentPeriodEnd: null,
    },
  });
}

async function handleInvoicePaymentFailed(invoice: Stripe.Invoice) {
  const customerId = invoice.customer as string;

  await db.user.updateMany({
    where: { stripeCustomerId: customerId },
    data: { subscriptionStatus: 'past_due' },
  });

  // Optionally send notification email
  // await sendPaymentFailedEmail(customerId, invoice);
}

async function handlePaymentIntentSucceeded(paymentIntent: Stripe.PaymentIntent) {
  const userId = paymentIntent.metadata?.userId;

  if (!userId) return;

  await db.purchase.upsert({
    where: { stripePaymentIntentId: paymentIntent.id },
    create: {
      userId,
      stripePaymentIntentId: paymentIntent.id,
      amount: paymentIntent.amount,
      status: 'completed',
    },
    update: {
      status: 'completed',
    },
  });
}

export async function POST(request: NextRequest) {
  const body = await request.text();
  const headersList = await headers();
  const signature = headersList.get('stripe-signature');

  if (!signature) {
    return NextResponse.json({ error: 'Missing signature' }, { status: 400 });
  }

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    );
  } catch (err) {
    console.error('Webhook signature verification failed:', err);
    return NextResponse.json(
      { error: 'Invalid signature' },
      { status: 400 }
    );
  }

  try {
    switch (event.type) {
      case 'checkout.session.completed':
        await handleCheckoutSessionCompleted(event.data.object as Stripe.Checkout.Session);
        break;

      case 'customer.subscription.created':
      case 'customer.subscription.updated':
        await handleSubscriptionUpdated(event.data.object as Stripe.Subscription);
        break;

      case 'customer.subscription.deleted':
        await handleSubscriptionDeleted(event.data.object as Stripe.Subscription);
        break;

      case 'invoice.payment_failed':
        await handleInvoicePaymentFailed(event.data.object as Stripe.Invoice);
        break;

      case 'payment_intent.succeeded':
        await handlePaymentIntentSucceeded(event.data.object as Stripe.PaymentIntent);
        break;

      default:
        console.log(`Unhandled event type: ${event.type}`);
    }

    return NextResponse.json({ received: true });
  } catch (error) {
    console.error('Webhook handler error:', error);
    return NextResponse.json(
      { error: 'Webhook handler failed' },
      { status: 500 }
    );
  }
}
```

### 5.3 NestJS Webhook Endpoint with Raw Body Middleware

```typescript
// stripe/stripe-webhook.controller.ts
import {
  Controller,
  Post,
  Headers,
  RawBodyRequest,
  Req,
  BadRequestException,
  Logger,
} from '@nestjs/common';
import { Request } from 'express';
import Stripe from 'stripe';
import { StripeService } from './stripe.service';
import { StripeWebhookService } from './stripe-webhook.service';

@Controller('webhooks/stripe')
export class StripeWebhookController {
  private readonly logger = new Logger(StripeWebhookController.name);

  constructor(
    private readonly stripeService: StripeService,
    private readonly webhookService: StripeWebhookService,
  ) {}

  @Post()
  async handleWebhook(
    @Req() request: RawBodyRequest<Request>,
    @Headers('stripe-signature') signature: string,
  ) {
    if (!signature) {
      throw new BadRequestException('Missing stripe-signature header');
    }

    const rawBody = request.rawBody;
    if (!rawBody) {
      throw new BadRequestException('Missing raw body');
    }

    const stripe = this.stripeService.getClient();
    const webhookSecret = this.stripeService.getWebhookSecret();

    let event: Stripe.Event;

    try {
      event = stripe.webhooks.constructEvent(rawBody, signature, webhookSecret);
    } catch (err) {
      this.logger.error('Webhook signature verification failed', err);
      throw new BadRequestException('Invalid signature');
    }

    try {
      await this.webhookService.handleEvent(event);
      return { received: true };
    } catch (error) {
      this.logger.error('Webhook handler error', error);
      throw error;
    }
  }
}
```

```typescript
// stripe/stripe-webhook.service.ts
import { Injectable, Logger } from '@nestjs/common';
import Stripe from 'stripe';
import { UsersService } from '@/users/users.service';
import { PurchasesService } from '@/purchases/purchases.service';

@Injectable()
export class StripeWebhookService {
  private readonly logger = new Logger(StripeWebhookService.name);

  constructor(
    private readonly usersService: UsersService,
    private readonly purchasesService: PurchasesService,
  ) {}

  async handleEvent(event: Stripe.Event): Promise<void> {
    this.logger.log(`Processing webhook event: ${event.type}`);

    switch (event.type) {
      case 'checkout.session.completed':
        await this.handleCheckoutSessionCompleted(
          event.data.object as Stripe.Checkout.Session,
        );
        break;

      case 'customer.subscription.created':
      case 'customer.subscription.updated':
        await this.handleSubscriptionUpdated(
          event.data.object as Stripe.Subscription,
        );
        break;

      case 'customer.subscription.deleted':
        await this.handleSubscriptionDeleted(
          event.data.object as Stripe.Subscription,
        );
        break;

      case 'invoice.payment_failed':
        await this.handleInvoicePaymentFailed(
          event.data.object as Stripe.Invoice,
        );
        break;

      case 'payment_intent.succeeded':
        await this.handlePaymentIntentSucceeded(
          event.data.object as Stripe.PaymentIntent,
        );
        break;

      default:
        this.logger.log(`Unhandled event type: ${event.type}`);
    }
  }

  private async handleCheckoutSessionCompleted(
    session: Stripe.Checkout.Session,
  ) {
    const userId = session.metadata?.userId || session.client_reference_id;
    if (!userId) {
      this.logger.error('No userId in checkout session');
      return;
    }

    if (session.mode === 'subscription') {
      await this.usersService.updateSubscription(userId, {
        stripeCustomerId: session.customer as string,
        stripeSubscriptionId: session.subscription as string,
        subscriptionStatus: 'active',
      });
    } else if (session.mode === 'payment') {
      await this.purchasesService.create({
        userId,
        stripePaymentIntentId: session.payment_intent as string,
        amount: session.amount_total || 0,
        status: 'completed',
      });
    }
  }

  private async handleSubscriptionUpdated(subscription: Stripe.Subscription) {
    const customerId = subscription.customer as string;
    const user = await this.usersService.findByStripeCustomerId(customerId);

    if (!user) {
      this.logger.warn(`No user found for customer: ${customerId}`);
      return;
    }

    await this.usersService.updateSubscription(user.id, {
      stripeSubscriptionId: subscription.id,
      subscriptionStatus: subscription.status,
      subscriptionPriceId: subscription.items.data[0]?.price.id,
      currentPeriodEnd: new Date(subscription.current_period_end * 1000),
      cancelAtPeriodEnd: subscription.cancel_at_period_end,
    });
  }

  private async handleSubscriptionDeleted(subscription: Stripe.Subscription) {
    await this.usersService.updateByStripeSubscriptionId(subscription.id, {
      subscriptionStatus: 'canceled',
      stripeSubscriptionId: null,
      currentPeriodEnd: null,
    });
  }

  private async handleInvoicePaymentFailed(invoice: Stripe.Invoice) {
    const customerId = invoice.customer as string;

    await this.usersService.updateByStripeCustomerId(customerId, {
      subscriptionStatus: 'past_due',
    });
  }

  private async handlePaymentIntentSucceeded(
    paymentIntent: Stripe.PaymentIntent,
  ) {
    const userId = paymentIntent.metadata?.userId;
    if (!userId) return;

    await this.purchasesService.upsert({
      stripePaymentIntentId: paymentIntent.id,
      userId,
      amount: paymentIntent.amount,
      status: 'completed',
    });
  }
}
```

#### NestJS Raw Body Configuration

```typescript
// main.ts
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule, {
    rawBody: true, // Enable raw body parsing for webhooks
  });

  // Configure raw body for specific routes
  app.useBodyParser('json', {
    verify: (req: any, res, buf) => {
      // Store raw body for webhook signature verification
      if (req.url?.includes('/webhooks/stripe')) {
        req.rawBody = buf;
      }
    },
  });

  await app.listen(3000);
}
bootstrap();
```

---

## 6. Best Practices

### 6.1 Security

```typescript
// NEVER expose secret keys client-side
// BAD: process.env.STRIPE_SECRET_KEY in client code
// GOOD: Only use NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY client-side

// Always verify webhook signatures
const event = stripe.webhooks.constructEvent(body, signature, webhookSecret);

// Validate user ownership before operations
async function updateSubscription(userId: string, subscriptionId: string) {
  const subscription = await stripe.subscriptions.retrieve(subscriptionId);
  const user = await db.user.findUnique({ where: { id: userId } });

  if (subscription.customer !== user?.stripeCustomerId) {
    throw new Error('Unauthorized');
  }

  // Proceed with update
}

// Use environment-specific keys
const isProduction = process.env.NODE_ENV === 'production';
// Test mode: sk_test_..., pk_test_...
// Live mode: sk_live_..., pk_live_...
```

### 6.2 Error Handling

```typescript
import Stripe from 'stripe';

async function handleStripeOperation<T>(operation: () => Promise<T>): Promise<T> {
  try {
    return await operation();
  } catch (error) {
    if (error instanceof Stripe.errors.StripeCardError) {
      // Card was declined
      throw new Error(`Card declined: ${error.message}`);
    } else if (error instanceof Stripe.errors.StripeRateLimitError) {
      // Too many requests
      throw new Error('Too many requests. Please try again later.');
    } else if (error instanceof Stripe.errors.StripeInvalidRequestError) {
      // Invalid parameters
      throw new Error(`Invalid request: ${error.message}`);
    } else if (error instanceof Stripe.errors.StripeAuthenticationError) {
      // API key issue
      console.error('Stripe authentication error - check API keys');
      throw new Error('Payment service configuration error');
    } else if (error instanceof Stripe.errors.StripeConnectionError) {
      // Network issue
      throw new Error('Unable to connect to payment service. Please try again.');
    } else if (error instanceof Stripe.errors.StripeAPIError) {
      // Stripe server error
      console.error('Stripe API error:', error);
      throw new Error('Payment service temporarily unavailable');
    } else {
      // Unknown error
      console.error('Unknown Stripe error:', error);
      throw new Error('An unexpected error occurred');
    }
  }
}

// Usage
const subscription = await handleStripeOperation(() =>
  stripe.subscriptions.create({
    customer: customerId,
    items: [{ price: priceId }],
  })
);
```

### 6.3 Idempotency Keys

```typescript
import { v4 as uuidv4 } from 'uuid';

// Use idempotency keys for critical operations to prevent duplicate charges
async function createPaymentWithIdempotency(
  amount: number,
  customerId: string,
  idempotencyKey?: string,
) {
  const key = idempotencyKey || uuidv4();

  const paymentIntent = await stripe.paymentIntents.create(
    {
      amount,
      currency: 'usd',
      customer: customerId,
    },
    {
      idempotencyKey: key,
    }
  );

  return paymentIntent;
}

// Idempotency keys are especially important for:
// - Payment creation
// - Subscription creation
// - Refunds
// - Any operation that shouldn't be duplicated
```

### 6.4 Testing

```typescript
// Use test mode API keys for development
// STRIPE_SECRET_KEY=sk_test_...

// Test card numbers
const TEST_CARDS = {
  success: '4242424242424242',
  declineGeneric: '4000000000000002',
  declineInsufficientFunds: '4000000000009995',
  requiresAuthentication: '4000002500003155',
  expiredCard: '4000000000000069',
};

// Test webhook events with Stripe CLI
// stripe trigger payment_intent.succeeded
// stripe trigger customer.subscription.created

// Integration test example
describe('Stripe Checkout', () => {
  it('creates checkout session', async () => {
    const response = await request(app)
      .post('/api/checkout')
      .send({ priceId: 'price_test123' })
      .expect(200);

    expect(response.body.sessionId).toBeDefined();
    expect(response.body.url).toContain('checkout.stripe.com');
  });
});
```

### 6.5 Performance

```typescript
// Use expand sparingly - only request data you need
const subscription = await stripe.subscriptions.retrieve(subscriptionId, {
  expand: ['latest_invoice'], // Only expand what you need
});

// Paginate large lists
async function* getAllCustomers() {
  let hasMore = true;
  let startingAfter: string | undefined;

  while (hasMore) {
    const customers = await stripe.customers.list({
      limit: 100,
      starting_after: startingAfter,
    });

    for (const customer of customers.data) {
      yield customer;
    }

    hasMore = customers.has_more;
    if (customers.data.length > 0) {
      startingAfter = customers.data[customers.data.length - 1].id;
    }
  }
}

// Cache frequently accessed data
import { cache } from 'react';

export const getSubscriptionPlans = cache(async () => {
  const prices = await stripe.prices.list({
    active: true,
    expand: ['data.product'],
    limit: 10,
  });
  return prices.data;
});

// Batch operations when possible
const customers = await stripe.customers.list({ limit: 100 });
await Promise.all(
  customers.data.map((customer) =>
    stripe.customers.update(customer.id, { metadata: { migrated: 'true' } })
  )
);
```

---

## 7. Common Stripe Events

### Payment Events

| Event | Description |
|-------|-------------|
| `payment_intent.created` | Payment intent created |
| `payment_intent.succeeded` | Payment completed successfully |
| `payment_intent.payment_failed` | Payment failed |
| `payment_intent.canceled` | Payment canceled |
| `payment_intent.requires_action` | Payment requires customer action (3D Secure) |

### Checkout Events

| Event | Description |
|-------|-------------|
| `checkout.session.completed` | Checkout session completed successfully |
| `checkout.session.expired` | Checkout session expired |
| `checkout.session.async_payment_succeeded` | Async payment succeeded |
| `checkout.session.async_payment_failed` | Async payment failed |

### Subscription Events

| Event | Description |
|-------|-------------|
| `customer.subscription.created` | Subscription created |
| `customer.subscription.updated` | Subscription updated (plan change, etc.) |
| `customer.subscription.deleted` | Subscription canceled/ended |
| `customer.subscription.trial_will_end` | Trial ending in 3 days |
| `customer.subscription.paused` | Subscription paused |
| `customer.subscription.resumed` | Subscription resumed |

### Invoice Events

| Event | Description |
|-------|-------------|
| `invoice.created` | Invoice created |
| `invoice.finalized` | Invoice finalized and ready |
| `invoice.paid` | Invoice paid successfully |
| `invoice.payment_succeeded` | Invoice payment succeeded |
| `invoice.payment_failed` | Invoice payment failed |
| `invoice.upcoming` | Invoice will be created soon |
| `invoice.marked_uncollectible` | Invoice marked as uncollectible |

### Customer Events

| Event | Description |
|-------|-------------|
| `customer.created` | Customer created |
| `customer.updated` | Customer updated |
| `customer.deleted` | Customer deleted |
| `customer.source.created` | Payment source added |
| `customer.source.updated` | Payment source updated |

### Charge Events

| Event | Description |
|-------|-------------|
| `charge.succeeded` | Charge succeeded |
| `charge.failed` | Charge failed |
| `charge.refunded` | Charge refunded |
| `charge.dispute.created` | Dispute/chargeback created |
| `charge.dispute.closed` | Dispute closed |

---

## 8. Example User Requests

### "Add Stripe payments to my app"

1. Install dependencies: `npm install stripe @stripe/stripe-js`
2. Set up environment variables
3. Create server-side Stripe client
4. Implement checkout session endpoint
5. Add checkout button component
6. Set up webhook endpoint
7. Configure webhook in Stripe Dashboard

### "Set up subscription billing"

1. Create products and prices in Stripe Dashboard
2. Implement subscription checkout endpoint
3. Add subscription management endpoints (update, cancel, reactivate)
4. Handle subscription webhooks
5. Store subscription status in database
6. Add customer portal for self-service

### "Handle Stripe webhooks"

1. Install Stripe CLI for local development
2. Create webhook endpoint with signature verification
3. Implement handlers for each event type
4. Store relevant data in database
5. Handle errors gracefully
6. Configure webhook endpoint in Stripe Dashboard

### "Let users manage their billing"

1. Create Stripe customer on signup
2. Implement customer portal session endpoint
3. Add "Manage Billing" button that redirects to portal
4. Configure portal settings in Stripe Dashboard

### "Add one-time payments"

1. Create Payment Intent endpoint
2. Implement payment form with Stripe Elements
3. Handle payment confirmation
4. Process `payment_intent.succeeded` webhook
5. Record purchase in database

---

## Resources

- [Stripe API Reference](https://stripe.com/docs/api)
- [Stripe Dashboard](https://dashboard.stripe.com)
- [Stripe CLI](https://stripe.com/docs/stripe-cli)
- [Test Card Numbers](https://stripe.com/docs/testing#cards)
- [Webhook Events](https://stripe.com/docs/api/events/types)
- [Checkout Sessions](https://stripe.com/docs/payments/checkout)
- [Payment Intents](https://stripe.com/docs/payments/payment-intents)
- [Subscriptions](https://stripe.com/docs/billing/subscriptions/overview)
- [Customer Portal](https://stripe.com/docs/billing/subscriptions/customer-portal)
