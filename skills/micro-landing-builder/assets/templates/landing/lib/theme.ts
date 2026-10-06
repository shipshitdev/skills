export type Theme = {
  primary: string
  accent?: string
  background: string
  foreground?: string
  mode?: string
}

const NEAR_BLACK = "#0a0a0a"
const NEAR_WHITE = "#fafafa"
const HEX = /^#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/

type Rgba = { r: number; g: number; b: number; a: number }

// Parses #rgb, #rgba, #rrggbb and #rrggbbaa; returns null for anything else.
export function parseColor(color: string): Rgba | null {
  if (!HEX.test(color)) return null
  const raw = color.slice(1)
  const full = raw.length <= 4 ? raw.replace(/./g, (c) => c + c) : raw
  const byte = (i: number) => parseInt(full.slice(i, i + 2), 16)
  return { r: byte(0), g: byte(2), b: byte(4), a: full.length === 8 ? byte(6) / 255 : 1 }
}

// WCAG 2.x relative luminance from linearized sRGB.
function luminance({ r, g, b }: Rgba): number {
  const lin = (v: number) => {
    const c = v / 255
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4
  }
  return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
}

function contrast(a: Rgba, b: Rgba): number {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x)
  return (hi + 0.05) / (lo + 0.05)
}

// Defaults are chosen to pass WCAG AA (4.5:1): primary has AA text on it, and the accent
// default has AA contrast against the background it lands on.
const DEFAULTS = { primary: "#4f46e5", background: "#0a0a0a" }
const ACCENT_ON_DARK = "#f59e0b"
const ACCENT_ON_LIGHT = "#b45309"

// Returns a color that is safe to serialize into the style attribute. React escapes HTML
// but not CSS separators, so anything that is not an anchored hex color (for example
// "#fff;outline:10px solid red") is dropped and the default is used instead.
// Alpha is treated as opaque for contrast, with a warning.
function safeColor(
  key: string,
  color: string | undefined,
  fallback: string | undefined,
): { value: string; rgba: Rgba } | null {
  const parsed = color === undefined ? null : parseColor(color)
  if (color !== undefined && parsed) {
    if (parsed.a < 1) {
      console.warn(
        `app.json theme.${key} has alpha ${parsed.a.toFixed(2)}; contrast is computed as if it were opaque.`,
      )
    }
    return { value: color, rgba: parsed }
  }
  if (color !== undefined) {
    console.warn(
      `app.json theme.${key}: unsupported color ${JSON.stringify(color)} ignored. ` +
        "Use #rgb, #rgba, #rrggbb or #rrggbbaa.",
    )
  }
  const fallbackRgba = fallback ? parseColor(fallback) : null
  return fallback && fallbackRgba ? { value: fallback, rgba: fallbackRgba } : null
}

const AA = 4.5
const PURE_BLACK = "#000000"
const PURE_WHITE = "#ffffff"

// Text color for `color`: the near-black / near-white pair when one of them reaches AA (4.5:1),
// otherwise the pure black or white extreme, which always reaches at least 4.58:1. The user's
// color is never changed; only the text drawn on it is.
function bestForeground(color: Rgba): string {
  const dark = contrast(color, parseColor(NEAR_BLACK) as Rgba)
  const light = contrast(color, parseColor(NEAR_WHITE) as Rgba)
  if (Math.max(dark, light) >= AA) return dark >= light ? NEAR_BLACK : NEAR_WHITE
  const black = contrast(color, parseColor(PURE_BLACK) as Rgba)
  const white = contrast(color, parseColor(PURE_WHITE) as Rgba)
  return black >= white ? PURE_BLACK : PURE_WHITE
}

// True when dark text reads better than light text on this color.
function usesDarkText(color: Rgba): boolean {
  return bestForeground(color) === NEAR_BLACK || bestForeground(color) === PURE_BLACK
}

export function isLight(color: string): boolean {
  const parsed = parseColor(color)
  return parsed ? usesDarkText(parsed) : false
}

// Turns app.json `theme` into the token set (mode) and CSS variable overrides.
// An explicit mode ("dark" | "light") wins; otherwise it follows the background
// brightness, so a light background alone gives the full light token set.
export function resolveTheme(theme: Theme) {
  const primary = safeColor("primary", theme.primary, DEFAULTS.primary)!
  const background = safeColor("background", theme.background, DEFAULTS.background)!
  const accent = safeColor(
    "accent",
    theme.accent,
    usesDarkText(background.rgba) ? ACCENT_ON_LIGHT : ACCENT_ON_DARK,
  )!
  const explicitForeground = safeColor("foreground", theme.foreground, undefined)

  const mode: "dark" | "light" =
    theme.mode === "light" || theme.mode === "dark"
      ? theme.mode
      : usesDarkText(background.rgba)
        ? "light"
        : "dark"

  // Text colors are paired with the configured background so a light or dark
  // background never ends up with same-tone text.
  const foreground = explicitForeground?.value ?? bestForeground(background.rgba)

  const vars = {
    "--primary": primary.value,
    "--primary-foreground": bestForeground(primary.rgba),
    "--ring": primary.value,
    "--brand": accent.value,
    "--brand-foreground": bestForeground(accent.rgba),
    "--background": background.value,
    "--foreground": foreground,
    "--card": `color-mix(in oklab, ${background.value} 94%, ${foreground})`,
    "--card-foreground": foreground,
    "--popover": `color-mix(in oklab, ${background.value} 94%, ${foreground})`,
    "--popover-foreground": foreground,
    "--muted-foreground": `color-mix(in oklab, ${foreground} 70%, ${background.value})`,
  }

  return { mode, vars }
}
