# Resend Email — Full Guide

## Installation

```bash
# Core
npm install resend

# React Email (optional but recommended)
npm install @react-email/components react-email

# Dev preview
npx react-email dev
```

## Environment Variables

```env
RESEND_API_KEY=re_...
EMAIL_FROM=App Name <hello@yourdomain.com>
```

## API Reference

### Send Single Email

```typescript
import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY);

const { data, error } = await resend.emails.send({
  from: "App <hello@yourdomain.com>",
  to: ["recipient@example.com"],
  cc: ["cc@example.com"],        // optional
  bcc: ["bcc@example.com"],      // optional
  replyTo: "support@yourdomain.com", // optional
  subject: "Hello",
  html: "<p>Hello world</p>",    // or use react: <Component />
  text: "Hello world",           // plain text fallback
  headers: {                     // optional custom headers
    "X-Entity-Ref-ID": "123",
  },
  tags: [                        // optional tags for analytics
    { name: "category", value: "welcome" },
  ],
});

// data.id contains the email ID for tracking
```

### Send Batch Emails

```typescript
const { data, error } = await resend.batch.send([
  {
    from: "App <hello@yourdomain.com>",
    to: ["user1@example.com"],
    subject: "Welcome",
    html: "<p>Welcome user 1</p>",
  },
  {
    from: "App <hello@yourdomain.com>",
    to: ["user2@example.com"],
    subject: "Welcome",
    html: "<p>Welcome user 2</p>",
  },
]);
// Batch limit: 100 emails per call
```

### Retrieve Email Status

```typescript
const { data } = await resend.emails.get(emailId);
// data.last_event: 'sent' | 'delivered' | 'opened' | 'clicked' | 'bounced' | 'complained'
```

## React Email Templates

### Shared Components

```tsx
// emails/components/button.tsx
import { Button } from "@react-email/components";

interface EmailButtonProps {
  href: string;
  children: React.ReactNode;
}

export function EmailButton({ href, children }: EmailButtonProps) {
  return (
    <Button
      href={href}
      style={{
        background: "#000",
        color: "#fff",
        padding: "12px 24px",
        borderRadius: "6px",
        fontWeight: "600",
        textDecoration: "none",
        display: "inline-block",
      }}
    >
      {children}
    </Button>
  );
}
```

```tsx
// emails/components/footer.tsx
import { Hr, Text, Link } from "@react-email/components";

export function EmailFooter({ unsubscribeUrl }: { unsubscribeUrl?: string }) {
  return (
    <>
      <Hr style={{ borderColor: "#e6ebf1", margin: "20px 0" }} />
      <Text style={{ color: "#8898aa", fontSize: "12px" }}>
        © {new Date().getFullYear()} Your Company. All rights reserved.
        {unsubscribeUrl && (
          <>
            {" "}
            <Link href={unsubscribeUrl}>Unsubscribe</Link>
          </>
        )}
      </Text>
    </>
  );
}
```

### Password Reset Template

```tsx
// emails/password-reset.tsx
import {
  Body,
  Container,
  Head,
  Heading,
  Html,
  Preview,
  Section,
  Text,
} from "@react-email/components";
import { EmailButton } from "./components/button";
import { EmailFooter } from "./components/footer";

interface PasswordResetProps {
  name: string;
  resetUrl: string;
}

export function PasswordResetEmail({ name, resetUrl }: PasswordResetProps) {
  return (
    <Html>
      <Head />
      <Preview>Reset your password</Preview>
      <Body style={{ fontFamily: "sans-serif", background: "#f6f9fc" }}>
        <Container
          style={{
            background: "#fff",
            padding: "40px",
            borderRadius: "8px",
            maxWidth: "480px",
          }}
        >
          <Heading style={{ fontSize: "24px" }}>Password Reset</Heading>
          <Text>Hi {name},</Text>
          <Text>
            Someone requested a password reset for your account. If this was
            you, click the button below:
          </Text>
          <Section style={{ textAlign: "center", margin: "32px 0" }}>
            <EmailButton href={resetUrl}>Reset Password</EmailButton>
          </Section>
          <Text style={{ color: "#8898aa", fontSize: "14px" }}>
            This link expires in 1 hour. If you didn't request this, ignore this
            email.
          </Text>
          <EmailFooter />
        </Container>
      </Body>
    </Html>
  );
}
```

### Receipt Template

