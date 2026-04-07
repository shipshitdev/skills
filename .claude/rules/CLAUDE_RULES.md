# Claude Rules (Consolidated)

## User Preferences (OVERRIDE ALL)

### Forbidden Actions
- **Background processes**: Use `run_in_background` for long-running tasks (training, generation, server ops). No trailing `&` in commands.
- **Sequential only**: Run tests/builds one package at a time — `bun run test --filter=@genfeedai/[name]` or `bun build:app @genfeedai/[name]`. Never run the full root suite (`bun test` with no filter) locally — that's CI/CD only. No `pnpm build` at root.
- **Auto-commit/push**: Wait for explicit user request
- **Work outside workspace**: No `/tmp`, no `~/Desktop`, stay in project
- **Force push main/master**: Never
- **Skip pre-commit hooks**: Never `--no-verify`

### Required Before Code
1. Read files you'll modify
2. Find 3+ similar implementations in codebase
3. Check session history for past solutions
4. Copy exact patterns (imports, naming, error handling)

### Session Management
- Document before `/clear`: files changed, decisions, incomplete work
- Save to `.agents/SESSIONS/YYYY-MM-DD.md`
- Check previous sessions before implementing
- **NEVER save secrets to session files**: If user shares .env values, API keys, tokens, passwords, or any sensitive data in conversation, DO NOT include them in session documentation. Redact or omit entirely.

## Code Standards

### TypeScript
- No `any` types - define interfaces
- Path aliases (`@components/`) over relative (`../../../`)
- No `console.log` - use project logger
- Interfaces in dedicated files, not inline
- Handle async errors with try/catch
- Use AbortController in React effects

### Imports Order
1. External packages (react, next)
2. Internal packages (@company/*)
3. Path aliases (@components/*)
4. Relative (same directory only)

### Git
- Conventional commits: `fix:`, `feat:`, `refactor:`, `chore:`
- Never commit secrets (.env, API keys)
- Descriptive messages, not "fix" or "wip"

## Behavior

### Default to Action
- Implement when intent is clear, don't just suggest
- Use tools to discover missing info instead of asking
- Ask only when genuinely ambiguous or breaking changes

### Code First
- Read files before proposing edits
- Never speculate about unread code
- Search codebase patterns before writing new code

### Minimize
- Only requested changes, no feature creep
- No error handling for impossible scenarios
- No abstractions for one-time operations
- Reuse existing code, follow DRY

### Communication
- Direct, fact-based
- Acknowledge mistakes, fix, move on
- No excuses or justifications

## Tool Usage
- Parallel calls when independent
- Read tool (not cat), Grep tool (not grep), Edit tool (not sed)
- Save state before context limits

## Frontend (when applicable)
- Unique typography (avoid Inter, Roboto, Arial)
- Cohesive color themes with sharp accents
- CSS animations for micro-interactions
- Avoid generic "AI slop" aesthetics
