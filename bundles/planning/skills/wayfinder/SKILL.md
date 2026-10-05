---
name: wayfinder
description: Charts a foggy effort too big for one session as a map issue of decision tickets, then resolves one ticket per session until the way is clear. Plans only.
disable-model-invocation: true
license: MIT
metadata:
  version: "2.2.2"
  tags: "planning, decisions, map, multi-session, fog-of-war"
  author: Ship Shit Dev
  source: https://github.com/mattpocock/skills/blob/main/skills/engineering/wayfinder/SKILL.md
  upstream_repo: mattpocock/skills
  upstream_ref: main
  upstream_commit: 4588b32ecab9
  last_synced: "2026-10-05"
  license: MIT
when_to_use: "wayfinder, map this effort, too big for one session, foggy effort"
argument-hint: "[loose idea, or a map issue number or URL]"
---

# Wayfinder

An idea arrived too big for one session and wrapped in fog: the way to the
**destination** is not visible yet. Chart that way as a **map** on the issue
tracker, then resolve its **decision tickets** one session at a time until the
route is clear. The skill finds the way; it never walks it.

## Contract

Inputs:

- A loose idea (chart mode), or a map issue number or URL (work mode)
- The repo's tracker config (`docs/agents/issue-tracker.md`) when present

Outputs:

- Chart mode: a map issue and its first decision tickets
- Work mode: one resolved ticket, the map updated, and the next frontier named
- When the way is clear: a recommendation to run `/prd prepare` on the settled
  decisions

Creates/Modifies:

- GitHub issues: the map (label `wayfinder:map`), child tickets (label
  `wayfinder:<type>`), assignments, blocking links, resolution comments

External Side Effects:

- GitHub writes only. No code, no branches, except a throwaway `research/<name>`
  branch a research ticket may use

Confirmation Required:

- Before publishing the map and its tickets: show destination, tickets and fog
  first, and confirm when the repo is public
- Invoking work mode on a map authorizes the claim, resolution comment, close and
  map update for one ticket; creating, updating or deleting any other
  ticket needs separate approval

Delegates To:

- Run the `grilling` and `domain-modeling` skills for grilling tickets and for
  naming the destination
- Run the `research` skill for research tickets
- Run the `prototype` skill for prototype tickets
- Recommend `prd-dispatch` to turn the finished map into a feature issue
- Recommend `show-me-your-work` for a long unattended run across tickets

## Plan, don't do

Each ticket resolves a decision, and the map is done when nothing is left to
decide before someone goes and builds. The pull to just do the work marks the
edge of the map: hand off there. An effort may override this in its **Notes**.
Tickets are decisions, never build slices; the build is one feature issue that
`/prd prepare` writes from the settled map.

## The map

One issue labelled `wayfinder:map`; its tickets are child issues. The map is an
**index**: it gists each decision and links the ticket that holds the detail, so a
decision lives in exactly one place. Refer to every map and ticket by its title,
never a bare number; the link rides inside the name.

```markdown
## Destination

<what reaching the end looks like: the spec, decision or change; one or two lines>

## Notes

<domain, skills every session should consult, standing preferences>

## Decisions so far

- [<closed ticket title>](link): <one-line gist of the answer>

## Not yet specified

<fog: in-scope questions too dim to ticket yet>

## Out of scope

<work ruled beyond the destination, each with its reason; never graduates>
```

Open tickets stay out of the map: they are the open child issues, found by query.

Child links use the repo's native sub-issue API (see `prd-task-creator`'s
independently-complete-children guide for the REST calls). Blocking uses the
native blocked-by relationship so the tracker's own view shows the frontier; fall
back to a `Blocked by:` body line only when the tracker lacks it, and say so. A
ticket is **unblocked** when every blocker is closed. The **frontier** is the
open, unblocked, unclaimed tickets. A session **claims** a ticket by assigning it
to the driver before any work.

Each ticket body is one `## Question`, sized to one session. The answer is
recorded on resolution, not in the body.

## Ticket types

HITL tickets resolve only through a live exchange; the agent never answers its own
questions for the human.

| Type | Mode | Resolved by |
|---|---|---|
| `research` | AFK | the `research` skill, for facts outside the working directory |
| `prototype` | HITL | the `prototype` skill: a cheap artifact to react to, linked as an asset |
| `grilling` | HITL | `grilling` plus `domain-modeling`; the default |
| `task` | either | doing the manual step a decision waits on (sign up, provision, move data); the answer records what was done and what later tickets depend on |

## Fog of war

Chart only what you can see. **Not yet specified** holds the dim view: questions
you can tell are coming but cannot yet phrase sharply. The test is whether you can
state the question precisely now, not whether you can answer it now. Sharp but
blocked is a ticket. Too dim to phrase is fog; do not pre-slice it. Resolving a
ticket graduates the fog it cleared into new tickets.

Work beyond the destination is out of scope, not fog. Close a ticket that turns
out to sit past the destination and leave one line in **Out of scope**: the gist,
the reason, the link. Keep it out of **Decisions so far**.

## Chart mode

1. **Name the destination.** Run `grilling` and `domain-modeling` until the
   destination is one or two lines. It fixes the scope.
2. **Map the frontier.** Grill again breadth-first: the open decisions and the
   first takeable steps. When no fog appears and one session can hold the whole
   journey, stop and say no map is needed.
3. Show the plan: destination, tickets, fog. On confirmation, create the map,
   then the tickets, then wire blocking in a second pass (ids exist only after
   creation).
4. Start each new `research` ticket's resolution in a parallel subagent.

Done when the map and its first tickets exist and nothing was resolved by hand.

## Work mode

1. Load the map only, not every ticket.
2. Take the ticket the user named, else the first frontier ticket. Claim it.
3. Resolve it, fetching related tickets on demand and consulting the skills the
   map's Notes name.
4. Post the answer as a resolution comment, close the ticket, and append one line
   to **Decisions so far**.
5. List the follow-on changes the answer implies: fog that graduates into new
   tickets, anything past the destination ruled out of scope, and tickets the
   answer invalidates. Show the list and apply only what the user approves;
   closing or deleting another ticket always needs that approval.

Resolve at most one ticket per session. A batch of research tickets counts as one
when the user approves the batch up front. Other sessions edit the tracker
concurrently, so re-read before each write.

Done when the ticket is closed, the map shows its gist, and the next frontier is
named. When no tickets and no fog remain, the way is clear: recommend
`/prd prepare` on the settled decisions.
