import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

const sha = (value) => /^[0-9a-f]{40}$/.test(value);

export function requirementsFingerprint(body) {
  const requirements = (body || '')
    .replace(/\r\n/g, '\n')
    .split('\n')
    .filter((line) => !line.startsWith('Current plan: '))
    .join('\n')
    .trim();
  return createHash('sha256').update(requirements).digest('hex');
}

export function checkPlan({ issueBody, planBody, headSha }) {
  const body = planBody.replace(/\r\n/g, '\n');
  const blockers = [];
  if (!/^## Implementation Plan\n/.test(body)) blockers.push('Plan heading missing');
  const field = (name) => {
    const matches = [...body.matchAll(new RegExp(`^${name}: (.+)$`, 'gm'))];
    if (matches.length !== 1) {
      blockers.push(`Plan must declare exactly one ${name}`);
      return null;
    }
    return matches[0][1].trim();
  };
  const fields = {
    planRevision: field('Plan revision'),
    baseCommit: field('Base commit'),
    requirementsSha256: field('Requirements SHA256'),
    readiness: field('Readiness'),
  };
  if (fields.readiness !== null && fields.readiness !== 'READY') blockers.push('Readiness is not READY');
  if (fields.planRevision !== null && !/^[1-9][0-9]*$/.test(fields.planRevision)) {
    blockers.push('Plan revision must be a positive integer');
  }
  if (fields.baseCommit !== null && !sha(fields.baseCommit)) {
    blockers.push('Base commit must be a 40-character lowercase SHA');
  } else if (fields.baseCommit !== null && fields.baseCommit !== headSha) {
    blockers.push('Base commit does not match head; return to planner');
  }
  if (fields.requirementsSha256 !== null && fields.requirementsSha256 !== requirementsFingerprint(issueBody)) {
    blockers.push('Requirements changed since planning; return to planner');
  }
  const lines = body.split('\n');
  const stepLine = /^- \[[ xX]\] (S-\d+):/;
  let steps = 0;
  for (let index = 0; index < lines.length; index += 1) {
    const step = lines[index].match(stepLine);
    if (!step) continue;
    steps += 1;
    const block = [];
    for (let next = index + 1; next < lines.length; next += 1) {
      if (stepLine.test(lines[next]) || lines[next].startsWith('#')) break;
      block.push(lines[next]);
    }
    for (const name of ['Touch', 'Pattern', 'Check', 'Stop if']) {
      if (!block.some((line) => new RegExp(`^\\s+- ${name}: \\S`).test(line))) {
        blockers.push(`${step[1]} missing ${name}`);
      }
    }
  }
  if (!steps) blockers.push('Plan has no S-n steps');
  return { ready: blockers.length === 0, blockers, fields };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    const [command, ...args] = process.argv.slice(2);
    if (command === 'digest' && args.length === 1) {
      process.stdout.write(`${requirementsFingerprint(readFileSync(args[0], 'utf8'))}\n`);
      process.exitCode = 0;
    } else if (command === 'check' && args.length === 3) {
      if (!sha(args[2])) throw new Error('Head SHA must be a 40-character lowercase SHA');
      const evaluated = checkPlan({
        issueBody: readFileSync(args[0], 'utf8'),
        planBody: readFileSync(args[1], 'utf8'),
        headSha: args[2],
      });
      process.stdout.write(`${JSON.stringify(evaluated)}\n`);
      process.exitCode = evaluated.ready ? 0 : 1;
    } else {
      throw new Error('Usage: node plan-header.mjs digest <issue-body-file> | check <issue-body-file> <plan-comment-file> <head-sha>');
    }
  } catch (error) {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 2;
  }
}
