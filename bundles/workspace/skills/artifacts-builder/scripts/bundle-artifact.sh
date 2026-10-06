#!/bin/bash
# Bundle a Vite project into one self-contained bundle.html with Bun.
# Run from the project root (the folder with package.json and index.html).

set -euo pipefail

echo "Bundling React app to a single HTML artifact..."

if ! command -v bun &> /dev/null; then
  echo "Error: Bun is not installed. Install it from https://bun.sh and re-run."
  exit 1
fi

if [ ! -f "package.json" ]; then
  echo "Error: No package.json found. Run this script from your project root."
  exit 1
fi

if [ ! -f "index.html" ]; then
  echo "Error: No index.html found in project root."
  echo "   This script requires an index.html entry point."
  exit 1
fi

BASE_CONFIG=""
for candidate in vite.config.ts vite.config.mts vite.config.js vite.config.mjs; do
  if [ -f "$candidate" ]; then
    BASE_CONFIG="$candidate"
    break
  fi
done

if [ -z "$BASE_CONFIG" ]; then
  echo "Error: No vite.config.* found. Create the project with init-artifact.sh first."
  exit 1
fi

echo "Installing vite-plugin-singlefile..."
bun add -d vite-plugin-singlefile

# A separate config keeps the normal dev and build setup untouched: it extends the
# project's Vite config and inlines all JS, CSS and assets into index.html.
SINGLEFILE_CONFIG="vite.singlefile.config.ts"
if [ ! -f "$SINGLEFILE_CONFIG" ]; then
  echo "Creating $SINGLEFILE_CONFIG..."
  cat > "$SINGLEFILE_CONFIG" << EOF
import { defineConfig, mergeConfig } from "vite"
import { viteSingleFile } from "vite-plugin-singlefile"
import baseConfig from "./$BASE_CONFIG"

export default mergeConfig(
  baseConfig,
  defineConfig({
    plugins: [viteSingleFile()],
    build: { outDir: "dist-bundle", emptyOutDir: true },
  }),
)
EOF
fi

echo "Cleaning previous build..."
rm -rf dist-bundle bundle.html

echo "Building with Vite..."
bunx vite build --config "$SINGLEFILE_CONFIG"

if [ ! -f "dist-bundle/index.html" ]; then
  echo "Error: the build produced no dist-bundle/index.html"
  exit 1
fi

cp dist-bundle/index.html bundle.html
rm -rf dist-bundle

FILE_SIZE=$(du -h bundle.html | cut -f1)

echo ""
echo "Bundle complete."
echo "Output: bundle.html ($FILE_SIZE)"
echo ""
echo "You can now use this single HTML file as an artifact in Claude conversations."
echo "To test locally: open bundle.html in your browser"
