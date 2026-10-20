#!/usr/bin/env node

import { execFileSync } from 'node:child_process';

// The dev-loop board-as-truth model: five human-facing columns. The AI-loop
// sub-phases (planning/executing/testing/shipping) live inside In Progress as
// `loop:*` labels — they are not board columns. Human Review is the human gate.
const DEFAULT_STATUS_OPTIONS = [
  {
    name: 'Backlog',
    color: 'GRAY',
    description: 'Not started; an un-gated issue waits here',
  },
  {
    name: 'In Progress',
    color: 'YELLOW',
    description: 'An agent is implementing (claim → branch → qa → PR)',
  },
  {
    name: 'Human Review',
    color: 'BLUE',
    description: 'PR open; awaiting human review/merge',
  },
  {
    name: 'Done',
    color: 'PURPLE',
    description: 'Merged / closed',
  },
  {
    name: 'Deferred',
    color: 'GRAY',
    description: 'Parked for later / wontfix',
  },
];

const DEFAULT_PRIORITY_OPTIONS = [
  {
    name: 'P0 🔥',
    color: 'RED',
    description: 'Critical priority',
  },
  {
    name: 'P1',
    color: 'ORANGE',
    description: 'High priority',
  },
  {
    name: 'P2',
    color: 'YELLOW',
    description: 'Normal priority',
  },
  {
    name: 'P3',
    color: 'GRAY',
    description: 'Low priority',
  },
];


function parseArgs(argv) {
  const args = {
    apply: false,
    allOpen: false,
    exact: false,
    includeClosed: false,
    owner: '',
    priority: '',
    project: '',
    status: '',
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === '--apply') {
      args.apply = true;
    } else if (arg === '--all-open') {
      args.allOpen = true;
    } else if (arg === '--exact') {
      args.exact = true;
    } else if (arg === '--include-closed') {
      args.includeClosed = true;
    } else if (arg === '--owner') {
      args.owner = readValue(argv, (index += 1), arg);
    } else if (arg === '--project') {
      args.project = readValue(argv, (index += 1), arg);
    } else if (arg === '--status') {
      args.status = readValue(argv, (index += 1), arg);
    } else if (arg === '--priority') {
      args.priority = readValue(argv, (index += 1), arg);
    } else if (arg === '--help' || arg === '-h') {
      printHelp();
      process.exit(0);
    } else {
      fail(`Unknown argument: ${arg}`);
    }
  }

  if (!args.owner) {
    fail('Missing required --owner <login>.');
  }

  if (!args.project && !args.allOpen) {
    fail('Pass --project <number> or --all-open.');
  }

  if (args.project && args.allOpen) {
    fail('Use either --project <number> or --all-open, not both.');
  }

  return args;
}

function readValue(argv, index, flag) {
  const value = argv[index];
  if (!value || value.startsWith('--')) {
    fail(`Missing value for ${flag}.`);
  }
  return value;
}

function printHelp() {
  process.stdout.write(`Usage:
  node setup-github-board.mjs --owner <owner> --project <number> [--apply]
  node setup-github-board.mjs --owner <owner> --all-open [--apply]

Options:
  --status "Backlog,In Progress,Human Review,Done,Deferred"
  --priority "P0 🔥,P1,P2,P3"
  --exact             Remove non-canonical options after approval.
  --include-closed    Include closed projects when processing all projects.

Dry-run is the default. Use --apply to write GitHub Projects fields.
`);
}

function fail(message) {
  process.stderr.write(`${message}\n`);
  process.exit(1);
}

function gh(args, { throwOnError = false } = {}) {
  try {
    return execFileSync('gh', args, {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
    }).trim();
  } catch (error) {
    const stderr = error.stderr ? String(error.stderr).trim() : '';
    const detail = stderr || error.message;
    const message = `gh ${args.join(' ')} failed:\n${detail}`;
    if (throwOnError) throw new Error(message);
    fail(message);
  }
}

function ghJson(args, options) {
  const output = gh(args, options);
  return output ? JSON.parse(output) : {};
}

