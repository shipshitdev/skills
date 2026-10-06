// Inline the local files that a built index.html still references (public/ images, fonts,
// icons, stylesheets and the url() assets inside them) as data: URIs, and fail when any local
// reference cannot be inlined or escapes the project.
//
// HTML is parsed and serialized with parse5 (browser-grade tokenizing, comment recovery and
// character-reference decoding), srcset with the WHATWG candidate algorithm (ASCII whitespace only,
// so NBSP stays inside a URL and data URIs with commas survive), and CSS with postcss and
// postcss-value-parser. bundle-artifact.sh installs these into the project and runs
// a copy of this file from there.
//
// Usage: bun inline-local-assets.mjs <build-dir> <output-html> [project-root]
import { mkdirSync, readFileSync, realpathSync, statSync, writeFileSync } from "node:fs"
import { dirname, extname, join, relative, resolve, sep } from "node:path"
import { parse, serialize } from "parse5"
import postcss from "postcss"
import valueParser from "postcss-value-parser"

const [buildDirArg, outFile, projectArg] = process.argv.slice(2)
if (!buildDirArg || !outFile) {
  console.error("Usage: inline-local-assets.mjs <build-dir> <output-html> [project-root]")
  process.exit(2)
}

const root = resolve(buildDirArg)
const projectRoot = resolve(projectArg ?? process.cwd())
const realRoot = realpathSync(root)
const realProject = realpathSync(projectRoot)

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

const problems = []
const problem = (ref, why) => problems.push(`${ref}  (${why})`)

const within = (path, base) => path === base || path.startsWith(base + sep)

// Browsers strip tabs and newlines inside URLs and trim control characters and spaces around them
// biome-ignore lint/suspicious/noControlCharactersInRegex: matching URL-stripped control characters
const cleanUrl = (text) => text.replace(/[\t\n\r]/g, "").replace(/^[\u0000-\u0020]+|[\u0000-\u0020]+$/g, "")

