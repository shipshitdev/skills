#!/usr/bin/env node
/**
 * Generates bundle directories for Claude marketplace distribution.
 * These are symlink-based bundles that reference skills from agents/.claude/skills/
 *
 * Usage:
 *   bun scripts/generate-marketplace-bundles.js
 */

import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const SKILLS_DIR = join(ROOT, 'skills');
const BUNDLES_DIR = join(ROOT, 'bundles');
const CATEGORIES = JSON.parse(readFileSync(join(__dirname, 'plugin-categories.json'), 'utf-8'));

function ensureDir(dir) {
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }
}

function generatePluginJson(name, description) {
  return JSON.stringify(
    {
      name,
      version: '1.0.0',
      description,
      author: 'Ship Shit Dev',
      license: 'MIT',
      skills: {
        path: './skills',
      },
    },
    null,
    2
  );
}

console.log('Generating marketplace bundles...\n');

// Clean existing bundles
if (existsSync(BUNDLES_DIR)) {
  rmSync(BUNDLES_DIR, { recursive: true });
}
ensureDir(BUNDLES_DIR);

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

    if (existsSync(srcSkill)) {
      cpSync(srcSkill, destSkill, { recursive: true });
    } else {
      console.warn(`  Warning: Skill not found: ${skillName}`);
    }
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

console.log(`\n✓ Generated ${Object.keys(CATEGORIES.bundles).length} bundles in: ${BUNDLES_DIR}`);
