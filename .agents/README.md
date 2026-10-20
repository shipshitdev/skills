# Ship Shit Dev - Agent Workspace

You are working **on the library**, not in a project that uses it.

| Need to... | Look at... |
|------------|------------|
| Find tasks | GitHub Issues |
| Read repo decisions | `memory/memory.md` |
| Read standards | `memory/system/` |

```text
.agents/
├── README.md          # You are here
├── memory/            # Durable decisions, do-and-dont, standards
│   └── system/        # skill-standards.md, execution-boundary.md
└── sessions/          # Local-only session logs (gitignored)
```

## Adding a Skill

1. Create `skills/<name>/SKILL.md` with `disable-model-invocation: true`.
2. Run `bun run lint`, `bun run validate`, and `bun run test`.

Plans and implementation state live on GitHub issues and PRs, not in local files.
