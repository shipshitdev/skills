#!/usr/bin/env python3
"""Validate every skill in skills/: frontmatter, user-only invocation, links, model IDs."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
NAME = re.compile(r"^[a-z0-9]+$")
KEY = re.compile(r"^([A-Za-z_][\w-]*):(.*)$")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
MODEL_ID = re.compile(
    r"\b(claude-(?:\d[\w.]*-)?(?:opus|sonnet|haiku|fable)-\d[\w.-]*"
    r"|claude-\d-\d[\w.-]*|gpt-\d[\w.-]*|gemini-\d[\w.-]*|grok-\d[\w.-]*)\b",
    re.IGNORECASE,
)
FORBIDDEN_KEYS = {"model", "effort"}
TEXT_SUFFIXES = {".md", ".py", ".sh", ".mjs", ".js", ".ts", ".json", ".yml", ".yaml", ".txt"}


def frontmatter(text):
    """Return top-level frontmatter keys mapped to their folded string values."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    fields, current = {}, None
    for line in text[4:end].splitlines():
        match = KEY.match(line)
        if match:
            current = match.group(1)
            value = match.group(2).strip()
            fields[current] = "" if value in (">-", ">", "|", "|-") else value.strip("\"'")
        elif current and line.startswith((" ", "\t")):
            fields[current] = (fields[current] + " " + line.strip()).strip()
    return fields


def check_skill(directory):
    root = directory.parent.parent
    errors = []
    skill_md = directory / "SKILL.md"
    if not skill_md.is_file():
        return [f"{directory.name}: missing SKILL.md"]
    fields = frontmatter(skill_md.read_text())
    if fields is None:
        return [f"{skill_md}: missing or unterminated frontmatter"]
    name = fields.get("name", "")
    if name != directory.name:
        errors.append(f"{skill_md}: name '{name}' does not match directory '{directory.name}'")
    if not NAME.match(name) or len(name) > 64:
        errors.append(f"{skill_md}: name '{name}' must be one lowercase word (letters and digits), max 64 chars; group related"
                f" workflows as actions under one router instead of hyphenating")
    description = fields.get("description", "")
    if not 1 <= len(description) <= 1024:
        errors.append(f"{skill_md}: description must be 1-1024 chars (has {len(description)})")
    if fields.get("disable-model-invocation") != "true":
        errors.append(f"{skill_md}: set 'disable-model-invocation: true'; skills here are user-invoked only")
    if fields.get("user-invocable") == "false":
        errors.append(f"{skill_md}: 'user-invocable: false' hides the skill from its user")
    for key in FORBIDDEN_KEYS & fields.keys():
        errors.append(f"{skill_md}: '{key}:' belongs to the harness, not the skill")

    for path in sorted(directory.rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(errors="ignore")
        for number, line in enumerate(text.splitlines(), 1):
            for model in MODEL_ID.findall(line):
                errors.append(f"{path.relative_to(root)}:{number}: concrete model ID '{model}'")
        if path.suffix != ".md":
            continue
        for target in LINK.findall(re.sub(r"```.*?```", "", text, flags=re.DOTALL)):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            resolved = (path.parent / target.split("#", 1)[0]).resolve()
            if not resolved.exists():
                errors.append(f"{path.relative_to(root)}: broken link '{target}'")
    return errors


def main(skills=SKILLS):
    directories = sorted(p for p in skills.iterdir() if p.is_dir())
    errors = [error for directory in directories for error in check_skill(directory)]
    for error in errors:
        print(f"error: {error}")
    print(f"{len(directories)} skills checked, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