function graphql(query, variables = {}) {
  const args = ['api', 'graphql', '-f', `query=${query}`];
  for (const [key, value] of Object.entries(variables)) {
    args.push(typeof value === 'string' ? '-f' : '-F', `${key}=${value}`);
  }
  return ghJson(args);
}

function listProjects(owner, includeClosed) {
  const identity = ghJson(['api', '--method', 'GET', `users/${owner}`]);
  const type = identity.type === 'Organization' ? 'Organization' : 'User';
  return readConnection(identity.node_id, type, 'projectsV2',
    'id number closed', includeClosed ? '' : ', query: "is:open"');
}

function readConnection(id, type, field, selection, extra = '') {
  const nodes = [];
  let after = null;
  const cursors = new Set();
  do {
    const response = graphql(`query($id: ID!, $after: String) {
      node(id: $id) { ... on ${type} {
        ${field}(first: 100, after: $after ${extra}) {
          pageInfo { hasNextPage endCursor } nodes { ${selection} }
        }
      } }
    }`, { id, ...(after ? { after } : {}) });
    const page = response.data?.node?.[field];
    if (!page?.nodes || !page.pageInfo) fail(`Could not fully read ${field}; no changes applied.`);
    nodes.push(...page.nodes);
    if (!page.pageInfo.hasNextPage) break;
    after = page.pageInfo.endCursor;
    if (!after || cursors.has(after)) fail(`Invalid cursor for ${field}; no changes applied.`);
    cursors.add(after);
  } while (true);
  return nodes;
}

function projectSummary(owner, number) {
  return ghJson(['project', 'view', String(number), '--owner', owner, '--format', 'json']);
}

function projectDetails(projectId) {
  const response = graphql('query($id: ID!) { node(id: $id) { ... on ProjectV2 { id title url closed } } }', { id: projectId });
  const project = response.data?.node;
  if (!project) fail(`Could not load project node ${projectId}.`);
  project.fields = { nodes: readConnection(projectId, 'ProjectV2', 'fields', `
    ... on ProjectV2Field { id name dataType }
    ... on ProjectV2IterationField { id name dataType }
    ... on ProjectV2SingleSelectField { id name dataType options { id name color description } }
  `) };
  project.views = { nodes: readConnection(projectId, 'ProjectV2', 'views', 'id name layout') };
  project.issueOwners = readConnection(projectId, 'ProjectV2', 'items',
    'content { ... on Issue { repository { owner { login } } } }')
    .map((item) => item.content?.repository?.owner?.login).filter(Boolean);
  return project;
}

function optionsFromCsv(value, defaults) {
  if (!value) {
    return defaults;
  }

  return value
    .split(',')
    .map((name) => name.trim())
    .filter(Boolean)
    .map((name) => {
      const fallback = defaults.find((option) => normalizeOptionName(option.name) === normalizeOptionName(name));
      return {
        name,
        color: fallback?.color ?? 'GRAY',
        description: fallback?.description ?? '',
      };
    });
}

function normalizeOptionName(name) {
  return name
    .normalize('NFKD')
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '');
}

function fieldByName(fields, name) {
  return fields.find((field) => field.name === name);
}

function buildPlan(field, fieldName, desiredOptions, exact) {
  if (!field) {
    return {
      action: 'create',
      fieldName,
      fieldId: '',
      desiredOptions,
      missingOptions: desiredOptions.map((option) => option.name),
      renamedOptions: [],
      preservedOptions: [],
      changed: true,
      error: '',
    };
  }

  if (field.dataType !== 'SINGLE_SELECT') {
    return {
      action: 'blocked',
      fieldName,
      fieldId: field.id,
      desiredOptions: [],
      missingOptions: [],
      renamedOptions: [],
      preservedOptions: [],
      changed: false,
      error: `${fieldName} exists but is ${field.dataType}, not SINGLE_SELECT.`,
    };
  }

  const existingOptions = field.options ?? [];
  const usedOptionIndexes = new Set();
  const mergedOptions = [];
  const missingOptions = [];
  const renamedOptions = [];

  for (const desired of desiredOptions) {
    const matchIndex = existingOptions.findIndex(
      (option, index) =>
        !usedOptionIndexes.has(index) &&
        normalizeOptionName(option.name) === normalizeOptionName(desired.name)
    );

    if (matchIndex === -1) {
      missingOptions.push(desired.name);
      mergedOptions.push(desired);
      continue;
    }

    usedOptionIndexes.add(matchIndex);
    const existing = existingOptions[matchIndex];
    if (existing.name !== desired.name) {
      renamedOptions.push(`${existing.name} -> ${desired.name}`);
    }

    mergedOptions.push({
      id: existing.id,
      name: desired.name,
      color: existing.color,
      description: existing.description ?? '',
    });
  }

  const preservedOptions = [];
  if (!exact) {
    for (const [index, option] of existingOptions.entries()) {
      if (!usedOptionIndexes.has(index)) {
        preservedOptions.push(option.name);
        mergedOptions.push(option);
      }
    }
  }

  return {
    action: 'update',
    fieldName,
    fieldId: field.id,
    desiredOptions: mergedOptions,
    missingOptions,
    renamedOptions,
    preservedOptions,
    changed: optionsChanged(existingOptions, mergedOptions),
    error: '',
  };
}

