import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { checkPlan, requirementsFingerprint } from './plan-header.mjs';

const headSha = 'a'.repeat(40);
const issueBody = 'Ship the complete feature.\nKeep the settled scope.';
const digest = createHash('sha256').update(issueBody).digest('hex');
const step = '- [ ] S-1: Implement the settled change\n  - Touch: README.md\n  - Pattern: D-1\n  - Check: bun run lint\n  - Stop if: the prescribed pattern is absent\n';
const headers = {
  'Plan revision': '1',
  'Base commit': headSha,
  'Requirements SHA256': digest,
  Readiness: 'READY',
};
function fixture() {
  return {
    issueBody, headSha,
    planBody: `## Implementation Plan\n${Object.entries(headers).map(([name, value]) => `${name}: ${value}`).join('\n')}\n${step}`,
  };
}

test('fingerprint normalizes CRLF, Current plan lines and surrounding whitespace', () => {
  for (const body of [issueBody, issueBody.replace(/\n/g, '\r\n'),
    `\n  ${issueBody}\n\t`, `${issueBody}\nCurrent plan: https://example.com/plan`,
    `\r\nCurrent plan: old\r\n${issueBody.replace(/\n/g, '\r\n')}\r\nCurrent plan: new\r\n`]) {
    assert.equal(requirementsFingerprint(body), digest);
  }
  assert.match(digest, /^[0-9a-f]{64}$/);
});

test('valid plans expose their fields and accept CRLF and checked steps', () => {
  for (const mark of [' ', 'x', 'X']) {
    const input = fixture();
    input.planBody = input.planBody.replace('[ ]', `[${mark}]`).replace(/\n/g, '\r\n');
    assert.deepEqual(checkPlan(input), {
      ready: true, blockers: [],
      fields: { planRevision: '1', baseCommit: headSha, requirementsSha256: digest, readiness: 'READY' },
    });
  }
});

test('missing and duplicate headers each produce only their declaration blocker', () => {
  const keys = ['planRevision', 'baseCommit', 'requirementsSha256', 'readiness'];
  for (const [index, [name, value]] of Object.entries(headers).entries()) {
    for (const replacement of ['', `${name}: ${value}\n${name}: invalid\n`]) {
      const input = fixture();
      input.planBody = input.planBody.replace(`${name}: ${value}\n`, replacement);
      const result = checkPlan(input);
      assert.equal(result.ready, false);
      assert.deepEqual(result.blockers, [`Plan must declare exactly one ${name}`]);
      assert.equal(result.fields[keys[index]], null);
    }
  }
});

test('each heading, value, freshness and missing-step blocker is isolated', () => {
  const cases = [
    ['## Implementation Plan', '# Implementation Plan', 'Plan heading missing'],
    ['Readiness: READY', 'Readiness: BLOCKED', 'Readiness is not READY'],
    ...['0', '-1', '1.5', '01', 'one'].map((value) => [
      'Plan revision: 1', `Plan revision: ${value}`, 'Plan revision must be a positive integer',
    ]),
    ...['A'.repeat(40), 'a'.repeat(39), 'g'.repeat(40)].map((value) => [
      `Base commit: ${headSha}`, `Base commit: ${value}`, 'Base commit must be a 40-character lowercase SHA',
    ]),
    [`Base commit: ${headSha}`, `Base commit: ${'b'.repeat(40)}`, 'Base commit does not match head; return to planner'],
    [`Requirements SHA256: ${digest}`, 'Requirements SHA256: changed', 'Requirements changed since planning; return to planner'],
    [step, '', 'Plan has no S-n steps'],
  ];
  for (const [before, after, blocker] of cases) {
    const input = fixture();
    input.planBody = input.planBody.replace(before, after);
    const result = checkPlan(input);
    assert.equal(result.ready, false);
    assert.deepEqual(result.blockers, [blocker]);
  }
});

