const test = require('node:test');
const assert = require('node:assert/strict');
const { createHash } = require('node:crypto');
const {
  parseBoard,
  validateEligibility,
  validateRuntime,
  validatePlan,
} = require('./agent-dispatch.cjs');

const issue = {
  state: 'open',
  html_url: 'https://github.com/acme/app/issues/7',
  labels: [{ name: 'dispatch:codex' }],
  body: 'Ship the complete feature.',
};
const eligible = {
  permission: 'write',
  issue,
  lane: 'codex',
  item: { status: 'Backlog', content: { url: issue.html_url } },
};
const runtime = {
  MODEL_ID: 'approved-model',
  MODEL_EFFORT: 'medium',
  MODEL_PROVIDER: 'openai',
  GH_TOKEN: 'fixture',
  MODEL_API_KEY: 'fixture',
};
const sha = 'a'.repeat(40);
const digest = createHash('sha256').update(issue.body).digest('hex');
const plan = {
  body: `## Implementation Plan\nPlan revision: 1\nBase commit: ${sha}\nRequirements SHA256: ${digest}\nReadiness: READY\n`,
};

test('only a writer may dispatch an unclaimed Backlog issue with exactly one gate', () => {
  assert.doesNotThrow(() => validateEligibility(eligible));
  for (const permission of ['read', 'triage', 'none'])
    assert.throws(() => validateEligibility({ ...eligible, permission }), /write permission/);
  for (const labels of [
    [{ name: 'dispatch:codex' }, { name: 'dispatch:claude' }],
    [],
    [{ name: 'dispatch:plan' }],
  ]) {
    assert.throws(
      () => validateEligibility({ ...eligible, issue: { ...issue, labels } }),
      /Exactly one/
    );
  }
  assert.throws(
    () =>
      validateEligibility({
        ...eligible,
        issue: { ...issue, labels: [...issue.labels, { name: 'claim:active' }] },
      }),
    /active claim/
  );
  assert.throws(
    () => validateEligibility({ ...eligible, issue: { ...issue, state: 'closed' } }),
    /open issue/
  );
});

test('board eligibility is tied to issue URL and Backlog, never just issue number', () => {
  for (const item of [
    undefined,
    { ...eligible.item, status: 'Human Review' },
    { ...eligible.item, content: { url: 'https://github.com/other/repo/issues/7' } },
  ]) {
    assert.throws(() => validateEligibility({ ...eligible, item }), /Backlog/);
  }
});

test('missing role configuration and automatic model routing block without fallback', () => {
  assert.doesNotThrow(() => validateRuntime(runtime));
  for (const field of Object.keys(runtime))
    assert.throws(() => validateRuntime({ ...runtime, [field]: '' }), /Missing explicit/);
  for (const MODEL_ID of ['openrouter/auto', 'openrouter/free', 'model --extra-flag'])
    assert.throws(() => validateRuntime({ ...runtime, MODEL_ID }), /explicit model/);
  assert.throws(
    () => validateRuntime({ ...runtime, MODEL_PROVIDER: 'openrouter' }),
    /actual implementation/
  );
  assert.throws(
    () =>
      validateRuntime({
        ...runtime,
        DISPATCH_LANE: 'openrouter',
        MODEL_ID: 'anthropic/approved-model',
      }),
    /namespace/
  );
});

test('board configuration is data and never executable shell', () => {
  const board = [
    'PROJECT_OWNER=acme',
    'PROJECT_NUMBER=1',
    'PROJECT_NODE_ID=PVT_1',
    'STATUS_FIELD_ID=PVTSSF_1',
    'STATUS_BACKLOG_OPTION_ID=a',
    'STATUS_IN_PROGRESS_OPTION_ID=b',
    'STATUS_HUMAN_REVIEW_OPTION_ID=c',
  ].join('\n');
  assert.equal(parseBoard(board).PROJECT_OWNER, 'acme');
  assert.throws(() => parseBoard(`${board}\nEVIL=$(printenv)`), /Invalid board/);
  assert.throws(
    () => parseBoard(board.replace('PROJECT_OWNER=acme', 'PROJECT_OWNER=')),
    /Invalid board/
  );
});

test('plan freshness binds exact revision metadata, repository commit, and normalized requirements', () => {
  assert.doesNotThrow(() => validatePlan(plan, issue, sha));
  assert.doesNotThrow(() =>
    validatePlan(
      plan,
      {
        ...issue,
        body: `\r\n${issue.body}\r\nCurrent plan: https://github.com/acme/app/issues/7#issuecomment-1\r\n`,
      },
      sha
    )
  );
  assert.throws(() => validatePlan(plan, issue, 'b'.repeat(40)), /stale/);
  assert.throws(
    () => validatePlan(plan, { ...issue, body: `${issue.body}\nChange behavior.` }, sha),
    /Requirements changed/
  );
  assert.throws(
    () => validatePlan({ body: plan.body.replace('READY', 'BLOCKED') }, issue, sha),
    /not explicitly READY/
  );
  assert.throws(
    () => validatePlan({ body: `${plan.body}Readiness: BLOCKED\n` }, issue, sha),
    /exactly one Readiness/
  );
  assert.throws(
    () => validatePlan({ body: plan.body.replace('revision: 1', 'revision: 0') }, issue, sha),
    /positive integer/
  );
});
