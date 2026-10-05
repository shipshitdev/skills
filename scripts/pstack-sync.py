#!/usr/bin/env python3
"""Verify pinned Pstack imports and stage upstream candidates without changing skills."""
from __future__ import annotations

import argparse
import difflib
import gzip
import hashlib
import io
import json
import re
import subprocess
import sys
import tarfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DISPOSITIONS = {"identical", "adapted", "reference", "superseded", "metadata"}
COMMIT = re.compile(r"[0-9a-f]{40}")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_path(value: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or str(path) != value:
        raise ValueError(f"Unsafe path: {value!r}")
    return value


def local_file(root: Path, value: str) -> Path:
    path = root / safe_path(value)
    if not path.resolve().is_relative_to(root.resolve()) or path.is_symlink():
        raise ValueError(f"Destination escapes root or is a symlink: {value}")
    return path


def read_json(path: Path) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def archive_bytes(files: dict[str, tuple[bytes, int]]) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, (data, mode) in sorted(files.items()):
            safe_path(name)
            entry = tarfile.TarInfo(name)
            entry.size = len(data)
            entry.mode = mode
            entry.mtime = 0
            archive.addfile(entry, io.BytesIO(data))
    return gzip.compress(buffer.getvalue(), mtime=0)


def read_archive(data: bytes) -> dict[str, tuple[bytes, int]]:
    result = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        for entry in archive:
            name = safe_path(entry.name)
            if not entry.isfile() or name in result or entry.mode not in (0o644, 0o755):
                raise ValueError(f"Invalid archive member: {name}")
            stream = archive.extractfile(entry)
            if stream is None:
                raise ValueError(f"Unreadable archive member: {name}")
            result[name] = (stream.read(), entry.mode)
    return result


def inventory(files: dict[str, tuple[bytes, int]]) -> dict:
    return {name: {"sha256": digest(data), "mode": mode}
            for name, (data, mode) in sorted(files.items())}


def git(checkout: Path, *arguments: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(checkout), *arguments])


def ignored_paths(source: dict) -> list[str]:
    """Exact upstream paths a source declares as repo-only and never shipped."""
    value = source.get("ignored_paths", [])
    if not isinstance(value, list) or len(set(value)) != len(value):
        raise ValueError("ignored_paths must be a list of unique exact paths")
    return [safe_path(path) for path in value]


def snapshot(checkout: Path, commit: str, paths: list[str], ignored: list[str] | None = None,
             skipped: list[str] | None = None) -> dict:
    ignored = ignored or []
    if not COMMIT.fullmatch(commit):
        raise ValueError("Use a full 40-character commit SHA, not a moving ref")
    resolved = git(checkout, "rev-parse", "--verify", commit + "^{commit}").decode().strip()
    if resolved != commit:
        raise ValueError("Commit resolution changed")
    if not paths or any(path != "." and safe_path(path) != path for path in paths):
        raise ValueError("Source paths are required")
    listing = git(checkout, "ls-tree", "-r", "-z", commit, "--", *paths)
    files = {}
    for item in listing.split(b"\0"):
        if not item:
            continue
        header, raw_name = item.split(b"\t", 1)
        mode, kind, oid = header.decode().split()
        name = safe_path(raw_name.decode())
        if name in ignored:
            if skipped is not None:
                skipped.append(name)
            continue
        if kind != "blob" or mode not in ("100644", "100755"):
            raise ValueError(f"Unsupported upstream object: {name} ({mode})")
        files[name] = (git(checkout, "cat-file", "blob", oid), int(mode[-3:], 8))
    if not files:
        raise ValueError("Selected upstream tree is empty")
    return files


def execution_source(name: str, mode: int) -> bool:
    parts = PurePosixPath(name).parts
    return any(part in {"skills", "agents", "hooks", "automations"} for part in parts) and (
        bool(mode & 0o111)
        or name.endswith((".md", ".ts", ".tsx", ".mts", ".js", ".mjs", ".sh", ".bash", ".zsh", ".py", ".ps1", ".cmd"))
        or PurePosixPath(name).name in {"session-start", "run-hook", "hooks.json"}
    )


