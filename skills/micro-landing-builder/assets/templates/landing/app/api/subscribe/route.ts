import { NextResponse } from "next/server"

// Waitlist endpoint used by components/sections/email-capture.tsx.
// Wire your email provider (for example Resend) in here before launch; until
// then the route validates the address and reports that signups are not
// connected, so the form never pretends to have stored an email.
export async function POST(request: Request) {
  const body = (await request.json().catch(() => null)) as { email?: unknown } | null
  const email = typeof body?.email === "string" ? body.email.trim() : ""

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return NextResponse.json({ message: "Enter a valid email address." }, { status: 400 })
  }

  return NextResponse.json(
    { message: "Signups are not connected yet. Please check back soon." },
    { status: 501 },
  )
}
