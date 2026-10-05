/**
 * Vitest Configuration Template
 *
 * Copy this to your project and adjust paths as needed.
 * This configuration enforces 80% coverage thresholds.
 */

import { defineConfig } from "vitest/config";
import path from "path";

export default defineConfig({
  test: {
    // Use global test APIs (describe, it, expect)
    globals: true,

    // Environment for tests
    environment: "node", // Use "jsdom" for frontend tests

    // Test file patterns
    include: ["src/**/*.{test,spec}.{ts,tsx}", "**/*.{test,spec}.{ts,tsx}"],

    // Exclude patterns
    exclude: ["node_modules", "dist", ".next", "build"],

    // Coverage configuration
    coverage: {
      // Use V8 provider (faster, built into Node)
      provider: "v8",

      // Output formats
      reporter: ["text", "json", "html", "lcov"],

      // Files to include in coverage
      include: ["src/**/*.ts", "src/**/*.tsx"],

      // Files to exclude from coverage
      exclude: [
        "src/**/*.test.ts",
        "src/**/*.spec.ts",
        "src/**/*.d.ts",
        "src/test/**",
        "src/**/__mocks__/**",
      ],

      // Coverage thresholds - fail if below these
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
    },

    // Setup files to run before tests
    setupFiles: ["./src/test/setup.ts"],

    // Reset mocks between tests
    mockReset: true,
    restoreMocks: true,

    // Timeout for tests (ms)
    testTimeout: 10000,

    // Path aliases (match tsconfig)
    alias: {
      "@collections": path.resolve(__dirname, "./src/collections"),
      "@services": path.resolve(__dirname, "./src/services"),
      "@guards": path.resolve(__dirname, "./src/guards"),
      "@helpers": path.resolve(__dirname, "./src/helpers"),
    },
  },
});
