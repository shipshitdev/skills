# Domain docs

> Seed for `docs/agents/domain.md`. Pick the layout that matches the repo, then
> delete the other section.

The domain glossary is the shared vocabulary the dev-loop skills read so PRDs,
issues, and code use the same terms for the same concepts. `CONTEXT.md` is a
**glossary and nothing else** — no specs, scratch notes, or implementation
details. Active sharpening (challenging terms, writing entries, recording ADRs)
is the upstream mattpocock/skills `domain-modeling` skill. Reading the glossary is a one-line habit any
skill can do.

## Single-context (default for a solo or single-product repo)

One `CONTEXT.md` at the repo root holds the living glossary:

- Canonical terms, each with a one- or two-sentence definition
- `_Avoid_` aliases so the same concept is not named three ways
- Relationships between terms, when they help disambiguate

Skills that resolve a term update `CONTEXT.md` inline.

## Multi-context (for a monorepo spanning several products or bounded contexts)

A `CONTEXT-MAP.md` at the root indexes one `CONTEXT.md` per context:

```text
CONTEXT-MAP.md            # index: which context owns what, and how they relate
packages/<a>/CONTEXT.md   # glossary for context A
packages/<b>/CONTEXT.md   # glossary for context B
```

`CONTEXT-MAP.md` records the relationships between contexts (shared kernel, upstream/
downstream, anti-corruption layers) so a change in one context's language does not
silently break another.

## Architecture decisions

When a choice is hard to reverse **and** surprising **and** carries a genuine
trade-off, record it under `docs/adr/` as a short ADR. Routine choices do not need
one — the three-gate filter keeps the ADR log signal-dense. Keep each ADR to
a few lines: context, decision, consequences.
