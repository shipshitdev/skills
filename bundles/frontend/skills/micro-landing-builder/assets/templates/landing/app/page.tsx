import config from "../app.json"
import { CTA } from "@/components/sections/cta"
import { FAQ } from "@/components/sections/faq"
import { Features } from "@/components/sections/features"
import { Footer } from "@/components/sections/footer"
import { Header } from "@/components/sections/header"
import { Hero } from "@/components/sections/hero"
import { Pricing } from "@/components/sections/pricing"
import { Stats } from "@/components/sections/stats"
import { Testimonials } from "@/components/sections/testimonials"

// Section props come straight from app.json, so the registry is keyed by `type`.
const sectionComponents: Record<string, React.ComponentType<any>> = {
  hero: Hero,
  stats: Stats,
  features: Features,
  pricing: Pricing,
  testimonials: Testimonials,
  faq: FAQ,
  cta: CTA,
}

export default function Landing() {
  return (
    <main>
      <Header
        logo={config.header.logo}
        nav={config.header.nav}
        cta={config.header.cta}
      />

      {config.sections.map((section, index) => {
        const Component = sectionComponents[section.type]
        if (!Component) return null
        return <Component key={index} {...section} />
      })}

      <Footer
        links={config.footer.links}
        social={config.footer.social}
        copyright={config.footer.copyright}
      />
    </main>
  )
}
