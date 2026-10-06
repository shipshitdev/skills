import path from "path";
import swc from "unplugin-swc";
import { defineConfig } from "vitest/config";

export default defineConfig({
  // unplugin-swc emits decorator metadata, which NestJS dependency injection needs
  plugins: [swc.vite({ module: { type: "es6" } })],
  test: {
    globals: true,
    environment: "node",
    include: ["src/**/*.spec.ts", "test/**/*.spec.ts"],
    exclude: ["node_modules", "dist"],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html", "lcov"],
      include: ["src/**/*.ts"],
      exclude: [
        "**/*.spec.ts",
        "**/*.test.ts",
        "**/*.d.ts",
        "src/main.ts",
        "**/*.module.ts",
        "**/index.ts",
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
    },
    setupFiles: ["./test/setup.ts"],
    mockReset: true,
    restoreMocks: true,
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
