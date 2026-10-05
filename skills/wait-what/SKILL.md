---
name: wait-what
description: Re-pitch the last message in plain English using the project's glossary vocabulary.
disable-model-invocation: true
license: MIT
metadata:
  version: "2.2.2"
  tags: "clarification, communication, context, glossary"
  author: Ship Shit Dev
  source: https://github.com/mattpocock/skills/blob/main/skills/productivity/wait-what/SKILL.md
  upstream_repo: mattpocock/skills
  upstream_ref: main
  upstream_commit: 4588b32ecab9
  last_synced: "2026-10-05"
  license: MIT
when_to_use: "wait what, wait-what, I don't follow, say that again, re-pitch that, that didn't land"
---

# Wait What

The last message did not land. Re-pitch it.

## Contract

Inputs:

- The immediately preceding assistant message (and enough surrounding turn context to know what it was trying to say)
- The repo's glossary when present: `CONTEXT.md` / `CONTEXT-MAP.md`, or `GLOSSARY.md` / `GLOSSARY-MAP.md`

Outputs:

- A short re-pitch of the same point: missing context filled in, jargon decoded, same conclusion

Creates/Modifies:

- None

External Side Effects:

- None

Confirmation Required:

- None. Advisory only.

Delegates To:

- `domain-modeling` only when the confusion is a glossary conflict that should be written down

## Re-pitch

1. Name the point that failed to land, in one sentence.
2. Add the missing context — the decision, constraint, or prior turn the user did not have.
3. Speak in plain English. Prefer Simplified Technical English: short sentences, one idea each, no filler.
4. Use the ubiquitous language from the glossary when one exists. In a repo with a map file, follow the map to the glossary of the context the message concerns. If a term in the last message is not in the glossary, say the plain-English meaning first, then the canonical term.
5. End with the same ask or conclusion as the original message, restated.

Do not restart the parent skill. Do not expand scope. This is a mid-conversation corrective; after the re-pitch, the parent flow continues.
