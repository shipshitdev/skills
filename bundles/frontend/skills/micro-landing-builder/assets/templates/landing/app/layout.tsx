import type { Metadata } from "next"
import type { CSSProperties } from "react"

import config from "../app.json"
import "./globals.css"

export const metadata: Metadata = {
  title: config.meta.title,
  description: config.meta.description,
}

type Theme = {
  primary: string
  accent: string
  background: string
  foreground?: string
  mode?: string
}
const theme = config.theme as Theme

// Rough perceived brightness of a #rgb / #rrggbb color; unknown formats count as dark.
function isLight(color: string): boolean {
  const hex = color.replace("#", "")
  const full = hex.length === 3 ? hex.replace(/./g, (c) => c + c) : hex
  if (!/^[0-9a-fA-F]{6}$/.test(full)) return false
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(full.slice(i, i + 2), 16))
  return 0.299 * r + 0.587 * g + 0.114 * b > 150
}

// mode picks the shadcn token set in globals.css (:root is light, .dark is dark).
const mode = theme.mode === "light" ? "light" : "dark"

// Text colors are paired with the configured background so a light or dark
// background never ends up with same-tone text.
const foreground = theme.foreground ?? (isLight(theme.background) ? "#0a0a0a" : "#fafafa")

// app.json theme values override the shadcn CSS variables declared in globals.css.
const themeVars = {
  "--primary": theme.primary,
  "--primary-foreground": isLight(theme.primary) ? "#0a0a0a" : "#ffffff",
  "--ring": theme.primary,
  "--brand": theme.accent,
  "--background": theme.background,
  "--foreground": foreground,
  "--card": `color-mix(in oklab, ${theme.background} 94%, ${foreground})`,
  "--card-foreground": foreground,
  "--popover": `color-mix(in oklab, ${theme.background} 94%, ${foreground})`,
  "--popover-foreground": foreground,
  "--muted-foreground": `color-mix(in oklab, ${foreground} 70%, ${theme.background})`,
} as CSSProperties

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className={mode === "dark" ? "dark" : undefined} style={themeVars}>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Space+Grotesk:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  )
}
