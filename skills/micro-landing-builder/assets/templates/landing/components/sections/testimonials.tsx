import { Card, CardContent, CardFooter } from "@/components/ui/card"

interface TestimonialsProps {
  title: string
  items: { quote: string; author: string; role: string; avatar?: string | null }[]
}

export function Testimonials({ title, items }: TestimonialsProps) {
  return (
    <section className="mx-auto max-w-5xl px-4 py-20">
      <h2 className="mb-12 text-center text-3xl font-bold tracking-tight">{title}</h2>
      <div className="grid gap-6 md:grid-cols-2">
        {items.map((item) => (
          <Card key={item.author}>
            <CardContent>
              <blockquote className="text-base text-pretty">&ldquo;{item.quote}&rdquo;</blockquote>
            </CardContent>
            <CardFooter className="gap-3 border-t-0 bg-transparent">
              {item.avatar ? (
                <img src={item.avatar} alt="" className="size-10 rounded-full object-cover" />
              ) : (
                <span
                  aria-hidden="true"
                  className="flex size-10 items-center justify-center rounded-full bg-muted text-sm font-medium"
                >
                  {item.author.slice(0, 1)}
                </span>
              )}
              <div className="text-sm">
                <p className="font-medium">{item.author}</p>
                <p className="text-muted-foreground">{item.role}</p>
              </div>
            </CardFooter>
          </Card>
        ))}
      </div>
    </section>
  )
}
