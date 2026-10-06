interface FooterProps {
  links: { label: string; href: string }[]
  social: { platform: string; href: string }[]
  copyright: string
}

export function Footer({ links, social, copyright }: FooterProps) {
  return (
    <footer className="border-t">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-4 py-8 text-sm text-muted-foreground sm:flex-row">
        <p>{copyright}</p>
        <nav aria-label="Footer" className="flex flex-wrap justify-center gap-4">
          {links.map((link) => (
            <a key={link.label} href={link.href} className="hover:text-foreground">
              {link.label}
            </a>
          ))}
          {social.map((item) => (
            <a key={item.platform} href={item.href} className="capitalize hover:text-foreground">
              {item.platform}
            </a>
          ))}
        </nav>
      </div>
    </footer>
  )
}
