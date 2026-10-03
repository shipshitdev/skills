---
description: "Strip AI slop from code, UI, product copy, or prose while keeping the project buildable."
argument-hint: "[ui|prose|all|dry-run] [--changed] [--product]"
disable-model-invocation: true
---

# Deslop - Remove AI Slop From Code and Product

Strip AI-generated slop while keeping the project buildable. Code slop: console
statements, `any` types, unused imports, dead/commented-out code, redundant comments,
unnecessary defensive checks, over-nesting. Product slop (`--product`): marketing-filler
copy, default-shadcn UI, missing loading/error states, dead buttons and half-wired flows.

## Usage

```bash
/deslop              # clean code slop in the current package/project
/deslop ui [target]  # audit/fix UI slop with the design-system primitive pass
/deslop prose        # cut AI tells from writing (replies, docs, PR copy)
/deslop --changed    # clean only the lines this branch introduced (diff-only)
/deslop --product    # also strip product slop (copy / UI / UX) and prose tells
/deslop --changed --product # combine diff-only scope with product cleanup
/deslop all          # sweep every package in a monorepo
/deslop dry-run      # preview the cleanup, change nothing
```

`/deslop help` prints this Usage block and stops without running anything.

Also reachable as `/refactor deslop`.

## Workflow

Use the `deslop` skill.

1. If invoked as `/deslop ui`, run the `deslop` UI mode. Do not run code cleanup
   first. If invoked as `/deslop prose`, run the prose catalog only.
2. Detect project structure (monorepo vs single package); in `--changed` mode,
   compute the branch diff (`git diff <merge-base>...HEAD`) and limit edits to those
   files/hunks.
3. Identify artifacts: console statements, `any`, unused imports/vars, commented-out
   code, debug code, redundant comments, defensive try-catch on trusted paths,
   over-nesting. With `--product`, also the copy/UI/UX slop from the skill's
   `references/product-slop.md` catalog.
4. Apply cleanup, replacing console with the project logger and `any` with real
   types; collapse deep nesting into early returns matching the file's style.
5. Verify: `bun run type-check || bunx tsc --noEmit`, then `bun run test`.

## Gates

- Never delete critical files (README, configs, entry points) or strip
  side-effect imports (CSS, polyfills).
- Keep comments that explain "why"; remove only those that restate "what".
- In `--changed` mode, do not touch pre-existing slop elsewhere — keep the cleanup
  scoped and reviewable.
- This skill edits and removes code. For a read-only structural review that only
  flags issues, use `structural-review` / `/review` instead.
