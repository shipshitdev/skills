#!/usr/bin/env node

import { execFileSync } from 'node:child_process';
import { realpathSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';

const PAGE = 'pageInfo { hasNextPage endCursor } totalCount';
const FIELDS = `... on ProjectV2ItemFieldSingleSelectValue {
  name field { ... on ProjectV2SingleSelectField { id name options { id name } } }
}`;
const PR_LINK = 'id number state merged mergedAt url repository { nameWithOwner }';
const ISSUE_LINK = 'id number state url repository { nameWithOwner }';
const CONTENT = `__typename
  ... on DraftIssue { title }
  ... on Issue {
    id number title state stateReason url updatedAt repository { nameWithOwner }
    subIssues(first: 100) { ${PAGE} nodes { ${ISSUE_LINK} } }
    closedByPullRequestsReferences(first: 100, includeClosedPrs: true) {
      ${PAGE} nodes { ${PR_LINK} }
    }
  }
  ... on PullRequest {
    id number title state url updatedAt merged mergedAt isDraft reviewDecision
    repository { nameWithOwner }
    commits(last: 1) { nodes { commit { statusCheckRollup { state } } } }
  }`;

const DEFAULT_STATUS_MAP = { backlog: ['Backlog'], inProgress: ['In Progress'],
  review: ['Human Review'], done: ['Done'], deferred: ['Deferred'] };

export function parseStatusMap(value) {
  const input = JSON.parse(value);
  if (!input || Array.isArray(input) || typeof input !== 'object') throw new Error('Status map must be an object.');
  const mapping = { ...DEFAULT_STATUS_MAP, ...input };
  const seen = new Set();
  for (const [key, names] of Object.entries(mapping)) {
    if (!(Object.hasOwn(DEFAULT_STATUS_MAP, key)) || !Array.isArray(names) || names.some((name) => typeof name !== 'string' || !name.trim())) {
      throw new Error(`Invalid status semantic mapping: ${key}`);
    }
    for (const name of names) {
      const normalized = name.trim().toLowerCase();
      if (seen.has(normalized)) throw new Error(`Ambiguous status: ${name}`);
      seen.add(normalized);
    }
  }
  return mapping;
}

function statusSemantic(status, mapping = DEFAULT_STATUS_MAP) {
  return Object.entries(mapping).find(([, names]) => names.some((name) => name.trim().toLowerCase() === status.trim().toLowerCase()))?.[0] ?? 'unknown';
}

export function ghJson(args) {
  return JSON.parse(execFileSync('gh', args, {
    encoding: 'utf8', maxBuffer: 64 * 1024 * 1024,
    stdio: ['ignore', 'pipe', 'pipe'],
  }));
}

export function createReader(run = ghJson) {
  const coverage = { complete: true, warnings: [], connections: [], archivedHistory: '', prioritySources: {} };
  const warn = (message) => {
    coverage.complete = false;
    if (!coverage.warnings.includes(message)) coverage.warnings.push(message);
  };
  const graphql = (query, variables = {}) => {
    const args = ['api', 'graphql', '-f', `query=${query}`];
    for (const [key, value] of Object.entries(variables)) {
      if (value !== null && value !== undefined) args.push(typeof value === 'string' ? '-f' : '-F', `${key}=${value}`);
    }
    const result = run(args);
    if (result.errors?.length) throw new Error(JSON.stringify(result.errors));
    return result.data;
  };
  const rest = (endpoint) => run(['api', '--method', 'GET', endpoint,
    '-H', 'X-GitHub-Api-Version: 2026-03-10']);
  const restPages = (endpoint) => {
    const pages = run(['api', '--method', 'GET', '--paginate', '--slurp', endpoint,
      '-H', 'X-GitHub-Api-Version: 2026-03-10']);
    if (!Array.isArray(pages) || pages.some((page) => !Array.isArray(page))) {
      throw new Error(`Unexpected list response: ${endpoint}`);
    }
    const nodes = pages.flat();
    coverage.connections.push({ name: endpoint, fetched: nodes.length, pages: pages.length });
    return nodes;
  };
  const connection = (name, fetch, initial, window) => {
    const nodes = [];
    let after = null;
    let page = initial;
    let pages = 0;
    const cursors = new Set();
    let termination = 'exhausted';
    let previousDate = Number.POSITIVE_INFINITY;
    let ordered = true;
    const ids = new Set();
    do {
      page ??= fetch(after);
      if (!page?.nodes || !page.pageInfo) throw new Error(`Missing connection: ${name}`);
      if (page.nodes.some((node) => !node)) warn(`${name}: inaccessible nodes in response.`);
      nodes.push(...page.nodes.filter(Boolean));
      pages += 1;
      if (window) {
        for (const node of page.nodes.filter(Boolean)) {
          const date = Date.parse(node[window.field]);
          if (!Number.isFinite(date) || date > previousDate) {
            ordered = false;
            warn(`${name}: invalid or unordered ${window.field}; window boundary cannot establish completeness.`);
          }
          previousDate = date;
          if (!node.id || ids.has(node.id)) warn(`${name}: duplicate or missing activity ID; collection changed or is incomplete.`);
          ids.add(node.id);
        }
      }
      if (!page.pageInfo.hasNextPage) break;
      if (window && ordered && previousDate < window.since) {
        termination = 'window_boundary';
        break;
      }
      after = page.pageInfo.endCursor;
      if (!after || cursors.has(after)) throw new Error(`Invalid pagination cursor: ${name}`);
      cursors.add(after);
      page = null;
    } while (true);
    if (termination === 'exhausted' && page.totalCount !== undefined && nodes.length !== page.totalCount) {
      warn(`${name}: fetched ${nodes.length}, expected ${page.totalCount}; changed during collection or inaccessible nodes.`);
    }
    coverage.connections.push({ name, fetched: nodes.length, total: page.totalCount, pages,
      termination, ...(window ? { scope: 'activity_window', orderedBy: window.field,
        since: new Date(window.since).toISOString() } : {}) });
    return nodes;
  };
  const nodeConnection = (id, type, field, selection, extra = '', initial) =>
    connection(`${id}.${field}`, (after) => graphql(`query($id: ID!, $after: String) {
      node(id: $id) { ... on ${type} {
        ${field}(first: 100, after: $after ${extra}) { ${PAGE} nodes { ${selection} } }
      } }
    }`, { id, after }).node?.[field], initial);
  return { run, coverage, warn, graphql, rest, restPages, connection, nodeConnection };
}

export function fetchBoardItems(reader, projectId) {
  const schema = reader.graphql('{ __type(name: "ProjectV2") { fields { name args { name } } } }');
  const archiveSupported = schema.__type?.fields?.find((field) => field.name === 'items')
    ?.args.some((arg) => arg.name === 'archivedStates');
  reader.coverage.archivedHistory = archiveSupported
    ? 'Active and archived items currently retained in this project; removed/deleted history is unavailable.'
    : 'Default API item scope only; archived coverage is unavailable on this schema.';
  if (!archiveSupported) reader.warn(reader.coverage.archivedHistory);
  const items = reader.nodeConnection(projectId, 'ProjectV2', 'items', `id isArchived
    fieldValues(first: 100) { ${PAGE} nodes { ${FIELDS} } }
    content { ${CONTENT} }`, archiveSupported ? ', archivedStates: [ARCHIVED, NOT_ARCHIVED]' : '');
  for (const raw of items) {
    raw.fieldValues.nodes = reader.nodeConnection(raw.id, 'ProjectV2Item', 'fieldValues', FIELDS, '', raw.fieldValues);
    if (raw.content?.__typename === 'Issue') {
      const issue = raw.content;
      issue.subIssues.nodes = reader.nodeConnection(issue.id, 'Issue', 'subIssues', ISSUE_LINK, '', issue.subIssues);
      issue.closedByPullRequestsReferences.nodes = reader.nodeConnection(issue.id, 'Issue',
        'closedByPullRequestsReferences', PR_LINK, ', includeClosedPrs: true', issue.closedByPullRequestsReferences);
    }
  }
  return items;
}

export function classifyItems(rawItems) {
  const drafts = [];
  const inaccessible = [];
  const items = [];
  for (const raw of rawItems) {
    const content = raw.content;
    if (!content) { inaccessible.push(raw.id); continue; }
    if (content.__typename === 'DraftIssue') {
      drafts.push({ itemId: raw.id, title: content.title, archived: raw.isArchived });
      continue;
    }
    const value = (name) => raw.fieldValues.nodes.find((field) => field.field?.name === name);
    items.push({
      ...content, type: content.__typename, itemId: raw.id, archived: raw.isArchived,
      repo: content.repository.nameWithOwner, status: value('Status')?.name ?? '',
      statusField: value('Status')?.field ?? null,
      priority: value('Priority')?.name ?? '', priorityField: value('Priority')?.field ?? null,
      prioritySource: 'project', priorityKnown: true,
      subIssues: content.subIssues?.nodes ?? [],
      closingPrs: content.closedByPullRequestsReferences?.nodes ?? [],
      checkState: content.commits?.nodes?.[0]?.commit?.statusCheckRollup?.state ?? '',
    });
  }
  return { items, drafts, inaccessible };
}

export function resolvePriorities(reader, items) {
  const owners = new Map();
  for (const item of items) {
    if (item.type !== 'Issue') continue;
    const owner = item.repo.split('/')[0];
    if (!owners.has(owner)) {
      try {
        const identity = reader.rest(`users/${owner}`);
        const fields = identity.type === 'Organization' ? reader.restPages(`orgs/${owner}/issue-fields`) : [];
        const priority = fields.filter((field) => field.name === 'Priority');
        if (priority.length > 1 || (priority[0] && priority[0].data_type !== 'single_select')) {
          throw new Error('Priority must be one unambiguous single-select field');
        }
        owners.set(owner, { field: priority[0] });
      } catch {
        owners.set(owner, { unavailable: true });
        reader.warn(`${owner}: native Priority discovery unavailable; project values cannot prove native completeness.`);
      }
    }
    const source = owners.get(owner);
    reader.coverage.prioritySources[owner] = source.unavailable ? 'unavailable' : source.field ? 'native' : 'project';
    if (source.unavailable) {
      item.priorityKnown = false; item.prioritySource = 'unavailable'; item.priority = ''; continue;
    }
    if (!source.field) continue;
    item.prioritySource = 'native'; item.priorityField = source.field; item.priority = '';
    try {
      const values = reader.restPages(`repos/${item.repo}/issues/${item.number}/issue-field-values?per_page=100`);
      const native = values.find((value) => value.issue_field_id === source.field.id);
      if (native?.value !== null && native?.value !== undefined) {
        const option = native.single_select_option ?? source.field.options?.find((entry) => entry.id === native.value);
        if (!option?.name) throw new Error('Unknown Priority option');
        item.priority = option.name;
      }
    } catch {
      item.priorityKnown = false;
      reader.warn(`${item.repo}#${item.number}: native Priority value unavailable.`);
    }
  }
}

export function fetchRepoActivity(reader, repo, windowDays, now = Date.now()) {
  const [owner, name] = repo.split('/');
  const since = now - windowDays * 86400000;
  // Repository connections avoid Search's 1,000-result ceiling entirely.
  const repoConnection = (field, selection, extra, dateField) => reader.connection(`${repo}.${field}`,
    (after) => reader.graphql(`query($owner: String!, $name: String!, $after: String) {
      repository(owner: $owner, name: $name) {
        ${field}(first: 100, after: $after, ${extra}) { ${PAGE} nodes { ${selection} } }
      }
    }`, { owner, name, after }).repository?.[field], undefined, { field: dateField, since });
  const allMergedPrs = repoConnection('pullRequests', `id number title url mergedAt updatedAt
    closingIssuesReferences(first: 100) { ${PAGE} nodes { ${ISSUE_LINK} } }`, 'states: MERGED, orderBy: { field: UPDATED_AT, direction: DESC }', 'updatedAt');
  const mergedPrs = allMergedPrs.filter((pr) => Date.parse(pr.mergedAt) >= since);
  for (const pr of mergedPrs) {
    pr.closingIssues = reader.nodeConnection(pr.id, 'PullRequest', 'closingIssuesReferences',
      ISSUE_LINK, '', pr.closingIssuesReferences);
  }
  const allOpenIssues = repoConnection('issues', 'id number title url createdAt',
    'states: OPEN, orderBy: { field: CREATED_AT, direction: DESC }', 'createdAt');
  const openIssues = allOpenIssues.filter((issue) => Date.parse(issue.createdAt) >= since);
  const milestones = reader.restPages(`repos/${repo}/milestones?state=open&per_page=100`);
  for (const milestone of milestones) {
    if (milestone.due_on) {
      milestone.focus = reader.restPages(`repos/${repo}/issues?state=open&milestone=${milestone.number}&per_page=100`)
        .filter((issue) => !issue.pull_request)
        .map((issue) => ({ number: issue.number, title: issue.title, url: issue.html_url }));
    }
  }
  return { repo, mergedPrs, openIssues, milestones,
    counts: { mergedPrsScanned: allMergedPrs.length, mergedPrsInWindow: mergedPrs.length,
      openIssuesScanned: allOpenIssues.length, openIssuesInWindow: openIssues.length, milestones: milestones.length } };
}

export function issueIsShipped(item) {
  if (item.type === 'PullRequest') return item.merged === true;
  return item.state === 'CLOSED' && item.stateReason === 'COMPLETED' && item.closingPrs.some((pr) => pr.merged);
}

export function buildFindings(items, drafts, repoActivity, options, now = Date.now()) {
  const findings = { mergedNotDone: [], doneNotMerged: [], staleInProgress: [], reviewStarvation: [],
    untrackedWork: [], missingFormalLinks: [], epicDrift: [], milestoneReadiness: [], priorityHygiene: [], closedWithoutMerge: [], closedInActive: [] };
  const key = (item) => `${item.repo.toLowerCase()}#${item.number}`;
  const issueKeys = new Set(items.filter((item) => item.type === 'Issue').map(key));
  const prKeys = new Set(items.filter((item) => item.type === 'PullRequest').map(key));
  for (const item of items) {
    if (item.archived) continue;
    const status = statusSemantic(item.status, options.statusMap);
    const shipped = issueIsShipped(item);
    if (item.priorityKnown && !item.priority) findings.priorityHygiene.push(item);
    if (status === 'deferred') continue;
    if (item.state === 'CLOSED' && !shipped) {
      findings.closedWithoutMerge.push(item);
      if (status === 'inProgress' || status === 'review') findings.closedInActive.push({
        ...item, reason: 'Closed work remains in an active lane; review its disposition. Closure is not shipment evidence.',
      });
    }
    if (shipped && status !== 'done') findings.mergedNotDone.push(item);
    if (status === 'done' && item.state === 'OPEN') findings.doneNotMerged.push(item);
    const hasOpenPr = item.type === 'PullRequest' ? item.state === 'OPEN' : item.closingPrs.some((pr) => pr.state === 'OPEN');
    const idleDays = Math.floor((now - Date.parse(item.updatedAt)) / 86400000);
    if (status === 'inProgress' && item.state === 'OPEN' && !hasOpenPr && idleDays >= options.stale) {
      findings.staleInProgress.push({ ...item, idleDays });
    }
    if (status === 'review' && (shipped || (item.type === 'PullRequest' && item.state === 'OPEN' &&
      !item.isDraft && item.reviewDecision === 'APPROVED' && item.checkState === 'SUCCESS'))) {
      findings.reviewStarvation.push({ ...item, reason: shipped ? 'merge evidenced' : 'approved with green checks; human decision pending' });
    }
    if (item.type === 'Issue' && item.state === 'OPEN' && item.subIssues.length &&
      item.subIssues.every((child) => child.state === 'CLOSED')) findings.epicDrift.push({ ...item, childCount: item.subIssues.length });
  }
  for (const activity of repoActivity) {
    for (const pr of activity.mergedPrs) {
      const boardMembership = prKeys.has(key({ repo: activity.repo, number: pr.number }));
      const linkedBoardIssue = pr.closingIssues.some((issue) => issueKeys.has(key({ repo: issue.repository.nameWithOwner, number: issue.number })));
      const evidence = { ...pr, repo: activity.repo, kind: 'merged-pr', boardMembership, linkedBoardIssue };
      if (!pr.closingIssues.length) findings.missingFormalLinks.push(evidence);
      if (!boardMembership && !linkedBoardIssue) findings.untrackedWork.push({ ...evidence,
        reason: 'No retained membership or formal closing link to this board; other tracking is unverified.' });
    }
    for (const issue of activity.openIssues) {
      if (!issueKeys.has(key({ repo: activity.repo, number: issue.number }))) findings.untrackedWork.push({
        ...issue, repo: activity.repo, kind: 'open-issue', reason: 'No retained membership in this board; other tracking is unverified.' });
    }
    for (const milestone of activity.milestones) {
      const due = Date.parse(milestone.due_on);
      if (due <= now + options.horizon * 86400000) findings.milestoneReadiness.push({
        repo: activity.repo, title: milestone.title, dueOn: milestone.due_on,
        openIssues: milestone.open_issues, closedIssues: milestone.closed_issues,
        overdue: due < now, focus: milestone.focus ?? [],
      });
    }
  }
  const driftKeys = ['mergedNotDone', 'doneNotMerged', 'staleInProgress', 'reviewStarvation', 'epicDrift', 'priorityHygiene', 'closedInActive'];
  const driftItemCount = new Set(driftKeys.flatMap((name) => findings[name].map((item) => item.itemId))).size;
  return { findings, draftCount: drafts.length, driftItemCount };
}

export function renderReport(report) {
  const lines = [`Board sync report — ${report.project.title} (#${report.project.number})`, report.project.url,
    `Coverage: ${report.coverage.complete ? 'complete for disclosed scope' : 'INCOMPLETE'}; ${report.coverage.archivedHistory}`,
    `Items: ${report.counts.boardItems}; archived: ${report.counts.archivedItems}; drafts: ${report.draftCount}; inaccessible: ${report.counts.inaccessibleItems}`,
    `Scope: ${report.options.repos.join(', ')}; activity ${report.options.window}d; stale ${report.options.stale}d; horizon ${report.options.horizon}d`,
    ...report.coverage.warnings.map((warning) => `WARNING: ${warning}`),
    ...report.activityCounts.map((entry) => `${entry.repo}: ${JSON.stringify(entry.counts)}`),
    `Collections: ${report.coverage.connections.length}; pages: ${report.coverage.connections.reduce((sum, entry) => sum + entry.pages, 0)}; deliberate activity-window stops: ${report.coverage.connections.filter((entry) => entry.termination === 'window_boundary').length}`,
    ...report.coverage.connections.filter((entry) => entry.scope === 'activity_window').map((entry) =>
      `Fetched ${entry.name}: ${entry.fetched} of ${entry.total ?? 'unknown'} historical items; ${entry.pages} page(s); ${entry.termination}; since ${entry.since}`),
  ];
  for (const [name, rows] of Object.entries(report.findings)) {
    lines.push(`\n${name}: ${rows.length}`);
    for (const row of rows) {
      const identity = row.number === undefined ? row.repo : `${row.repo}#${row.number}`;
      const evidence = [row.status && `lane=${row.status}`, row.state && `state=${row.state}`,
        row.stateReason && `closure=${row.stateReason}`, row.prioritySource && `Priority=${row.priority || '(empty)'} (${row.prioritySource})`,
        row.mergedAt && `merged=${row.mergedAt}`, row.updatedAt && `updated=${row.updatedAt}`,
        row.reason, row.idleDays !== undefined && `idle=${row.idleDays}d`,
        row.dueOn && `due=${row.dueOn} (${row.closedIssues}/${row.openIssues + row.closedIssues} closed)`,
        row.boardMembership !== undefined && `board membership=${row.boardMembership}`,
        ...(row.closingPrs ?? []).filter((pr) => pr.merged).map((pr) => `merge evidence=${pr.url}`),
      ].filter(Boolean).join('; ');
      lines.push(`  ${identity}: ${row.title} ${row.url ?? ''} — ${evidence}`);
      for (const issue of row.focus ?? []) lines.push(`    focus: #${issue.number} ${issue.title} ${issue.url}`);
    }
  }
  lines.push(`\nVerdict: ${report.verdict}`);
  return `${lines.join('\n')}\n`;
}

export function audit(options, run = ghJson) {
  const reader = createReader(run);
  const project = run(['project', 'view', String(options.project), '--owner', options.owner, '--format', 'json']);
  if (!project.id) throw new Error('Project could not be resolved.');
  const projectFields = reader.nodeConnection(project.id, 'ProjectV2', 'fields',
    '... on ProjectV2SingleSelectField { id name options { id name } }');
  const rawItems = fetchBoardItems(reader, project.id);
  const { items, drafts, inaccessible } = classifyItems(rawItems);
  if (inaccessible.length) reader.warn(`${inaccessible.length} redacted/inaccessible board item(s); not drafts.`);
  for (const item of items) {
    if (!item.archived && statusSemantic(item.status, options.statusMap) === 'unknown') {
      reader.warn(`Unmapped Status ${JSON.stringify(item.status)}; supply --status-map before interpreting lane drift.`);
    }
    item.statusField ??= projectFields.find((field) => field.name === 'Status') ?? null;
    item.priorityField ??= projectFields.find((field) => field.name === 'Priority') ?? null;
  }
  resolvePriorities(reader, items.filter((item) => !item.archived));
  const repos = options.repo ? [options.repo] : [...new Set(items.map((item) => item.repo))];
  const activity = repos.map((repo) => fetchRepoActivity(reader, repo, options.window));
  const result = buildFindings(items, drafts, activity, options);
  const verdict = !reader.coverage.complete ? 'INCOMPLETE audit; no trust verdict available.' : result.driftItemCount
    ? `${result.driftItemCount} distinct item(s) have drift.`
    : result.findings.untrackedWork.length || result.findings.missingFormalLinks.length
      ? 'No item-state drift found; tracking evidence needs review.'
      : 'No drift found within the disclosed scope; closed without merge is not proof of shipment.';
  return { project, options: { ...options, repos }, ...result, verdict, coverage: reader.coverage,
    counts: { boardItems: rawItems.length, archivedItems: rawItems.filter((item) => item.isArchived).length, inaccessibleItems: inaccessible.length },
    activityCounts: activity.map(({ repo, counts }) => ({ repo, counts })) };
}

export function parseArgs(argv) {
  const options = { window: 14, stale: 7, horizon: 7, json: false, owner: '', project: '', repo: '' };
  for (let index = 0; index < argv.length; index += 1) {
    const flag = argv[index];
    if (flag === '--status-map') {
      const value = argv[++index];
      if (!value || value.startsWith('--')) throw new Error('Missing value for --status-map');
      options.statusMap = parseStatusMap(value);
      continue;
    }
    if (flag === '--json') { options.json = true; continue; }
    if (flag === '--help' || flag === '-h') return null;
    const name = flag.slice(2);
    if (!flag.startsWith('--') || !['owner', 'project', 'repo', 'window', 'stale', 'horizon'].includes(name)) throw new Error(`Unknown argument: ${flag}`);
    const value = argv[++index];
    if (!value || value.startsWith('--')) throw new Error(`Missing value for ${flag}`);
    options[name] = ['window', 'stale', 'horizon'].includes(name) ? Number(value) : value;
  }
  if (!options.owner || !/^\d+$/.test(options.project) || Number(options.project) < 1) throw new Error('Require --owner <login> --project <positive integer>.');
  for (const name of ['window', 'stale', 'horizon']) if (!Number.isInteger(options[name]) || options[name] < 1) throw new Error(`--${name} must be a positive integer.`);
  return options;
}

function realPath(path) {
  try { return realpathSync(path); } catch { return path; }
}

// Node resolves the main module through symlinks, so a skill installed via a
// symlinked directory yields an import.meta.url that never equals argv[1].
export function isEntrypoint(argvPath, moduleUrl) {
  if (!argvPath) return false;
  return realPath(argvPath) === realPath(fileURLToPath(moduleUrl));
}

if (isEntrypoint(process.argv[1], import.meta.url)) {
  try {
    const options = parseArgs(process.argv.slice(2));
    if (!options) process.stdout.write('Read-only: --owner <login> --project <number> [--repo owner/name] [--window 14] [--stale 7] [--horizon 7] [--status-map JSON] [--json]\n');
    else {
      const report = audit(options);
      process.stdout.write(options.json ? `${JSON.stringify(report, null, 2)}\n` : renderReport(report));
    }
  } catch (error) {
    process.stderr.write(`Board audit failed: ${error.message}\n`);
    process.exitCode = 1;
  }
}
