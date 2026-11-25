#!/usr/bin/env node
// Collects the inputs for `/qa prod`: the features a release shipped and the
// cards waiting in the board's human-review column. Read-only; never writes.

import { execFileSync } from 'node:child_process';
import { realpathSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

const EARS = /^\s*(?:[-*]\s*)?(?:\d+\.\s*)?(?:\[[ xX]\]\s*)?((?:WHEN|WHILE|WHERE|IF|THE SYSTEM)\b.*\bSHALL\b.*)$/;
const SLUG = '[\\w.-]+\\/[\\w.-]+';
const CLOSING = new RegExp(
  `\\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\\s*:?\\s+(?:(${SLUG})#(\\d+)|#(\\d+)|https://github\\.com/(${SLUG})/issues/(\\d+))`, 'gi');
const URL_REFERENCE = new RegExp(`github\\.com/(${SLUG})/(?:pull|issues)/(\\d+)\\b`, 'g');
const QUALIFIED_REFERENCE = new RegExp(`(?:^|[^\\w/.-])(${SLUG})#(\\d+)\\b`, 'g');
const BARE_REFERENCE = /(?:^|[^\w&/])#(\d+)\b/g;

export function ghJson(args) {
  const out = execFileSync('gh', args, {
    encoding: 'utf8', maxBuffer: 64 * 1024 * 1024, stdio: ['ignore', 'pipe', 'pipe'],
  });
  return out.trim() ? JSON.parse(out) : null;
}

export function parseArgs(argv) {
  const options = { status: null, json: false };
  const names = { '--repo': 'repo', '--tag': 'tag', '--owner': 'owner', '--project': 'project', '--status': 'status' };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--json') options.json = true;
    else if (names[arg]) {
      const value = argv[(i += 1)];
      if (!value || value.startsWith('--')) throw new Error(`${arg} needs a value`);
      options[names[arg]] = value;
    } else throw new Error(`Unknown argument: ${arg}`);
  }
  if (!options.repo || !/^[\w.-]+\/[\w.-]+$/.test(options.repo)) throw new Error('--repo <owner/name> is required');
  if (options.project && !options.owner) throw new Error('--project needs --owner');
  if (options.project && !/^\d+$/.test(options.project)) throw new Error('--project must be a number');
  return options;
}

const refKey = (ref) => `${ref.repo}#${ref.number}`;

/**
 * Issue or PR references a release body or a list of commit subjects mention, as
 * { repo, number } pairs. Only unqualified `#n` resolves against `defaultRepo`;
 * `owner/repo#n` and github.com URLs keep the repository they name.
 */
export function extractReferences(texts, defaultRepo) {
  const found = new Map();
  const add = (repo, number) => found.set(refKey({ repo, number: Number(number) }), { repo, number: Number(number) });
  for (const text of texts) {
    let value = String(text ?? '');
    for (const m of value.matchAll(URL_REFERENCE)) add(m[1], m[2]);
    value = value.replace(URL_REFERENCE, ' ');
    for (const m of value.matchAll(QUALIFIED_REFERENCE)) add(m[1], m[2]);
    // Qualified spans are consumed first so a repo name ending in `-` or `.` cannot leak a bare `#n`.
    value = value.replace(QUALIFIED_REFERENCE, (match) => ' '.repeat(match.length));
    for (const m of value.matchAll(BARE_REFERENCE)) add(defaultRepo, m[1]);
  }
  return [...found.values()].sort((a, b) => a.repo.localeCompare(b.repo) || a.number - b.number);
}

/** References a PR body promises to close, with the repository each one names. */
export function closingReferences(body, defaultRepo) {
  const found = new Map();
  for (const m of String(body ?? '').matchAll(CLOSING)) {
    const ref = { repo: m[1] ?? m[4] ?? defaultRepo, number: Number(m[2] ?? m[3] ?? m[5]) };
    found.set(refKey(ref), ref);
  }
  return [...found.values()];
}

/** EARS acceptance-criteria lines, which become the test cases. */
export function acceptanceCriteria(body) {
  return String(body ?? '').split(/\r?\n/).map((line) => EARS.exec(line)?.[1].trim()).filter(Boolean);
}

export function buildFeature(entry, linked = [], repo = null) {
  const criteria = [entry.body, ...linked.map((item) => item.body)].flatMap(acceptanceCriteria);
  return {
    repo,
    number: entry.number,
    kind: entry.pull_request ? 'pull_request' : 'issue',
    title: entry.title,
    url: entry.html_url,
    labels: (entry.labels ?? []).map((label) => (typeof label === 'string' ? label : label.name)),
    closes: linked.map((item) => `${item.repo ?? repo}#${item.number}`),
    acceptance: [...new Set(criteria)],
    untestable: criteria.length === 0
      ? 'No EARS acceptance criteria found; derive checks from the title and body and say so.' : undefined,
  };
}

