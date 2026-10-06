// Inline the local files that a built index.html still references (public/ images, fonts,
// icons, stylesheets and the url() assets inside them) as data: URIs, and fail when any local
// reference cannot be inlined or escapes the project.
// Usage: bun inline-local-assets.mjs <build-dir> <output-html> [project-root]
import { mkdirSync, readFileSync, realpathSync, statSync, writeFileSync } from "node:fs"
import { dirname, extname, join, relative, resolve, sep } from "node:path"

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

// Absolute URLs, fragments, data/blob URIs and other schemes are not local files
const isLocal = (ref) => ref !== "" && !/^(#|\/\/|[a-zA-Z][a-zA-Z0-9+.-]*:)/.test(ref)

/**
 * Resolve a reference to a real file inside the build directory.
 * Returns { real, fragment } or null (after recording why it failed).
 * Confinement is checked on canonical (realpath) paths, so a symlinked file or symlinked parent
 * directory cannot pull in content from outside the build or the project.
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

  return { real, fragment }
}

const mimeOf = (file) => MIME[extname(file).toLowerCase()] ?? "application/octet-stream"
const toDataUri = (bytes, mime, fragment) => `data:${mime};base64,${Buffer.from(bytes).toString("base64")}${fragment}`

const activeCss = new Set()

/** Inline url() and @import references of CSS text; refs resolve relative to baseDir. */
function processCss(css, baseDir) {
  // Leave comments untouched so a commented-out url() cannot fail the build
  return css
    .split(/(\/\*[\s\S]*?\*\/)/)
    .map((part, index) => {
      if (index % 2 === 1) return part
      return part
        .replace(/@import\s+(["'])([^"']*)\1/gi, (match, quote, ref) => {
          const uri = inlineCssFile(ref, baseDir)
          return uri === null ? match : `@import ${quote}${uri}${quote}`
        })
        .replace(/url\(\s*(["']?)([^)"']*)\1\s*\)/gi, (match, quote, ref) => {
          const trimmed = ref.trim()
          const uri = inlineRefAsUri(trimmed, baseDir)
          return uri === null ? match : `url(${quote}${uri}${quote})`
        })
    })
    .join("")
}

/** A CSS reference: stylesheets are processed recursively, everything else is encoded as is. */
function inlineRefAsUri(ref, baseDir) {
  if (!isLocal(ref)) return null
  const found = resolveRef(ref, baseDir)
  if (found === null) return null
  if (extname(found.real).toLowerCase() === ".css") return stylesheetUri(found)
  return toDataUri(readFileSync(found.real), mimeOf(found.real), found.fragment)
}

function inlineCssFile(ref, baseDir) {
  if (!isLocal(ref)) return null
  const found = resolveRef(ref, baseDir)
  return found === null ? null : stylesheetUri(found)
}

function stylesheetUri({ real, fragment }) {
  if (activeCss.has(real)) {
    problem(real, "stylesheet imports itself (cycle)")
    return null
  }
  activeCss.add(real)
  try {
    const css = processCss(readFileSync(real, "utf8"), dirname(real))
    return toDataUri(css, "text/css", fragment)
  } finally {
    activeCss.delete(real)
  }
}

// --- HTML character references -------------------------------------------------------

// Named references that can occur in URLs and CSS (the full HTML table has 2,231 entries; any
// other `&name;` is reported instead of guessed).
const NAMED = {
  amp: "&", AMP: "&", lt: "<", LT: "<", gt: ">", GT: ">", quot: '"', QUOT: '"', apos: "'",
  nbsp: "\u00a0", num: "#", sol: "/", bsol: "\\", colon: ":", semi: ";", comma: ",",
  period: ".", excl: "!", quest: "?", equals: "=", percnt: "%", lpar: "(", rpar: ")",
  lsqb: "[", lbrack: "[", rsqb: "]", rbrack: "]", lcub: "{", lbrace: "{", rcub: "}", rbrace: "}",
  lowbar: "_", UnderBar: "_", plus: "+", ast: "*", midast: "*", commat: "@", dollar: "$",
  grave: "`", Hat: "^", vert: "|", verbar: "|", VerticalLine: "|", Tab: "\t", NewLine: "\n",
}
// Legacy names the HTML parser also accepts without a trailing semicolon
const LEGACY = new Set(["amp", "AMP", "lt", "LT", "gt", "GT", "quot", "QUOT", "nbsp"])

function codePoint(value) {
  if (value === 0 || value > 0x10ffff || (value >= 0xd800 && value <= 0xdfff)) return "\ufffd"
  return String.fromCodePoint(value)
}

/**
 * Decode character references the way the HTML tokenizer does inside an attribute value.
 * Returns { text, unknown } where `unknown` lists `&name;` references this table cannot decide.
 */
function decodeAttribute(value) {
  const unknown = []
  const text = value.replace(/&(?:#([xX][0-9a-fA-F]+|[0-9]+);?|([A-Za-z][A-Za-z0-9]*)(;?))/g, (match, num, name, semi, offset) => {
    if (num !== undefined) {
      const parsed = /^[xX]/.test(num) ? Number.parseInt(num.slice(1), 16) : Number.parseInt(num, 10)
      return codePoint(parsed)
    }
    if (semi === ";") {
      if (Object.hasOwn(NAMED, name)) return NAMED[name]
      unknown.push(match)
      return match
    }
    // No semicolon: only legacy names, and in attributes not when followed by "=" or alphanumerics
    if (LEGACY.has(name) && value[offset + match.length] !== "=") return NAMED[name]
    // anything else (including a legacy prefix followed by more name characters) is literal
    return match
  })
  return { text, unknown }
}

const encodeAttribute = (value, quote) => {
  const escaped = value.replaceAll("&", "&amp;")
  return quote === "'" ? escaped.replaceAll("'", "&#39;") : escaped.replaceAll('"', "&quot;")
}

// Browsers strip tabs and newlines inside URLs and trim control characters and spaces around them
// eslint-disable-next-line no-control-regex
const cleanUrl = (text) => text.replace(/[\t\n\r]/g, "").replace(/^[\u0000-\u0020]+|[\u0000-\u0020]+$/g, "")

// --- HTML tokenizer -------------------------------------------------------------------

const RAW_TEXT = new Set(["script", "style", "textarea", "title"])
const WS = /\s/

/** Parse one start tag beginning at `start` ("<name ..."). Returns { end, name, attrs }. */
function parseTag(html, start) {
  let i = start + 1
  const nameStart = i
  while (i < html.length && !WS.test(html[i]) && html[i] !== "/" && html[i] !== ">") i++
  const name = html.slice(nameStart, i).toLowerCase()
  const attrs = []

  while (i < html.length) {
    while (i < html.length && (WS.test(html[i]) || html[i] === "/")) i++
    if (html[i] === ">") return { end: i + 1, name, attrs }
    if (i >= html.length) break

    const attrStart = i
    while (i < html.length && !WS.test(html[i]) && html[i] !== "/" && html[i] !== ">" && html[i] !== "=") i++
    if (i === attrStart) {
      i++ // stray "=" at the start of a name
      continue
    }
    const attr = { name: html.slice(attrStart, i).toLowerCase(), value: null, start: -1, end: -1, quote: "" }

    let j = i
    while (j < html.length && WS.test(html[j])) j++
    if (html[j] === "=") {
      j++
      while (j < html.length && WS.test(html[j])) j++
      const q = html[j]
      if (q === '"' || q === "'") {
        const close = html.indexOf(q, j + 1)
        const valueEnd = close === -1 ? html.length : close
        Object.assign(attr, { value: html.slice(j + 1, valueEnd), start: j + 1, end: valueEnd, quote: q })
        i = close === -1 ? html.length : close + 1
      } else {
        const valueStart = j
        while (j < html.length && !WS.test(html[j]) && html[j] !== ">") j++
        Object.assign(attr, { value: html.slice(valueStart, j), start: valueStart, end: j, quote: "" })
        i = j
      }
    }
    attrs.push(attr)
  }
  return { end: html.length, name, attrs }
}

/** Rewrite the asset-bearing attributes of a start tag; returns the new tag text. */
function rewriteTag(html, start, tag) {
  const edits = []
  // Attribute values are character-reference decoded before anything is resolved, and a changed
  // value is encoded again when written back. Untouched attributes keep their original text.
  const read = (a) => {
    const { text, unknown } = decodeAttribute(a.value)
    if (unknown.length > 0) {
      problem(unknown.join(" "), `unrecognized character reference in ${a.name}="${a.value}"`)
      return null
    }
    return text
  }
  const write = (a, decodedBefore, decodedAfter) => {
    if (decodedAfter === decodedBefore) return
    // An unquoted value becomes a quoted one so any data URI is safe in the attribute
    const quote = a.quote || '"'
    const encoded = encodeAttribute(decodedAfter, quote)
    edits.push({ from: a.start, to: a.end, text: a.quote ? encoded : `${quote}${encoded}${quote}` })
  }
  const relAttr = tag.attrs.find((a) => a.name === "rel" && a.value !== null)
  const rel = (relAttr ? decodeAttribute(relAttr.value).text : "").toLowerCase().split(/\s+/)

  for (const a of tag.attrs) {
    if (a.value === null) continue
    if (a.name === "src" || a.name === "poster" || (a.name === "href" && tag.name === "link")) {
      const before = read(a)
      if (before === null) continue
      const ref = cleanUrl(before)
      if (!isLocal(ref)) continue
      const found = resolveRef(ref, root)
      if (found === null) continue
      if (tag.name === "link" && a.name === "href" && rel.includes("stylesheet")) {
        const uri = stylesheetUri(found)
        if (uri !== null) write(a, before, uri)
      } else {
        write(a, before, toDataUri(readFileSync(found.real), mimeOf(found.real), found.fragment))
      }
    } else if (a.name === "srcset" || a.name === "imagesrcset") {
      const before = read(a)
      if (before === null) continue
      const candidates = before.split(",").map((candidate) => {
        const [url, ...descriptor] = candidate.trim().split(/\s+/)
        const ref = cleanUrl(url ?? "")
        if (!ref || !isLocal(ref)) return candidate.trim()
        const found = resolveRef(ref, root)
        if (found === null) return candidate.trim()
        return [toDataUri(readFileSync(found.real), mimeOf(found.real), found.fragment), ...descriptor].join(" ")
      })
      write(a, before, candidates.join(", "))
    } else if (a.name === "style") {
      const before = read(a)
      if (before === null) continue
      write(a, before, processCss(before, root))
    }
  }

  let text = html.slice(start, tag.end)
  for (const { from, to, text: value } of edits.sort((x, y) => y.from - x.from)) {
    text = text.slice(0, from - start) + value + text.slice(to - start)
  }
  return text
}

/** Walk the document; only tags (and <style> text) are rewritten, never prose, comments or scripts. */
function processHtml(html) {
  let out = ""
  let i = 0
  while (i < html.length) {
    const lt = html.indexOf("<", i)
    if (lt === -1) {
      out += html.slice(i)
      break
    }
    out += html.slice(i, lt)

    if (html.startsWith("<!--", lt)) {
      const close = html.indexOf("-->", lt + 4)
      const end = close === -1 ? html.length : close + 3
      out += html.slice(lt, end)
      i = end
    } else if (/^<[!?]/.test(html.slice(lt, lt + 2)) || /^<\//.test(html.slice(lt, lt + 2))) {
      const close = html.indexOf(">", lt)
      const end = close === -1 ? html.length : close + 1
      out += html.slice(lt, end)
      i = end
    } else if (/^<[a-zA-Z]/.test(html.slice(lt, lt + 2))) {
      const tag = parseTag(html, lt)
      out += rewriteTag(html, lt, tag)
      i = tag.end
      if (RAW_TEXT.has(tag.name)) {
        const closeRe = new RegExp(`</${tag.name}(?=[\\s/>])`, "i")
        const rest = html.slice(i)
        const found = closeRe.exec(rest)
        const contentEnd = found ? i + found.index : html.length
        const content = html.slice(i, contentEnd)
        out += tag.name === "style" ? processCss(content, root) : content
        i = contentEnd
      }
    } else {
      out += "<"
      i = lt + 1
    }
  }
  return out
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
