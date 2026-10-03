#!/usr/bin/env node
/**
 * Generates bundle directories for Claude marketplace distribution.
 * These are committed bundle snapshots copied from the root skills directory.
 *
 * Usage:
 *   bun scripts/generate-marketplace-bundles.js
 */

import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { basename, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const SKILLS_DIR = join(ROOT, 'skills');
const BUNDLES_DIR = join(ROOT, 'bundles');
const CATEGORIES = JSON.parse(readFileSync(join(__dirname, 'plugin-categories.json'), 'utf-8'));
// Skills and bundles share the repo release; version:sync aligns canonical metadata.
const PACKAGE_VERSION = JSON.parse(readFileSync(join(ROOT, 'package.json'), 'utf-8')).version;

function ensureDir(dir) {
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }
}

function generatePluginJson(name, description) {
  return `${JSON.stringify(
    {
      name,
      version: PACKAGE_VERSION,
      description,
      author: 'Ship Shit Dev',
      license: 'MIT',
      skills: {
        path: './skills',
      },
    },
    null,
    2
  )}\n`;
}

console.log('Generating marketplace bundles...\n');

// Clean existing bundles
if (existsSync(BUNDLES_DIR)) {
  rmSync(BUNDLES_DIR, { recursive: true });
}
ensureDir(BUNDLES_DIR);

const missingSkills = [];

// Generate each category bundle
for (const [category, config] of Object.entries(CATEGORIES.bundles)) {
  const bundleDir = join(BUNDLES_DIR, category);
  const skillsDir = join(bundleDir, 'skills');

  console.log(`Creating bundle: ${category} (${config.skills.length} skills)`);

  ensureDir(skillsDir);

  // Copy skills to bundle
  for (const skillName of config.skills) {
    const srcSkill = join(SKILLS_DIR, skillName);
    const destSkill = join(skillsDir, skillName);

    if (!existsSync(srcSkill)) {
      missingSkills.push(`${category}:${skillName}`);
      continue;
    }

    cpSync(srcSkill, destSkill, {
      recursive: true,
      filter: (source) =>
        !['node_modules', '__pycache__', '.git', '.DS_Store'].includes(basename(source)) &&
        !source.endsWith('.pyc'),
    });
  }

  // Generate plugin.json
  writeFileSync(
    join(bundleDir, 'plugin.json'),
    generatePluginJson(`shipshitdev-${category}`, config.description)
  );

  // Generate README
  const skillList = config.skills.map((s) => `- \`${s}\``).join('\n');
  writeFileSync(
    join(bundleDir, 'README.md'),
    `# Ship Shit Dev - ${category.charAt(0).toUpperCase() + category.slice(1)} Bundle

${config.description}

## Installation

\`\`\`bash
/plugin marketplace add shipshitdev/skills
/plugin install shipshitdev-${category}@shipshitdev
\`\`\`

## Included Skills

${skillList}
`
  );
}

if (missingSkills.length > 0) {
  console.error('\nMissing skills in scripts/plugin-categories.json:');
  for (const missing of missingSkills) {
    console.error(`  - ${missing}`);
  }
  process.exit(1);
}

console.log(`\n✓ Generated ${Object.keys(CATEGORIES.bundles).length} bundles in: ${BUNDLES_DIR}`);