test('every step field must have a nonempty value in its own block', () => {
  for (const name of ['Touch', 'Pattern', 'Check', 'Stop if']) {
    for (const replacement of ['', `  - ${name}: \n`]) {
      const input = fixture();
      input.planBody = input.planBody.replace(new RegExp(`  - ${name}: [^\n]+\n`), replacement);
      input.planBody += step.replace('S-1', 'S-2');
      assert.deepEqual(checkPlan(input).blockers, [`S-1 missing ${name}`]);
    }
  }
  const input = fixture();
  input.planBody = input.planBody.replace('  - Touch:', '### Next section\n  - Touch:');
  assert.deepEqual(checkPlan(input).blockers, [
    'S-1 missing Touch', 'S-1 missing Pattern', 'S-1 missing Check', 'S-1 missing Stop if',
  ]);
});

test('all simultaneous failures are reported', () => {
  const result = checkPlan({ issueBody, headSha, planBody: [
    '# Wrong heading', 'Plan revision: 0', 'Base commit: invalid',
    'Requirements SHA256: changed', 'Readiness: BLOCKED',
    '- [ ] S-1: First change', '- [X] S-2: Second change',
  ].join('\n') });
  assert.equal(result.ready, false);
  assert.deepEqual(result.blockers, [
    'Plan heading missing', 'Readiness is not READY',
    'Plan revision must be a positive integer', 'Base commit must be a 40-character lowercase SHA',
    'Requirements changed since planning; return to planner',
    'S-1 missing Touch', 'S-1 missing Pattern', 'S-1 missing Check', 'S-1 missing Stop if',
    'S-2 missing Touch', 'S-2 missing Pattern', 'S-2 missing Check', 'S-2 missing Stop if',
  ]);
  assert.deepEqual(checkPlan({ issueBody, headSha, planBody: '' }).blockers, [
    'Plan heading missing', 'Plan must declare exactly one Plan revision',
    'Plan must declare exactly one Base commit', 'Plan must declare exactly one Requirements SHA256',
    'Plan must declare exactly one Readiness', 'Plan has no S-n steps',
  ]);
});

test('CLI emits digest and JSON with exits 0, 1 and invocation errors with exit 2', () => {
  const directory = mkdtempSync(join(tmpdir(), 'plan-header-'));
  const issueFile = join(directory, 'issue.md');
  const planFile = join(directory, 'plan.md');
  const missingFile = join(directory, 'missing.md');
  const script = fileURLToPath(new URL('./plan-header.mjs', import.meta.url));
  const run = (...args) => spawnSync(process.execPath, [script, ...args], { encoding: 'utf8' });
  try {
    writeFileSync(issueFile, issueBody);
    writeFileSync(planFile, fixture().planBody);
    const fingerprint = run('digest', issueFile);
    assert.equal(fingerprint.status, 0);
    assert.equal(fingerprint.stdout, `${digest}\n`);
    assert.equal(fingerprint.stderr, '');
    const valid = run('check', issueFile, planFile, headSha);
    assert.equal(valid.status, 0);
    assert.equal(valid.stdout, `${JSON.stringify(checkPlan(fixture()))}\n`);
    assert.equal(valid.stderr, '');
    writeFileSync(planFile, fixture().planBody.replace('READY', 'BLOCKED'));
    const blocked = run('check', issueFile, planFile, headSha);
    assert.equal(blocked.status, 1);
    assert.equal(blocked.stderr, '');
    assert.equal(JSON.parse(blocked.stdout).ready, false);
    assert.deepEqual(JSON.parse(blocked.stdout).blockers, ['Readiness is not READY']);
    for (const args of [[], ['unknown'], ['digest'], ['digest', issueFile, 'extra'],
      ['check', issueFile, planFile], ['check', issueFile, planFile, headSha, 'extra'],
      ['digest', missingFile], ['check', missingFile, planFile, headSha],
      ['check', issueFile, missingFile, headSha],
      ...['short', 'A'.repeat(40), 'g'.repeat(40)].map((sha) => ['check', issueFile, planFile, sha])]) {
      const result = run(...args);
      assert.equal(result.status, 2);
      assert.equal(result.stdout, '');
      assert.match(result.stderr, /Usage:|ENOENT|Head SHA must be a 40-character lowercase SHA/);
    }
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});
