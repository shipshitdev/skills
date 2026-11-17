import assert from 'node:assert/strict';
import test from 'node:test';
import {
  acceptanceCriteria, buildFeature, closingReferences, collect, extractReferences, humanReviewCards, parseArgs,
} from './release-inputs.mjs';

test('extractReferences keeps the repository a reference names', () => {
  const refs = extractReferences([
    '* add export (#12)\n* fix login https://github.com/o/r/pull/7\n* api change app/api#9',
    'feat: thing (#12)',
    'color #fff and a&#39;b are not references',
  ], 'o/r');
  assert.deepEqual(refs, [
    { repo: 'app/api', number: 9 },
    { repo: 'o/r', number: 7 },
    { repo: 'o/r', number: 12 },
  ]);
});

test('the same number in two repositories stays two references', () => {
  const refs = extractReferences(['#9 and app/api#9 and https://github.com/app/web/issues/9'], 'o/r');
  assert.deepEqual(refs.map((r) => `${r.repo}#${r.number}`), ['app/api#9', 'app/web#9', 'o/r#9']);
});

test('closingReferences reads closing keywords and resolves only bare numbers against the repo', () => {
  assert.deepEqual(closingReferences('Closes #4, fixes o/x#9. See #5.', 'o/r'), [
    { repo: 'o/r', number: 4 },
    { repo: 'o/x', number: 9 },
  ]);
  assert.deepEqual(closingReferences('Resolves https://github.com/app/api/issues/9', 'app/web'), [{ repo: 'app/api', number: 9 }]);
});

test('acceptanceCriteria keeps EARS lines and drops the rest', () => {
  const body = [
    '## Acceptance Criteria',
    '- WHEN the user exports, THE SYSTEM SHALL download a CSV',
    '1. THE SYSTEM SHALL reject empty names',
    '- [ ] IF the file is large, THE SYSTEM SHALL stream it',
    '- nice to have',
  ].join('\n');
  assert.equal(acceptanceCriteria(body).length, 3);
  assert.deepEqual(acceptanceCriteria(null), []);
});

test('buildFeature merges linked issue criteria and flags missing ones', () => {
  const pr = { number: 3, title: 'Export', body: 'Closes #2', html_url: 'u', pull_request: {}, labels: [{ name: 'feat' }] };
  const issue = { number: 2, body: '- THE SYSTEM SHALL export CSV' };
  const feature = buildFeature(pr, [{ ...issue, repo: 'o/r' }], 'o/r');
  assert.deepEqual(feature.acceptance, ['THE SYSTEM SHALL export CSV']);
  assert.deepEqual(feature.labels, ['feat']);
  assert.deepEqual(feature.closes, ['o/r#2']);
  assert.equal(feature.untestable, undefined);
  assert.match(buildFeature(pr, []).untestable, /No EARS/);
});

test('humanReviewCards filters by status case-insensitively', () => {
  const cards = humanReviewCards({ items: [
    { title: 'A', status: 'Human Review', content: { type: 'Issue', number: 1, repository: 'o/r', body: '- THE SYSTEM SHALL a' } },
    { title: 'B', status: 'Done', content: { type: 'Issue', number: 2 } },
    { title: 'C', status: 'human review', content: { type: 'PullRequest', number: 3 } },
  ] });
  assert.deepEqual(cards.map((c) => c.number), [1, 3]);
  assert.equal(cards[0].acceptance.length, 1);
});

test('parseArgs validates input', () => {
  assert.throws(() => parseArgs([]), /--repo/);
  assert.throws(() => parseArgs(['--repo', 'o/r', '--project', '1']), /--owner/);
  assert.throws(() => parseArgs(['--repo', 'o/r', '--bogus']), /Unknown/);
  assert.equal(parseArgs(['--repo', 'o/r', '--json']).json, true);
});

test('collect assembles features and review cards through an injected runner', () => {
  const calls = [];
  const run = (args) => {
    calls.push(args.join(' '));
    const joined = args.join(' ');
    if (args[0] === 'release') return { tagName: 'v2', name: 'v2', body: '* Export (#3)', url: 'ru', publishedAt: 'd', isDraft: false };
    if (joined.includes('/releases?')) return [
      { tag_name: 'v2', published_at: '2026-02-01', draft: false, prerelease: false },
      { tag_name: 'v1', published_at: '2026-01-01', draft: false, prerelease: false },
    ];
    if (joined.includes('/compare/v1...v2')) return { commits: [{ commit: { message: 'fix: y (#4)\n\nbody' } }] };
    if (joined.endsWith('repos/o/r/issues/3')) return { number: 3, title: 'Export', body: 'Closes #2 and closes app/api#9', pull_request: {}, html_url: 'u3' };
    if (joined.endsWith('repos/o/r/issues/4')) return { number: 4, title: 'Y', body: '', html_url: 'u4' };
    if (joined.endsWith('repos/o/r/issues/2')) return { number: 2, title: 'Spec', body: '- THE SYSTEM SHALL export' };
    if (joined.endsWith('repos/app/api/issues/9')) return { number: 9, title: 'Other repo', body: '- THE SYSTEM SHALL serve the api' };
    if (args[0] === 'project') return { totalCount: 1, items: [{ title: 'Z', status: 'Human Review', content: { type: 'Issue', number: 9, repository: 'o/r' } }] };
    throw new Error(`unexpected ${joined}`);
  };
  const report = collect({ repo: 'o/r', owner: 'o', project: '5', status: 'Human Review' }, run);
  assert.equal(report.release.previousTag, 'v1');
  assert.deepEqual(report.features.map((f) => f.number), [3, 4]);
  assert.deepEqual(report.features[0].acceptance, ['THE SYSTEM SHALL export', 'THE SYSTEM SHALL serve the api']);
  assert.deepEqual(report.features[0].closes, ['o/r#2', 'app/api#9']);
  assert.equal(report.humanReview.length, 1);
  assert.deepEqual(report.warnings, []);
});

test('collect refuses a draft release and warns when no board is given', () => {
  const draft = () => ({ tagName: 'v1', body: '', isDraft: true });
  assert.throws(() => collect({ repo: 'o/r' }, draft), /draft/);
  const run = (args) => (args[0] === 'release' ? { tagName: 'v1', body: '', isDraft: false } : []);
  const report = collect({ repo: 'o/r' }, run);
  assert.equal(report.humanReview, null);
  assert.ok(report.warnings.some((w) => /No --project/.test(w)));
});
