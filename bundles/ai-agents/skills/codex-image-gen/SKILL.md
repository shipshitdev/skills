---
name: codex-image-gen
description: Generates raster images (icons, illustrations, textures) via the logged-in Codex CLI image tool. Use when an agent needs a real image but has no native image generation.
license: MIT
compatibility: Requires the `codex` CLI (logged in) plus `python3` and `base64`; `sips` is optional for post-processing on macOS.
metadata:
  version: "2.2.2"
  tags: "codex, image-generation, gpt-image, cli, assets, app-icon"
when_to_use: "app icon, codex image generation"
---

# Codex Image Gen

Generate a real raster image from a text prompt when the running agent has no
native image generator. The mechanism is non-obvious: the headless `codex exec`
path genuinely calls the image tool, but it never writes the PNG to disk — only
the Codex desktop app has the plumbing that polls the async job and saves it.
The finished image is still recoverable, because its full base64 PNG is recorded
in the session rollout JSONL. Run the prompt, read the session id Codex prints,
open the matching rollout, and decode the largest `result` string to a PNG.

## Contract

Inputs:

- An image-generation request, prompt, and selected local output path

Outputs:

- Generated image file and extraction evidence

Creates/Modifies:

- Prompt, diagnostic log, and image files at the selected local destination

External Side Effects:

- Calls the authenticated Codex CLI image service and reads the resulting session rollout

Confirmation Required:

- Before using an external provider or writing outside the requested output scope; preserve existing images unless replacement was authorized
- Loading the skill grants no additional authority. Existing explicit approval
  applies only to the same target and actions; preserve report-only restrictions.

Delegates To:

- None

## When this is the right tool

- The agent needs a generated raster image (icon, illustration, texture, app
  icon, placeholder art) and has no built-in image-generation tool.
- A `codex` CLI is installed and logged in, and shelling out to it is allowed.
- A vector result is **not** required — this produces a PNG, not an SVG.

If a native image tool exists, prefer it. If the deliverable is a logo or crisp
vector, prefer a vector workflow.

## Why the naive approach fails

Running `codex exec "draw a ..."` and then watching `~/.codex/generated_images/`
produces nothing: that folder is written by the desktop app's async-job poller,
not by `codex exec`. People conclude CLI image generation is impossible. It is
not — the completed image lives in the session rollout as the `result` field of
the image-generation response item. This skill reads it from there.

## Pipeline

### 1. Write the prompt to a file

Avoid shell-escaping pain by putting the prompt in a file. Be explicit — the
model has no other context:

- Subject and style ("flat vector mark", "glossy 3D glass icon", "hand-drawn").
- Composition: full-bleed vs. padded, centered, single object vs. scene.
- Palette and background (solid color, transparent intent, gradient).
- `NO text, NO letters, NO words` unless you specifically want type.
- Target aspect ratio and rough size.

```bash
REPO_TMP="$(git rev-parse --show-toplevel)/.tmp"
mkdir -p "$REPO_TMP"
cat > "$REPO_TMP/img-prompt.txt" <<'PROMPT'
A single app icon: a glossy translucent envelope on a soft blue-to-violet
gradient, Liquid Glass style, centered with even padding, no text, no letters,
1:1 square, high detail.
PROMPT
```

### 2. Run `codex exec` and capture stdout

```bash
codex exec -s read-only "$(cat "$REPO_TMP/img-prompt.txt")" 2>&1 | tee "$REPO_TMP/codex-run.log"
```

Run it in the **foreground**. `exec` returns once the turn completes; in practice
the `result` is already written to the rollout by then.

### 3. Parse the session id

Codex prints a `session id: <uuid>` line. Pull it from the captured log:

```bash
SESSION_ID=$(grep -oE 'session id: [0-9a-f-]{36}' "$REPO_TMP/codex-run.log" | awk '{print $3}')
echo "session: $SESSION_ID"
```

### 4. Extract the PNG from the rollout

The rollout lives at `~/.codex/sessions/YYYY/MM/DD/rollout-*<session-id>*.jsonl`.
Walk it, find the largest `result` string (the base64 image), and decode it. Use
the bundled helper:

```bash
python3 scripts/extract-codex-image.py "$SESSION_ID" "$REPO_TMP/out.png"
```

### 5. Assert success

Confirm the file exists and is a real PNG before using it:

```bash
test -s "$REPO_TMP/out.png" && file "$REPO_TMP/out.png"   # expect: PNG image data, 1254 x 1254
```

