import assert from 'node:assert/strict';
import { test } from 'node:test';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, rmSync, symlinkSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { audit, buildFindings, createReader, fetchRepoActivity, isEntrypoint, issueIsShipped, parseArgs, parseStatusMap, renderReport, resolvePriorities } from './github-board-report.mjs';

const NOW = Date.now();
const RECENT = new Date(NOW - 86400000).toISOString();
const OLD = new Date(NOW - 30 * 86400000).toISOString();
const options = { owner: 'org', project: '1', window: 14, stale: 7, horizon: 7 };
const page = (nodes, after) => {
  const offset = Number(after ?? 0);
  return { nodes: nodes.slice(offset, offset + 100), totalCount: nodes.length,
    pageInfo: { hasNextPage: offset + 100 < nodes.length, endCursor: String(offset + 100) } };
};
const issue = (number, extra = {}) => ({ id: `I${number}`, type: 'Issue', __typename: 'Issue', itemId: `B${number}`,
  number, title: `Issue ${number}`, url: `https://github.com/org/repo/issues/${number}`, state: 'OPEN',
  stateReason: null, repo: 'org/repo', repository: { nameWithOwner: 'org/repo' }, updatedAt: OLD,
  status: 'Backlog', priority: 'High', priorityKnown: true, closingPrs: [], subIssues: [], ...extra });