def verify(root: Path) -> list[str]:
    directory = root / "upstream/pstack"
    lock = read_json(directory / "lock.json")
    mapping = read_json(directory / "mapping.json")
    errors = []
    if lock.get("schema_version") != 1 or mapping.get("schema_version") != 1:
        return ["Unsupported Pstack manifest schema"]
    sources = lock["sources"]
    if len({source["id"] for source in sources}) != len(sources):
        return ["Duplicate upstream source ID"]
    expected = {}
    for source in sources:
        if not COMMIT.fullmatch(source["commit"]):
            errors.append(f"{source['id']}: expected full pinned commit")
        raw = local_file(root, source["archive"]).read_bytes()
        if digest(raw) != source["sha256"]:
            errors.append(f"{source['id']}: archive checksum mismatch")
        contents = read_archive(raw)
        if inventory(contents) != source["files"]:
            errors.append(f"{source['id']}: archive inventory differs from lock")
        try:
            for path in ignored_paths(source):
                if path in contents:
                    errors.append(f"{source['id']}: ignored path is also archived: {path}")
        except ValueError as error:
            errors.append(f"{source['id']}: {error}")
        expected.update({source["id"] + ":" + name: value for name, value in contents.items()})
    entries = mapping["files"]
    for missing in sorted(expected.keys() - entries.keys()):
        errors.append(f"Unmapped upstream file: {missing}")
    for stale in sorted(entries.keys() - expected.keys()):
        errors.append(f"Mapping has no pinned source: {stale}")
    for key in sorted(expected.keys() & entries.keys()):
        entry = entries[key]
        kind = entry.get("disposition")
        if kind not in DISPOSITIONS:
            errors.append(f"{key}: unknown or pending disposition")
        if not entry.get("reason", "").strip() or not entry.get("verification"):
            errors.append(f"{key}: reason and verification evidence required")
        destinations = entry.get("destinations", [])
        if not destinations:
            errors.append(f"{key}: canonical destination required")
        if execution_source(key.split(":", 1)[1], expected[key][1]) and (
            kind == "metadata" or not any(d.get("path", "").startswith("skills/") for d in destinations)
        ):
            errors.append(f"{key}: executable/procedure resource cannot be archive-only")
        for destination in destinations:
            path = local_file(root, destination["path"])
            if not path.is_file():
                errors.append(f"{key}: missing destination {destination['path']}")
                continue
            raw = path.read_bytes()
            if digest(raw) != destination.get("sha256"):
                errors.append(f"{key}: unreviewed destination change {destination['path']}")
            if bool(path.stat().st_mode & 0o111) != destination.get("executable"):
                errors.append(f"{key}: unreviewed executable-bit change {destination['path']}")
            if kind == "identical" and raw != expected[key][0]:
                errors.append(f"{key}: identical disposition differs from upstream")
        for evidence in entry.get("verification", []):
            if not local_file(root, evidence).is_file():
                errors.append(f"{key}: missing verification reference {evidence}")
    return errors


def changes(before: dict, after: dict) -> dict:
    return {
        "added": sorted(after.keys() - before.keys()),
        "removed": sorted(before.keys() - after.keys()),
        "changed": sorted(name for name in before.keys() & after.keys() if before[name] != after[name]),
    }


def diff_text(before: bytes, after: bytes, old: str, new: str) -> str:
    try:
        return "".join(difflib.unified_diff(
            before.decode("utf-8").splitlines(keepends=True),
            after.decode("utf-8").splitlines(keepends=True),
            fromfile=old, tofile=new,
        ))
    except UnicodeDecodeError:
        return f"Binary change: {old} ({digest(before)}) -> {new} ({digest(after)})\n"


