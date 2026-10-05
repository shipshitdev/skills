/**
 * Mongoose Schema Template
 *
 * Replace {{Entity}} with PascalCase entity name (e.g., Task)
 * Replace {{FIELDS}} with actual field definitions
 */

import { Prop, Schema, SchemaFactory } from "@nestjs/mongoose";
import { Document } from "mongoose";

export type {{Entity}}Document = {{Entity}} & Document;

@Schema({ timestamps: true })
export class {{Entity}} {
  /**
   * FIELD EXAMPLES - Replace with actual fields:
   *
   * Required string:
   * @Prop({ required: true })
   * title: string;
   *
   * Optional string:
   * @Prop()
   * description?: string;
   *
   * Enum:
   * @Prop({ required: true, default: 'medium', enum: ['low', 'medium', 'high'] })
   * priority: string;
   *
   * Date:
   * @Prop()
   * dueDate?: Date;
   *
   * Boolean:
   * @Prop({ default: false })
   * isCompleted: boolean;
   *
   * Array of strings:
   * @Prop({ type: [String], default: [] })
   * tags?: string[];
   *
   * Reference to another collection:
   * @Prop()
   * projectId?: string;
   */

  // {{FIELDS}}

  // Always include userId for multi-tenancy
  @Prop({ required: true })
  userId: string;
}

export const {{Entity}}Schema = SchemaFactory.createForClass({{Entity}});

// Add indexes for common queries
{{Entity}}Schema.index({ userId: 1 });
{{Entity}}Schema.index({ userId: 1, createdAt: -1 });
