/**
 * Vitest Configuration Template for Frontend (React/Next.js)
 *
 * Copy this to your frontend project and adjust paths as needed.
 * This configuration enforces 80% coverage thresholds.
 */

import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    // Use global test APIs (describe, it, expect)
    globals: true,

    // Environment for React tests
    environment: "jsdom",

    // Setup files for React Testing Library
    setupFiles: ["./src/test/setup.ts"],

    // Test file patterns
    include: [
      "src/**/*.{test,spec}.{ts,tsx}",
      "components/**/*.{test,spec}.{ts,tsx}",
      "hooks/**/*.{test,spec}.{ts,tsx}",
    ],

    // Exclude patterns
    exclude: ["node_modules", "dist", ".next", "build", "e2e"],

    // Coverage configuration
    coverage: {
      // Use V8 provider
      provider: "v8",

      // Output formats
      reporter: ["text", "json", "html", "lcov"],

      // Files to include in coverage
      include: [
        "src/**/*.{ts,tsx}",
        "components/**/*.{ts,tsx}",
        "hooks/**/*.{ts,tsx}",
        "lib/**/*.{ts,tsx}",
      ],

      // Files to exclude from coverage
      exclude: [
        "**/*.test.{ts,tsx}",
        "**/*.spec.{ts,tsx}",
        "**/*.d.ts",
        "**/test/**",
        "**/__mocks__/**",
        "**/types/**",
        "**/*.stories.{ts,tsx}",
      ],

      // Coverage thresholds - fail if below these
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
    },

    // Timeout for tests (ms)
    testTimeout: 10000,

    // CSS handling
    css: true,

    // Path aliases (match tsconfig/next.config)
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@components": path.resolve(__dirname, "./components"),
      "@hooks": path.resolve(__dirname, "./hooks"),
      "@lib": path.resolve(__dirname, "./lib"),
      "@services": path.resolve(__dirname, "./services"),
    },
  },
});