function optionsChanged(existingOptions, desiredOptions) {
  const serialize = (options) =>
    options.map((option) => ({
      id: option.id ?? '',
      name: option.name,
      color: option.color,
      description: option.description ?? '',
    }));

  return JSON.stringify(serialize(existingOptions)) !== JSON.stringify(serialize(desiredOptions));
}

function graphQlString(value) {
  return JSON.stringify(value);
}

function optionsInput(options) {
  return `[${options
    .map((option) => {
      const id = option.id ? `id: ${graphQlString(option.id)}, ` : '';
      return `{ ${id}name: ${graphQlString(option.name)}, color: ${option.color}, description: ${graphQlString(
        option.description ?? ''
      )} }`;
    })
    .join(', ')}]`;
}

function createSingleSelectField(projectId, plan) {
  const mutation = `
mutation {
  createProjectV2Field(input: {
    projectId: ${graphQlString(projectId)}
    dataType: SINGLE_SELECT
    name: ${graphQlString(plan.fieldName)}
    singleSelectOptions: ${optionsInput(plan.desiredOptions)}
  }) {
    projectV2Field {
      ... on ProjectV2SingleSelectField {
        id
        name
      }
    }
  }
}`;

  graphql(mutation);
}

function updateSingleSelectField(plan) {
  const mutation = `
mutation {
  updateProjectV2Field(input: {
    fieldId: ${graphQlString(plan.fieldId)}
    singleSelectOptions: ${optionsInput(plan.desiredOptions)}
  }) {
    projectV2Field {
      ... on ProjectV2SingleSelectField {
        id
        name
      }
    }
  }
}`;

  graphql(mutation);
}

function boardViewNames(project) {
  return (project.views?.nodes ?? [])
    .filter((view) => view.layout === 'BOARD_LAYOUT')
    .map((view) => view.name);
}

function printPlan(plan) {
  if (plan.error) {
    process.stdout.write(`  ${plan.fieldName}: BLOCKED - ${plan.error}\n`);
    return;
  }

  if (plan.action === 'create') {
    process.stdout.write(`  ${plan.fieldName}: create with ${formatNames(plan.desiredOptions)}\n`);
    return;
  }

  if (!plan.changed) {
    process.stdout.write(`  ${plan.fieldName}: already matches\n`);
    return;
  }

  process.stdout.write(`  ${plan.fieldName}: update to ${formatNames(plan.desiredOptions)}\n`);
  if (plan.missingOptions.length > 0) {
    process.stdout.write(`    add: ${plan.missingOptions.join(', ')}\n`);
  }
  if (plan.renamedOptions.length > 0) {
    process.stdout.write(`    rename: ${plan.renamedOptions.join(', ')}\n`);
  }
  if (plan.preservedOptions.length > 0) {
    process.stdout.write(`    preserve extra: ${plan.preservedOptions.join(', ')}\n`);
  }
}

function formatNames(options) {
  return options.map((option) => option.name).join(', ');
}

