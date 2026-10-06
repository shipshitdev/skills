import {
  Check,
  Globe,
  Heart,
  Lock,
  Settings,
  Shield,
  Star,
  TrendingUp,
  Users,
  Zap,
  type LucideIcon,
} from "lucide-react"

import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

const icons: Record<string, LucideIcon> = {
  zap: Zap,
  shield: Shield,
  "trending-up": TrendingUp,
  users: Users,
  lock: Lock,
  globe: Globe,
  check: Check,
  star: Star,
  heart: Heart,
  settings: Settings,
}

interface FeaturesProps {
  title: string
  subtitle?: string
  items: { icon: string; title: string; description: string }[]
}

export function Features({ title, subtitle, items }: FeaturesProps) {
  return (
    <section id="features" className="mx-auto max-w-6xl scroll-mt-14 px-4 py-20">
      <div className="mb-12 text-center">
        <h2 className="text-3xl font-bold tracking-tight">{title}</h2>
        {subtitle ? <p className="mt-3 text-muted-foreground">{subtitle}</p> : null}
      </div>
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {items.map((item) => {
          const Icon = icons[item.icon] ?? Check
          return (
            <Card key={item.title}>
              <CardHeader>
                <Icon className="mb-2 size-6 text-brand" aria-hidden="true" />
                <CardTitle>{item.title}</CardTitle>
                <CardDescription>{item.description}</CardDescription>
              </CardHeader>
            </Card>
          )
        })}
      </div>
    </section>
  )
}