function fixture() {
  const calls = [];
  const nested = Array.from({ length: 101 }, (_, index) => ({ ...issue(1000 + index), state: index === 100 ? 'OPEN' : 'CLOSED' }));
  const closing = Array.from({ length: 101 }, (_, index) => ({ id: `P${index}`, number: index, merged: index === 0,
    state: index === 100 ? 'OPEN' : 'CLOSED', url: `https://github.com/org/repo/pull/${index}` }));
  const lanes = ['Backlog', 'In Progress', 'Human Review', 'Done', 'Deferred'];
  const board = Array.from({ length: 101 }, (_, index) => ({ id: `B${index}`, isArchived: index === 100,
    fieldValues: page([{ name: lanes[index % 5], field: { id: 'STATUS', name: 'Status', options: [] } },
      { name: 'stale-local', field: { id: 'LOCAL', name: 'Priority' } },
      ...Array.from({ length: 99 }, () => ({}))]),
    content: { ...issue(index), subIssues: page(index === 0 ? nested : []), closedByPullRequestsReferences: page(index === 1 ? closing : []) } }));
  board.push({ id: 'draft', isArchived: false, content: { __typename: 'DraftIssue', title: 'idea' }, fieldValues: page([]) });
  board.push({ id: 'pr-card', isArchived: true, content: { ...issue(1), __typename: 'PullRequest', merged: true }, fieldValues: page([]) });
  const prs = Array.from({ length: 105 }, (_, index) => ({ id: `PR${index}`, number: index, title: `PR ${index}`, mergedAt: RECENT, updatedAt: RECENT,
    url: `https://github.com/org/repo/pull/${index}`, closingIssuesReferences: page(index === 104 ? nested : []) }));
  const issues = Array.from({ length: 205 }, (_, index) => ({ ...issue(index), createdAt: index === 204 ? OLD : RECENT }));
  const milestones = Array.from({ length: 101 }, (_, index) => ({ number: index, title: `M${index}`, due_on: index === 100 ? RECENT : null, open_issues: 101, closed_issues: 0 }));
  const run = (args) => {
    calls.push(args);
    assert.ok(!args.includes('POST') && !args.includes('PUT') && !args.includes('PATCH') && !args.includes('DELETE'));
    if (args[0] === 'project') return { id: 'PROJECT', title: 'Fixture', number: 1, url: 'https://github.com/orgs/org/projects/1' };
    const query = args.find((arg) => arg.startsWith('query='))?.slice(6);
    const argValue = (key) => args.find((arg) => arg.startsWith(`${key}=`))?.slice(key.length + 1);
    if (query) {
      assert.doesNotMatch(query, /\bmutation\b/);
      for (const [index, arg] of args.entries()) {
        if (/^(id|after)=/.test(arg)) assert.equal(args[index - 1], '-f');
      }
      if (query.includes('__type(')) return { data: { __type: { fields: [{ name: 'items', args: [{ name: 'archivedStates' }] }] } } };
      const after = argValue('after');
      if (query.includes('repository(owner:')) {
        const field = query.includes('pullRequests(') ? 'pullRequests' : 'issues';
        return { data: { repository: { [field]: page(field === 'pullRequests' ? prs : issues, after) } } };
      }
      const id = argValue('id');
      let field; let nodes;
      if (id === 'PROJECT' && query.includes('fields(first:')) return { data: { node: { fields: page([{ id: 'STATUS', name: 'Status' }]) } } };
      if (id === 'PROJECT') { field = 'items'; nodes = board; assert.match(query, /archivedStates: \[ARCHIVED, NOT_ARCHIVED\]/); }
      else if (query.includes('fieldValues(')) {
        field = 'fieldValues'; nodes = [...board.find((item) => item.id === id).fieldValues.nodes, {}];
      } else if (query.includes('subIssues(')) { field = 'subIssues'; nodes = nested; }
      else if (query.includes('closedByPullRequestsReferences(')) { field = 'closedByPullRequestsReferences'; nodes = closing; }
      else { field = 'closingIssuesReferences'; nodes = nested; }
      return { data: { node: { [field]: page(nodes, after) } } };
    }
    const endpoint = args.find((arg) => /^(users|orgs|repos)\//.test(arg));
    if (endpoint.startsWith('users/')) return { type: 'Organization' };
    assert.ok(args.includes('--paginate') && args.includes('--slurp'));
    if (endpoint.startsWith('orgs/')) return [[{ id: 9, name: 'Priority', data_type: 'single_select', options: [{ id: 1, name: 'High' }] }]];
    if (endpoint.includes('issue-field-values')) return [[]];
    if (endpoint.includes('/milestones?')) return [milestones.slice(0, 100), milestones.slice(100)];
    return [issues.slice(0, 100), issues.slice(100, 101)];
  };
  return { run, calls, board };
}

test('whole audit paginates every relevant connection and emits equal console/JSON evidence', () => {
  const { run, calls } = fixture();
  const report = audit(options, run);
  assert.equal(report.counts.boardItems, 103);
  assert.equal(report.counts.archivedItems, 2);
  assert.equal(report.draftCount, 1);
  assert.deepEqual(report.activityCounts[0].counts, { mergedPrsScanned: 105, mergedPrsInWindow: 105,
    openIssuesScanned: 205, openIssuesInWindow: 204, milestones: 101 });
  assert.equal(report.findings.milestoneReadiness[0].focus.length, 101);
  assert.equal(report.findings.priorityHygiene.length, 100);
  assert.deepEqual(new Set(report.findings.priorityHygiene.map((item) => item.status)), new Set(['Backlog', 'In Progress', 'Human Review', 'Done', 'Deferred']));
  assert.ok(!report.findings.epicDrift.some((item) => item.number === 0), 'open child on page two prevents false parent completion');
  assert.ok(!report.findings.staleInProgress.some((item) => item.number === 1), 'open PR on page two prevents stale finding');
  assert.ok(!report.findings.untrackedWork.some((item) => item.kind === 'merged-pr' && item.number === 1), 'archived PR membership proves tracking');
  assert.ok(report.findings.missingFormalLinks.some((item) => item.number === 1));
  assert.ok(report.coverage.complete);
  assert.ok(report.coverage.connections.filter((entry) => entry.pages > 1).length > 100);
  const parsed = JSON.parse(JSON.stringify(report));
  const consoleOutput = renderReport(parsed);
  assert.match(consoleOutput, /mergedPrsInWindow.*105/);
  assert.match(consoleOutput, /openIssuesScanned.*205/);
  assert.match(consoleOutput, /archived: 2/);
  assert.match(consoleOutput, /Deferred/);
  assert.ok(calls.length > 200);
});

test('current OPEN state overrides older merged closing PR, with or without newer PR', () => {
  for (const closingPrs of [[{ merged: true }], [{ merged: true }, { state: 'OPEN' }]]) {
    const card = issue(1, { status: 'Done', closingPrs });
    assert.equal(issueIsShipped(card), false);
    const { findings } = buildFindings([card], [], [], options, NOW);
    assert.equal(findings.mergedNotDone.length, 0);
    assert.equal(findings.doneNotMerged.length, 1);
  }
});

test('completed without merge, cancelled, duplicate, and shipped remain distinct', () => {
  for (const stateReason of ['NOT_PLANNED', 'DUPLICATE', 'COMPLETED']) {
    const card = issue(1, { state: 'CLOSED', stateReason, status: 'Done' });
    const { findings } = buildFindings([card], [], [], options, NOW);
    assert.equal(findings.doneNotMerged.length, 0);
    assert.equal(findings.closedWithoutMerge.length, 1);
  }
  assert.ok(issueIsShipped(issue(1, { state: 'CLOSED', stateReason: 'COMPLETED', closingPrs: [{ merged: true }] })));
  assert.equal(issueIsShipped(issue(1, { state: 'CLOSED', stateReason: 'NOT_PLANNED', closingPrs: [{ merged: true }] })), false);
});

test('native empty values never fall back to stale project values; unavailable is not missing', () => {
  for (const mode of ['native', 'project', 'unavailable', 'unreadable-value']) {
    const card = issue(1, { priority: 'stale' });
    const reader = createReader((args) => {
      if (args.includes('users/org')) return { type: 'Organization' };
      if (args.includes('orgs/org/issue-fields')) {
        if (mode === 'unavailable') throw new Error('403');
        return [mode === 'project' ? [] : [{ id: 9, name: 'Priority', data_type: 'single_select' }]];
      }
      if (mode === 'unreadable-value') throw new Error('404');
      return [[]];
    });
    resolvePriorities(reader, [card]);
    assert.equal(card.priority, mode === 'project' ? 'stale' : '');
    assert.equal(card.priorityKnown, !['unavailable', 'unreadable-value'].includes(mode));
    assert.equal(reader.coverage.complete, card.priorityKnown);
  }
});

test('missing archived support and redaction make the verdict incomplete', () => {
  const { run } = fixture();
  const report = audit(options, (args) => {
    const query = args.find((arg) => arg.startsWith('query=')) ?? '';
    if (query.includes('__type(')) return { data: { __type: { fields: [] } } };
    if (query.includes('archivedStates')) assert.fail('unsupported filter');
    if (query.includes('items(first:')) {
      return { data: { node: { items: page([{ id: 'redacted', content: null, fieldValues: page([]) }]) } } };
    }
    return run(args);
  });
  assert.equal(report.coverage.complete, false);
  assert.equal(report.draftCount, 0);
  assert.equal(report.counts.inaccessibleItems, 1);
  assert.match(report.verdict, /INCOMPLETE/);
  assert.match(renderReport(report), /redacted\/inaccessible/);
});

test('pagination cannot quietly loop or claim completeness across changing totals', () => {
  const reader = createReader();
  assert.throws(() => reader.connection('broken', () => ({ nodes: [], pageInfo: { hasNextPage: true, endCursor: 'same' } })), /Invalid pagination/);
  reader.connection('changed', () => ({ nodes: [1], totalCount: 2, pageInfo: { hasNextPage: false } }));
  assert.equal(reader.coverage.complete, false);
});

test('report arguments never authorize writes and reject malformed numbers', () => {
  assert.throws(() => parseArgs(['--owner', 'org', '--project', '1', '--apply']), /Unknown argument/);
  assert.throws(() => parseArgs(['--owner', 'org', '--project', '1', '--window', '14oops']), /positive integer/);
});


test('custom lane semantics preserve the board workflow and missing metadata in parked lanes', () => {
  const statusMap = parseStatusMap('{"done":["Released"],"deferred":["Parked"],"inProgress":["Building"],"review":["Acceptance"]}');
  const cards = [issue(1, { status: 'Released' }), issue(2, { status: 'Parked', priority: '' }),
    issue(3, { status: 'Building' }), issue(4, { status: 'Acceptance', state: 'CLOSED',
      stateReason: 'COMPLETED', closingPrs: [{ merged: true }] })];
  const { findings } = buildFindings(cards, [], [], { ...options, statusMap }, NOW);
  assert.equal(findings.doneNotMerged.length, 1);
  assert.equal(findings.priorityHygiene[0].status, 'Parked');
  assert.equal(findings.staleInProgress[0].status, 'Building');
  assert.equal(findings.reviewStarvation[0].status, 'Acceptance');
  assert.throws(() => parseStatusMap('{"done":["Backlog"]}'), /Ambiguous/);
  assert.throws(() => parseStatusMap('{"unknown":["Custom"]}'), /Invalid/);
});


test('closed work in active lanes affects the verdict without implying shipment or Done', () => {
  for (const status of ['In Progress', 'Human Review']) {
    for (const type of ['Issue', 'PullRequest']) {
      const card = issue(1, { type, state: 'CLOSED', stateReason: 'NOT_PLANNED', status });
      const result = buildFindings([card], [], [], options, NOW);
      assert.equal(result.findings.closedInActive.length, 1);
      assert.equal(result.driftItemCount, 1);
      assert.equal(result.findings.mergedNotDone.length, 0);
      assert.match(result.findings.closedInActive[0].reason, /review its disposition/i);
    }
  }
  const { run, board } = fixture();
  board.splice(1);
  board[0].fieldValues = page([{name: 'In Progress', field: {id:'STATUS',name:'Status'}}]);
  board[0].content = { ...board[0].content, state:'CLOSED', stateReason:'NOT_PLANNED', subIssues:page([]) };
  const report = audit(options, (args) => args.some((arg) => arg.includes('/issue-field-values?'))
    ? [[{ issue_field_id:9, value:1, single_select_option:{id:1,name:'High'} }]] : run(args));
  assert.equal(report.findings.priorityHygiene.length, 0);
  assert.equal(report.driftItemCount, 1);
  assert.equal(report.verdict, '1 distinct item(s) have drift.');
  assert.match(renderReport(report), /closedInActive: 1/);
});

test('old-created PR merged recently survives ordered window boundary; stale merge updated recently is excluded', () => {
  const history = Array.from({length:350}, (_, index) => ({id:`H${index}`,number:index,title:`PR${index}`,
    createdAt:OLD, updatedAt:index < 105 ? RECENT : OLD,
    mergedAt:index < 105 && index !== 0 ? RECENT : OLD,
    closingIssuesReferences:page([])}));
  const issues = Array.from({length:350}, (_,index)=>({id:`I${index}`,number:index,createdAt:index < 205 ? RECENT : OLD}));
  const requests = [];
  const reader = createReader((args) => {
    const query = args.find((arg)=>arg.startsWith('query='));
    if (!query) return [[]];
    const after = args.find((arg)=>arg.startsWith('after='))?.slice(6);
    const field = query.includes('pullRequests(') ? 'pullRequests' : 'issues';
    assert.match(query, field === 'pullRequests' ? /field: UPDATED_AT, direction: DESC/ : /field: CREATED_AT, direction: DESC/);
    requests.push([field,Number(after ?? 0)]);
    return {data:{repository:{[field]:page(field === 'pullRequests' ? history : issues,after)}}};
  });
  const activity = fetchRepoActivity(reader,'org/repo',14,NOW);
  assert.equal(activity.mergedPrs.length,104);
  assert.ok(activity.mergedPrs.some((pr)=>pr.number===104), 'old-created PR merged recently is included across pages');
  assert.ok(!activity.mergedPrs.some((pr)=>pr.number===0), 'updated old merge is not new shipment');
  assert.equal(activity.openIssues.length,205);
  assert.deepEqual(requests,[['pullRequests',0],['pullRequests',100],['issues',0],['issues',100],['issues',200]]);
  assert.equal(reader.coverage.complete,true);
  const stopped = reader.coverage.connections.filter((entry)=>entry.termination==='window_boundary');
  assert.equal(stopped.length,2);
  assert.ok(stopped.every((entry)=>entry.scope==='activity_window' && entry.fetched < entry.total));
});

test('window boundary is inclusive and untrustworthy ordering prevents an early stop', () => {
  const reader=createReader();
  const since=NOW-14*86400000;
  const history=[{id:'a',createdAt:new Date(since).toISOString()},
    {id:'b',createdAt:new Date(since).toISOString()},
    {id:'c',createdAt:OLD}];
  let calls=0;
  reader.connection('inclusive',(after)=> {
    const index=Number(after ?? 0); calls++;
    return {nodes:[history[index]],totalCount:3,pageInfo:{hasNextPage:index<2,endCursor:String(index+1)}};
  },undefined,{field:'createdAt',since});
  assert.equal(calls,3, 'equal boundary dates cannot stop pagination');
  const unordered=createReader();
  let secondRead=false;
  unordered.connection('unordered',(after)=>{
    if (!after) return {nodes:[{id:'a',createdAt:OLD},{id:'b',createdAt:RECENT},{id:'c',createdAt:OLD}],
      totalCount:4,pageInfo:{hasNextPage:true,endCursor:'next'}};
    secondRead=true;
    return {nodes:[{id:'d',createdAt:RECENT}],totalCount:4,pageInfo:{hasNextPage:false}};
  },undefined,{field:'createdAt',since});
  assert.equal(secondRead,true);
  assert.equal(unordered.coverage.complete,false);
  assert.equal(unordered.coverage.connections[0].termination,'exhausted');
});

test('status map needs its own value rather than consuming the following option', () => {
  for (const tail of [[],['--json']]) {
    assert.throws(()=>parseArgs(['--owner','org','--project','1','--status-map',...tail]),/Missing value for --status-map/);
  }
});

test('GraphQL transport preserves explicit numeric and boolean values', () => {
  let captured;
  const reader = createReader((args) => { captured = args; return { data: {} }; });
  reader.graphql('query($count: Int!, $enabled: Boolean!) { fixture }', { count: 12, enabled: false });
  for (const value of ['count=12', 'enabled=false']) {
    const index = captured.indexOf(value);
    assert.ok(index > 0);
    assert.equal(captured[index - 1], '-F');
  }
});

test('entrypoint detection survives a symlinked skill directory', () => {
  const script = fileURLToPath(new URL('./github-board-report.mjs', import.meta.url));
  const dir = mkdtempSync(join(tmpdir(), 'board-sync-'));
  const link = join(dir, 'linked-report.mjs');
  symlinkSync(script, link);
  try {
    assert.equal(isEntrypoint(link, pathToFileURL(script).href), true);
    assert.equal(isEntrypoint(script, pathToFileURL(script).href), true);
    assert.equal(isEntrypoint(join(dir, 'other.mjs'), pathToFileURL(script).href), false);
    assert.equal(isEntrypoint(undefined, pathToFileURL(script).href), false);
    const output = execFileSync(process.execPath, [link, '--help'], { encoding: 'utf8' });
    assert.match(output, /^Read-only: --owner/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
