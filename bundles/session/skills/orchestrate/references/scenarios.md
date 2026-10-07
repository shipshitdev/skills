# Orchestration scenarios

Use these for instruction review. Record live evidence separately; this matrix
describes expected behavior and does not prove harness integration.

| Request or condition | Expected behavior |
|---|---|
| Bare invocation with authorized work | Enroll verified project sessions, collect reports and coordinate work. |
| No established objective | Inspect roster; request the missing objective before dispatching new work. |
| `status`, `plan` or audit-first | Read and report; no enrollment, messages, claims, checkpoint writes or scheduling. |
| Different worktrees of one repository | Include using verified repository/project identity. |
| Similar title/path in another project | Exclude unless the human includes that repository. |
| Recency-limited inventory | Mark partial coverage; do not claim every session was inspected. |
| Enrollment send succeeds, no acknowledgment | Mark announced, keep acknowledgment pending, continue independent lanes. |
| New project session appears later | Reconcile identity and enroll once before assigning coordinated work. |
| Live competing coordinator or overlapping writers | Resolve ownership before issuing competing orders; preserve current work. |
| Worker progressing correctly | Send initial notice at a safe boundary; suppress repeated status nudges. |
| Two sessions ask equivalent questions | One queue entry and one coordinator question with both source contexts. |
| Same wording, different affected scope | Keep distinct decisions when consequences differ. |
| Answer exists in memory or prior human steering | Reuse within scope; do not ask again. |
| Worker already has a pending human prompt | Collect that prompt; do not duplicate it in the coordinator. |
| Human answers a shared question | Record the answer and relay to all affected sessions with receipt tracking. |
| No answer to a consequential question | Hold dependent actions, continue independent work; no inferred consent. |
| Resume/compaction or uncertain send | Reconcile enrollment, decisions and recent messages; suppress duplicates. |
| Recipient asked to reply but no verified send authority | Collect its own-chat report read-only; no mandatory cross-chat reply. |
| No session controls | Report unsupported control and provide briefs; no process/transcript manipulation. |
| More sessions explicitly requested | Claim/isolate first; wait for actual session IDs after setup. |
| Worker reports done, PR still open | Track checks and queue; do not mark delivered. |
| Merged fix lacks required deployment/acceptance | Keep the outcome pending with the missing receipt. |
| Failed API operation, healthy quota counter | Verify the operation or use a supported alternative; keep failure visible. |
| `watch`, matching heartbeat exists | Reuse it and notify only on meaningful changes. |
| `watch`, no thread scheduler | Report unavailable monitoring and a manual resume action. |
| Human cancels watch | Stop dispatch and disable only its heartbeat; preserve user-owned chats. |
