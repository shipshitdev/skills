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

async function getAuthHeaders(): Promise<HeadersInit> {
  // Get token from Clerk
  const token = await window.Clerk?.session?.getToken();

  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "Request failed" }));
    throw new Error(error.message || `HTTP ${response.status}`);
  }
  return response.json();
}

export const {{Entity}}Service = {
  async getAll(options?: RequestOptions): Promise<{{Entity}}[]> {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_URL}/{{entities}}`, {
      headers,
      signal: options?.signal,
    });
    return handleResponse<{{Entity}}[]>(response);
  },

  async getById(id: string, options?: RequestOptions): Promise<{{Entity}}> {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_URL}/{{entities}}/${id}`, {
      headers,
      signal: options?.signal,
    });
    return handleResponse<{{Entity}}>(response);
  },

  async create(data: Partial<{{Entity}}>): Promise<{{Entity}}> {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_URL}/{{entities}}`, {
      method: "POST",
      headers,
      body: JSON.stringify(data),
    });
    return handleResponse<{{Entity}}>(response);
  },

  async update(id: string, data: Partial<{{Entity}}>): Promise<{{Entity}}> {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_URL}/{{entities}}/${id}`, {
      method: "PATCH",
      headers,
      body: JSON.stringify(data),
    });
    return handleResponse<{{Entity}}>(response);
  },

  async delete(id: string): Promise<void> {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_URL}/{{entities}}/${id}`, {
      method: "DELETE",
      headers,
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: "Delete failed" }));
      throw new Error(error.message);
    }
  },
};
