// Test helper: print a normalized dump of the DOM that parse5 builds from an HTML file.
// Usage: bun dump-dom.mjs <file>
import { readFileSync } from "node:fs"
import { parse } from "parse5"

const dump = (node, depth = 0) => {
  const pad = "  ".repeat(depth)
  let line = `${pad}${node.nodeName}`
  if (node.nodeName === "#documentType") line += ` name=${JSON.stringify(node.name)} public=${JSON.stringify(node.publicId)} system=${JSON.stringify(node.systemId)}`
  if (node.nodeName === "#text" || node.nodeName === "#comment") line += ` ${JSON.stringify(node.value ?? node.data)}`
  if (node.attrs) line += ` ${JSON.stringify(node.attrs.map((a) => [a.name, a.value]))}`
  const out = [line]
  for (const child of node.childNodes ?? []) out.push(dump(child, depth + 1))
  if (node.content) out.push(dump(node.content, depth + 1))
  return out.join("\n")
}

console.log(dump(parse(readFileSync(process.argv[2], "utf8"))))
