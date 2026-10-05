/**
 * React Component Test Template (Vitest + Testing Library)
 *
 * Replace {{Entity}} with PascalCase entity name (e.g., Task)
 * Replace {{entity}} with camelCase entity name (e.g., task)
 * Replace {{entities}} with plural camelCase (e.g., tasks)
 *
 * Requires: npm install -D @testing-library/react @testing-library/jest-dom jsdom
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { {{Entity}}List } from "./{{entity}}-list";
import { {{Entity}}Form } from "./{{entity}}-form";
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
    isSignedIn: true,
  }),
  useUser: () => ({
    user: { id: "user-123", firstName: "Test" },
  }),
}));

describe("{{Entity}}List", () => {
  const mock{{Entity}}s = [
    { _id: "1", title: "{{Entity}} 1", userId: "user-123" },
    { _id: "2", title: "{{Entity}} 2", userId: "user-123" },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    ({{Entity}}Service.getAll as any).mockResolvedValue(mock{{Entity}}s);
  });

  it("should render loading state initially", () => {
    render(<{{Entity}}List />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("should render {{entities}} after loading", async () => {
    render(<{{Entity}}List />);

    await waitFor(() => {
      expect(screen.getByText("{{Entity}} 1")).toBeInTheDocument();
      expect(screen.getByText("{{Entity}} 2")).toBeInTheDocument();
    });
  });

  it("should handle empty state", async () => {
    ({{Entity}}Service.getAll as any).mockResolvedValue([]);

    render(<{{Entity}}List />);

    await waitFor(() => {
      expect(screen.getByText(/no {{entities}} found/i)).toBeInTheDocument();
    });
  });

  it("should handle error state", async () => {
    ({{Entity}}Service.getAll as any).mockRejectedValue(new Error("Failed to fetch"));

    render(<{{Entity}}List />);

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it("should delete a {{entity}}", async () => {
    ({{Entity}}Service.delete as any).mockResolvedValue(undefined);

    render(<{{Entity}}List />);

    await waitFor(() => {
      expect(screen.getByText("{{Entity}} 1")).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByRole("button", { name: /delete/i });
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect({{Entity}}Service.delete).toHaveBeenCalledWith("1", expect.any(Object));
    });
  });
});

describe("{{Entity}}Form", () => {
  const mockOnSubmit = vi.fn();
  const mockOnCancel = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render empty form for new {{entity}}", () => {
    render(<{{Entity}}Form onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

    expect(screen.getByLabelText(/title/i)).toHaveValue("");
  });

  it("should render populated form for editing", () => {
    const {{entity}} = { _id: "1", title: "Existing {{Entity}}" };

    render(
      <{{Entity}}Form
        initialData={{ entity }}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByLabelText(/title/i)).toHaveValue("Existing {{Entity}}");
  });

  it("should call onSubmit with form data", async () => {
    render(<{{Entity}}Form onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

    const titleInput = screen.getByLabelText(/title/i);
    fireEvent.change(titleInput, { target: { value: "New {{Entity}}" } });

    const submitButton = screen.getByRole("button", { name: /save|submit/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({ title: "New {{Entity}}" })
      );
    });
  });

  it("should call onCancel when cancel button clicked", () => {
    render(<{{Entity}}Form onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

    const cancelButton = screen.getByRole("button", { name: /cancel/i });
    fireEvent.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalled();
  });

  it("should show validation errors for empty required fields", async () => {
    render(<{{Entity}}Form onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

    const submitButton = screen.getByRole("button", { name: /save|submit/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/title is required/i)).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });
});
