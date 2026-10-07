# Coordinate all project sessions

Use `/orchestrate` in the session that should coordinate the project. It announces
itself to verified project sessions, requests acknowledgment and status reports,
then matches work to live issues and PRs. Manage the project through that one
session: it relays instructions, consolidates progress and brings human decisions
back with the source-session and issue context.

| Invocation | Behavior |
|---|---|
| `/orchestrate` | Enroll and coordinate existing authorized project work. |
| `/orchestrate status` | Read the roster, progress and blockers once. |
| `/orchestrate plan bugs first` | Audit and propose lanes without messages or writes. |
| `/orchestrate run finish the bugs` | Coordinate that goal through existing sessions. |
| `/orchestrate watch finish the bugs` | Coordinate now and arrange a thread heartbeat where supported. |
| `/orchestrate run <session references>` | Coordinate a selected subset. |

Enrolled sessions report unresolved questions instead of asking you separately.
The coordinator keeps a decision queue, merges equivalent questions, reuses prior
answers, and asks through the harness's structured question interface with clear
session/issue context. Your answer returns to every affected session. Questions
already pending during enrollment stay visible without being asked again.

The coordinator collects reports in workers' own chats through read-only result
controls. Direct replies are optional only with verified human authorization.
Enrollment preserves active work; announcement and acknowledgment are tracked
separately. Newly discovered project sessions join the same protocol.

Existing chats are reused by default; explicitly request fresh sessions or
subagents when needed. Each implementation surface has one owner. Done requires
current CI, merge and all required deployment/acceptance evidence. Project rules
on production, providers, costs and verification remain in effect.

Watch reuses a matching heartbeat on the coordinator and disables it at completion
or cancellation. Without a thread scheduler, the skill leaves a manual resume
checkpoint. Without cross-session discovery or messaging, it reports the gap and
returns briefs rather than claiming access to every chat. A limited recent-chat
inventory remains partial coverage.

Install the [orchestrate skill](../../skills/orchestrate/SKILL.md) through the
repository's supported installer. The same-named skill owns `/orchestrate`; no
duplicate command file or deprecated Codex prompt is required. Installation does
not enroll chats or schedule monitoring.

## Related workflows

[Pstack's Orchestrate playbook](../../skills/pstack/playbooks/orchestrate.md)
already supplies a standing coordinator, upward reporting, an inbox, durable human
gates and delivery receipts for large multi-PR programs. This session workflow
uses those organizational ideas with the harness's existing chat controls; it does
not require Pstack's runtime, stack management or worker fan-out.

Matt Pocock's [wayfinder](../../skills/wayfinder/SKILL.md) models decisions as shared
tracker tickets, and [handoff](../../skills/handoff/SKILL.md) carries state across
sessions. Those are useful complements; neither is the existing-session enrollment
and centralized question protocol defined here. `swarm` retains worker fan-out.
