# Questionnaire (send mode)

Turns a decision the user cannot answer alone into a Markdown **questionnaire**
for one recipient to fill in asynchronously, or to work through together in a
meeting. The recipient holds knowledge the user lacks; the document pulls it out.

Adapted from `to-questionnaire` in
[mattpocock/skills](https://github.com/mattpocock/skills) (MIT, commit
`4588b32ecab9`). Owned here; not a sync target.

## Grill the send, not the subject

The user can always answer questions about the *send*, so interview only on that,
one exchange each:

1. **Who gets it?** Role, expertise, relationship to the user. This fixes tone and
   how much context the document carries. Done when you know what the recipient
   knows that the user does not.
2. **What must come back?** The concrete decisions or facts the user needs to walk
   away able to act on. Done when that is a list.

Then write questions aimed at the **gap** between those two answers.

## Write the document

Most important question first: asynchronous means you may get one pass. Group under
`##` headings by theme once there are more than a handful. One idea per question,
never compound, with an answer stub beneath. Add a one-line "why this matters"
only where a question could be misread or invite a throwaway answer. Save to
`${CODEX_HOME:-$HOME/.codex}/artifacts/questionnaires/<slug>.md` (or a path the
user names) and report the absolute path.

```markdown
# <Questionnaire title>

**Purpose:** why this exists and the decision riding on it.
**From:** <user> **To:** <recipient> **Use of your answers:** <where they go>

## Context

One paragraph for a recipient who was not in the user's head: enough to answer
well, not a page.

## How to answer

Deadline and rough effort. Partial answers and "I don't know" are useful; flag
anything you are unsure of rather than skipping it.

## <Theme>

### <One question>

_Why this matters: <only when needed>_

>

## Anything else?

Anything we did not ask that we should know?
```

Done when the file exists and every item from the second exchange is covered by
a question.
