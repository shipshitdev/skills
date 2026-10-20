import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { chmodSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../../../', import.meta.url));
const script = fileURLToPath(new URL('./setup-github-board.mjs', import.meta.url));

function runNormalizer(mode, apply = false, allOpen = false) {
  mkdirSync(join(root, '.tmp'), { recursive: true });
  const directory = mkdtempSync(join(root, '.tmp/board-normalizer-'));
  const log = join(directory, 'calls.jsonl');
  writeFileSync(join(directory, 'gh'), `#!/usr/bin/env node
const fs = require('node:fs');
const args = process.argv.slice(2);
fs.appendFileSync(process.env.FIXTURE_LOG, JSON.stringify(args) + '\\n');
const query = args.find(x => x.startsWith('query=')) ?? '';
const page = nodes => ({nodes, pageInfo: {hasNextPage:false}});
const mode = process.env.FIXTURE_MODE;
let result;
if (args[0] === 'project') result = {id:'PROJECT'};
else if (query.includes('projectsV2(first:')) result = {data:{node:{projectsV2:page([{id:'PROJECT',number:1,closed:false}])}}};
else if (query.includes('mutation')) result = {data:{}};
else if (query.includes('fields(first:')) result = {data:{node:{fields:page([])}}};
else if (query.includes('items(first:')) result = {data:{node:{items:page(mode === 'cross-org' ? [{content:{repository:{owner:{login:'native-org'}}}}] : [])}}};
else if (query.includes('views(first:')) result = {data:{node:{views:page([{id:'VIEW', name:'Board',layout:'BOARD_LAYOUT'}])}}};
else if (query) result = {data:{node:{id:'PROJECT',title:'Board',url:'https://github.com/orgs/org/projects/1',closed:false}}};
else if (args.includes('users/org')) result = {node_id:'OWNER',type:mode === 'cross-org' ? 'User' : 'Organization'};
else if (args.includes('users/native-org')) result = {type:'Organization'};
else if (args.includes('orgs/org/issue-fields') || args.includes('orgs/native-org/issue-fields')) {
  if (mode === 'unavailable') { process.stderr.write('403 forbidden'); process.exit(1); }
  result = [['native','cross-org','malformed'].includes(mode) ? [{id:9,name:'Priority',data_type:'single_select',...(mode === 'malformed' ? {} : {options:[{id:1,name:'High'}]})}] : []];
} else throw new Error('Unexpected call ' + args);
process.stdout.write(JSON.stringify(result));
`);
  chmodSync(join(directory, 'gh'), 0o755);
  let output = ''; let failed = false;
  try {
    output = execFileSync(process.execPath, [script, '--owner', 'org', ...(allOpen ? ['--all-open'] : ['--project', '1']), ...(apply ? ['--apply'] : [])], {
      encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'],
      env: { ...process.env, PATH: `${directory}:${process.env.PATH}`, FIXTURE_LOG: log, FIXTURE_MODE: mode },
    });
  } catch (error) { failed = true; output = String(error.stdout) + String(error.stderr); }
  const calls = readFileSync(log, 'utf8').trim().split('\n').map(JSON.parse);
  rmSync(directory, { recursive: true, force: true });
  return { output, failed, calls, mutations: calls.flat().filter((arg) => arg.includes('mutation')) };
}

test('native schema blocks project Priority creation even during authorized normalization', () => {
  const result = runNormalizer('native', true);
  assert.equal(result.failed, false);
  assert.match(result.output, /organization-native field 9/);
  assert.equal(result.mutations.length, 1);
  assert.match(result.mutations[0], /name: "Status"/);
  assert.doesNotMatch(result.mutations[0], /Priority/);
});

test('verified project-local schema supports existing Priority configuration', () => {
  const result = runNormalizer('project', true);
  assert.equal(result.failed, false);
  assert.equal(result.mutations.length, 2);
  assert.ok(result.mutations.some((query) => query.includes('name: "Priority"')));
});

test('read-only default and unavailable native schema make no mutations', () => {
  assert.equal(runNormalizer('native').mutations.length, 0);
  const result = runNormalizer('unavailable', true);
  assert.equal(result.failed, true);
  assert.equal(result.mutations.length, 0);
});


test('user-owned boards respect native fields on linked organization issues', () => {
  const result = runNormalizer('cross-org', true);
  assert.equal(result.failed, false);
  assert.equal(result.mutations.length, 1);
  assert.doesNotMatch(result.mutations[0], /Priority/);
});


test('read-only native discovery failures retain the Status/view audit and withhold Priority', () => {
  const result = runNormalizer('unavailable');
  assert.equal(result.failed,false);
  assert.match(result.output,/Status: create/);
  assert.match(result.output,/Board view: yes/);
  assert.match(result.output,/INCOMPLETE audit/);
  assert.match(result.output,/Priority discovery unavailable; its plan is withheld/);
  assert.doesNotMatch(result.output,/Priority: create/);
  assert.equal(result.mutations.length,0);
  const apply = runNormalizer('unavailable',true);
  assert.equal(apply.failed,true);
  assert.match(apply.output,/Status: create/);
  assert.match(apply.output,/BLOCKED: no changes applied/);
  assert.equal(apply.mutations.length,0);
});

test('all-open enumeration resolves each title and URL from project details', () => {
  const result=runNormalizer('native',false,true);
  assert.equal(result.failed,false);
  assert.match(result.output,/Board \(#1\)/);
  assert.match(result.output,/https:\/\/github.com\/orgs\/org\/projects\/1/);
  assert.ok(result.calls.some((args)=>args.some((arg)=>arg.includes('projectsV2(first:'))));
  assert.equal(result.mutations.length,0);
});

test('malformed native options preserve a partial audit and block every write', () => {
  const report = runNormalizer('malformed');
  assert.equal(report.failed, false);
  assert.match(report.output, /INCOMPLETE audit/);
  assert.match(report.output, /Status: create/);
  assert.equal(report.mutations.length, 0);
  const apply = runNormalizer('malformed', true);
  assert.equal(apply.failed, true);
  assert.equal(apply.mutations.length, 0);
});

test('GraphQL identity variables remain strings in the CLI transport', () => {
  const report = runNormalizer('native');
  for (const args of report.calls.filter((call) => call.includes('graphql'))) {
    for (const [index, arg] of args.entries()) {
      if (/^(id|after)=/.test(arg)) assert.equal(args[index - 1], '-f');
    }
  }
});
