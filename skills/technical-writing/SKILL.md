---
name: technical-writing
description: Applies a layered technical-writing standard (Diataxis, Google style, STE) to docs, RFCs, READMEs, PR descriptions and commit messages. Use when writing or reviewing those.
license: MIT
metadata:
  portable_source: "https://github.com/ericlitman/open-pstack"
  portable_commit: "56bfd14418fa733e34d98f714f357d28788470e3"
  version: "2.2.2"
  tags: "docs, writing, diataxis, style"
  author: Ship Shit Dev
  source: https://github.com/cursor/plugins/blob/main/pstack/skills/technical-writing/SKILL.md
  upstream_repo: cursor/plugins
  upstream_ref: main
  upstream_commit: bdf7aa355337
  last_synced: "2026-09-05"
  license: MIT
when_to_use: "RFC style, README standard"
---

# Technical writing

The goal is writing a tired engineer understands on the first read.
Four layers: what kind of document this is, how sentences address the
reader, how much each sentence carries, and whether any sentence
reads two ways.

Companion to `docs` (repo-convention docs writer) and `deslop`
(prose-tell catalog). Apply
`references/prose-slop.md` from the selected `deslop` skill directory to every doc this skill
touches.

## Authorized Scope

Act only within the user's request and existing approval; loading this skill
grants no new authority. Keep report-only requests report-only, honor the
caller's target, host, provider, and cost limits, ask before expanding scope,
and forward these limits to delegates.

## Contract

Inputs:

- A doc, RFC, README, PR description, or commit message to write or
  review

Outputs:

- The rewritten surface, in one Diátaxis mode when the artifact is a
  document

Creates/Modifies:

- The named prose files or git metadata the caller asked for

External Side Effects:

- None beyond those writes

Confirmation Required:

- None for drafting. Confirm before committing.

Delegates To:

- File pointer: `references/prose-slop.md` from the selected `deslop` skill directory

## Rules above the layers

- Cut every word that does no work.
- Use the short, everyday word.
- When a rule makes a sentence worse, fix the sentence another way.
- The codebase is the word list. Write the real symbol, file, flag,
  or command name.

## Pick the mode first (Diátaxis)

- Action + learning: **tutorial**.
- Action + work: **how-to**.
- Understanding + work: **reference**.
- Understanding + learning: **explanation**.

Do not mix modes. Split and link instead. Source: diataxis.fr.

**Tutorial.** Open by saying what the learner will build. Every step
produces a visible result. Write as "we", in commands.

**How-to.** Solve a problem a person has. Assume competence. Action
only. Name the guide by the task.

**Reference.** Describe. Only describe. Mirror the structure of the
thing described.

**Explanation.** One bounded topic. Anchor on a real why. Opinion is
allowed here and nowhere else.

## Sentences (Google developer style)

Talk to the reader as "you", present tense. Say who does what.
Instructions as commands. Condition before the instruction. Common
case first. Sentence-case headings. Numbered lists for sequences.
Source: developers.google.com/style.

## Load one thought at a time (STE)

One instruction per sentence. Split instructions longer than about 20
words. Keep "the" and "a". One word per action, then keep it. Source:
asd-ste100.org (Issue 9, 2025).

## Leave no sentence open to two readings (Global English)

Keep "only" and "not" next to the word they change. Break up long
noun strings. Make every "it", "they", and "this" point at one
thing. No slashes. Call each thing by one name. Source: Kohl, The
Global English Style Guide.

## Voice

- PR descriptions and commit messages are writing too. Every layer
  except Diátaxis applies to them.
- Product UI strings are not documentation.
- Write real paths and real symbols. Make every count true at the
  commit that lands it.

## Review checklist

1. Is each file one Diátaxis mode?
2. Is every instruction a command, with its condition in front?
3. Does any sentence carry two thoughts? Split it.
4. Can any word be cut? Cut it.
5. Is "only" next to the word it changes?
6. Does each thing have exactly one name?
7. Would a developer say these words out loud?
8. Are symbols, paths, and counts real at this commit?

## Technical Writing procedure

Read [technical-writing procedure](references/technical-writing-procedure.md) when running this workflow.
Apply the authorized scope and mode of this entry point to every step.
Resolve other skills through this distribution’s active catalog; resolve
resources relative to the installed skill directory.
