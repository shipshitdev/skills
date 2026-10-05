# Make it yours

pstack is one person's style. The machinery underneath, playbooks, routing, model roles, works just as well wearing yours. This page covers generating a personal mode, capturing lessons from a session, authoring a focused skill, and testing a skill change before you trust it.

## Generate a personal mode through Pstack

```text
/pstack capture my working conventions as a personal mode
```

You don't describe your style, because [`/pstack capture my working conventions as a personal mode`](../../../../SKILL.md) reads it out of your history. It mines your recent transcripts in the active workspace for repeated preferences, in how you like replies, delegation, verification, code, prose, and process, then asks you which patterns are really you. It uses canonical `skill-creator` to draft a real `SKILL.md` in the active harness's selected skill root, runs the draft through `/deslop prose` (resolve the `deslop` skill through the active catalog), and opens a PR from a worktree so you review it like any other change.

Run it again whenever your habits drift:

```text
/pstack update my mode skill with everything since its last edit
```

Update mode mines only the history since the skill last changed. It keeps rules you haven't contradicted, revises the ones with new evidence, and adds sections only for genuinely new patterns.

## Capture a session's lessons with `/retro --deep`

Right after a task that taught you something, run:

```text
/retro --deep that took way too long. capture what we learned so the next run doesn't repeat it.
```

`/retro --deep` (resolve the `retro` skill through the active catalog) sends the transcript to three parallel reviewers, then a synthesizer sorts the proposals into `Accepted`, `Rejected`, and `Backlog`. Retro presents them as ranked candidates and applies only the ones you pick. Keep a proposal only if it would change a future decision. One weird session is an anecdote, not a rule.

## Author a focused skill

When you already know the workflow you want to capture:

```text
/pstack write a skill for verifying database migrations in this repo
```

Writing a skill matches the [Authoring or modifying a skill playbook](../../../../playbooks/authoring-a-skill.md), which routes through canonical `skill-creator`, validates the frontmatter and links, and ships the result through the Opening a PR playbook. Agent-facing prose has a higher bar than human prose, because an unhelpful sentence becomes an instruction some future agent follows. Let the playbook hold that bar rather than writing an unvalidated `SKILL.md`.

One special case has its own generator. A skill that must drive your app and prove behavior is a verification skill, so use `/create-verification-skill` (resolve the `create-verification-skill` skill through the active catalog) and `/maintain-verification-skill` (resolve the `maintain-verification-skill` skill through the active catalog) instead. [Verify and ship](06-verify-and-ship.md#create-a-project-verification-skill) covers both.

## Write docs to a standard with `/technical-writing`

Skills aren't the only prose you ship. For docs, RFCs, readmes, PR descriptions, and commit messages:

```text
/technical-writing review the readme changes
```

`/technical-writing` (resolve the `technical-writing` skill through the active catalog) applies a layered standard with one goal, prose a tired engineer understands on the first read. It picks the document's mode first (tutorial, how-to, reference, or explanation), then works sentence by sentence: who does what, one thought per sentence, nothing readable two ways. Use it to review what you or an agent just wrote, or name it up front when you ask for a doc.

## Test a skill change blind

A skill edit affects every future session, so test it like the experiment it is:

```text
/pstack run the eval playbook on this skill change. same task for both variants, candidates stay blind.
```

The [Eval playbook](../../../../playbooks/eval.md) is built around one failure mode, the observer effect. An agent that knows it's being evaluated behaves differently. So candidate agents get an organic-looking task in sanitized directories, never the words "eval" or "candidate", and never each other's existence. One judge scores all outputs under neutral labels, and chain-following gets graded from which files each candidate actually read, not from what it claims.

Read every output yourself before accepting the verdict. If you disagree with the judge, suspect the rubric before you suspect your judgment.

**Pitfall:** don't edit a skill mid-task because it's misbehaving. Fix it in its own PR and keep the task moving. A skill edit that ships tangled into feature work is invisible to review and impossible to evaluate.

Next: [Recipes and pitfalls](10-recipes-and-pitfalls.md).
