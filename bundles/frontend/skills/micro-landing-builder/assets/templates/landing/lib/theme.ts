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
    return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4
  }
  return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
}

const hex2 = (v: number) => Math.round(Math.min(255, Math.max(0, v))).toString(16).padStart(2, "0")
const toHex = ({ r, g, b }: Rgba) => `#${hex2(r)}${hex2(g)}${hex2(b)}`

// sRGB mix: `amount` of `toward` blended into `from`, always opaque.
function mixRgba(from: Rgba, toward: Rgba, amount: number): Rgba {
  const lerp = (a: number, b: number) => a + (b - a) * amount
  return { r: lerp(from.r, toward.r), g: lerp(from.g, toward.g), b: lerp(from.b, toward.b), a: 1 }
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

const WHITE: Rgba = { r: 255, g: 255, b: 255, a: 1 }
const BLACK: Rgba = { r: 0, g: 0, b: 0, a: 1 }
const TEXT_TARGET = 4.5

// Opaque hover color for a filled primary: moves away from the text color so contrast with the
// text improves. (hover:bg-primary/80 blended with the surface behind it and could drop below AA.)
function hoverColor(primary: Rgba, textIsDark: boolean): Rgba {
  const amount = 0.15
  const first = mixRgba(primary, textIsDark ? WHITE : BLACK, amount)
  if (toHex(first) !== toHex(primary)) return first
  return mixRgba(primary, textIsDark ? BLACK : WHITE, amount)
}

// Text-safe variant of `color` for small text on every surface: the color itself when it
// already reaches AA on all of them, otherwise the smallest step toward `toward` that does.
function readableText(
  value: string,
  color: Rgba,
  surfaces: Rgba[],
  toward: Rgba,
): string {
  for (let step = 0; step <= 20; step++) {
    const candidate = step === 0 ? color : mixRgba(color, toward, step / 20)
    if (surfaces.every((surface) => contrast(candidate, surface) >= TEXT_TARGET)) {
      return step === 0 ? value : toHex(candidate)
    }
  }
  return toHex(toward)
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

  const foregroundRgba = explicitForeground?.rgba ?? (parseColor(foreground) as Rgba)
  const card = mixRgba(background.rgba, foregroundRgba, 0.06)
  const surfaces = [background.rgba, card]
  const primaryText = bestForeground(primary.rgba)
  const hover = hoverColor(primary.rgba, primaryText === NEAR_BLACK || primaryText === PURE_BLACK)

  const vars = {
    "--primary": primary.value,
    "--primary-foreground": primaryText,
    "--primary-hover": toHex(hover),
    "--primary-hover-foreground": bestForeground(hover),
    "--primary-text": readableText(primary.value, primary.rgba, surfaces, foregroundRgba),
    "--ring": primary.value,
    "--brand": accent.value,
    "--brand-foreground": bestForeground(accent.rgba),
    "--brand-text": readableText(accent.value, accent.rgba, surfaces, foregroundRgba),
    "--background": background.value,
    "--foreground": foreground,
    "--card": toHex(card),
    "--card-foreground": foreground,
    "--popover": toHex(card),
    "--popover-foreground": foreground,
    "--muted-foreground": toHex(mixRgba(background.rgba, foregroundRgba, 0.7)),
  }

  return { mode, vars }
}
