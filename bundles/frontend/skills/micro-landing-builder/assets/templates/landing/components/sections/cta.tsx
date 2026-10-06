import { EmailCapture } from "@/components/sections/email-capture"
import { Button } from "@/components/ui/button"

interface CTAProps {
  headline: string
  subheadline?: string
  emailCapture?: {
    enabled: boolean
    provider?: string
    placeholder?: string
    buttonText?: string
  }
  cta?: { label: string; href: string }
}

export function CTA({ headline, subheadline, emailCapture, cta }: CTAProps) {
  return (
    <section id="signup" className="scroll-mt-14 border-t bg-card">
      <div className="mx-auto flex max-w-2xl flex-col items-center gap-6 px-4 py-20 text-center">
        <h2 className="text-3xl font-bold tracking-tight text-balance">{headline}</h2>
        {subheadline ? <p className="text-muted-foreground">{subheadline}</p> : null}
        {emailCapture?.enabled ? (
          <EmailCapture
            placeholder={emailCapture.placeholder}
            buttonText={emailCapture.buttonText}
          />
        ) : cta ? (
          <Button asChild size="lg">
            <a href={cta.href}>{cta.label}</a>
          </Button>
        ) : null}
      </div>
    </section>
  )
}
