---
name: bun-development
description: "Fast, modern JavaScript/TypeScript development with the Bun runtime. Covers installation, project setup, package management, built-in APIs (file system, HTTP server, SQLite, WebSocket), testing, bundling, and Node.js migration. Use when building new JS/TS projects with Bun or migrating from Node.js."
license: MIT
metadata:
  version: "1.0.0"
  tags: "bun, javascript, typescript, runtime, bundler, testing"
  author: "antigravity-awesome-skills"
---

# Bun Development

Fast, modern JavaScript/TypeScript development with the Bun runtime.

## When to Use

- Starting new JS/TS projects with Bun
- Migrating from Node.js to Bun
- Optimizing development speed
- Using Bun's built-in tools (bundler, test runner, SQLite, HTTP server)
- Troubleshooting Bun-specific issues

## Why Bun?

| Feature | Bun | Node.js |
|:--------|:----|:--------|
| Startup time | ~25ms | ~100ms+ |
| Package install | 10-100x faster | Baseline |
| TypeScript | Native | Requires transpiler |
| JSX | Native | Requires transpiler |
| Test runner | Built-in | External (Jest, Vitest) |
| Bundler | Built-in | External (Webpack, esbuild) |

## Quick Reference

| Task | Command |
|:-----|:--------|
| Init project | `bun init` |
| Install deps | `bun install` |
| Add package | `bun add <pkg>` |
| Dev dependency | `bun add -d <pkg>` |
| Run script | `bun run <script>` |
| Run file | `bun run file.ts` |
| Watch mode | `bun --watch run file.ts` |
| Hot reload | `bun --hot run server.ts` |
| Run tests | `bun test` |
| Build | `bun build ./src/index.ts --outdir ./dist` |
| Execute pkg | `bunx <pkg>` |

## Key Built-in APIs

### Bun.file — Native File I/O

```typescript
const file = Bun.file('./data.json')
const json = await file.json()
await Bun.write('./output.txt', 'Hello!')
```

### Bun.serve — HTTP Server

```typescript
Bun.serve({
  port: 3000,
  fetch(request) {
    const url = new URL(request.url)
    if (url.pathname === '/') return new Response('Hello World!')
    return new Response('Not Found', { status: 404 })
  },
})
```

### Bun SQLite

```typescript
import { Database } from 'bun:sqlite'
const db = new Database('mydb.sqlite')
const user = db.prepare('SELECT * FROM users WHERE id = ?').get(1)
```

### Bun Password

```typescript
const hash = await Bun.password.hash('super-secret')
const isValid = await Bun.password.verify('super-secret', hash)
```

## Testing

```bash
bun test                    # run all tests
bun test math.test.ts       # run specific file
bun test --grep "adds"      # filter by name
bun test --watch            # watch mode
bun test --coverage         # with coverage
```

```typescript
import { describe, it, expect } from 'bun:test'

describe('Math', () => {
  it('adds two numbers', () => {
    expect(1 + 1).toBe(2)
  })
})
```

## tsconfig.json (Bun-optimized)

```json
{
  "compilerOptions": {
    "lib": ["ESNext"],
    "module": "esnext",
    "target": "esnext",
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "noEmit": true,
    "strict": true,
    "jsx": "react-jsx",
    "types": ["bun-types"]
  }
}
```

## Node.js Migration Key Points

- `require()` → `import`
- `process.hrtime()` → `Bun.nanoseconds()`
- `fs.readFile` → `Bun.file()` (faster)
- `express/fastify` → `Bun.serve()` or Elysia (4-10x faster)
- Delete `package-lock.json`, run `bun install`

## Performance Tips

- Prefer `Bun.file()` over `fs/promises` for file I/O
- Prefer `Bun.serve()` over Express for HTTP servers
- Always bundle and minify for production: `bun build --minify --target node`
- Use `bun --hot` for development hot reloading

## Full Reference

See `references/full-guide.md` for complete API docs, bundling, mocking, WebSocket, and cross-compilation examples.

## Limitations

- Use only when task matches Bun runtime scope.
- Not all Node.js native addons work in Bun — check compatibility first.
