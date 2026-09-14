import assert from 'node:assert/strict';
import test from 'node:test';
import { deliveryStatus } from './delivery-status.mjs';

const head = 'a'.repeat(40);
const merged = 'b'.repeat(40);
function fixture() {
  return {
    head, implementationProviders: ['openai'], expectedAcceptanceIds: ['AC1', 'AC2'],
    acceptance: ['AC1', 'AC2'].map((id) => ({ id, passed: true, evidence: 'run:123', head })),
    review: { provider: 'anthropic', reviewer: 'independent-context', independent: true,
      head, verdict: 'PASS', unresolvedFindings: 0, evidence: 'review:456' },
    ci: { discovered: true, noneRequired: false, required: [{ name: 'checks', app: 'actions' }],
      checks: [{ name: 'checks', app: 'actions', head, conclusion: 'success' }] },
    merge: { allowed: true, merged: false, head },
    delivery: { required: ['deploy', 'smoke'], results: [] },
  };
}

test('green reviewed head is merge-ready, not done', () => {
  assert.equal(deliveryStatus(fixture()).state, 'merge_ready');
});

test('all issue acceptance is required, not just implemented children', () => {
  const receipt = fixture();
  receipt.acceptance.pop();
  assert.equal(deliveryStatus(receipt).state, 'acceptance_pending');
});

test('self-review and same lab with another model cannot satisfy independent review', () => {
  for (const provider of ['openai', '']) {
    const receipt = fixture();
    receipt.review.provider = provider;
    assert.equal(deliveryStatus(receipt).state, 'review_pending');
  }
  const receipt = fixture();
  receipt.review.independent = false;
  assert.equal(deliveryStatus(receipt).state, 'review_pending');
});

test('repair contributors also determine provider independence', () => {
  const receipt = fixture();
  receipt.implementationProviders.push('anthropic');
  assert.equal(deliveryStatus(receipt).state, 'review_pending');
});

test('stale review, empty receipt, malformed verdict and unaddressed findings block', () => {
  for (const amendment of [{ head: merged }, { evidence: '' }, { verdict: 'looks good' },
    { unresolvedFindings: -1 }]) {
    const receipt = fixture();
    Object.assign(receipt.review, amendment);
    assert.equal(deliveryStatus(receipt).state, 'review_pending');
  }
  const receipt = fixture();
  receipt.review.unresolvedFindings = 1;
  assert.equal(deliveryStatus(receipt).state, 'changes_requested');
});

test('unknown requirements, wrong app, old head, skipped and absent checks stay pending', () => {
  for (const amendment of [{ head: merged }, { app: 'other' }, { conclusion: 'skipped' },
    { conclusion: 'neutral' }, { conclusion: 'pending' }]) {
    const receipt = fixture();
    Object.assign(receipt.ci.checks[0], amendment);
    assert.equal(deliveryStatus(receipt).state, 'ci_pending');
  }
  const receipt = fixture();
  receipt.ci.discovered = false;
  assert.equal(deliveryStatus(receipt).state, 'ci_pending');
  receipt.ci.discovered = true;
  receipt.ci.checks = [];
  assert.equal(deliveryStatus(receipt).state, 'ci_pending');
});

test('empty required set needs explicit policy discovery', () => {
  const receipt = fixture();
  receipt.ci.required = [];
  assert.equal(deliveryStatus(receipt).state, 'ci_pending');
  receipt.ci.noneRequired = true;
  assert.equal(deliveryStatus(receipt).state, 'merge_ready');
});

test('failed and cancelled required checks block, even if another check is missing', () => {
  for (const conclusion of ['failure', 'timed_out', 'cancelled']) {
    const receipt = fixture();
    receipt.ci.required.push({ name: 'other', app: 'actions' });
    receipt.ci.checks[0].conclusion = conclusion;
    assert.equal(deliveryStatus(receipt).state, 'ci_failed');
  }
});

test('merge protections cannot be overridden by a passing reviewer', () => {
  const receipt = fixture();
  receipt.merge.allowed = false;
  assert.equal(deliveryStatus(receipt).state, 'merge_blocked');
});

test('merge alone is not delivery; deployment evidence must match merged commit', () => {
  const receipt = fixture();
  Object.assign(receipt.merge, { merged: true, commit: merged });
  assert.equal(deliveryStatus(receipt).state, 'delivery_pending');
  receipt.delivery.results = ['deploy', 'smoke'].map((name) => ({
    name, passed: true, commit: head, evidence: 'deployment:789',
  }));
  assert.equal(deliveryStatus(receipt).state, 'delivery_pending');
  for (const entry of receipt.delivery.results) entry.commit = merged;
  assert.equal(deliveryStatus(receipt).state, 'done');
});

test('missing fields and duplicate evidence fail rather than fabricating success', () => {
  assert.throws(() => deliveryStatus({}));
  const receipt = fixture();
  receipt.ci.checks.push({ ...receipt.ci.checks[0] });
  assert.throws(() => deliveryStatus(receipt));
  const duplicate = fixture();
  duplicate.expectedAcceptanceIds.push('AC1');
  assert.throws(() => deliveryStatus(duplicate));
});
