import { Check } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface Plan {
  name: string
  price: { monthly: number; yearly: number }
  description: string
  features: string[]
  cta: { label: string; href: string }
  highlighted?: boolean
}

interface PricingProps {
  title: string
  subtitle?: string
  plans: Plan[]
}

export function Pricing({ title, subtitle, plans }: PricingProps) {
  return (
    <section id="pricing" className="mx-auto max-w-5xl scroll-mt-14 px-4 py-20">
      <div className="mb-12 text-center">
        <h2 className="text-3xl font-bold tracking-tight">{title}</h2>
        {subtitle ? <p className="mt-3 text-muted-foreground">{subtitle}</p> : null}
      </div>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-[repeat(auto-fit,minmax(16rem,1fr))]">
        {plans.map((plan) => (
          <Card key={plan.name} className={cn(plan.highlighted && "ring-2 ring-primary")}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                {plan.name}
                {plan.highlighted ? <Badge>Popular</Badge> : null}
              </CardTitle>
              <CardDescription>{plan.description}</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-1 flex-col gap-4">
              <p>
                <span className="font-heading text-4xl font-bold">${plan.price.monthly}</span>
                <span className="text-muted-foreground"> / month</span>
                {plan.price.yearly > 0 ? (
                  <span className="mt-1 block text-sm text-muted-foreground">
                    or ${plan.price.yearly} billed yearly
                  </span>
                ) : null}
              </p>
              <ul className="flex flex-col gap-2 text-sm">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2">
                    <Check className="size-4 text-brand" aria-hidden="true" />
                    {feature}
                  </li>
                ))}
              </ul>
            </CardContent>
            <CardFooter>
              <Button asChild className="w-full" variant={plan.highlighted ? "default" : "outline"}>
                <a href={plan.cta.href}>{plan.cta.label}</a>
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </section>
  )
}
