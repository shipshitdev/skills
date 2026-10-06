import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

interface Cta {
  label: string
  href: string
}

interface HeroProps {
  eyebrow?: string
  headline: string
  subheadline: string
  badges?: string[]
  primaryCta: Cta
  secondaryCta?: Cta
  image?: string | null
  note?: string
}

export function Hero({
  eyebrow,
  headline,
  subheadline,
  badges = [],
  primaryCta,
  secondaryCta,
  image,
  note,
}: HeroProps) {
  return (
    <section className="mx-auto flex max-w-4xl flex-col items-center gap-6 px-4 py-24 text-center">
      {eyebrow ? (
        <Badge variant="outline" className="text-brand">
          {eyebrow}
        </Badge>
      ) : null}
      <h1 className="text-4xl font-bold tracking-tight text-balance sm:text-6xl">{headline}</h1>
      <p className="max-w-2xl text-lg text-pretty text-muted-foreground">{subheadline}</p>
      <div className="flex flex-wrap justify-center gap-3">
        <Button asChild size="lg">
          <a href={primaryCta.href}>{primaryCta.label}</a>
        </Button>
        {secondaryCta ? (
          <Button asChild size="lg" variant="outline">
            <a href={secondaryCta.href}>{secondaryCta.label}</a>
          </Button>
        ) : null}
      </div>
      {note ? <p className="text-sm text-muted-foreground">{note}</p> : null}
      {badges.length > 0 ? (
        <ul className="flex flex-wrap justify-center gap-2">
          {badges.map((badge) => (
            <li key={badge}>
              <Badge variant="secondary">{badge}</Badge>
            </li>
          ))}
        </ul>
      ) : null}
      {image ? <img src={image} alt="" className="mt-8 w-full rounded-xl ring-1 ring-foreground/10" /> : null}
    </section>
  )
}
