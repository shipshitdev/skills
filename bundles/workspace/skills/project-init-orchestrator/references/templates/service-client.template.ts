/**
 * Frontend API Service Template
 *
 * Replace {{Entity}} with PascalCase entity name (e.g., Task)
 * Replace {{entity}} with camelCase entity name (e.g., task)
 * Replace {{entities}} with plural camelCase (e.g., tasks)
 */

import { {{Entity}} } from "@interfaces/{{entity}}.interface";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001";

interface RequestOptions {
  signal?: AbortSignal;
}

// Better Auth keeps the session in an HTTP-only cookie set by the API, so requests only
// need to send credentials; no token handling lives in the browser.
const jsonHeaders: HeadersInit = { "Content-Type": "application/json" };

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "Request failed" }));
    throw new Error(error.message || `HTTP ${response.status}`);
  }
  return response.json();
}

export const {{Entity}}Service = {
  async getAll(options?: RequestOptions): Promise<{{Entity}}[]> {
    const response = await fetch(`${API_URL}/{{entities}}`, {
      headers: jsonHeaders,
      credentials: "include",
      signal: options?.signal,
    });
    return handleResponse<{{Entity}}[]>(response);
  },

  async getById(id: string, options?: RequestOptions): Promise<{{Entity}}> {
    const response = await fetch(`${API_URL}/{{entities}}/${id}`, {
      headers: jsonHeaders,
      credentials: "include",
      signal: options?.signal,
    });
    return handleResponse<{{Entity}}>(response);
  },

  async create(data: Partial<{{Entity}}>): Promise<{{Entity}}> {
    const response = await fetch(`${API_URL}/{{entities}}`, {
      method: "POST",
      headers: jsonHeaders,
      credentials: "include",
      body: JSON.stringify(data),
    });
    return handleResponse<{{Entity}}>(response);
  },

  async update(id: string, data: Partial<{{Entity}}>): Promise<{{Entity}}> {
    const response = await fetch(`${API_URL}/{{entities}}/${id}`, {
      method: "PATCH",
      headers: jsonHeaders,
      credentials: "include",
      body: JSON.stringify(data),
    });
    return handleResponse<{{Entity}}>(response);
  },

  async delete(id: string): Promise<void> {
    const response = await fetch(`${API_URL}/{{entities}}/${id}`, {
      method: "DELETE",
      credentials: "include",
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: "Delete failed" }));
      throw new Error(error.message);
    }
  },
};
