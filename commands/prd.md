# Prd - Prepare Work for Agents

Use `/prd prepare <request>` to turn a rough request into an execution-ready issue
with settled requirements, an implementation plan, and a blocking readiness check.
Preparation finishes before implementation begins.

## Usage

```text
/prd prepare <request>  # prepare the complete issue and implementation contract
/prd intake <request>   # the same preparation with stakeholder/board context
/prd write <request>    # requirements only; not execution-ready
/prd new <request>      # file settled work through the task-creation engine
/prd plan <issue>       # resolve implementation decisions on the same issue
/prd lint <issue>       # warning-only draft requirements lint
/prd gate <issue>       # check readiness; draft lint never authorizes execution
/prd spec <request>     # apply the shared specification and planning contract
/prd interview <topic>  # discover missing product requirements
/prd                   # read-only status and usage
```

## Workflow

Resolve `prd-dispatch` from the installed catalog and pass the selected mode,
request, target, existing authorization, and caller restrictions. The router
composes shared engines; this command defines no separate issue template.

Complete the feature end to end in one issue/PR by default. Internal API, UI, and
verification tasks do not count as finished features. Preparation settles all
product and engineering decisions. Executors escalate gaps to the planner instead
of inventing answers. Model and effort selection belong to the harness.