def candidate(root: Path, source_id: str, checkout: Path, commit: str, output: Path) -> dict:
    lock = read_json(root / "upstream/pstack/lock.json")
    mapping = read_json(root / "upstream/pstack/mapping.json")
    selected = [source for source in lock["sources"] if source["id"] == source_id]
    if len(selected) != 1:
        raise ValueError(f"Unknown source: {source_id}")
    source = selected[0]
    origin = git(checkout, "remote", "get-url", "origin").decode().strip()
    normalized = origin.removesuffix(".git").replace("git@github.com:", "https://github.com/")
    if normalized != source["repository"].removesuffix(".git"):
        raise ValueError("Checkout origin does not match the pinned upstream repository")
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("Stage candidates outside the maintained repository")
    ignored = ignored_paths(source)
    mapped = [path for path in ignored if source_id + ":" + path in mapping["files"]]
    if mapped:
        raise ValueError(f"Ignored paths cannot be mapped shipped files: {mapped}")
    skipped: list[str] = []
    newer = snapshot(checkout, commit, source["paths"], ignored, skipped)
    accepted = local_file(root, source["archive"]).read_bytes()
    if digest(accepted) != source["sha256"]:
        raise ValueError("Pinned archive checksum differs from lock")
    older = read_archive(accepted)
    if inventory(older) != source["files"]:
        raise ValueError("Pinned archive inventory differs from lock")
    report = {"source": source_id, "from": source["commit"], "to": commit,
              **changes(older, newer), "ignored_paths": sorted(skipped),
              "adaptations_requiring_review": []}
    new_entries = dict(mapping["files"])
    patches = []
    touched = sorted(set(report["added"] + report["removed"] + report["changed"]))
    for name in touched:
        key = source_id + ":" + name
        entry = mapping["files"].get(key, {})
        destinations = []
        for destination in entry.get("destinations", []):
            path = local_file(root, destination["path"])
            raw = path.read_bytes() if path.is_file() else b""
            destinations.append({
                "path": destination["path"],
                "changed_since_acceptance": digest(raw) != destination["sha256"],
                "upstream_to_local_diff": diff_text(
                    older.get(name, (b"", 0))[0], raw, "accepted-upstream/" + name, "local/" + destination["path"]),
            })
        report["adaptations_requiring_review"].append({"source_file": name, "destinations": destinations})
        patches.append(diff_text(older.get(name, (b"", 0))[0], newer.get(name, (b"", 0))[0],
                                 "accepted-upstream/" + name, "candidate-upstream/" + name))
        if name in newer:
            new_entries[key] = {**entry, "disposition": "pending"}
        else:
            new_entries.pop(key, None)
    blob = archive_bytes(newer)
    replacement = {**source, "commit": commit, "sha256": digest(blob), "files": inventory(newer)}
    candidate_lock = {**lock, "sources": [replacement if s["id"] == source_id else s for s in lock["sources"]]}
    output.mkdir(parents=True, exist_ok=False)
    (output / Path(source["archive"]).name).write_bytes(blob)
    write_json(output / "candidate-lock.json", candidate_lock)
    write_json(output / "candidate-mapping.json", {**mapping, "files": new_entries})
    write_json(output / "report.json", report)
    (output / "upstream.diff").write_text("".join(patches))
    return report


def record(root: Path, note: str) -> int:
    if not note.strip():
        raise ValueError("A review note is required")
    path = root / "upstream/pstack/mapping.json"
    mapping = read_json(path)
    count = 0
    for entry in mapping["files"].values():
        for destination in entry.get("destinations", []):
            target = local_file(root, destination["path"])
            current = digest(target.read_bytes())
            executable = bool(target.stat().st_mode & 0o111)
            if destination.get("sha256") != current or destination.get("executable") != executable:
                destination["sha256"] = current
                destination["executable"] = executable
                entry["review_note"] = note
                count += 1
    write_json(path, mapping)
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("verify", help="Offline source, coverage and canonical hash verification")
    stage = sub.add_parser("candidate", help="Stage an upstream update; never promote it")
    stage.add_argument("--source", required=True)
    stage.add_argument("--checkout", type=Path, required=True)
    stage.add_argument("--commit", required=True)
    stage.add_argument("--output", type=Path, required=True)
    accept = sub.add_parser("record", help="Record destination hashes after reviewing local adaptations")
    accept.add_argument("--review-note", required=True)
    args = parser.parse_args()
    try:
        if args.command == "verify":
            errors = verify(args.root)
            print("\n".join(errors) if errors else "Pstack source inventory, mappings and destination hashes verified.")
            return bool(errors)
        if args.command == "candidate":
            report = candidate(args.root, args.source, args.checkout, args.commit, args.output)
            print(json.dumps({key: value for key, value in report.items() if key != "adaptations_requiring_review"}, indent=2))
        else:
            print(f"Recorded {record(args.root, args.review_note)} reviewed destination hashes.")
    except (ValueError, KeyError, TypeError, OSError, tarfile.TarError, subprocess.CalledProcessError) as error:
        print(f"Pstack sync failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