/** Board cards in the human-review column: `status` when given, else Review or legacy Human Review. */
export function humanReviewCards(projectItems, status) {
  const wanted = (status ? [status] : ['Review', 'Human Review']).map((name) => name.trim().toLowerCase());
  return (projectItems?.items ?? [])
    .filter((item) => wanted.includes(String(item.status ?? '').trim().toLowerCase()))
    .map((item) => ({
      title: item.title ?? item.content?.title ?? '',
      type: item.content?.type ?? 'Unknown',
      repository: item.content?.repository ?? null,
      number: item.content?.number ?? null,
      url: item.content?.url ?? null,
      acceptance: acceptanceCriteria(item.content?.body),
    }));
}

function previousTag(releases, tag) {
  const published = releases.filter((r) => !r.draft && !r.prerelease)
    .sort((a, b) => Date.parse(b.published_at) - Date.parse(a.published_at));
  const index = published.findIndex((r) => r.tag_name === tag);
  return index >= 0 ? published[index + 1]?.tag_name ?? null : null;
}

export function collect(options, run = ghJson) {
  const { repo } = options;
  const warnings = [];
  const release = run(['release', 'view', ...(options.tag ? [options.tag] : []), '--repo', repo,
    '--json', 'tagName,name,body,url,publishedAt,isDraft,isPrerelease']);
  if (release.isDraft) throw new Error(`Release ${release.tagName} is a draft; QA starts after it is published.`);

  const releases = run(['api', '--method', 'GET', `repos/${repo}/releases?per_page=30`]) ?? [];
  const previous = previousTag(releases, release.tagName);
  const subjects = [];
  if (previous) {
    const compare = run(['api', '--method', 'GET', `repos/${repo}/compare/${previous}...${release.tagName}`]);
    subjects.push(...(compare?.commits ?? []).map((c) => String(c.commit?.message ?? '').split('\n')[0]));
    if (compare?.commits?.length >= 250) warnings.push('Compare result is capped at 250 commits; the feature list may be incomplete.');
  } else warnings.push('No previous published release found; the feature list comes from the release notes alone.');

  const fetchEntry = (ref) => {
    try { return { ...run(['api', '--method', 'GET', `repos/${ref.repo}/issues/${ref.number}`]), repo: ref.repo }; } catch (error) {
      warnings.push(`${refKey(ref)} unreadable: ${String(error.message).split('\n')[0]}`);
      return null;
    }
  };
  const features = [];
  for (const ref of extractReferences([release.body, ...subjects], repo)) {
    const entry = fetchEntry(ref);
    if (!entry) continue;
    const linked = entry.pull_request ? closingReferences(entry.body, ref.repo).map(fetchEntry).filter(Boolean) : [];
    features.push(buildFeature(entry, linked, ref.repo));
  }

  let cards = null;
  if (options.project) {
    const items = run(['project', 'item-list', options.project, '--owner', options.owner,
      '--limit', '500', '--format', 'json']);
    if ((items?.totalCount ?? 0) > (items?.items?.length ?? 0)) warnings.push('Board has more than 500 items; the review queue may be incomplete.');
    cards = humanReviewCards(items, options.status);
  } else warnings.push('No --project given; Review cards were not collected.');

  return {
    repo,
    release: { tag: release.tagName, name: release.name, url: release.url, publishedAt: release.publishedAt, previousTag: previous },
    features, humanReview: cards, warnings,
  };
}

export function render(report) {
  const lines = [`Release ${report.release.tag} (${report.release.url})`, `Features: ${report.features.length}`];
  for (const f of report.features) {
    lines.push(`- ${f.repo}#${f.number} ${f.title} [${f.kind}] criteria=${f.acceptance.length}`);
  }
  if (report.humanReview) {
    lines.push(`Review cards: ${report.humanReview.length}`);
    for (const c of report.humanReview) lines.push(`- ${c.repository ?? ''}#${c.number ?? '?'} ${c.title} criteria=${c.acceptance.length}`);
  }
  for (const w of report.warnings) lines.push(`warning: ${w}`);
  return `${lines.join('\n')}\n`;
}

const isMain = process.argv[1] && import.meta.url === pathToFileURL(realpathSync(process.argv[1])).href;
if (isMain) {
  try {
    const report = collect(parseArgs(process.argv.slice(2)));
    const json = process.argv.includes('--json');
    process.stdout.write(json ? `${JSON.stringify(report, null, 2)}\n` : render(report));
  } catch (error) {
    process.stderr.write(`${error.message}\n`);
    process.exit(1);
  }
}
