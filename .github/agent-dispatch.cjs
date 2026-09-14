const { execFileSync } = require('node:child_process');
const { createHash } = require('node:crypto');
const { readFileSync, writeFileSync, appendFileSync, existsSync } = require('node:fs');
const { join } = require('node:path');

function fail(message) {
  throw new Error(message);
}
function gh(args, input) {
  return execFileSync('gh', args, { encoding: 'utf8', input, stdio: ['pipe', 'pipe', 'pipe'] });
}
function api(path, body, method) {
  return JSON.parse(
    gh(
      ['api', path, ...(body ? ['--method', method || 'POST', '--input', '-'] : [])],
      body ? JSON.stringify(body) : undefined
    )
  );
}
function parseBoard(text) {
  const config = {};
  for (const raw of text.split('\n')) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    const match = line.match(/^([A-Z_]+)=([A-Za-z0-9_-]*)$/);
    if (!match)
      fail('Invalid board configuration; expected unquoted identifiers, never shell commands.');
    config[match[1]] = match[2];
  }
  for (const key of [
    'PROJECT_OWNER',
    'PROJECT_NUMBER',
    'PROJECT_NODE_ID',
    'STATUS_FIELD_ID',
    'STATUS_BACKLOG_OPTION_ID',
    'STATUS_IN_PROGRESS_OPTION_ID',
    'STATUS_HUMAN_REVIEW_OPTION_ID',
  ]) {
    if (!config[key]) fail(`Missing board configuration: ${key}`);
  }
  return config;
}
function validateEligibility({ permission, issue, lane, item }) {
  if (!['admin', 'maintain', 'write'].includes(permission))
    fail('Dispatch requires a current repository maintainer with write permission.');
  if (issue.state !== 'open' || issue.pull_request) fail('Dispatch requires an open issue.');
  const labels = issue.labels.map((label) => (typeof label === 'string' ? label : label.name));
  const gates = labels.filter((label) => label.startsWith('dispatch:'));
  if (gates.length !== 1 || gates[0] !== `dispatch:${lane}`)
    fail('Exactly one current dispatch gate must match this lane.');
  if (labels.includes('claim:active'))
    fail('Issue already has an active claim; release or recover it explicitly.');
  if (!item || item.content.url !== issue.html_url || item.status !== 'Backlog') {
    fail('Issue must be in this repository’s configured board Backlog.');
  }
}
function validateRuntime(env) {
  for (const name of ['MODEL_ID', 'MODEL_EFFORT', 'MODEL_PROVIDER', 'GH_TOKEN', 'MODEL_API_KEY']) {
    if (!env[name]?.trim())
      fail(`Missing explicit runtime configuration: ${name}. No fallback selected.`);
  }
  if (!/^[A-Za-z0-9_.:/-]+$/.test(env.MODEL_ID) || /(^|\/)(auto|free)$/.test(env.MODEL_ID))
    fail('Choose an explicit model, not automatic routing.');
  // Transport syntax only: individual model capability still requires a real run.
  const effortByLane = {
    plan: ['none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max'],
    codex: ['none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max'],
    openrouter: ['none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max'],
    claude: ['low', 'medium', 'high', 'xhigh', 'max', 'ultracode'],
  };
  if (!effortByLane[env.DISPATCH_LANE]?.includes(env.MODEL_EFFORT))
    fail(`Unsupported configured effort for ${env.DISPATCH_LANE || 'unknown lane'}.`);
  if (!/^[a-z0-9-]+$/.test(env.MODEL_PROVIDER) || env.MODEL_PROVIDER === 'openrouter')
    fail('Declare the actual implementation model provider, not its transport.');
  if (env.DISPATCH_LANE === 'openrouter' && env.MODEL_ID.split('/')[0] !== env.MODEL_PROVIDER)
    fail('OpenRouter model namespace must match the declared provider.');
}
function validateActors(actor, triggeringActor, permissionFor) {
  if (!['admin', 'maintain', 'write'].includes(permissionFor(actor))) {
    fail('Dispatch requires a current repository maintainer with write permission.');
  }
  if (
    triggeringActor &&
    triggeringActor !== actor &&
    !['admin', 'maintain', 'write'].includes(permissionFor(triggeringActor))
  ) {
    fail('Untrusted workflow rerun actor.');
  }
}
function selectTrustedPlan(issue, issueComments, permissionFor) {
  const pointers = [...(issue.body || '').matchAll(/^Current plan: (https:\/\/\S+)\s*$/gm)];
  if (pointers.length !== 1) fail('Exactly one Current plan URL is required in the issue body.');
  const plan = issueComments.find((comment) => comment.html_url === pointers[0][1]);
  if (!plan || !plan.html_url.startsWith(`${issue.html_url}#issuecomment-`)) {
    fail('Current plan must point to a comment on this issue.');
  }
  const actionsApp =
    plan.user.login === 'github-actions[bot]' &&
    plan.performed_via_github_app?.slug === 'github-actions';
  if (!actionsApp && !['admin', 'maintain', 'write'].includes(permissionFor(plan.user.login))) {
    fail('Current plan author is not a trusted repository writer.');
  }
  return plan;
}
function finalizationDecision(state, issue, issueComments, outcome) {
  const claims = issueComments.filter((comment) => /^Claimed-By: /m.test(comment.body));
  const latest = claims.reduce(
    (current, comment) => (!current || Number(comment.id) > Number(current.id) ? comment : current),
    null
  );
  const labels = issue.labels.map((label) => (typeof label === 'string' ? label : label.name));
  if (
    !state.claimCommentId ||
    latest?.id !== state.claimCommentId ||
    !latest.body.split('\n').includes(`Claim-Run: ${state.runId}:${state.runAttempt}`) ||
    !labels.includes('claim:active')
  ) {
    return {
      mutate: false,
      status: 'blocked: claim ownership changed or was released; no issue state modified',
      removeLabels: [],
    };
  }
  const status =
    outcome !== 'success'
      ? 'blocked: dispatch failed or was skipped; inspect run evidence'
      : state.lane === 'plan'
        ? 'planning handoff: inspect plan readiness verdict'
        : 'implementation handoff: independent review and required CI remain pending';
  return {
    mutate: true,
    status,
    statusOptionId: state.board.STATUS_HUMAN_REVIEW_OPTION_ID,
    assignee: state.actor,
    removeLabels: labels.filter(
      (name) =>
        name === 'claim:active' ||
        name === `dispatch:${state.lane}` ||
        ['loop:planning', 'loop:executing', 'loop:testing', 'loop:shipping'].includes(name)
    ),
  };
}
function blockedSummary(reason) {
  return `## Dispatch blocked\n\n${reason}\n\nNo successful delivery is recorded. For a pre-claim failure, fix the reported prerequisite, then remove and re-apply the dispatch label. Pre-claim failures do not change the issue.\n`;
}
function validatePlan(comment, issue, sha) {
  const body = comment.body;
  if (!/^## Implementation Plan\r?\n/.test(body)) fail('Plan heading missing.');
  // The full semantic readiness gate still runs in the agent before any edit.
  const field = (name) => {
    const matches = [...body.matchAll(new RegExp(`^${name}: (.+)$`, 'gm'))];
    if (matches.length !== 1) fail(`Plan must declare exactly one ${name}.`);
    return matches[0][1].trim();
  };
  if (field('Readiness') !== 'READY') fail('Plan is not explicitly READY.');
  if (!/^[1-9][0-9]*$/.test(field('Plan revision')))
    fail('Plan revision must be a positive integer.');
  if (field('Base commit') !== sha) fail('Plan repository SHA is stale; return to planner.');
  const requirements = (issue.body || '')
    .replace(/\r\n/g, '\n')
    .split('\n')
    .filter((line) => !line.startsWith('Current plan: '))
    .join('\n')
    .trim();
  const fingerprint = createHash('sha256').update(requirements).digest('hex');
  if (field('Requirements SHA256') !== fingerprint)
    fail('Requirements changed since planning; return to planner.');
}
function resolveSkillRoot(lane, exists = existsSync) {
  const required = [
    'prd-quality-gate/SKILL.md',
    'prd-quality-gate/references/execution-readiness.md',
    ...(lane === 'plan'
      ? ['prd-writer/SKILL.md', 'writing-plans/SKILL.md']
      : ['executing-plans/SKILL.md', 'executing-plans/references/delivery-gate.md']),
  ];
  const root = ['.github/agent-skills', 'skills'].find((candidate) =>
    required.every((resource) => exists(join(candidate, resource)))
  );
  if (!root)
    fail(
      'Prepared workflow skill resources are missing; reinstall with setup-dev-loop.sh from the current skills release.'
    );
  return root;
}
function setStatus(board, itemId, optionId) {
  gh([
    'project',
    'item-edit',
    '--id',
    itemId,
    '--field-id',
    board.STATUS_FIELD_ID,
    '--project-id',
    board.PROJECT_NODE_ID,
    '--single-select-option-id',
    optionId,
  ]);
}
function permission(repo, login) {
  return api(`repos/${repo}/collaborators/${encodeURIComponent(login)}/permission`).permission;
}
function comments(repo, number) {
  return JSON.parse(
    gh(['api', '--paginate', '--slurp', `repos/${repo}/issues/${number}/comments?per_page=100`])
  ).flat();
}
function prepare(env) {
  validateRuntime(env);
  const event = JSON.parse(readFileSync(env.GITHUB_EVENT_PATH, 'utf8'));
  const repo = env.GITHUB_REPOSITORY;
  const number = event.issue.number;
  const lane = env.DISPATCH_LANE;
  if (!['plan', 'codex', 'claude', 'openrouter'].includes(lane)) fail('Unknown dispatch lane.');
  if (event.label.name !== `dispatch:${lane}`) fail('Event does not authorize this lane.');
  if (!existsSync('.github/agent-dispatch.md'))
    fail('Missing shared dispatch contract; reinstall workflows with setup-dev-loop.sh.');
  const skillRoot = resolveSkillRoot(lane);
  const board = parseBoard(readFileSync('.github/agent-loop.env', 'utf8'));
  const issue = api(`repos/${repo}/issues/${number}`);
  validateActors(env.GITHUB_ACTOR, env.GITHUB_TRIGGERING_ACTOR, (login) => permission(repo, login));
  const items = JSON.parse(
    gh([
      'project',
      'item-list',
      board.PROJECT_NUMBER,
      '--owner',
      board.PROJECT_OWNER,
      '--format',
      'json',
      '--limit',
      '1000',
    ])
  ).items;
  const matches = items.filter((item) => item.content?.url === issue.html_url);
  if (matches.length !== 1)
    fail('Expected one matching board item; missing or beyond query limit.');
  validateEligibility({ permission: 'write', issue, lane, item: matches[0] });
  if (lane !== 'plan') {
    const plan = selectTrustedPlan(issue, comments(repo, number), (login) =>
      permission(repo, login)
    );
    validatePlan(
      plan,
      issue,
      execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim()
    );
  }
  const state = {
    repo,
    number,
    lane,
    board,
    itemId: matches[0].id,
    actor: env.GITHUB_ACTOR,
    runId: env.GITHUB_RUN_ID,
    runAttempt: env.GITHUB_RUN_ATTEMPT || '1',
    claimCommentId: null,
  };
  if (lane !== 'plan') gh(['auth', 'setup-git']);
  // Publish the unique ownership marker before changing labels or board state.
  writeFileSync(join(env.RUNNER_TEMP, 'agent-dispatch-state.json'), JSON.stringify(state));
  const claim = api(`repos/${repo}/issues/${number}/comments`, {
    body: `Claimed-By: ${env.GITHUB_ACTOR}\nClaimed-At: ${new Date().toISOString()}\nClaim-Run: ${state.runId}:${state.runAttempt}\nRun: ${env.GITHUB_SERVER_URL}/${repo}/actions/runs/${state.runId}\nRole: ${lane === 'plan' ? 'planner' : 'executor'}\nProvider: ${env.MODEL_PROVIDER}\nModel: ${env.MODEL_ID}\nEffort: ${env.MODEL_EFFORT}`,
  });
  state.claimCommentId = claim.id;
  writeFileSync(join(env.RUNNER_TEMP, 'agent-dispatch-state.json'), JSON.stringify(state));
  api(`repos/${repo}/issues/${number}/labels`, {
    labels: ['claim:active', lane === 'plan' ? 'loop:planning' : 'loop:executing'],
  });
  setStatus(board, state.itemId, board.STATUS_IN_PROGRESS_OPTION_ID);
  const prompt = `Run the ${lane === 'plan' ? 'planning' : 'execution'} role for issue #${number} in ${repo}.\nRead and follow .github/agent-dispatch.md in full.\nResolve workflow skills from ${skillRoot}.\nThe workflow owns claim release and status handoff.\nRuntime provider: ${env.MODEL_PROVIDER}; model: ${env.MODEL_ID}; effort: ${env.MODEL_EFFORT}.\n`;
  writeFileSync(join(env.RUNNER_TEMP, 'agent-dispatch-prompt.md'), prompt);
  appendFileSync(env.GITHUB_OUTPUT, `ready=true\nskill-root=${skillRoot}\n`);
}
function finalize(env) {
  const path = join(env.RUNNER_TEMP, 'agent-dispatch-state.json');
  if (!existsSync(path)) return;
  const state = JSON.parse(readFileSync(path, 'utf8'));
  const issue = api(`repos/${state.repo}/issues/${state.number}`);
  const decision = finalizationDecision(
    state,
    issue,
    comments(state.repo, state.number),
    env.AGENT_OUTCOME
  );
  const status = decision.status;
  appendFileSync(
    env.GITHUB_STEP_SUMMARY,
    `## Dispatch handoff\n\n${status}. No merge or Done transition was performed.\n`
  );
  if (!decision.mutate) return;
  api(`repos/${state.repo}/issues/${state.number}/comments`, {
    body: `Delivery state: ${status}.\nThis workflow does not certify merge-ready or Done.\n${state.lane === 'plan' ? 'Return a READY issue to Backlog and apply one execution gate when authorized.' : 'Independent reviewer automation is not provisioned by this workflow. Block delivery until a different frontier provider reviews the exact PR head, findings are resolved, and required CI is green. Merge and required deployment evidence are still required for Done.'}`,
  });
  setStatus(state.board, state.itemId, decision.statusOptionId);
  for (const label of decision.removeLabels) {
    gh([
      'api',
      '--method',
      'DELETE',
      `repos/${state.repo}/issues/${state.number}/labels/${encodeURIComponent(label)}`,
    ]);
  }
  api(`repos/${state.repo}/issues/${state.number}/assignees`, { assignees: [decision.assignee] });
}
module.exports = {
  parseBoard,
  validateEligibility,
  validateRuntime,
  validatePlan,
  resolveSkillRoot,
  validateActors,
  selectTrustedPlan,
  finalizationDecision,
  blockedSummary,
};
if (require.main === module) {
  try {
    if (process.argv[2] === 'prepare') prepare(process.env);
    else if (process.argv[2] === 'finalize') finalize(process.env);
    else fail('Expected prepare or finalize.');
  } catch (error) {
    process.stderr.write(`Dispatch blocked: ${error.message}\n`);
    if (process.env.GITHUB_STEP_SUMMARY)
      appendFileSync(process.env.GITHUB_STEP_SUMMARY, blockedSummary(error.message));
    process.exitCode = 1;
  }
}
