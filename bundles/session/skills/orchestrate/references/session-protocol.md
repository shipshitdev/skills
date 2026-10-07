# Session protocol

Send this notice once per recipient and coordinator/scope. Substitute real IDs,
links and authorization; do not invent access, ownership or a human instruction.

```text
Project coordination: <project/repository identity>
Coordinator: <actual session title, ID/link>
Goal and scope: <authorized objective and included repositories/sessions>
Human authorization: <pointer to the human's orchestration request>
Restrictions: <project, verification, delivery, production and cost limits>

The human will manage this scope through the coordinator. Preserve the current
task and report at the next safe boundary; do not cancel the current turn.
Acknowledge this coordinator and provide the report below in this chat so the
coordinator can collect it. Direct replies require verified human send authority.
Route unresolved human decisions through the coordinator instead of asking the
human here. Hold the dependent action and continue independent authorized work.
Include any question already awaiting the human, so it is not asked twice.
Apply relayed human decisions within their stated scope. Report delivery evidence
and new blockers at meaningful boundaries. Do not start unrelated work.
```

Request this report without demanding another reporting tool or another chat:

```text
ENROLLMENT   acknowledged coordinator <ID> / conflict / unsupported
SESSION      <actual ID/link and title>
TASK         <goal, repository and issue/PR links>
OWNERSHIP    <surface, checkout, branch and current head>
STATE        running / awaiting-input / idle / completed / blocked
DELIVERY     implementation, review, CI, queue, merge, deployment, acceptance
EVIDENCE     <fresh receipt links or commands; unknowns explicitly marked>
NEXT         <next action and dependencies>
QUESTIONS    <none, or decision packets below>
```

Decision packet:

```text
SUBJECT      <decision subject and affected scope>
SOURCE       <session title/ID, issue/PR and relevant evidence>
QUESTION     <the missing human decision>
OPTIONS      <recommended option first, with consequences>
BLOCKED      <dependent action awaiting the answer>
CONTINUE     <independent authorized work>
PRIOR        <known answer or pending prompt, including its source>
```

Decision relay:

```text
DECISION     <stable queue key, subject and affected scope>
ANSWER       <actual human answer and source; distinguish assumptions>
APPLIES TO   <affected sessions/issues>
NEXT         <action now authorized; remaining restrictions>
RECEIPT      <acknowledge in this chat at the next safe boundary>
```

Collect own-chat reports with read-only status and result controls. Carry cursors
and merge equivalent decision packets into one queue entry. No mandatory worker
return message: a coordinator instruction alone does not authorize sending one.
