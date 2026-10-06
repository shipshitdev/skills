import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"

interface FAQProps {
  title: string
  items: { q: string; a: string }[]
}

export function FAQ({ title, items }: FAQProps) {
  return (
    <section id="faq" className="mx-auto max-w-3xl scroll-mt-14 px-4 py-20">
      <h2 className="mb-8 text-center text-3xl font-bold tracking-tight">{title}</h2>
      <Accordion type="single" collapsible>
        {items.map((item, index) => (
          <AccordionItem key={item.q} value={`item-${index}`}>
            <AccordionTrigger className="text-base">{item.q}</AccordionTrigger>
            <AccordionContent className="text-muted-foreground">{item.a}</AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </section>
  )
}