function nativePriority(owner) {
  const identity = ghJson(['api', '--method', 'GET', `users/${owner}`], { throwOnError: true });
  if (identity.type !== 'Organization') return null;
  // A failed discovery stops before writes; it does not justify a duplicate field.
  const pages = ghJson(['api', '--method', 'GET', '--paginate', '--slurp',
    `orgs/${owner}/issue-fields`, '-H', 'X-GitHub-Api-Version: 2026-03-10'], { throwOnError: true });
  const fields = pages.flat().filter((field) => field.name === 'Priority');
  if (fields.length > 1 || (fields[0] && (fields[0].data_type !== 'single_select' || !Array.isArray(fields[0].options)))) {
    throw new Error('Native Priority is ambiguous or its single-select options are unavailable; inspect organization schema before applying.');
  }
  return fields[0] ?? null;
}

function normalizeProject(owner, number, options) {
  const summary = projectSummary(owner, number);
  const project = projectDetails(summary.id);
  const fields = project.fields?.nodes ?? [];
  const statusPlan = buildPlan(
    fieldByName(fields, 'Status'),
    'Status',
    options.statusOptions,
    options.exact
  );
  let native;
  let priorityError;
  try {
    native = [...new Set([owner, ...project.issueOwners])]
      .map((issueOwner) => nativePriority(issueOwner)).find(Boolean);
  } catch (error) {
    priorityError = error.message;
  }
  const priorityPlan = native || priorityError ? null : buildPlan(
    fieldByName(fields, 'Priority'),
    'Priority',
    options.priorityOptions,
    options.exact
  );
  const boardViews = boardViewNames(project);
  const plans = [statusPlan, priorityPlan].filter(Boolean);
  if (native) {
    process.stdout.write(`  Priority: organization-native field ${native.id}; options: ${native.options.map((option) => option.name).join(', ')}; project Priority normalization skipped\n`);
  }
  const blocked = plans.filter((plan) => plan.error);
  const changed = plans.filter((plan) => !plan.error && plan.changed);

  process.stdout.write(`\n${project.title} (#${number})\n`);
  process.stdout.write(`${project.url}\n`);
  process.stdout.write(
    `  Board view: ${boardViews.length > 0 ? `yes (${boardViews.join(', ')})` : 'missing'}\n`
  );

  for (const plan of plans) {
    printPlan(plan);
  }

  if (boardViews.length === 0) {
    process.stdout.write(
      '  warning: field normalization cannot create a board view through the public GitHub Projects API\n'
    );
  }

  if (priorityError) {
    process.stdout.write(`  WARNING: Priority discovery unavailable; its plan is withheld. ${priorityError}\n`);
    if (options.apply) {
      process.stdout.write('  BLOCKED: no changes applied while Priority ownership is unresolved.\n');
      process.exitCode = 2;
    } else {
      process.stdout.write('  INCOMPLETE audit: Status/view evidence above remains available.\n');
    }
    return;
  }

  if (blocked.length > 0) {
    process.exitCode = 2;
    return;
  }

  if (!options.apply) {
    if (changed.length > 0) {
      process.stdout.write('  dry-run: rerun with --apply to write these field changes\n');
    }
    return;
  }

  for (const plan of changed) {
    if (plan.action === 'create') {
      createSingleSelectField(project.id, plan);
    } else if (plan.action === 'update') {
      updateSingleSelectField(plan);
    }
  }

  process.stdout.write(`  applied: ${changed.length} field change(s)\n`);
}

const args = parseArgs(process.argv.slice(2));
const statusOptions = optionsFromCsv(args.status, DEFAULT_STATUS_OPTIONS);
const priorityOptions = optionsFromCsv(args.priority, DEFAULT_PRIORITY_OPTIONS);

if (args.allOpen) {
  const projects = listProjects(args.owner, args.includeClosed).filter(
    (project) => args.includeClosed || !project.closed
  );

  for (const project of projects) {
    normalizeProject(args.owner, project.number, {
      apply: args.apply,
      exact: args.exact,
      priorityOptions,
      statusOptions,
    });
  }
} else {
  normalizeProject(args.owner, args.project, {
    apply: args.apply,
    exact: args.exact,
    priorityOptions,
    statusOptions,
  });
}
