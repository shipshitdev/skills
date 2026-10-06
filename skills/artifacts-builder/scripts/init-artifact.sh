#!/bin/bash
# Scaffold a React + TypeScript + Vite + Tailwind CSS v4 + shadcn/ui project with Bun.
# Usage: bash init-artifact.sh <project-name>

set -euo pipefail

if [ -z "${1:-}" ]; then
  echo "Usage: bash init-artifact.sh <project-name>"
  exit 1
fi

PROJECT_NAME="$1"

# Bun is the package manager and runner for the whole scaffold
if ! command -v bun &> /dev/null; then
  echo "Error: Bun is not installed. Install it from https://bun.sh and re-run."
  exit 1
fi

# Vite 8 and Tailwind CSS v4 run on Node: Vite requires 20.19+ or 22.12+ (see node-version-check.sh)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=node-version-check.sh disable=SC1091
source "$SCRIPT_DIR/node-version-check.sh"

if ! command -v node &> /dev/null; then
  echo "Error: Node.js $NODE_MIN_DISPLAY is required (Vite runs on it)."
  exit 1
fi
NODE_VERSION="$(node -v)"
echo "Detected Node.js $NODE_VERSION, Bun $(bun -v)"
if ! node_version_supported "$NODE_VERSION"; then
  echo "Error: Node.js $NODE_MIN_DISPLAY is required by Vite (current: $NODE_VERSION)."
  echo "       Upgrade Node and re-run."
  exit 1
fi

# In-place sed that works on both macOS (BSD) and Linux (GNU)
sed_inplace() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "$@"
  else
    sed -i "$@"
  fi
}

echo "Creating new React + Vite project: $PROJECT_NAME"
bun create vite "$PROJECT_NAME" --template react-ts --no-interactive

cd "$PROJECT_NAME"

echo "Cleaning up Vite template..."
sed_inplace '/<link rel="icon"/d' index.html
sed_inplace 's/<title>.*<\/title>/<title>'"$PROJECT_NAME"'<\/title>/' index.html
rm -f src/App.css
rm -rf src/assets public/favicon.svg public/icons.svg

echo "Installing dependencies..."
bun install

echo "Installing Tailwind CSS v4 (CSS-first, no tailwind.config file)..."
bun add tailwindcss @tailwindcss/vite
bun add -d @types/node

# Tailwind v4 is configured in CSS; shadcn init adds the theme tokens to this file
cat > src/index.css << 'EOF'
@import "tailwindcss";
EOF

# shadcn/ui needs the @/* alias in both tsconfig files and in Vite.
# paths resolves relative to the tsconfig, so no baseUrl (deprecated in TypeScript 6).
echo "Adding the @/* path alias to tsconfig.json and tsconfig.app.json..."
# shellcheck disable=SC2016  # the JS below is single-quoted on purpose
bun -e '
const fs = require("fs");
const addAlias = (file) => {
  const raw = fs.readFileSync(file, "utf8");
  // tsconfig files are JSONC: drop block comments and full-line // comments, then trailing commas
  const json = raw
    .replace(/\/\*[\s\S]*?\*\//g, "")
    .split("\n")
    .filter((line) => !line.trim().startsWith("//"))
    .join("\n")
    .replace(/,(\s*[}\]])/g, "$1");
  const config = JSON.parse(json);
  config.compilerOptions = config.compilerOptions || {};
  config.compilerOptions.paths = { "@/*": ["./src/*"] };
  fs.writeFileSync(file, JSON.stringify(config, null, 2) + "\n");
};
addAlias("tsconfig.json");
addAlias("tsconfig.app.json");
'

echo "Writing vite.config.ts (React, Tailwind v4 plugin, @ alias)..."
cat > vite.config.ts << 'EOF'
import path from "node:path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "./src"),
    },
  },
})
EOF

echo "Initializing shadcn/ui (components.json, CSS variables, cn util, tw-animate-css)..."
# Radix primitives with the Nova preset; --preset also skips the interactive prompt
bunx --bun shadcn@latest init --yes --base radix --preset nova --force --no-monorepo

if [ ! -f components.json ]; then
  echo "Error: shadcn init did not create components.json"
  exit 1
fi

echo "Adding the shadcn/ui component set..."
bunx --bun shadcn@latest add --all --yes --overwrite

echo "Writing a starter src/App.tsx..."
cat > src/App.tsx << EOF
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export default function App() {
  return (
    <main className="mx-auto max-w-2xl p-8">
      <Card>
        <CardHeader>
          <CardTitle>Artifact</CardTitle>
          <CardDescription>Edit src/App.tsx to build your artifact.</CardDescription>
        </CardHeader>
        <CardContent>
          <Button>Get started</Button>
        </CardContent>
      </Card>
    </main>
  )
}
EOF

echo ""
echo "Setup complete: React + TypeScript + Vite + Tailwind CSS v4 + shadcn/ui (Bun)."
echo ""
echo "To start developing:"
echo "  cd $PROJECT_NAME"
echo "  bun run dev"
echo ""
echo "Import components like:"
echo "  import { Button } from '@/components/ui/button'"
echo "  import { Card, CardContent } from '@/components/ui/card'"
echo ""
echo "Add more with: bunx shadcn@latest add <component>"
