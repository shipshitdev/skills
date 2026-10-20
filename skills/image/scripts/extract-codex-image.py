#!/usr/bin/env python3
"""Extract the generated PNG from a Codex session rollout.

The headless `codex exec` path fires image generation but never writes the PNG
to disk — only the desktop app's async-job poller does. The finished image is
still recoverable: its full base64 PNG is recorded in the session rollout JSONL
as the `result` field of the image-generation response item. This script finds
the rollout for a session id, pulls the largest base64 `result`, and decodes it.

Usage:
    extract-codex-image.py <session-id> <out.png>

Example:
    extract-codex-image.py 0f4c1e2a-... .tmp/out.png
"""

import base64
import glob
import json
import os
import sys

# Below this length a `result` string is not a full-resolution image payload.
MIN_RESULT_LEN = 100_000


def find_rollout(session_id: str) -> str:
    """Return the newest rollout JSONL matching the session id."""
    pattern = os.path.expanduser(f"~/.codex/sessions/**/*{session_id}*.jsonl")
    matches = glob.glob(pattern, recursive=True)
    if not matches:
        sys.exit(f"no rollout found for session {session_id} under ~/.codex/sessions/")
    return max(matches, key=os.path.getmtime)


def largest_result(rollout_path: str) -> str | None:
    """Walk every JSON line and return the longest base64 `result` string."""
    best: str | None = None

    def walk(node) -> None:
        nonlocal best
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "result" and isinstance(value, str) and len(value) > MIN_RESULT_LEN:
                    if best is None or len(value) > len(best):
                        best = value
                else:
                    walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    with open(rollout_path, encoding="utf-8") as handle:
        for line in handle:
            try:
                walk(json.loads(line))
            except (ValueError, TypeError):
                continue
    return best


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("usage: extract-codex-image.py <session-id> <out.png>")
    session_id, out_path = sys.argv[1], sys.argv[2]

    rollout = find_rollout(session_id)
    payload = largest_result(rollout)
    if payload is None:
        sys.exit(
            "no base64 image result found in rollout — the turn may not have "
            "generated an image (re-run with an explicit 'generate an image' instruction)"
        )

    with open(out_path, "wb") as out_file:
        out_file.write(base64.b64decode(payload))
    print(f"WROTE {out_path} (from {rollout})")


if __name__ == "__main__":
    main()