```tsx
// emails/receipt.tsx
import {
  Body,
  Column,
  Container,
  Head,
  Heading,
  Hr,
  Html,
  Preview,
  Row,
  Section,
  Text,
} from "@react-email/components";
import { EmailFooter } from "./components/footer";

interface LineItem {
  name: string;
  quantity: number;
  price: string;
}

interface ReceiptEmailProps {
  customerName: string;
  orderId: string;
  items: LineItem[];
  total: string;
}

export function ReceiptEmail({
  customerName,
  orderId,
  items,
  total,
}: ReceiptEmailProps) {
  return (
    <Html>
      <Head />
      <Preview>
        Receipt for order #{orderId}
      </Preview>
      <Body style={{ fontFamily: "sans-serif", background: "#f6f9fc" }}>
        <Container
          style={{
            background: "#fff",
            padding: "40px",
            borderRadius: "8px",
            maxWidth: "480px",
          }}
        >
          <Heading style={{ fontSize: "24px" }}>Receipt</Heading>
          <Text>Hi {customerName}, here's your receipt.</Text>
          <Text style={{ color: "#8898aa" }}>Order #{orderId}</Text>
          <Hr />
          {items.map((item, i) => (
            <Row key={i}>
              <Column>
                <Text>
                  {item.name} × {item.quantity}
                </Text>
              </Column>
              <Column align="right">
                <Text>{item.price}</Text>
              </Column>
            </Row>
          ))}
          <Hr />
          <Row>
            <Column>
              <Text style={{ fontWeight: "bold" }}>Total</Text>
            </Column>
            <Column align="right">
              <Text style={{ fontWeight: "bold" }}>{total}</Text>
            </Column>
          </Row>
          <EmailFooter />
        </Container>
      </Body>
    </Html>
  );
}
```

## Email Service Wrapper

Create a reusable service for your app:

```typescript
// lib/email.ts
import { Resend } from "resend";
import { WelcomeEmail } from "@/emails/welcome";
import { PasswordResetEmail } from "@/emails/password-reset";
import { ReceiptEmail } from "@/emails/receipt";

const resend = new Resend(process.env.RESEND_API_KEY);
const FROM = process.env.EMAIL_FROM || "App <hello@yourdomain.com>";

export const email = {
  async sendWelcome(to: string, name: string) {
    return resend.emails.send({
      from: FROM,
      to: [to],
      subject: `Welcome to our app, ${name}!`,
      react: WelcomeEmail({ name }),
    });
  },

  async sendPasswordReset(to: string, name: string, resetUrl: string) {
    return resend.emails.send({
      from: FROM,
      to: [to],
      subject: "Reset your password",
      react: PasswordResetEmail({ name, resetUrl }),
    });
  },

  async sendReceipt(
    to: string,
    data: { customerName: string; orderId: string; items: any[]; total: string }
  ) {
    return resend.emails.send({
      from: FROM,
      to: [to],
      subject: `Receipt for order #${data.orderId}`,
      react: ReceiptEmail(data),
    });
  },
};
```

## Webhook Handling

Resend can send webhooks for email events:

```typescript
// app/api/webhooks/resend/route.ts
import { NextResponse } from "next/server";
import { Webhook } from "svix";

const webhookSecret = process.env.RESEND_WEBHOOK_SECRET!;

export async function POST(request: Request) {
  const body = await request.text();
  const headers = Object.fromEntries(request.headers);

  const wh = new Webhook(webhookSecret);

  let event: any;
  try {
    event = wh.verify(body, {
      "svix-id": headers["svix-id"],
      "svix-timestamp": headers["svix-timestamp"],
      "svix-signature": headers["svix-signature"],
    });
  } catch {
    return NextResponse.json({ error: "Invalid signature" }, { status: 400 });
  }

  switch (event.type) {
    case "email.delivered":
      console.log("Email delivered:", event.data.email_id);
      break;
    case "email.bounced":
      console.log("Email bounced:", event.data.email_id);
      // Mark email as invalid in your database
      break;
    case "email.complained":
      console.log("Spam complaint:", event.data.email_id);
      // Unsubscribe user immediately
      break;
  }

  return NextResponse.json({ received: true });
}
```

## Domain & Deliverability

### DNS Records Required

| Type | Name | Value |
|------|------|-------|
| TXT | `@` or subdomain | SPF record from Resend |
| CNAME | `resend._domainkey` | DKIM record from Resend |
| TXT | `_dmarc` | `v=DMARC1; p=none;` (start permissive, tighten later) |

### Deliverability Tips

1. **Warm up your domain** — start with low volume, increase gradually
2. **Use a subdomain** for transactional emails (e.g., `mail.yourdomain.com`)
3. **Always include plain text** alongside HTML
4. **Keep HTML simple** — avoid heavy images, complex layouts
5. **Monitor bounce rates** — remove invalid emails promptly
6. **Include unsubscribe for marketing** — required by law
7. **Set reply-to** to a monitored inbox
8. **Use tags** to track email categories and performance

### Testing

```bash
# Preview templates locally
npx react-email dev

# Use Resend test key (free tier) for development
# Emails sent with test key go to the Resend dashboard but aren't delivered
```

## Rate Limits

| Plan | Emails/day | Emails/second |
|------|-----------|---------------|
| Free | 100 | 1 |
| Pro | 50,000 | 10 |
| Enterprise | Custom | Custom |

## Error Handling

```typescript
import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY);

async function sendEmailSafely(params: Parameters<typeof resend.emails.send>[0]) {
  try {
    const { data, error } = await resend.emails.send(params);

    if (error) {
      console.error("Resend API error:", error);
      // Queue for retry if transient
      if (error.name === "rate_limit_exceeded") {
        // Implement exponential backoff retry
      }
      return { success: false, error };
    }

    return { success: true, id: data?.id };
  } catch (err) {
    console.error("Network error sending email:", err);
    return { success: false, error: err };
  }
}
```
