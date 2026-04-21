#!/usr/bin/env python3
"""
Migrate SKILL.md frontmatter to Agent Skills spec compliance.

Changes applied:
  - top-level `version: X.Y.Z`  →  metadata.version: "X.Y.Z"
  - top-level `tags: [...]`      →  metadata.tags: "tag1, tag2, ..."
  - `auto_activate: ...`         →  removed (not in spec)
  - `auto_trigger: ...`          →  removed (not in spec)
  - existing `metadata:` block   →  merged with above, not duplicated

Usage:
  python3 scripts/migrate-frontmatter.py            # dry-run (preview only)
  python3 scripts/migrate-frontmatter.py --write    # apply changes
"""

import sys
import re
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / "skills"
DRY_RUN = "--write" not in sys.argv

INVALID_FIELDS = {"auto_activate", "auto_trigger"}


def parse_frontmatter(text: str) -> tuple[str, str, str]:
    """Split file into (before_fm, fm_body, after_fm). Returns ('', '', text) if no FM."""
    if not text.startswith("---"):
        return "", "", text
    end = text.find("\n---", 3)
    if end == -1:
        return "", "", text
    fm_body = text[4:end]          # content between opening --- and closing ---
    after = text[end + 4:]         # everything after closing ---
    return "---\n", fm_body, after


def parse_yaml_frontmatter(fm_body: str) -> dict:
    """Parse just the fields we care about from raw frontmatter text."""
    result = {}
    lines = fm_body.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        # top-level key: value
        m = re.match(r'^(\w[\w_-]*):\s*(.*)', line)
        if m:
            key = m.group(1)
            val = m.group(2).strip()
            if key == "tags":
                # collect indented list items
                tags = []
                if val:
                    tags.append(val.lstrip("- ").strip())
                i += 1
                while i < len(lines) and re.match(r'^\s+-\s+', lines[i]):
                    tags.append(lines[i].strip().lstrip("- ").strip())
                    i += 1
                result[key] = tags
                continue
            elif key == "metadata":
                # collect existing metadata sub-keys
                meta = {}
                i += 1
                while i < len(lines) and re.match(r'^\s+\w', lines[i]):
                    mm = re.match(r'^\s+(\w[\w_-]*):\s*(.*)', lines[i])
                    if mm:
                        meta[mm.group(1)] = mm.group(2).strip().strip('"')
                    i += 1
                result[key] = meta
                continue
            else:
                result[key] = val
        i += 1
    return result


def rebuild_frontmatter(fm_body: str) -> tuple[str, bool]:
    """
    Rewrite frontmatter:
    - Remove auto_activate, auto_trigger
    - Move version → metadata.version
    - Move tags list → metadata.tags string
    Returns (new_fm_body, changed).
    """
    lines = fm_body.split("\n")
    parsed = parse_yaml_frontmatter(fm_body)

    version = parsed.get("version", "")
    tags = parsed.get("tags", [])  # list or empty
    existing_meta = parsed.get("metadata", {})

    # Build merged metadata
    new_meta = dict(existing_meta)
    if version and "version" not in new_meta:
        # strip quotes if present
        new_meta["version"] = version.strip('"')
    if tags and "tags" not in new_meta:
        if isinstance(tags, list):
            new_meta["tags"] = ", ".join(tags)
        else:
            new_meta["tags"] = str(tags)

    # Rebuild line by line, skipping migrated fields
    new_lines = []
    skip_tags_block = False
    skip_meta_block = False
    inserted_meta = False
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip auto_activate / auto_trigger entirely
        if re.match(r'^(auto_activate|auto_trigger)\s*:', line):
            i += 1
            continue

        # Skip top-level version (migrating to metadata)
        if re.match(r'^version\s*:', line) and version:
            i += 1
            continue

        # Skip top-level tags block (migrating to metadata)
        if re.match(r'^tags\s*:', line) and tags:
            i += 1
            # skip indented list items
            while i < len(lines) and re.match(r'^\s+-\s+', lines[i]):
                i += 1
            continue

        # Replace existing metadata block with merged one
        if re.match(r'^metadata\s*:', line):
            if not inserted_meta and new_meta:
                new_lines.append("metadata:")
                for k, v in new_meta.items():
                    new_lines.append(f'  {k}: "{v}"')
                inserted_meta = True
            # skip old metadata sub-lines
            i += 1
            while i < len(lines) and re.match(r'^\s+\w', lines[i]):
                i += 1
            continue

        new_lines.append(line)
        i += 1

    # If metadata block didn't exist but we have data to write, append it before end
    if not inserted_meta and new_meta:
        new_lines.append("metadata:")
        for k, v in new_meta.items():
            new_lines.append(f'  {k}: "{v}"')

    new_fm = "\n".join(new_lines)
    changed = new_fm.strip() != fm_body.strip()
    return new_fm, changed


def migrate_skill(skill_md: Path) -> bool:
    """Returns True if file was (or would be) changed."""
    text = skill_md.read_text(encoding="utf-8")
    prefix, fm_body, suffix = parse_frontmatter(text)

    if not prefix:
        return False  # no frontmatter

    new_fm, changed = rebuild_frontmatter(fm_body)
    if not changed:
        return False

    new_text = f"---\n{new_fm}\n---{suffix}"

    if DRY_RUN:
        print(f"  [dry] Would update: {skill_md.relative_to(SKILLS_DIR.parent)}")
    else:
        skill_md.write_text(new_text, encoding="utf-8")
        print(f"  [✓] Updated: {skill_md.relative_to(SKILLS_DIR.parent)}")

    return True


def main():
    mode = "DRY RUN (preview)" if DRY_RUN else "WRITE MODE"
    print(f"\n=== Frontmatter migration — {mode} ===\n")

    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    changed = []
    skipped = []

    for f in skill_files:
        if migrate_skill(f):
            changed.append(f)
        else:
            skipped.append(f)

    print(f"\nSummary: {len(changed)} changed, {len(skipped)} already compliant")
    if DRY_RUN and changed:
        print("\nRun with --write to apply changes.")


if __name__ == "__main__":
    main()
