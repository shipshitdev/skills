#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { existsSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const digest = (content) => createHash('sha256').update(content).digest('hex');

try {
  const args = process.argv.slice(2);
  let root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
  let check = false;
  for (let index = 0; index < args.length; index += 1) {
    if (args[index] === '--check') check = true;
    else if (args[index] === '--root' && args[index + 1]) root = resolve(args[++index]);
    else throw new Error(`Unknown or incomplete argument: ${args[index]}`);
  }
  const version = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8')).version;
  if (typeof version !== 'string' || !/^\d+\.\d+\.\d+(?:-[\w.-]+)?(?:\+[\w.-]+)?$/.test(version)) {
    throw new Error('package.json must contain a release version');
  }
  const changes = new Map();
  let count = 0;
  for (const directory of ['skills', '.agents/skills']) {
    if (directory !== 'skills' && !existsSync(join(root, directory))) continue;
    for (const entry of readdirSync(join(root, directory), { withFileTypes: true })) {
      if (!entry.isDirectory()) continue;
      const path = `${directory}/${entry.name}/SKILL.md`;
      if (!existsSync(join(root, path))) continue;
      count += 1;
      const before = readFileSync(join(root, path), 'utf8');
      const frontmatter = before.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);
      const metadata = frontmatter?.[1].match(/^metadata:\r?\n(?:[ \t].*\r?\n|\r?\n|[ \t].*$)*/m);
      const fields = metadata?.[0].match(/^ {2}version:[^\r\n]*/gm);
      if (fields?.length !== 1) throw new Error(`${path}: require one metadata.version`);
      const replacement = metadata[0].replace(fields[0], `  version: "${version}"`);
      const offset = frontmatter.index + frontmatter[0].indexOf(frontmatter[1]) + metadata.index;
      const after =
        before.slice(0, offset) + replacement + before.slice(offset + metadata[0].length);
      if (after !== before) changes.set(path, { before, after });

      const pluginPath = `${directory}/${entry.name}/plugin.json`;
      if (directory !== 'skills' && !existsSync(join(root, pluginPath))) continue;
      const pluginBefore = readFileSync(join(root, pluginPath), 'utf8');
      const plugin = JSON.parse(pluginBefore);
      if (plugin.version !== version) {
        plugin.version = version;
        changes.set(pluginPath, {
          before: pluginBefore,
          after: `${JSON.stringify(plugin, null, 2)}\n`,
        });
      }
    }
  }
  if (!count) throw new Error('No canonical skills found');
  if (check) {
    if (changes.size) {
      process.stderr.write(
        `${changes.size} skill metadata files differ from repository ${version}:\n`
      );
      for (const path of changes.keys()) process.stderr.write(`  ${path}\n`);
      process.exitCode = 1;
    } else
      process.stdout.write(`All ${count} skills and plugins use repository version ${version}.\n`);
  } else {
    // Only version edits to already accepted bytes may advance fingerprints.
    // Unreviewed body changes retain their old hashes and fail pstack:verify.
    const mappingPath = join(root, 'upstream/pstack/mapping.json');
    let mapping;
    let updated = 0;
    if (existsSync(mappingPath)) {
      mapping = JSON.parse(readFileSync(mappingPath, 'utf8'));
      for (const item of Object.values(mapping.files)) {
        for (const destination of item.destinations || []) {
          const change = changes.get(destination.path);
          if (change && destination.sha256 === digest(change.before)) {
            destination.sha256 = digest(change.after);
            updated += 1;
          }
        }
      }
    }
    // Validate every source and the mapping before writing any metadata.
    for (const [path, change] of changes) writeFileSync(join(root, path), change.after);
    if (updated) writeFileSync(mappingPath, `${JSON.stringify(mapping, null, 2)}\n`);
    process.stdout.write(
      `Aligned ${count} skills to ${version}; changed ${changes.size} files and ${updated} accepted version fingerprints.\n`
    );
  }
} catch (error) {
  process.stderr.write(`Skill version alignment failed: ${error.message}\n`);
  process.exitCode = 1;
}
