interface StatsProps {
  items: { value: string; label: string }[]
}

export function Stats({ items }: StatsProps) {
  return (
    <section className="border-y bg-card/40">
      <dl className="mx-auto grid max-w-4xl grid-cols-2 gap-8 px-4 py-12 text-center sm:grid-cols-3 md:grid-cols-4">
        {items.map((item) => (
          <div key={item.label}>
            <dt className="text-sm text-muted-foreground">{item.label}</dt>
            <dd className="font-heading text-3xl font-bold text-primary-text">{item.value}</dd>
          </div>
        ))}
      </dl>
    </section>
  )
}
