/**
 * React Hook Test Template (Vitest + Testing Library)
 *
 * Replace {{Entity}} with PascalCase entity name (e.g., Task)
 * Replace {{entity}} with camelCase entity name (e.g., task)
 * Replace {{entities}} with plural camelCase (e.g., tasks)
 *
 * Requires: npm install -D @testing-library/react-hooks
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import { use{{Entity}}s } from "./use-{{entities}}";
import { {{Entity}}Service } from "@services/{{entity}}.service";

// Mock the service
vi.mock("@services/{{entity}}.service", () => ({
  {{Entity}}Service: {
    getAll: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}));

// Mock Clerk
vi.mock("@clerk/nextjs", () => ({
  useAuth: () => ({
    getToken: vi.fn().mockResolvedValue("test-token"),
  }),
}));

describe("use{{Entity}}s", () => {
  const mock{{Entity}}s = [
    { _id: "1", title: "{{Entity}} 1", userId: "user-123" },
    { _id: "2", title: "{{Entity}} 2", userId: "user-123" },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    ({{Entity}}Service.getAll as any).mockResolvedValue(mock{{Entity}}s);
  });

  it("should fetch {{entities}} on mount", async () => {
    const { result } = renderHook(() => use{{Entity}}s());

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.{{entities}}).toEqual(mock{{Entity}}s);
    expect(result.current.error).toBeNull();
  });

  it("should handle fetch error", async () => {
    const errorMessage = "Failed to fetch";
    ({{Entity}}Service.getAll as any).mockRejectedValue(new Error(errorMessage));

    const { result } = renderHook(() => use{{Entity}}s());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe(errorMessage);
    expect(result.current.{{entities}}).toEqual([]);
  });

  it("should create a new {{entity}}", async () => {
    const new{{Entity}} = { _id: "3", title: "New {{Entity}}", userId: "user-123" };
    ({{Entity}}Service.create as any).mockResolvedValue(new{{Entity}});

    const { result } = renderHook(() => use{{Entity}}s());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    await act(async () => {
      await result.current.create{{ Entity }}({ title: "New {{Entity}}" });
    });

    expect({{Entity}}Service.create).toHaveBeenCalledWith(
      { title: "New {{Entity}}" },
      expect.any(Object)
    );
  });

  it("should update a {{entity}}", async () => {
    const updated{{Entity}} = { ...mock{{Entity}}s[0], title: "Updated" };
    ({{Entity}}Service.update as any).mockResolvedValue(updated{{Entity}});

    const { result } = renderHook(() => use{{Entity}}s());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    await act(async () => {
      await result.current.update{{Entity}}("1", { title: "Updated" });
    });

    expect({{Entity}}Service.update).toHaveBeenCalledWith(
      "1",
      { title: "Updated" },
      expect.any(Object)
    );
  });

  it("should delete a {{entity}}", async () => {
    ({{Entity}}Service.delete as any).mockResolvedValue(undefined);

    const { result } = renderHook(() => use{{Entity}}s());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    await act(async () => {
      await result.current.delete{{Entity}}("1");
    });

    expect({{Entity}}Service.delete).toHaveBeenCalledWith("1", expect.any(Object));
  });

  it("should refetch {{entities}}", async () => {
    const { result } = renderHook(() => use{{Entity}}s());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    ({{Entity}}Service.getAll as any).mockClear();

    await act(async () => {
      await result.current.refetch();
    });

    expect({{Entity}}Service.getAll).toHaveBeenCalledTimes(1);
  });
});