// Absolute URLs, fragments, data/blob URIs and other schemes are not local files
const isLocal = (ref) => ref !== "" && !/^(#|\/\/|[a-zA-Z][a-zA-Z0-9+.-]*:)/.test(ref)

/**
 * Resolve a reference to a real file inside the build directory.
 * Returns { real, lexical, fragment } or null (after recording why it failed).
 * `lexical` is the URL-style path (symlinks not followed); relative references inside a
 * stylesheet resolve against its directory. Confinement is checked on canonical (realpath)
 * paths, so a symlinked file or symlinked parent directory cannot pull in content from outside
 * the build or the project.
 */
function resolveRef(ref, baseDir) {
  const hash = ref.indexOf("#")
  const fragment = hash >= 0 ? ref.slice(hash) : ""
  const noFragment = hash >= 0 ? ref.slice(0, hash) : ref
  const query = noFragment.indexOf("?")
  const pathname = query >= 0 ? noFragment.slice(0, query) : noFragment
  if (pathname === "") {
    problem(ref, "no file path")
    return null
  }

  let decoded
  try {
    decoded = pathname.split("/").map((segment) => {
      const value = decodeURIComponent(segment)
      if (value.includes("/") || value.includes("\\") || value.includes("\0")) throw new Error("separator")
      return value
    })
  } catch {
    problem(ref, "invalid percent-encoding or path separator in a segment")
    return null
  }
  const rel = decoded.join("/")
  const lexical = pathname.startsWith("/") ? resolve(root, `.${rel}`) : resolve(baseDir, rel)

  if (!within(lexical, root)) {
    problem(ref, "points outside the build directory")
    return null
  }

  let real
  try {
    real = realpathSync(lexical)
  } catch {
    problem(ref, "file not found")
    return null
  }
  if (!within(real, realRoot)) {
    problem(ref, "escapes the build directory through a symlink")
    return null
  }
  if (!statSync(real).isFile()) {
    problem(ref, "not a file")
    return null
  }

  // Vite copies public/ into the build following symlinks, so also check the source side
  const source = join(projectRoot, "public", relative(root, lexical))
  let realSource = null
  try {
    realSource = realpathSync(source)
  } catch {
    // not a public/ file (e.g. a generated asset)
  }
  if (realSource !== null && !within(realSource, realProject)) {
    problem(ref, "public/ file escapes the project through a symlink")
    return null
  }

  return { real, lexical, fragment }
}

const mimeOf = (file) => MIME[extname(file).toLowerCase()] ?? "application/octet-stream"
const toDataUri = (bytes, mime, fragment) => `data:${mime};base64,${Buffer.from(bytes).toString("base64")}${fragment}`

const activeCss = new Set()

/** Resolve and encode one reference; stylesheets are processed recursively. Null = left as is. */
function inlineRef(rawRef, baseDir) {
  const ref = cleanUrl(rawRef)
  if (!isLocal(ref)) return null
  const found = resolveRef(ref, baseDir)
  if (found === null) return null
  if (extname(found.real).toLowerCase() === ".css") return stylesheetUri(found)
  return toDataUri(readFileSync(found.real), mimeOf(found.real), found.fragment)
}

function stylesheetUri({ real, lexical, fragment }) {
  if (activeCss.has(real)) {
    problem(real, "stylesheet imports itself (cycle)")
    return null
  }
  activeCss.add(real)
  try {
    // References inside resolve against the stylesheet's URL directory, not its symlink target
    const css = processCss(readFileSync(real, "utf8"), dirname(lexical))
    return toDataUri(css, "text/css", fragment)
  } finally {
    activeCss.delete(real)
  }
}

// --- CSS ---------------------------------------------------------------------------------

const cssUnescape = (text) =>
  text.replace(/\\(?:([0-9a-fA-F]{1,6})\s?|([^\n]))/g, (_, hex, ch) =>
    hex ? String.fromCodePoint(Math.min(Number.parseInt(hex, 16), 0x10ffff)) : ch,
  )
const cssString = (value) => ({
  type: "string",
  quote: '"',
  value: value.replaceAll("\\", "\\\\").replaceAll('"', '\\"').replaceAll("\n", "\\a "),
})

/** Rewrite the url() / image-set() / @import references of a parsed CSS value. */
function processValue(value, baseDir) {
  const parsed = valueParser(value)
  let changed = false
  const rewriteNode = (holder, index) => {
    const node = holder[index]
    const uri = inlineRef(cssUnescape(node.value), baseDir)
    if (uri !== null) {
      holder[index] = { ...cssString(uri), sourceIndex: node.sourceIndex }
      changed = true
    }
  }
  parsed.walk((node) => {
    if (node.type !== "function") return
    const name = node.value.toLowerCase()
    if (name === "url") {
      const index = node.nodes.findIndex((n) => n.type === "word" || n.type === "string")
      if (index >= 0 && node.nodes.length === 1) rewriteNode(node.nodes, index)
      return false
    }
    if (name === "image-set" || name === "-webkit-image-set") {
      node.nodes.forEach((child, index) => {
        if (child.type === "string") rewriteNode(node.nodes, index)
        else if (child.type === "function" && child.value.toLowerCase() === "url" && child.nodes.length === 1) {
          rewriteNode(child.nodes, 0)
        }
      })
      return false
    }
    return undefined
  })
  return changed ? parsed.toString() : value
}

/** Inline references in CSS text. Only url(), image-set() and @import tokens count. */
function processCss(css, baseDir) {
  let tree
  try {
    tree = postcss.parse(css)
  } catch (error) {
    problem("CSS", `cannot parse stylesheet: ${error.message}`)
    return css
  }
  tree.walkDecls((decl) => {
    decl.value = processValue(decl.value, baseDir)
  })
  tree.walkAtRules("import", (rule) => {
    rule.params = processValue(rule.params, baseDir)
    // @import "file.css": the first token is a bare string
    const nodes = valueParser(rule.params).nodes
    if (nodes[0]?.type === "string") {
      const uri = inlineRef(cssUnescape(nodes[0].value), baseDir)
      if (uri !== null) {
        nodes[0] = cssString(uri)
        rule.params = valueParser.stringify(nodes)
      }
    }
  })
  return tree.toString()
}

// --- srcset ------------------------------------------------------------------------------

const ASCII_WS = /[ \t\n\f\r]/
const trimAscii = (text) => text.replace(/^[ \t\n\f\r]+|[ \t\n\f\r]+$/g, "")

/** WHATWG "parse a srcset attribute": candidates are { url, descriptors }. */
function parseSrcset(input) {
  const candidates = []
  let i = 0
  while (i < input.length) {
    while (i < input.length && (ASCII_WS.test(input[i]) || input[i] === ",")) i++
    if (i >= input.length) break
    const start = i
    while (i < input.length && !ASCII_WS.test(input[i])) i++
    let url = input.slice(start, i)
    let descriptors = ""
    if (url.endsWith(",")) {
      url = url.replace(/,+$/, "")
    } else {
      const descriptorStart = i
      let inParens = false
      while (i < input.length) {
        const c = input[i]
        if (!inParens && c === ",") break
        if (c === "(") inParens = true
        else if (c === ")") inParens = false
        i++
      }
      descriptors = trimAscii(input.slice(descriptorStart, i))
      if (i < input.length) i++ // the comma
    }
    if (url !== "") candidates.push({ url, descriptors })
  }
  return candidates
}

const stringifySrcset = (candidates) =>
  candidates.map((c) => (c.descriptors ? `${c.url} ${c.descriptors}` : c.url)).join(", ")

// --- HTML --------------------------------------------------------------------------------

function walk(node, visit) {
  visit(node)
  for (const child of node.childNodes ?? []) walk(child, visit)
  if (node.content) walk(node.content, visit)
}

function processElement(node) {
  for (const a of node.attrs) {
    if (a.name === "src" || a.name === "poster" || (a.name === "href" && node.tagName === "link")) {
      const uri = inlineRef(a.value, root)
      if (uri !== null) a.value = uri
    } else if (a.name === "srcset" || a.name === "imagesrcset") {
      const candidates = parseSrcset(a.value)
      let changed = false
      for (const candidate of candidates) {
        const uri = inlineRef(candidate.url, root)
        if (uri !== null) {
          candidate.url = uri
          changed = true
        }
      }
      if (changed) a.value = stringifySrcset(candidates)
    } else if (a.name === "style") {
      a.value = processCss(a.value, root)
    }
  }
}

function processHtml(html) {
  const document = parse(html)
  walk(document, (node) => {
    if (node.attrs) processElement(node)
    if (node.tagName === "style") {
      for (const child of node.childNodes) {
        if (child.nodeName === "#text") child.value = processCss(child.value, root)
      }
    }
  })
  return serialize(document)
}

const output = processHtml(readFileSync(join(root, "index.html"), "utf8"))

if (problems.length > 0) {
  console.error("Error: bundle.html would still reference files that are not inlined:")
  for (const line of [...new Set(problems)]) console.error(`  ${line}`)
  console.error("Put the files in public/ (or import them from code), or use absolute URLs.")
  process.exit(1)
}

mkdirSync(dirname(resolve(outFile)), { recursive: true })
writeFileSync(outFile, output, { flag: "wx" })
