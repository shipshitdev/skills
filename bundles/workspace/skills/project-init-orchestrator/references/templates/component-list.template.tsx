/**
 * React List Component Template
 *
 * Replace {{Entity}} with PascalCase entity name (e.g., Task)
 * Replace {{entity}} with camelCase entity name (e.g., task)
 * Replace {{entities}} with plural camelCase (e.g., tasks)
 */

"use client";

import { useEffect, useState } from "react";
import { {{Entity}}Service } from "@services/{{entity}}.service";
import { {{Entity}} } from "@interfaces/{{entity}}.interface";
import { {{Entity}}Item } from "./{{entity}}-item";
import { {{Entity}}Form } from "./{{entity}}-form";

export function {{Entity}}List() {
  const [{{entities}}, set{{Entity}}s] = useState<{{Entity}}[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  const fetch{{Entity}}s = async () => {
    try {
      setLoading(true);
      const controller = new AbortController();
      const data = await {{Entity}}Service.getAll({ signal: controller.signal });
      set{{Entity}}s(data);
      setError(null);
    } catch (err) {
      if (err instanceof Error && err.name !== "AbortError") {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const controller = new AbortController();

    {{Entity}}Service.getAll({ signal: controller.signal })
      .then(set{{Entity}}s)
      .catch((err) => {
        if (err.name !== "AbortError") {
          setError(err.message);
        }
      })
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, []);

  const handleCreate = async (data: Partial<{{Entity}}>) => {
    try {
      await {{Entity}}Service.create(data);
      setShowForm(false);
      fetch{{Entity}}s();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create");
    }
  };

  const handleUpdate = async (id: string, data: Partial<{{Entity}}>) => {
    try {
      await {{Entity}}Service.update(id, data);
      fetch{{Entity}}s();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update");
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await {{Entity}}Service.delete(id);
      fetch{{Entity}}s();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-danger p-4 text-danger" role="alert">
        Error: {error}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">{{Entity}}s</h2>
        <button
          type="button"
          className="rounded-lg bg-primary px-3 py-2 font-medium text-primary-foreground"
          onClick={() => setShowForm(true)}
        >
          Add {{Entity}}
        </button>
      </div>

      {showForm && (
        <{{Entity}}Form
          onSubmit={handleCreate}
          onCancel={() => setShowForm(false)}
        />
      )}

      {{{entities}}.length === 0 ? (
        <div className="py-8 text-center text-muted">
          No {{entities}} yet. Create your first one!
        </div>
      ) : (
        <div className="space-y-2">
          {{{entities}}.map(({{entity}}) => (
            <{{Entity}}Item
              key={{{entity}}.id}
              {{entity}}={{{entity}}}
              onUpdate={handleUpdate}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}
