export type Theme = {
  primary: string
  accent: string
  background: string
  foreground?: string
  mode?: string
}

// Rough perceived brightness of a #rgb / #rrggbb color; unknown formats count as dark.
export function isLight(color: string): boolean {
  const hex = color.replace("#", "")
  const full = hex.length === 3 ? hex.replace(/./g, (c) => c + c) : hex
  if (!/^[0-9a-fA-F]{6}$/.test(full)) return false
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(full.slice(i, i + 2), 16))
  return 0.299 * r + 0.587 * g + 0.114 * b > 150
}

// Turns app.json `theme` into the token set (mode) and CSS variable overrides.
// An explicit mode ("dark" | "light") wins; otherwise it follows the background
// brightness, so a light background alone gives the full light token set.
export function resolveTheme(theme: Theme) {
  const mode: "dark" | "light" =
    theme.mode === "light" || theme.mode === "dark"
      ? theme.mode
      : isLight(theme.background)
        ? "light"
        : "dark"

  // Text colors are paired with the configured background so a light or dark
  // background never ends up with same-tone text.
  const foreground = theme.foreground ?? (isLight(theme.background) ? "#0a0a0a" : "#fafafa")

  const vars = {
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
  }

  return { mode, vars }
}
