/**
 * Vitest Configuration Template for NestJS
 *
 * Copy this to your API project (rename to vitest.config.mts to avoid Vite's CommonJS
 * config warning) and adjust paths as needed. This configuration enforces 80% coverage
 * thresholds and matches the config init-workspace.py generates.
 */

import swc from "unplugin-swc";
import { defineConfig } from "vitest/config";

export default defineConfig({
  // esbuild does not emit decorator metadata, which NestJS dependency injection needs;
  // unplugin-swc does (requires: bun add -D unplugin-swc @swc/core)
  plugins: [swc.vite({ module: { type: "es6" } })],
  test: {
    // Use global test APIs (describe, it, expect)
    globals: true,

    // Environment for tests
    environment: "node",

    // Test file patterns
    include: ["**/*.spec.ts", "**/*.test.ts"],

    // Exclude patterns
    exclude: ["node_modules", "dist"],

    // Coverage configuration
    coverage: {
      // Use V8 provider (faster, built into Node)
      provider: "v8",

      // Output formats
      reporter: ["text", "json", "html", "lcov"],

      // Files to include in coverage
      include: ["apps/**/src/**/*.ts"],

      // Files to exclude from coverage
      exclude: [
        "**/*.spec.ts",
        "**/*.test.ts",
        "**/*.d.ts",
        "**/main.ts",
        "**/index.ts",
        "**/generated/**",
        "**/*.module.ts",
      ],

      // Coverage thresholds - fail if below these
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
    },

    // Reset mocks between tests
    mockReset: true,
    restoreMocks: true,
  },
});
