#!/usr/bin/env bun
/**
 * Generate plugin.json manifest from skill/command metadata
 */

const fs = require('fs');
const path = require('path');

/**
 * Extract YAML frontmatter from markdown file
 */
function extractFrontmatter(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);

  if (!frontmatterMatch) {
    return null;
  }

  const frontmatterText = frontmatterMatch[1];
  const frontmatter = {};

  frontmatterText.split('\n').forEach((line) => {
    const match = line.match(/^(\w+):\s*(.+)$/);
    if (match) {
      const key = match[1];
      let value = match[2].trim();

      // Handle array values (tags, etc.)
      if (value.startsWith('[') && value.endsWith(']')) {
        // Simple array parsing - handle basic cases
        value = value
          .slice(1, -1)
          .split(',')
          .map((v) => v.trim().replace(/^["']|["']$/g, ''));
      } else if (value.startsWith('-')) {
        // YAML list item
        value = [value.slice(1).trim()];
      } else {
        // Remove quotes if present
        value = value.replace(/^["']|["']$/g, '');
      }

      frontmatter[key] = value;
    }
  });

  return frontmatter;
}

/**
 * Generate plugin manifest
 */
function generateManifest(options) {
  const {
    name,
    description,
    version = '1.0.0',
    type, // 'skill' or 'command'
    platform, // 'cursor', 'claude', 'codex'
    skillName,
    commandName,
    homepage,
    repository = 'https://github.com/shipshitdev/skills',
    license = 'MIT',
    tags = [],
    author = {
      name: 'Ship Shit Dev',
    },
  } = options;

  const pluginName =
    name ||
    (type === 'skill' ? `@agenticdev/skill-${skillName}` : `@agenticdev/command-${commandName}`);

  const manifest = {
    name: pluginName,
    description: description || `Ship Shit Dev ${type}: ${skillName || commandName}`,
    version: version,
    author: author,
    homepage: homepage || `https://skillhub.com/plugins/${skillName || commandName}`,
    repository: repository,
    license: license,
  };

  if (tags && tags.length > 0) {
    manifest.keywords = tags;
  }

  // Add compatibility info
  manifest.compatibility = {
    claude: '>=1.0.33',
    cursor: '>=0.40.0',
    codex: '>=0.1.0',
    openclaw: '>=0.1.0',
    gemini: '>=0.1.0',
  };

  return manifest;
}

/**
 * Generate manifest from skill directory
 */
function generateFromSkill(skillPath, platform, options = {}) {
  const skillName = path.basename(skillPath);
  const skillMdPath = path.join(skillPath, 'SKILL.md');

  if (!fs.existsSync(skillMdPath)) {
    throw new Error(`SKILL.md not found in ${skillPath}`);
  }

  const frontmatter = extractFrontmatter(skillMdPath);
  if (!frontmatter) {
    throw new Error(`No frontmatter found in ${skillMdPath}`);
  }

  const tags = frontmatter.tags || [];
  if (Array.isArray(tags) && tags.length === 0 && typeof frontmatter.tags === 'string') {
    // Handle single tag as string
    tags.push(frontmatter.tags);
  }

  return generateManifest({
    type: 'skill',
    platform,
    skillName,
    description: frontmatter.description,
    version: frontmatter.version || '1.0.0',
    tags: Array.isArray(tags) ? tags : [tags],
    ...options,
  });
}

/**
 * Generate manifest from command file
 */
function generateFromCommand(commandPath, platform, options = {}) {
  const commandName = path.basename(commandPath, '.md');

  // Commands don't have frontmatter, so we read the first line as description
  const content = fs.readFileSync(commandPath, 'utf8');
  const firstLine = content.split('\n')[0];
  const description = firstLine.replace(/^#\s*/, '').trim() || `Command: ${commandName}`;

  return generateManifest({
    type: 'command',
    platform,
    commandName,
    description,
    version: '1.0.0',
    tags: ['command', commandName],
    ...options,
  });
}

module.exports = {
  generateManifest,
  generateFromSkill,
  generateFromCommand,
  extractFrontmatter,
};

// CLI usage
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.length < 2) {
    console.error('Usage: generate-manifest.js <type> <path> [platform]');
    console.error('  type: skill|command');
    console.error('  path: path to skill directory or command file');
    console.error('  platform: cursor|claude|codex|openclaw|gemini (optional, defaults to cursor)');
    process.exit(1);
  }

  const [type, inputPath, platform = 'cursor'] = args;
  const fullPath = path.resolve(inputPath);

  try {
    let manifest;

    if (type === 'skill') {
      manifest = generateFromSkill(fullPath, platform);
    } else if (type === 'command') {
      manifest = generateFromCommand(fullPath, platform);
    } else {
      throw new Error(`Invalid type: ${type}. Must be 'skill' or 'command'`);
    }

    console.log(JSON.stringify(manifest, null, 2));
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}
