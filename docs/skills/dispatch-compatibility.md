# Dispatch Compatibility Evidence

Checked 2026-09-14 while addressing independent review of PR #149. These checks
establish CLI/action interfaces, not live account entitlement or model availability.
A failed live invocation remains blocked and never becomes a successful delivery.

## Pinned Action Inputs

The [pinned Codex action manifest](https://github.com/openai/codex-action/blob/e0fdf01220eb9a88167c4898839d273e3f2609d1/action.yml)
defines `prompt-file`, `codex-args`, `effort`, and `responses-api-endpoint`. Its
proxy forwards to that explicit endpoint. Use this supported override rather than
a custom-provider configuration that the action's proxy setup can replace.

The [pinned Claude action manifest](https://github.com/anthropics/claude-code-action/blob/9dd8b95a392eb34b6f5fb56cf5a64cb735912d4b/action.yml)
accepts `claude_args`. The [official Claude CLI reference](https://code.claude.com/docs/en/cli-reference)
documents `--effort`, including `xhigh` and `max`; installed CLI help also confirms
those flags without a model call. A review claim that Claude lacks `--effort` or
rejects `xhigh` is outdated. Individual model support remains model-dependent.

## Optional OpenRouter Transport

[OpenRouter's Responses API reference](https://openrouter.ai/docs/api/api-reference/responses/create-responses)
documents `https://openrouter.ai/api/v1/responses` and reasoning configuration.
[Its reasoning guide](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens)
describes provider-dependent effort support. Select an explicit model and actual
lab; the transport name does not establish independent review.

No live paid OpenRouter dispatch was run for this repair. This optional lane stays
unconfigured until the operator supplies its model, effort, provider, and account.
A public API interface is not evidence that every model supports every effort or
that a particular account is entitled to it. No silent fallback is authorized.

## Verification Boundaries

Focused regressions exercise metadata freshness, trust decisions, claim ownership,
missing configuration, and delivery-state rejection. Required PR CI covers the
repository checks. Actual model execution, reviewer authenticity, project access,
and deployment evidence must be observed in each configured consumer workflow.
Static tests cannot certify a live provider session or a self-reported PASS.
