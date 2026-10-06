import { vi } from "vitest";

// Mock environment variables for tests
process.env.NODE_ENV = "test";
process.env.DATABASE_URL =
  process.env.DATABASE_URL ??
  "postgresql://postgres:postgres@localhost:5432/test?schema=public";

// Global test utilities
declare global {
  // eslint-disable-next-line no-var
  var vi: typeof import("vitest").vi;
}

global.vi = vi;

// Reset mocks between tests
beforeEach(() => {
  vi.clearAllMocks();
});

// Cleanup after all tests
afterAll(async () => {
  // Close any open handles
  vi.restoreAllMocks();
});
