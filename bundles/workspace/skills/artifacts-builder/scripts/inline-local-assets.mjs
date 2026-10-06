// Inline the local files that a built index.html still references (public/ images, fonts,
// icons, stylesheets and the url() assets inside them) as data: URIs, and fail when any local
// reference cannot be inlined or escapes the project.
//
// HTML is parsed with parse5 (browser-grade tokenizing, comment recovery, character-reference
// decoding) and written back so that it parses to the same DOM. CSS is tokenized with the
// css-tree tokenizer (CSS Syntax 3) and edited at token level, so only real url(), image-set()
// and @import tokens count. srcset follows the WHATWG candidate and descriptor algorithm.
// bundle-artifact.sh installs the parsers into the project and runs a copy of this file there.
//
// Usage: bun inline-local-assets.mjs <build-dir> <output-html> [project-root]
import { constants, closeSync, fstatSync, mkdirSync, openSync, readFileSync, realpathSync, statSync, writeFileSync } from "node:fs"
import { dirname, extname, join, relative, resolve, sep } from "node:path"
import { fileURLToPath } from "node:url"
import { tokenTypes, tokenize } from "css-tree"
import { parse, serializeOuter } from "parse5"

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

const within = (path, base) => path === base || path.startsWith(base + sep)
const mimeOf = (file) => MIME[extname(file).toLowerCase()] ?? "application/octet-stream"
const toDataUri = (bytes, mime, fragment) => `data:${mime};base64,${Buffer.from(bytes).toString("base64")}${fragment}`

// Browsers strip tabs and newlines inside URLs and trim control characters and spaces around them
// biome-ignore lint/suspicious/noControlCharactersInRegex: matching URL-stripped control characters
const cleanUrl = (text) => text.replace(/[\t\n\r]/g, "").replace(/^[\u0000-\u0020]+|[\u0000-\u0020]+$/g, "")

