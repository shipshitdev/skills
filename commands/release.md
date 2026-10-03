---
description: "Cut a release from a green trunk: prove checks, derive semver and notes, publish after you confirm."
argument-hint: "[gates|notes|cut [patch|minor|major|vX.Y.Z]]"
disable-model-invocation: true
---

# Release - Cut a Release From a Green Trunk

One command from "is master green?" to a published, deployed release. Trunk-based:
releases are cut from the default branch; staging and production are deployment
environments driven by CI/CD and tags, not branch promotions.

## Usage

```bash
/release                     # status: trunk SHA, check verdict, latest tag, release mode
/release gates               # wait until the trunk SHA's checks conclude; report the verdict
/release notes               # next version + patch notes only — cut nothing
/release cut                 # infer the next semver, preview, then publish after confirmation
/release cut patch|minor|major|vX.Y.Z   # force the bump or version
```

`/release help` prints this Usage block and stops without running anything.

Branch and worktree pruning is not a release step — that's `/cleanup`.

## Workflow

Use the `release` skill. It detects the trunk and the repo's release mechanism
(release-please PR, guarded `workflow_dispatch` release workflow, or annotated
tag), proves the checks for the exact trunk SHA, and publishes only through that
mechanism after you confirm the plan. It then reports deploy evidence for the
released SHA.

- Unknown argument → print Usage, don't guess.
- Never tags a moved trunk, reuses a tag, force-pushes, or bypasses a guarded
  release workflow with a local tag.
