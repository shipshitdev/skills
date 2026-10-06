import type { Metadata } from "next"
import type { CSSProperties } from "react"

import config from "../app.json"
import { resolveTheme } from "@/lib/theme"
import "./globals.css"

export const metadata: Metadata = {
  title: config.meta.title,
  description: config.meta.description,
}

// app.json theme -> shadcn token set (mode) and CSS variable overrides; see lib/theme.ts.
const { mode, vars } = resolveTheme(config.theme)
const themeVars = vars as CSSProperties

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
