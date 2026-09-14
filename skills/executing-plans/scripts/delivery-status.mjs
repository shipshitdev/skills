import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

const sha = (value) => typeof value === 'string' && /^[a-f0-9]{40}$/i.test(value);
const text = (value) => typeof value === 'string' && value.trim().length > 0;
const unique = (values) => new Set(values).size === values.length;
const key = ({ name, app }) => JSON.stringify([name, app]);
const result = (state, ...blockers) => ({ state, blockers });
const provider = (value) => text(value) && /^[a-z][a-z0-9-]*$/.test(value);

export function deliveryStatus(receipt) {
  if (!receipt || !sha(receipt.head)) throw new Error('A full current head SHA is required');
  const {
    head, implementationProviders, expectedAcceptanceIds, acceptance,
    review, ci, merge, delivery,
  } = receipt;
  if (!Array.isArray(implementationProviders) || !implementationProviders.length ||
      !implementationProviders.every(provider) || !unique(implementationProviders)) {
    throw new Error('Implementation providers must be unique normalized lab identifiers');
  }
  if (!Array.isArray(expectedAcceptanceIds) || !expectedAcceptanceIds.length ||
      !expectedAcceptanceIds.every(text) || !unique(expectedAcceptanceIds) ||
      !Array.isArray(acceptance) || !acceptance.every((entry) => entry && text(entry.id)) ||
      !unique(acceptance.map(({ id }) => id)) ||
      acceptance.some(({ id }) => !expectedAcceptanceIds.includes(id))) {
    throw new Error('Acceptance IDs must identify the approved scope without duplicates or additions');
  }
  if (!ci || !Array.isArray(ci.required) || !Array.isArray(ci.checks) ||
      !ci.required.every((entry) => entry && text(entry.name) && text(entry.app)) ||
      !ci.checks.every((entry) => entry && text(entry.name) && text(entry.app)) ||
      !unique(ci.required.map(key)) || !unique(ci.checks.map(key))) {
    throw new Error('CI requires unique named checks with source app identifiers');
  }
  if (!merge || typeof merge.merged !== 'boolean' || !delivery ||
      !Array.isArray(delivery.required) || !delivery.required.every(text) ||
      !unique(delivery.required) || !Array.isArray(delivery.results) ||
      !delivery.results.every((entry) => entry && text(entry.name)) ||
      !unique(delivery.results.map(({ name }) => name))) {
    throw new Error('Merge state and unique delivery steps are required');
  }
  const missingAcceptance = expectedAcceptanceIds.filter((id) => !acceptance.some(
    (entry) => entry.id === id && entry.passed === true && entry.head === head && text(entry.evidence),
  ));
  if (missingAcceptance.length) return result('acceptance_pending', ...missingAcceptance);
  if (!review || !provider(review.provider) || implementationProviders.includes(review.provider) ||
      review.independent !== true || review.head !== head || !text(review.reviewer) ||
      !text(review.evidence) || !Number.isInteger(review.unresolvedFindings) ||
      review.unresolvedFindings < 0 || !['PASS', 'CHANGES_REQUESTED'].includes(review.verdict)) {
    return result('review_pending', 'Current independent review from a different implementation lab is required');
  }
  if (review.verdict === 'CHANGES_REQUESTED' || review.unresolvedFindings > 0) {
    return result('changes_requested', 'Resolve findings and obtain a new review of the current head');
  }
  if (ci.discovered !== true || (!ci.required.length && ci.noneRequired !== true)) {
    return result('ci_pending', 'Discover all required checks from current repository policy');
  }
  const requiredChecks = ci.required.map((required) => ({
    required,
    observed: ci.checks.find((check) => key(check) === key(required) && check.head === head),
  }));
  const failed = requiredChecks.filter(({ observed }) => observed &&
    ['failure', 'timed_out', 'cancelled'].includes(observed.conclusion));
  if (failed.length) return result('ci_failed', ...failed.map(({ required }) => key(required)));
  const pending = requiredChecks.filter(({ observed }) => observed?.conclusion !== 'success');
  if (pending.length) return result('ci_pending', ...pending.map(({ required }) => key(required)));
  if (merge.head !== head || (!merge.merged && merge.allowed !== true)) {
    return result('merge_blocked', 'Forge merge gates must pass for the reviewed head');
  }
  if (!merge.merged) return result('merge_ready');
  if (!sha(merge.commit)) throw new Error('A verified merge requires the actual merge commit SHA');
  const pendingDelivery = delivery.required.filter((name) => !delivery.results.some(
    (entry) => entry.name === name && entry.passed === true &&
      entry.commit === merge.commit && text(entry.evidence),
  ));
  if (pendingDelivery.length) return result('delivery_pending', ...pendingDelivery);
  return result('done');
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    if (process.argv.length !== 3) throw new Error('Usage: node delivery-status.mjs <receipt.json>');
    const evaluated = deliveryStatus(JSON.parse(readFileSync(process.argv[2], 'utf8')));
    process.stdout.write(`${JSON.stringify(evaluated)}\n`);
    process.exitCode = ['merge_ready', 'done'].includes(evaluated.state) ? 0 : 1;
  } catch (error) {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 2;
  }
}
