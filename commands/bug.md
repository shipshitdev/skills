# Bug - File a GitHub Bug Issue

Turn a description of something broken into a GitHub issue of type **Bug**.
Drafts a structured report, previews it, and files it only after you confirm —
typed `Bug` where the repo supports issue types, otherwise labelled `bug`.

## Usage

```bash
/bug <description>   # draft a bug report from the description, preview, then file (default)
/bug                 # draft from the current context / recent error, preview, then file
/bug draft <desc>    # draft and print the report only — create nothing
```

## Workflow

Use the `bug` skill.

1. Detect the repo (from the current remote) and whether it supports a `Bug` issue
   type or needs the `bug` label fallback. Stop if issues are disabled.
2. Draft a structured report — title, summary, steps to reproduce, expected vs
   actual, environment. Unknowns are marked, never invented. Pasted errors/stack
   traces are quoted verbatim.
3. Print the drafted issue and wait for explicit confirmation.
4. Create the issue with `--type Bug` (or `--label bug` fallback), applying only the
   labels/assignee/milestone you named, and return the issue URL.

## Gates

- Never open the issue without explicit confirmation.
- Never fabricate reproduction steps, versions, or behavior — mark gaps as not provided.
- Files bugs only; for feature requests or tasks, use the matching issue type.
- To root-cause before filing, use `debug` — it escalates to its four-phase loop
  itself once a fix attempt has failed; for a failing CI check, use `github-fix-ci`.
