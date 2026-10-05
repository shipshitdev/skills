## Distribution boundary

Use the active Shipshit skill catalog and the caller's existing authorization.
The harness owns host, account, model, effort, sandbox, worktree and schedule.
Upstream examples describe mechanisms; they do not grant permission or select
providers. Preserve report-only scope. External messages, publication, installs,
deployment and destructive actions require authorization covering that action.
Read configuration from the harness source of truth; never replace its role map
with an example here. Use only capabilities the active harness actually exposes.

# Retro deep mode

Run three read-only reviewer lenses over one session record, then merge them with
a synthesizer. The merged list replaces retro's single-pass classification; the
parent then filters, presents and applies through retro's own steps.

**Dispatch contract.** Resolve every configured role through `provider-dispatch.md` (resolve the `pstack` skill through the active catalog). Reviewers need the parent's live MCP surface, so the default and supported portable route is `inherit-parent` (or its `auto` alias). Pass the transcript or digest plus any required evidence paths. On Codex, resolve remaining Claude tool names via `codex-tools.md` (resolve the `pstack` skill through the active catalog).

## 1. Hand over the record

Use the session record retro resolved in its first step. Pass reviewers the exact
record, an approved transcript path or a tightly scoped digest. If the full record
is unavailable, label that limitation and use the digest instead of claiming
transcript-backed verification.

## 2. Spawn three reviewers in parallel

Start all three read-only lanes in one fan-out phase through provider dispatch. Reviewers need MCP access for context lookups (tickets, chat threads, observability traces referenced in the transcript), so keep them native to the parent. The prompt forbids file writes; the parent applies edits.

| Lens | Model descriptor | Prompt template |
|---|---|---|
| Judgment | your configured reflect-judgment choice (default `inherit-parent`) | the judgment reviewer template |
| Tooling | your configured reflect-tooling choice (default `inherit-parent`) | the tooling reviewer template |
| Divergent | your configured reflect-judgment choice (default `inherit-parent`) | the divergent reviewer template |

Retro's Deep mode section links every template. Pass each template verbatim, substituting the transcript path or digest where marked. Reviewers return findings in the `Agent` response body.

## 3. Synthesize

Dispatch one lane using your configured reflect-judgment descriptor (default `inherit-parent`). Preserve relevant MCP access because the synthesizer spot-verifies citations. Use the synthesizer template verbatim, with each reviewer's full output inlined where marked. The synthesizer returns a structured Accepted / Rejected / Backlog list.

## 4. Map into retro

Convert the synthesizer output into retro candidates:

- Each Accepted row becomes a candidate: a skill body edit, description tune or
  new skill is **Skill**; an `environment:` row takes the category it names.
- Each Backlog row (a lint rule, script, metadata flag or runtime check would
  enforce it) becomes a **Guardrail** candidate.
- Each Rejected row goes to retro's dropped list with its reason.

Done when every synthesizer row is a candidate or a dropped line. Continue with
retro's filter, present and apply steps; creating tracker issues still needs the
user's request.
