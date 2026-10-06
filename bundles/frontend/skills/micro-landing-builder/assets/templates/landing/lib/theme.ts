export type Theme = {
  primary?: string
  accent?: string
  background?: string
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

// Opaque hover color for a filled primary: moves away from the text color so contrast with the
// text improves. (hover:bg-primary/80 blended with the surface behind it and could drop below AA.)
function hoverColor(primary: Rgba, textIsDark: boolean): Rgba {
  const amount = 0.15
  const first = mixRgba(primary, textIsDark ? WHITE : BLACK, amount)
  if (toHex(first) !== toHex(primary)) return first
  return mixRgba(primary, textIsDark ? BLACK : WHITE, amount)
}

// Search opaque, rounded sRGB in 5% steps. Validate the actual emitted hex on every surface.
function readableText(color: Rgba, surfaces: Rgba[], toward: Rgba, target = AA): string {
  for (let step = 0; step <= 20; step++) {
    const value = toHex(mixRgba(color, toward, step / 20))
    if (surfaces.every((surface) => contrast(parseColor(value)!, surface) >= target)) return value
  }
  return toHex(toward) // The complete pair audit below rejects an insufficient fallback.
}

export function inspectTheme(input: Theme) {
  const validObject = input && typeof input === "object" && !Array.isArray(input)
  const theme = validObject ? input : {}
  const errors: string[] = validObject ? [] : ["theme must be an object"]
  function color(key: string, value: string | undefined, fallback: string): string {
    const parsed = typeof value === "string" ? parseColor(value) : null
    if (value !== undefined && !parsed) errors.push(`theme.${key}: unsupported color; use an anchored hex color`)
    if (parsed && parsed.a < 1) console.warn(`theme.${key} alpha is normalized to opaque hex.`)
    return toHex(parsed ?? parseColor(fallback)!)
  }
  const primary = color("primary", theme.primary, DEFAULTS.primary)
  const background = color("background", theme.background, DEFAULTS.background)
  const backgroundRgba = parseColor(background)!
  const foreground = color("foreground", theme.foreground, bestForeground(backgroundRgba))
  const foregroundRgba = parseColor(foreground)!
  const brand = color("accent", theme.accent, usesDarkText(backgroundRgba) ? ACCENT_ON_LIGHT : ACCENT_ON_DARK)
  const mode: "dark" | "light" = theme.mode === "dark" || theme.mode === "light"
    ? theme.mode : usesDarkText(backgroundRgba) ? "light" : "dark"
  if (theme.mode !== undefined && theme.mode !== "dark" && theme.mode !== "light") {
    errors.push("theme.mode must be dark or light")
  }
  const card = toHex(mixRgba(backgroundRgba, foregroundRgba, 0.06))
  const secondaryHover = toHex(mixRgba(backgroundRgba, foregroundRgba, 0.09))
  const surfaces = [background, card, secondaryHover].map((value) => parseColor(value)!)
  const primaryRgba = parseColor(primary)!
  const hover = toHex(hoverColor(primaryRgba, usesDarkText(primaryRgba)))
  const vars: Record<string, string> = {
    "--primary": primary,
    "--primary-foreground": bestForeground(primaryRgba),
    "--primary-hover": hover,
    "--primary-hover-foreground": bestForeground(parseColor(hover)!),
    "--primary-text": readableText(primaryRgba, surfaces, foregroundRgba),
    "--brand": brand,
    "--brand-foreground": bestForeground(parseColor(brand)!),
    "--brand-text": readableText(parseColor(brand)!, surfaces, foregroundRgba),
    "--background": background,
    "--foreground": foreground,
    "--card": card,
    "--card-foreground": foreground,
    "--popover": card,
    "--popover-foreground": foreground,
    "--muted": card,
    "--muted-foreground": readableText(mixRgba(backgroundRgba, foregroundRgba, 0.7), surfaces, foregroundRgba),
    "--secondary": card,
    "--secondary-foreground": foreground,
    "--secondary-hover": secondaryHover,
    "--accent": card,
    "--accent-foreground": foreground,
    "--ring": readableText(primaryRgba, surfaces, foregroundRgba, 3),
    "--input": readableText(mixRgba(backgroundRgba, foregroundRgba, 0.4), surfaces, foregroundRgba, 3),
    "--border": readableText(mixRgba(backgroundRgba, foregroundRgba, 0.4), surfaces, foregroundRgba, 3),
    "--destructive": readableText(parseColor("#dc2626")!, surfaces, foregroundRgba),
    "--destructive-fill": "#b91c1c",
    "--destructive-fill-foreground": "#ffffff",
    "--destructive-hover": "#991b1b",
    "--destructive-hover-foreground": "#ffffff",
  }
  function pair(text: string, surface: string, target: number) {
    const ratio = contrast(parseColor(vars[`--${text}`])!, parseColor(vars[`--${surface}`])!)
    if (ratio < target) errors.push(`${text} on ${surface}: contrast ${ratio.toFixed(4)}:1 < ${target}:1`)
  }
  for (const surface of ["background", "card", "secondary-hover"]) {
    for (const text of ["foreground", "muted-foreground", "primary-text", "brand-text", "destructive"]) pair(text, surface, AA)
    for (const edge of ["ring", "input", "border"]) pair(edge, surface, 3)
  }
  for (const fill of ["primary", "primary-hover", "brand", "destructive-fill", "destructive-hover"]) {
    pair(`${fill}-foreground`, fill, AA)
  }
  return { resolved: { mode, vars }, errors }
}

// Invalid runtime edits fall back to one complete default theme, preserving no partial override.
export function resolveTheme(theme: Theme) {
  const result = inspectTheme(theme)
  if (!result.errors.length) return result.resolved
  console.warn(`Invalid app.json theme: ${result.errors.join("; ")}. Using the complete default theme. ` +
    "Choose a darker/lighter background or remove the explicit foreground.")
  return inspectTheme({}).resolved
}