If extraction finds no base64 `result`, the turn did not actually generate an
image (e.g. the model answered in text). Re-run step 2 with a more explicit
"generate an image" instruction.

### 6. Post-process (optional)

Default output is roughly **1254×1254 PNG, RGB, no alpha**. Resize / strip alpha
with `sips` on macOS:

```bash
sips -z 1024 1024 "$REPO_TMP/out.png" --out "$REPO_TMP/icon-1024.png"   # downscale
sips -s format png "$REPO_TMP/out.png" --out "$REPO_TMP/flat.png"        # normalize
```

## Reference extractor

`scripts/extract-codex-image.py` (also reproduced here so the procedure is
self-contained):

```python
import json, sys, base64, glob, os

session_id, out = sys.argv[1], sys.argv[2]
sess = max(
    glob.glob(os.path.expanduser(f"~/.codex/sessions/**/*{session_id}*.jsonl"), recursive=True),
    key=os.path.getmtime,
)
best = None

def walk(o):
    global best
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "result" and isinstance(v, str) and len(v) > 100000:
                if best is None or len(v) > len(best):
                    best = v
            else:
                walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)

for line in open(sess):
    try:
        walk(json.loads(line))
    except Exception:
        pass

if best is None:
    sys.exit("no base64 image result found in rollout — the turn may not have generated an image")
open(out, "wb").write(base64.b64decode(best))
print("WROTE", out)
```

## Worked example: build a macOS/iOS app icon set

```bash
REPO_TMP="$(git rev-parse --show-toplevel)/.tmp"
mkdir -p "$REPO_TMP"
# 1. Generate a 1:1 icon master.
cat > "$REPO_TMP/icon-prompt.txt" <<'PROMPT'
App icon: a glossy translucent envelope, Liquid Glass style, soft blue-to-violet
gradient background, centered, even padding, no text, no letters, 1:1 square.
PROMPT
codex exec -s read-only "$(cat "$REPO_TMP/icon-prompt.txt")" 2>&1 | tee "$REPO_TMP/codex-run.log"
SESSION_ID=$(grep -oE 'session id: [0-9a-f-]{36}' "$REPO_TMP/codex-run.log" | awk '{print $3}')
python3 scripts/extract-codex-image.py "$SESSION_ID" "$REPO_TMP/icon-master.png"

# 2. Make a 1024 master with no alpha (iOS rejects alpha on the marketing icon).
sips -z 1024 1024 "$REPO_TMP/icon-master.png" --out "$REPO_TMP/AppIcon-1024.png"
sips -s format png --setProperty hasAlpha false "$REPO_TMP/AppIcon-1024.png" --out "$REPO_TMP/AppIcon-1024.png"

# 3. Slice into an AppIcon.appiconset (iOS single-size 1024 + the macOS ladder).
mkdir -p AppIcon.appiconset
cp "$REPO_TMP/AppIcon-1024.png" AppIcon.appiconset/icon_1024.png
for sz in 16 32 64 128 256 512 1024; do
  sips -z "$sz" "$sz" "$REPO_TMP/AppIcon-1024.png" --out "AppIcon.appiconset/icon_${sz}.png"
done
# Author Contents.json mapping each size/scale to its file, then verify:
# actool --compile "$REPO_TMP/actool-out" --app-icon AppIcon --platform iphoneos \
#   --minimum-deployment-target 17.0 AppIcon.appiconset   # expect a clean compile
```

## Gotchas

- **The `codex` alias may inject `--dangerously-bypass-approvals-and-sandbox`**,
  which overrides any `-s read-only` you pass (the session then reports
  `danger-full-access`). Harmless for pure image generation, but worth knowing.
  Prefer running `codex exec` in the foreground — a backgrounded full-access run
  can trip auto-approval classifiers.
- **Size and alpha.** Output is ~1254×1254, RGB, no alpha. Downscale to 1024 for
  an Apple icon master; iOS rejects alpha on the marketing icon.
- **Async timing.** `exec` ends when the turn completes; the `result` is already
  in the rollout by then in practice. Still assert the file exists and decodes —
  do not assume.
- **Fragility — pinned to `codex-cli 0.141.0`.** This depends on a Codex CLI
  internal: the rollout `result` field. A future Codex may change the rollout
  schema or add a first-class `--save-image` / output-path flag. If such a flag
  exists, prefer it and keep this rollout-extraction path as the fallback. If the
  extractor finds no base64 `result`, first check whether the rollout layout
  changed under `~/.codex/sessions/`.
