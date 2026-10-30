#!/usr/bin/env bun
import { YAML } from 'bun';
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const skills = process.argv[2] ?? fileURLToPath(new URL('../skills', import.meta.url));
const directories = readdirSync(skills, { withFileTypes: true }).filter((entry) => entry.isDirectory());
let errors = 0;

for (const directory of directories) {
  const path = join(skills, directory.name, 'agents/openai.yaml');
  try {
    const config = YAML.parse(readFileSync(path, 'utf8'));
    if (config?.policy?.allow_implicit_invocation !== false) {
      throw new Error('set policy.allow_implicit_invocation to the boolean false');
    }
  } catch (error) {
    console.error(`error: ${path}: ${error.message}`);
    errors += 1;
  }
}

console.log(`${directories.length} Codex invocation policies checked, ${errors} errors`);
process.exitCode = errors ? 1 : 0;