// Absolute URLs, fragments, data/blob URIs and other schemes are not local files
const isLocal = (ref) => ref !== "" && !/^(#|\/\/|[a-zA-Z][a-zA-Z0-9+.-]*:)/.test(ref)

// --- CSS Syntax 3 helpers ----------------------------------------------------------------

const isCssWhitespace = (c) => c === " " || c === "\t" || c === "\n" || c === "\r" || c === "\f"
const isHex = (c) => c !== undefined && /^[0-9a-fA-F]$/.test(c)
const isNewline = (c) => c === "\n" || c === "\r" || c === "\f"

/**
 * "Consume an escaped code point" (the backslash is already consumed, `i` is the next index).
 * Only CSS whitespace ends a hex escape (not NBSP or other Unicode spaces); zero, surrogates and
 * values above U+10FFFF become U+FFFD. Returns [text, nextIndex].
 */
function consumeEscape(css, i) {
  if (i >= css.length) return ["\ufffd", i]
  if (!isHex(css[i])) {
    const point = css.codePointAt(i)
    return [String.fromCodePoint(point), i + (point > 0xffff ? 2 : 1)]
  }
  let hex = ""
  while (hex.length < 6 && isHex(css[i])) hex += css[i++]
  if (css[i] === "\r" && css[i + 1] === "\n") i += 2
  else if (isCssWhitespace(css[i])) i++
  const value = Number.parseInt(hex, 16)
  const bad = value === 0 || (value >= 0xd800 && value <= 0xdfff) || value > 0x10ffff
  return [bad ? "\ufffd" : String.fromCodePoint(value), i]
}

/** Decode the escapes of an identifier such as `u\72l` or `@im\70ort` (without the `@`). */
function decodeIdent(raw) {
  let out = ""
  for (let i = 0; i < raw.length; ) {
    if (raw[i] === "\\" && i + 1 < raw.length && !isNewline(raw[i + 1])) {
      const [text, next] = consumeEscape(raw, i + 1)
      out += text
      i = next
    } else {
      out += raw[i++]
    }
  }
  return out
}

/** The value of a string token (raw includes its quotes): escapes decoded, continuations removed. */
function stringValue(raw) {
  const quote = raw[0]
  const closed = raw.length > 1 && raw.endsWith(quote) && !endsWithOddBackslashes(raw.slice(0, -1))
  const inner = raw.slice(1, closed ? -1 : raw.length)
  let out = ""
  for (let i = 0; i < inner.length; ) {
    if (inner[i] !== "\\") {
      out += inner[i++]
    } else if (i + 1 >= inner.length) {
      i++
    } else if (isNewline(inner[i + 1])) {
      i += inner[i + 1] === "\r" && inner[i + 2] === "\n" ? 3 : 2
    } else {
      const [text, next] = consumeEscape(inner, i + 1)
      out += text
      i = next
    }
  }
  return out
}
const endsWithOddBackslashes = (text) => (text.match(/\\*$/)?.[0].length ?? 0) % 2 === 1

/**
 * "Consume a url token" for the unquoted form; `i` is the index right after "(".
 * Returns { value, bad, end }.
 */
function consumeUrlToken(css, start) {
  let i = start
  while (isCssWhitespace(css[i])) i++
  let value = ""
  const badRemnants = () => {
    while (i < css.length && css[i] !== ")") {
      if (css[i] === "\\" && i + 1 < css.length) i++
      i++
    }
    return { value, bad: true, end: Math.min(i + 1, css.length) }
  }
  while (i < css.length) {
    const c = css[i]
    const code = c.charCodeAt(0)
    if (c === ")") return { value, bad: false, end: i + 1 }
    if (isCssWhitespace(c)) {
      while (isCssWhitespace(css[i])) i++
      if (i >= css.length) return { value, bad: false, end: i }
      if (css[i] === ")") return { value, bad: false, end: i + 1 }
      return badRemnants()
    }
    if (c === '"' || c === "'" || c === "(" || code <= 0x08 || code === 0x0b || (code >= 0x0e && code <= 0x1f) || code === 0x7f) {
      return badRemnants()
    }
    if (c === "\\") {
      if (i + 1 >= css.length || isNewline(css[i + 1])) return badRemnants()
      const [text, next] = consumeEscape(css, i + 1)
      value += text
      i = next
      continue
    }
    value += c
    i++
  }
  return { value, bad: false, end: css.length }
}

const cssStringLiteral = (value) =>
  `"${value.replaceAll("\\", "\\\\").replaceAll('"', '\\"').replaceAll("\n", "\\a ")}"`

// --- srcset (WHATWG "parse a srcset attribute") -----------------------------------------

const ASCII_WS = /[ \t\n\f\r]/
const trimAscii = (text) => text.replace(/^[ \t\n\f\r]+|[ \t\n\f\r]+$/g, "")

/** Parse the descriptor list of one candidate; returns null when the candidate must be discarded. */
function parseDescriptors(descriptors) {
  const tokens = []
  let current = ""
  let inParens = false
  for (const c of descriptors) {
    if (!inParens && ASCII_WS.test(c)) {
      if (current !== "") tokens.push(current)
      current = ""
      continue
    }
    if (c === "(") inParens = true
    else if (c === ")") inParens = false
    current += c
  }
  if (current !== "") tokens.push(current)

  let width = null
  let density = null
  let height = null
  for (const token of tokens) {
    const last = token.at(-1)
    const number = token.slice(0, -1)
    if (last === "w" && /^[0-9]+$/.test(number)) {
      if (width !== null || density !== null || height !== null) return null
      if (Number.parseInt(number, 10) === 0) return null
      width = Number.parseInt(number, 10)
    } else if (last === "x" && /^-?([0-9]+(\.[0-9]+)?|\.[0-9]+)([eE][+-]?[0-9]+)?$/.test(number)) {
      if (width !== null || density !== null || height !== null) return null
      if (Number.parseFloat(number) < 0) return null
      density = Number.parseFloat(number)
    } else if (last === "h" && /^[0-9]+$/.test(number)) {
      if (height !== null || density !== null) return null
      if (Number.parseInt(number, 10) === 0) return null
      height = Number.parseInt(number, 10)
    } else {
      return null
    }
  }
  return { width, density, height }
}

/** Returns { candidates, discarded }; candidates with invalid descriptors are discarded. */
function parseSrcset(input) {
  const candidates = []
  let discarded = 0
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
    if (url === "") continue
    if (parseDescriptors(descriptors) === null) {
      discarded++ // a parse error for the browser too, so not ours to fail the bundle over
      continue
    }
    candidates.push({ url, descriptors })
  }
  return { candidates, discarded }
}

const stringifySrcset = (candidates) =>
  candidates.map((c) => (c.descriptors ? `${c.url} ${c.descriptors}` : c.url)).join(", ")

// --- document serialization ---------------------------------------------------------------

const quoteDoctypeId = (id) => (id.includes('"') ? `'${id}'` : `"${id}"`)

function doctypeToString(node) {
  let out = `<!DOCTYPE ${node.name}`
  if (node.publicId) {
    out += ` PUBLIC ${quoteDoctypeId(node.publicId)}`
    if (node.systemId) out += ` ${quoteDoctypeId(node.systemId)}`
  } else if (node.systemId) {
    out += ` SYSTEM ${quoteDoctypeId(node.systemId)}`
  }
  return `${out}>`
}

