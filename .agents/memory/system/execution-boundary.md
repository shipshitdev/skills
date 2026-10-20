# Harness-Owned Execution Boundary

Reusable agent content defines **what outcome to pursue and what constraints to
honor**. The harness or app defines **where, when, and with which execution lane it
runs**. This boundary applies to public skills, Claude command bodies, Claude
scheduled-task routines, and Codex automation prompt bodies.

## Normative split

| Harness or app owns | Reusable content owns |
|---|---|
| Model and reasoning/effort level | Objective and selection logic |
| Schedule, recurrence, and wake-up policy | Domain invariants and stop conditions |
| Project, current working directory, and workspace | Safety and confirmation gates |
| Worktree versus local/source checkout | Evidence and verification requirements |
| Approval mode, sandbox, and execution environment | Output and handoff contract |
| Authentication and account selection | Parameter names and safe defaults |

Do not copy app-owned values into a reusable prompt or frontmatter. A prompt may
**verify** a safety invariant supplied by the app—for example, stop if the current
repository is not the expected one—but it must not choose a checkout, model, effort
level, schedule, sandbox, or working directory.

## Artifact rules

### Public skills

- Omit `model` and `effort` from public skill frontmatter. Inherit the active session
  lane selected by the harness.
- Keep execution prerequisites in `compatibility`, but do not turn compatibility into
  app configuration. "Requires an authenticated GitHub CLI" is portable; "run in
  `/path/to/project` with model X" is not.
- Put mutation, external-message, and destructive-action gates in the body so every
  harness sees them. Platform-only invocation guards may add defense in depth, but
  never carry the only copy of a safety rule.

### Claude commands

- Treat commands as thin entry points that route to portable skills.
- Keep model, effort, project directory, and scheduling out of command bodies. Claude
  settings and the active session own them.
- A repo-specific command may name a stable domain concept or route, but paths and
  environment selection still come from the project/session context.

### Scheduled routines and automations

- Write one parameterized routine body per objective family. Bind its target through
  the app's project/cwd fields instead of cloning the body per repository.
- Keep the routine body limited to objective, scope selection, safety gates, evidence,
  and output. The schedule editor or automation configuration owns recurrence, model,
  effort, environment, target checkout, and cwd.
- Unattended does not mean unrestricted. Default to reporting. Require explicit policy
  in the routine body before writing files, sending external messages, merging,
  deploying, deleting, or performing another irreversible action.

## Portable routine example

Use the same routine body in both harnesses:

```text
Review dependency drift in the current repository. Report high-risk changes with
file-backed evidence. Do not modify files or open issues unless this routine instance
explicitly authorizes that write. Never merge, deploy, delete, or send an external
message without an explicit action-specific gate.
```

Configure the execution outside that body:

| Claude scheduled task | Codex automation |
|---|---|
| App selects project, schedule, session effort, and execution context | Automation fields select cwds/target, schedule, model, reasoning effort, and environment |
| Task `SKILL.md` contains the portable routine body | Automation prompt contains the same portable routine body |

These examples describe ownership only; they do not create a schedule or prescribe a
particular app configuration shape.

## Project-specific content

Project-specific content is legitimate when it is a durable **domain invariant**:
protected branch names, release policy, required evidence, or a known safety boundary.
Store those facts in the project's instruction or memory files and let the routine read
the current project context.

Do not bake machine paths, workspace IDs, account names, worktree selection, or
environment names into reusable content. If an objective truly needs a target name,
declare a semantic parameter such as `TARGET_REPOSITORY`; let the app bind it and use
the app-selected cwd as the execution location.

## Migration

To migrate existing duplicated prompts without creating or changing live schedules:

1. Inventory normalized routine bodies and group copies by objective.
2. Redact values; compare only field names and prompt structure.
3. Extract one portable body containing the objective, invariants, safety gates,
   evidence, and output contract.
4. Remove model, effort, schedule, cwd, workspace, environment, and checkout selection
   from the body.
5. Parameterize only genuine domain inputs; bind execution location through app fields.
6. Review each existing app configuration against the new body before manually
   replacing it. Do not create, enable, or reschedule anything during the audit.
7. Keep the old copies until each migrated instance has produced one expected report;
   then retire the duplicates.

## Review checklist

- [ ] No concrete model, tier, or effort selection in reusable content
- [ ] No recurrence or schedule text duplicated from the app
- [ ] No machine path, workspace ID, or checkout-selection instruction
- [ ] Objective and scope selection remain understandable without platform metadata
- [ ] Writes, external messages, and destructive actions have explicit gates
- [ ] Evidence and output contracts are deterministic
