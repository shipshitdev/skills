const test = require('node:test');
const assert = require('node:assert/strict');
const { createHash } = require('node:crypto');
const {
  parseBoard,
  validateEligibility,
  validateRuntime,
  validatePlan,
  resolveSkillRoot,
  validateActors,
  selectTrustedPlan,
  finalizationDecision,
  blockedSummary,
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
  DISPATCH_LANE: 'codex',
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
  for (const field of Object.keys(runtime).filter((name) => name !== 'DISPATCH_LANE'))
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
    /Missing board configuration: PROJECT_OWNER/
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

test('consumer workflow resolves complete packaged resources and fails closed if absent', () => {
  assert.equal(
    resolveSkillRoot('plan', (path) => path.startsWith('.github/agent-skills/')),
    '.github/agent-skills'
  );
  assert.equal(
    resolveSkillRoot('codex', (path) => path.startsWith('skills/')),
    'skills'
  );
  assert.throws(
    () => resolveSkillRoot('codex', (path) => !path.endsWith('delivery-gate.md')),
    /resources are missing/
  );
  assert.throws(() => resolveSkillRoot('plan', () => false), /resources are missing/);
});

test('effort validation follows transport capabilities without rejecting supported high efforts', () => {
  for (const MODEL_EFFORT of ['none', 'minimal', 'max'])
    assert.doesNotThrow(() => validateRuntime({ ...runtime, MODEL_EFFORT }));
  for (const MODEL_EFFORT of ['xhigh', 'max', 'ultracode'])
    assert.doesNotThrow(() =>
      validateRuntime({
        ...runtime,
        DISPATCH_LANE: 'claude',
        MODEL_EFFORT,
        MODEL_PROVIDER: 'anthropic',
      })
    );
  for (const [DISPATCH_LANE, MODEL_EFFORT] of [
    ['codex', 'ultracode'],
    ['claude', 'none'],
    ['plan', 'banana'],
    ['unknown', 'medium'],
  ]) {
    assert.throws(
      () => validateRuntime({ ...runtime, DISPATCH_LANE, MODEL_EFFORT }),
      /Unsupported configured effort/
    );
  }
});

test('original gate actor and a distinct rerun actor both require write permission', () => {
  const permissions = (login) => ({ writer: 'write', admin: 'admin', stranger: 'read' })[login];
  assert.doesNotThrow(() => validateActors('writer', 'admin', permissions));
  assert.doesNotThrow(() => validateActors('writer', 'writer', permissions));
  assert.throws(() => validateActors('stranger', 'admin', permissions), /write permission/);
  assert.throws(() => validateActors('writer', 'stranger', permissions), /rerun actor/);
});

test('authoritative plan pointer must resolve on this issue and to a trusted writer or Actions app', () => {
  const url = `${issue.html_url}#issuecomment-1`;
  const prepared = { ...issue, body: `${issue.body}\nCurrent plan: ${url}` };
  const comment = { ...plan, html_url: url, user: { login: 'writer' } };
  const permissions = (login) => (login === 'writer' ? 'write' : 'read');
  assert.equal(selectTrustedPlan(prepared, [comment], permissions), comment);
  assert.throws(() => selectTrustedPlan(prepared, [], permissions), /this issue/);
  assert.throws(
    () => selectTrustedPlan(prepared, [{ ...comment, user: { login: 'stranger' } }], permissions),
    /trusted repository writer/
  );
  const bot = {
    ...comment,
    user: { login: 'github-actions[bot]' },
    performed_via_github_app: { slug: 'github-actions' },
  };
  assert.equal(selectTrustedPlan(prepared, [bot], permissions), bot);
  assert.throws(
    () =>
      selectTrustedPlan(
        prepared,
        [{ ...bot, performed_via_github_app: { slug: 'other-app' } }],
        permissions
      ),
    /trusted repository writer/
  );
  const foreign = { ...comment, html_url: 'https://github.com/other/repo/issues/7#issuecomment-1' };
  assert.throws(
    () =>
      selectTrustedPlan(
        { ...prepared, body: `Current plan: ${foreign.html_url}` },
        [foreign],
        permissions
      ),
    /this issue/
  );
  assert.throws(
    () =>
      selectTrustedPlan(
        { ...prepared, body: `${prepared.body}\nCurrent plan: ${url}` },
        [comment],
        permissions
      ),
    /Exactly one/
  );
});

const claimedIssue = {
  ...issue,
  labels: [
    'claim:active',
    'dispatch:codex',
    'loop:testing',
    'priority:high',
    'dispatch:claude',
    'loop:custom',
  ],
};
const claimState = {
  runId: '42',
  runAttempt: '1',
  claimCommentId: 11,
  lane: 'codex',
  actor: 'writer',
  board: { STATUS_HUMAN_REVIEW_OPTION_ID: 'review-id' },
};
const ownedClaim = { id: 11, body: 'Claimed-By: writer\nClaim-Run: 42:1' };

test('finalizer returns explicit handoff transitions for success, failure and skipped work', () => {
  for (const outcome of ['success', 'failure', 'skipped']) {
    const decision = finalizationDecision(claimState, claimedIssue, [ownedClaim], outcome);
    assert.equal(decision.mutate, true);
    assert.equal(decision.statusOptionId, 'review-id');
    assert.equal(decision.assignee, 'writer');
    assert.deepEqual(decision.removeLabels, ['claim:active', 'dispatch:codex', 'loop:testing']);
    assert.match(
      decision.status,
      outcome === 'success' ? /review and required CI remain pending/ : /blocked/
    );
  }
  assert.match(
    finalizationDecision({ ...claimState, lane: 'plan' }, claimedIssue, [ownedClaim], 'success')
      .status,
    /plan readiness/
  );
});

test('finalizer preserves all issue state when the claim was replaced, edited, or released', () => {
  for (const comments of [
    [],
    [{ ...ownedClaim, body: 'Claimed-By: writer\nClaim-Run: 42:2' }],
    [ownedClaim, { id: 12, body: 'Claimed-By: another-run' }],
  ]) {
    const decision = finalizationDecision(claimState, claimedIssue, comments, 'success');
    assert.equal(decision.mutate, false);
    assert.deepEqual(decision.removeLabels, []);
    assert.equal(decision.assignee, undefined);
    assert.equal(decision.statusOptionId, undefined);
  }
  assert.equal(finalizationDecision(claimState, issue, [ownedClaim], 'failure').mutate, false);
  assert.equal(
    finalizationDecision(
      { ...claimState, claimCommentId: null },
      claimedIssue,
      [ownedClaim],
      'failure'
    ).mutate,
    false
  );
});

test('pre-claim failure summary explains the reason and safe re-dispatch without issue writes', () => {
  const summary = blockedSummary('Plan repository SHA is stale');
  assert.match(summary, /Plan repository SHA is stale/);
  assert.match(summary, /remove and re-apply the dispatch label/);
  assert.match(summary, /Pre-claim failures do not change the issue/);
});
