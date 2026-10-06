// Inline the local files that a built index.html still references (public/ images, fonts,
// icons, CSS url() assets) as data: URIs, and fail when any local reference cannot be inlined.
// Usage: bun inline-local-assets.mjs <build-dir> <output-html>
import { existsSync, readFileSync, statSync, writeFileSync } from "node:fs"
import { extname, join, normalize, sep } from "node:path"

const [buildDir, outFile] = process.argv.slice(2)
if (!buildDir || !outFile) {
  console.error("Usage: inline-local-assets.mjs <build-dir> <output-html>")
  process.exit(2)
}

const MIME = {
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".webp": "image/webp",
  ".avif": "image/avif",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".ttf": "font/ttf",
  ".otf": "font/otf",
  ".mp3": "audio/mpeg",
  ".mp4": "video/mp4",
  ".webm": "video/webm",
  ".css": "text/css",
  ".js": "text/javascript",
  ".json": "application/json",
}

const unresolved = []

// Absolute URLs, fragments, data/blob URIs and other schemes are not local files
const isLocal = (ref) =>
  ref !== "" && !/^(#|\/\/|[a-zA-Z][a-zA-Z0-9+.-]*:)/.test(ref) && !ref.startsWith("var(")

function toDataUri(ref) {
  const clean = decodeURI(ref.split(/[?#]/)[0]).replace(/^\.?\//, "")
  const file = normalize(join(buildDir, clean))
  if (!file.startsWith(normalize(buildDir) + sep) || !existsSync(file) || !statSync(file).isFile()) {
    return null
  }
  const mime = MIME[extname(file).toLowerCase()] ?? "application/octet-stream"
  return `data:${mime};base64,${readFileSync(file).toString("base64")}`
}

function inlineRef(ref) {
  if (!isLocal(ref)) return ref
  const uri = toDataUri(ref)
  if (uri === null) {
    unresolved.push(ref)
    return ref
  }
  return uri
}

const inlineCssUrls = (css) =>
  css.replace(/url\(\s*(["']?)([^)"']*)\1\s*\)/g, (_, quote, ref) => `url(${quote}${inlineRef(ref.trim())}${quote})`)

// src and poster on any tag; href only on <link> (anchors are navigation, not assets)
function inlineTag(tag) {
  const name = /^<\s*([a-zA-Z][\w-]*)/.exec(tag)?.[1]?.toLowerCase()
  return tag.replace(/\b(src|href|poster)=(["'])([^"']*)\2/g, (match, attr, quote, ref) => {
    if (attr === "href" && name !== "link") return match
    return `${attr}=${quote}${inlineRef(ref)}${quote}`
  })
}

const html = readFileSync(join(buildDir, "index.html"), "utf8")
// Never rewrite script bodies: the JS bundle may contain markup-looking strings
const parts = html.split(/(<script\b[^>]*>[\s\S]*?<\/script>)/gi)
const output = parts
  .map((part) => {
    if (/^<script\b/i.test(part)) {
      const open = /^<script\b[^>]*>/i.exec(part)[0]
      return inlineTag(open) + part.slice(open.length)
    }
    return inlineCssUrls(part.replace(/<[a-zA-Z][^>]*>/g, inlineTag))
  })
  .join("")

if (unresolved.length > 0) {
  console.error("Error: bundle.html would still reference files that are not inlined:")
  for (const ref of [...new Set(unresolved)]) console.error(`  ${ref}`)
  console.error("Put the files in public/ (or import them from code), or use absolute URLs.")
  process.exit(1)
}

writeFileSync(outFile, output)
