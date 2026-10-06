import { inspectTheme } from "../assets/templates/landing/lib/theme"

const theme = JSON.parse(await Bun.stdin.text())
if (!theme || typeof theme !== "object" || Array.isArray(theme)) {
  process.stdout.write(JSON.stringify(["theme must be an object"]))
} else {
  process.stdout.write(JSON.stringify(inspectTheme(theme).errors))
}
