---
name: resend-email
description: Implement transactional and marketing emails with Resend, React Email templates, and best practices for deliverability
---

# Resend Email

Expert in email integration using Resend — the modern email API for developers. Covers transactional emails, React Email templates, domain setup, and deliverability.

## When to Use This Skill

Use when you're:

- Setting up transactional emails (welcome, password reset, receipts)
- Building email templates with React Email
- Configuring custom domains for email deliverability
- Implementing email verification flows
- Sending batch or broadcast emails
- Integrating email into Next.js API routes or server actions

## Quick Setup

```bash
npm install resend @react-email/components
```

```env
RESEND_API_KEY=re_...
```

## Key Patterns

### Send a Simple Email

```typescript
import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY);

await resend.emails.send({
  from: "App <hello@yourdomain.com>",
  to: ["user@example.com"],
  subject: "Welcome!",
  html: "<p>Thanks for signing up.</p>",
});
```

### Send with React Email Template

```typescript
import { Resend } from "resend";
import { WelcomeEmail } from "@/emails/welcome";

const resend = new Resend(process.env.RESEND_API_KEY);

await resend.emails.send({
  from: "App <hello@yourdomain.com>",
  to: ["user@example.com"],
  subject: "Welcome!",
  react: WelcomeEmail({ name: "John" }),
});
```

### React Email Template

```tsx
import {
  Body,
  Container,
  Head,
  Heading,
  Html,
  Preview,
  Text,
} from "@react-email/components";

interface WelcomeEmailProps {
  name: string;
}

export function WelcomeEmail({ name }: WelcomeEmailProps) {
  return (
    <Html>
      <Head />
      <Preview>Welcome to our app</Preview>
      <Body style={{ fontFamily: "sans-serif", background: "#f6f9fc" }}>
        <Container
          style={{
            background: "#ffffff",
            padding: "40px",
            borderRadius: "8px",
          }}
        >
          <Heading>Welcome, {name}!</Heading>
          <Text>Thanks for joining. We're excited to have you.</Text>
        </Container>
      </Body>
    </Html>
  );
}
```

### Next.js API Route

```typescript
// app/api/send/route.ts
import { Resend } from "resend";
import { NextResponse } from "next/server";

const resend = new Resend(process.env.RESEND_API_KEY);

export async function POST(request: Request) {
  const { email, name } = await request.json();

  const { data, error } = await resend.emails.send({
    from: "App <hello@yourdomain.com>",
    to: [email],
    subject: "Welcome!",
    react: WelcomeEmail({ name }),
  });

  if (error) {
    return NextResponse.json({ error }, { status: 400 });
  }

  return NextResponse.json({ id: data?.id });
}
```

### Next.js Server Action

```typescript
"use server";

import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY);

export async function sendWelcomeEmail(email: string, name: string) {
  const { error } = await resend.emails.send({
    from: "App <hello@yourdomain.com>",
    to: [email],
    subject: "Welcome!",
    react: WelcomeEmail({ name }),
  });

  if (error) throw new Error("Failed to send email");
}
```

### Batch Emails

```typescript
await resend.batch.send([
  {
    from: "App <hello@yourdomain.com>",
    to: ["user1@example.com"],
    subject: "Update",
    html: "<p>New features available.</p>",
  },
  {
    from: "App <hello@yourdomain.com>",
    to: ["user2@example.com"],
    subject: "Update",
    html: "<p>New features available.</p>",
  },
]);
```

## Domain Setup

1. Add your domain in the Resend dashboard
2. Add the DNS records (SPF, DKIM, DMARC) to your domain provider
3. Verify the domain in Resend
4. Use `from: "Name <email@yourdomain.com>"` instead of the default `onboarding@resend.dev`

## Common Email Types

| Type | Subject Pattern | Priority |
|------|----------------|----------|
| Welcome | "Welcome to {app}" | High |
| Password Reset | "Reset your password" | Critical |
| Email Verification | "Verify your email" | Critical |
| Invoice/Receipt | "Your receipt from {app}" | High |
| Notification | "{action} on your account" | Medium |
| Marketing | Keep it compelling | Low |

## Best Practices

- Always use a verified custom domain for production (not `onboarding@resend.dev`)
- Set up SPF, DKIM, and DMARC records for deliverability
- Use React Email for maintainable, type-safe templates
- Keep email templates in an `emails/` directory at project root
- Preview templates locally with `npx react-email dev`
- Handle errors gracefully — email sending can fail
- Use batch API for sending to multiple recipients
- Include unsubscribe links for marketing emails (CAN-SPAM compliance)
- Test with Resend's test API key before going live

## Project Structure

```
emails/
  welcome.tsx
  password-reset.tsx
  receipt.tsx
  components/
    footer.tsx
    header.tsx
    button.tsx
```

## References

- [Full guide: setup, templates, domains, patterns](references/full-guide.md)
