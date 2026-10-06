/**
 * React Form Component Template
 *
 * Replace {{Entity}} with PascalCase entity name (e.g., Task)
 * Replace {{entity}} with camelCase entity name (e.g., task)
 * Replace {{FIELDS}} with actual form fields
 */

"use client";

import { useState } from "react";
import { {{Entity}} } from "@interfaces/{{entity}}.interface";

interface {{Entity}}FormProps {
  {{entity}}?: {{Entity}};
  onSubmit: (data: Partial<{{Entity}}>) => Promise<void>;
  onCancel: () => void;
}

export function {{Entity}}Form({ {{entity}}, onSubmit, onCancel }: {{Entity}}FormProps) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<Partial<{{Entity}}>>({
    // Initialize with existing data or defaults
    // {{FIELDS}}
    ...{{entity}},
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSubmit(formData);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: keyof {{Entity}}, value: unknown) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 border rounded-lg">
      {/**
       * FORM FIELD EXAMPLES:
       *
       * Text input:
       * <div>
       *   <label className="block text-sm font-medium mb-1">Title</label>
       *   <input
       *     className="w-full rounded-lg border border-border bg-background px-3 py-2"
       *     value={formData.title || ""}
       *     onChange={(e) => handleChange("title", e.target.value)}
       *     placeholder="Enter title"
       *     required
       *   />
       * </div>
       *
       * Textarea:
       * <div>
       *   <label className="block text-sm font-medium mb-1">Description</label>
       *   <textarea
       *     className="w-full rounded-lg border border-border bg-background px-3 py-2"
       *     value={formData.description || ""}
       *     onChange={(e) => handleChange("description", e.target.value)}
       *     rows={3}
       *   />
       * </div>
       *
       * Select:
       * <div>
       *   <label className="block text-sm font-medium mb-1">Priority</label>
       *   <select
       *     className="w-full rounded-lg border border-border bg-background px-3 py-2"
       *     value={formData.priority || "medium"}
       *     onChange={(e) => handleChange("priority", e.target.value)}
       *   >
       *     <option value="low">Low</option>
       *     <option value="medium">Medium</option>
       *     <option value="high">High</option>
       *   </select>
       * </div>
       *
       * Date:
       * <div>
       *   <label className="block text-sm font-medium mb-1">Due Date</label>
       *   <input
       *     className="w-full rounded-lg border border-border bg-background px-3 py-2"
       *     type="date"
       *     value={formData.dueDate || ""}
       *     onChange={(e) => handleChange("dueDate", e.target.value)}
       *   />
       * </div>
       */}

      {/* {{FIELDS}} */}

      <div className="flex gap-2 justify-end">
        <button type="button" className="rounded-lg px-3 py-2 hover:bg-border" onClick={onCancel}>
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-primary px-3 py-2 font-medium text-primary-foreground disabled:opacity-50"
        >
          {loading ? "Saving..." : {{entity}} ? "Update" : "Create"}
        </button>
      </div>
    </form>
  );
}
