import { Button } from "@/components/ui/button"

interface HeaderProps {
  logo: { mark: string; text: string; image?: string }
  nav: { label: string; href: string }[]
  cta: { label: string; href: string }
}

export function Header({ logo, nav, cta }: HeaderProps) {
  return (
    <header className="sticky top-0 z-40 border-b bg-background backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
        <a href="#" className="flex items-center gap-2 font-heading font-bold">
          {logo.image ? (
            <img src={logo.image} alt="" className="size-7" />
          ) : (
            <span className="flex size-7 items-center justify-center rounded-md bg-primary text-xs text-primary-foreground">
              {logo.mark}
            </span>
          )}
          <span>{logo.text}</span>
        </a>
        <nav aria-label="Primary" className="hidden items-center gap-6 md:flex">
          {nav.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              {item.label}
            </a>
          ))}
        </nav>
        <Button asChild>
          <a href={cta.href}>{cta.label}</a>
        </Button>
      </div>
    </header>
  )
}
