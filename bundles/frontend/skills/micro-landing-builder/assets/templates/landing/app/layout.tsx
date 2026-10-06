import type { Metadata } from "next"
import type { CSSProperties } from "react"

import config from "../app.json"
import "./globals.css"

export const metadata: Metadata = {
  title: config.meta.title,
  description: config.meta.description,
}

// app.json theme values override the shadcn CSS variables declared in globals.css.
const themeVars = {
  "--primary": config.theme.primary,
  "--primary-foreground": "#ffffff",
  "--ring": config.theme.primary,
  "--brand": config.theme.accent,
  "--background": config.theme.background,
} as CSSProperties

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="dark" style={themeVars}>
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