// The HTML parser drops one leading newline in these elements; the serializer does not put it
// back, so a text that itself starts with a newline must be written with an extra one.
const LEADING_NEWLINE_ELEMENTS = new Set(["pre", "textarea", "listing"])

function walk(node, visit) {
  visit(node)
  for (const child of node.childNodes ?? []) walk(child, visit)
  if (node.content) walk(node.content, visit)
}

// --- the inliner ------------------------------------------------------------------------

/**
 * Create an inliner for one build directory. `problems` collects everything that could not be
 * inlined; the caller decides what to do with it.
 */
export function createInliner({ buildDir, projectRoot: projectArg }) {
  const root = resolve(buildDir)
  const projectRoot = resolve(projectArg ?? process.cwd())
  const realRoot = realpathSync(root)
  const realProject = realpathSync(projectRoot)
  const problems = []
  const problem = (ref, why) => problems.push(`${ref}  (${why})`)
  const activeCss = new Set()

  /**
   * Resolve a reference to a real file inside the build directory.
   * Returns { real, lexical, fragment, dev, ino } or null (after recording why it failed).
   * `lexical` is the URL-style path (symlinks not followed); relative references inside a
   * stylesheet resolve against its directory. Confinement is checked on canonical (realpath)
   * paths, so a symlinked file or parent directory cannot pull in content from outside the build
   * or the project, and files with several hard links are rejected.
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
    const stat = statSync(real, { bigint: true })
    if (!stat.isFile()) {
      problem(ref, "not a file")
      return null
    }
    if (stat.nlink > 1n) {
      problem(ref, `file has ${stat.nlink} hard links; refusing to read it`)
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
    if (realSource !== null) {
      if (!within(realSource, realProject)) {
        problem(ref, "public/ file escapes the project through a symlink")
        return null
      }
      if (statSync(realSource).nlink > 1) {
        problem(ref, "public/ file has several hard links; refusing to read it")
        return null
      }
    }

    return { real, lexical, fragment, dev: stat.dev, ino: stat.ino }
  }

  /**
   * Read a resolved file through one descriptor: opened without following a final symlink, then
   * compared (device and inode) with what resolveRef checked, so a swap between check and read
   * is detected. Returns the bytes or null (after recording the problem).
   */
  function readChecked(record) {
    let fd
    try {
      fd = openSync(record.real, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0))
      const stat = fstatSync(fd, { bigint: true })
      if (!stat.isFile() || stat.dev !== record.dev || stat.ino !== record.ino || stat.nlink > 1n) {
        problem(record.lexical, "file changed between the check and the read")
        return null
      }
      if (realpathSync(record.lexical) !== record.real) {
        problem(record.lexical, "path changed between the check and the read")
        return null
      }
      return readFileSync(fd)
    } catch (error) {
      problem(record.lexical, `file changed between the check and the read (${error.code ?? error.message})`)
      return null
    } finally {
      if (fd !== undefined) closeSync(fd)
    }
  }

  /** Resolve and encode one reference. kind "css" forces stylesheet processing. Null = left alone. */
  function inlineRef(rawRef, baseDir, kind = "asset") {
    const ref = cleanUrl(rawRef)
    if (!isLocal(ref)) return null
    const found = resolveRef(ref, baseDir)
    if (found === null) return null
    if (kind === "css" || extname(found.real).toLowerCase() === ".css") return stylesheetUri(found)
    const bytes = readChecked(found)
    return bytes === null ? null : toDataUri(bytes, mimeOf(found.real), found.fragment)
  }

  function stylesheetUri(found) {
    const { real, lexical, fragment } = found
    if (activeCss.has(real)) {
      problem(real, "stylesheet imports itself (cycle)")
      return null
    }
    const bytes = readChecked(found)
    if (bytes === null) return null
    activeCss.add(real)
    try {
      // References inside resolve against the stylesheet's URL directory, not its symlink target
      const css = processCss(bytes.toString("utf8"), dirname(lexical))
      return toDataUri(css, "text/css", fragment)
    } finally {
      activeCss.delete(real)
    }
  }

  // --- CSS: edits at token level ---------------------------------------------------------

  /**
   * Inline the references of CSS text. Only url() tokens (any case, escapes decoded), strings that
   * are the argument of url() or image-set(), and the target of @import count; strings such as
   * content:"url(x)" and comments are never touched.
   */
  function processCss(css, baseDir) {
    const tokens = []
    tokenize(css, (type, start, end) => tokens.push({ type, start, end }))
    const edits = []
    const stack = []
    let inImport = false
    let skipUntil = 0

    const nextSignificant = (from) => {
      let j = from
      while (j < css.length && isCssWhitespace(css[j])) j++
      return j
    }
    const refKind = () => (inImport ? "css" : "asset")

    for (const token of tokens) {
      if (token.start < skipUntil) continue
      const raw = css.slice(token.start, token.end)
      switch (token.type) {
        case tokenTypes.AtKeyword:
          inImport = decodeIdent(raw.slice(1)).toLowerCase() === "import"
          break
        case tokenTypes.Semicolon:
        case tokenTypes.LeftCurlyBracket:
          inImport = false
          break
        case tokenTypes.Function:
        case tokenTypes.Url: {
          const name = decodeIdent(raw.slice(0, raw.indexOf("(") >= 0 ? raw.indexOf("(") : raw.length)).toLowerCase()
          const open = token.start + raw.indexOf("(") + 1
          if (name === "url") {
            const after = nextSignificant(open)
            if (css[after] === '"' || css[after] === "'") {
              stack.push("url") // a string argument follows: handled as a string token
              break
            }
            const url = consumeUrlToken(css, open)
            skipUntil = url.end
            if (url.bad) {
              problem(css.slice(token.start, url.end), "malformed url() token")
              break
            }
            const uri = inlineRef(url.value, baseDir, refKind())
            if (uri !== null) edits.push({ start: token.start, end: url.end, text: `url(${cssStringLiteral(uri)})` })
          } else if (name === "image-set" || name === "-webkit-image-set") {
            stack.push("image-set")
          } else {
            stack.push("other")
          }
          break
        }
        case tokenTypes.LeftParenthesis:
          stack.push("other")
          break
        case tokenTypes.RightParenthesis:
          stack.pop()
          break
        case tokenTypes.BadUrl:
          problem(raw, "malformed url() token")
          break
        case tokenTypes.String: {
          const context = stack.at(-1)
          const isImportTarget = inImport && stack.length === 0
          if (context === "url" || context === "image-set" || isImportTarget) {
            const uri = inlineRef(stringValue(raw), baseDir, context === "url" ? refKind() : isImportTarget ? "css" : "asset")
            if (uri !== null) edits.push({ start: token.start, end: token.end, text: cssStringLiteral(uri) })
          }
          break
        }
        default:
          break
      }
    }

    let out = ""
    let pos = 0
    for (const edit of edits.sort((a, b) => a.start - b.start)) {
      out += css.slice(pos, edit.start) + edit.text
      pos = edit.end
    }
    return out + css.slice(pos)
  }

  // --- HTML --------------------------------------------------------------------------------

  function processElement(node) {
    const rel = (node.attrs.find((a) => a.name === "rel")?.value ?? "").toLowerCase().split(/\s+/)
    for (const a of node.attrs) {
      if (a.name === "src" || a.name === "poster" || (a.name === "href" && node.tagName === "link")) {
        const kind = node.tagName === "link" && a.name === "href" && rel.includes("stylesheet") ? "css" : "asset"
        const uri = inlineRef(a.value, root, kind)
        if (uri !== null) a.value = uri
      } else if (a.name === "srcset" || a.name === "imagesrcset") {
        const { candidates, discarded } = parseSrcset(a.value)
        let changed = discarded > 0
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
      if (LEADING_NEWLINE_ELEMENTS.has(node.tagName)) {
        const first = node.childNodes[0]
        if (first?.nodeName === "#text" && first.value.startsWith("\n")) first.value = `\n${first.value}`
      }
    })
    return document.childNodes
      .map((node) => (node.nodeName === "#documentType" ? doctypeToString(node) : serializeOuter(node)))
      .join("")
  }

  /** Read and process <build-dir>/index.html. */
  function processIndex() {
    const found = resolveRef("/index.html", root)
    if (found === null) return null
    const bytes = readChecked(found)
    return bytes === null ? null : processHtml(bytes.toString("utf8"))
  }

  return { root, problems, resolveRef, readChecked, processCss, processHtml, processIndex }
}

// --- CLI ----------------------------------------------------------------------------------

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [buildDirArg, outFile, projectArg] = process.argv.slice(2)
  if (!buildDirArg || !outFile) {
    console.error("Usage: inline-local-assets.mjs <build-dir> <output-html> [project-root]")
    process.exit(2)
  }
  const inliner = createInliner({ buildDir: buildDirArg, projectRoot: projectArg })
  const output = inliner.processIndex()

  if (output === null || inliner.problems.length > 0) {
    console.error("Error: bundle.html would still reference files that are not inlined:")
    for (const line of [...new Set(inliner.problems)]) console.error(`  ${line}`)
    console.error("Put the files in public/ (or import them from code), or use absolute URLs.")
    process.exit(1)
  }

  mkdirSync(dirname(resolve(outFile)), { recursive: true })
  writeFileSync(outFile, output, { flag: "wx" })
}
