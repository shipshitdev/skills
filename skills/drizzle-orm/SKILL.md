---
name: drizzle-orm
description: Set up and use Drizzle ORM for type-safe database access — schemas, migrations, queries, relations, and integration with Next.js and NestJS
---

# Drizzle ORM

Expert in Drizzle ORM — the lightweight, type-safe TypeScript ORM with zero dependencies and SQL-like query syntax.

## When to Use This Skill

Use when you're:

- Setting up Drizzle ORM in a new or existing project
- Defining database schemas with TypeScript
- Running or generating migrations with drizzle-kit
- Writing type-safe queries (select, insert, update, delete)
- Defining table relations and joins
- Integrating Drizzle with Next.js App Router or NestJS
- Choosing between PostgreSQL, MySQL, or SQLite adapters
- Optimizing query performance with prepared statements

## Quick Setup

### PostgreSQL (most common)

```bash
npm install drizzle-orm postgres
npm install -D drizzle-kit
```

### SQLite (Turso/Libsql)

```bash
npm install drizzle-orm @libsql/client
npm install -D drizzle-kit
```

### MySQL

```bash
npm install drizzle-orm mysql2
npm install -D drizzle-kit
```

## Configuration

### drizzle.config.ts

```ts
import { defineConfig } from "drizzle-kit";

export default defineConfig({
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  dialect: "postgresql", // "mysql" | "sqlite"
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
});
```

### Database Client (src/db/index.ts)

```ts
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "./schema";

const client = postgres(process.env.DATABASE_URL!);
export const db = drizzle(client, { schema });
```

## Schema Definition

### Tables (src/db/schema.ts)

```ts
import {
  pgTable,
  uuid,
  varchar,
  text,
  timestamp,
  integer,
  boolean,
  pgEnum,
} from "drizzle-orm/pg-core";
import { relations } from "drizzle-orm";

// Enums
export const roleEnum = pgEnum("role", ["user", "admin", "moderator"]);

// Users table
export const users = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  email: varchar("email", { length: 255 }).notNull().unique(),
  name: varchar("name", { length: 255 }),
  role: roleEnum("role").default("user").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

// Posts table
export const posts = pgTable("posts", {
  id: uuid("id").primaryKey().defaultRandom(),
  title: varchar("title", { length: 255 }).notNull(),
  content: text("content"),
  published: boolean("published").default(false).notNull(),
  authorId: uuid("author_id")
    .references(() => users.id, { onDelete: "cascade" })
    .notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});
```

### Relations

```ts
export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
}));

export const postsRelations = relations(posts, ({ one }) => ({
  author: one(users, {
    fields: [posts.authorId],
    references: [users.id],
  }),
}));
```

## Migrations

```bash
# Generate migration from schema changes
npx drizzle-kit generate

# Apply migrations
npx drizzle-kit migrate

# Open Drizzle Studio (database GUI)
npx drizzle-kit studio

# Push schema directly (dev only, no migration files)
npx drizzle-kit push
```

## Queries

### Select

```ts
import { eq, and, like, desc, sql } from "drizzle-orm";

// Basic select
const allUsers = await db.select().from(users);

// With conditions
const admins = await db
  .select()
  .from(users)
  .where(eq(users.role, "admin"));

// With relations (query API)
const usersWithPosts = await db.query.users.findMany({
  with: {
    posts: true,
  },
});

// Single record
const user = await db.query.users.findFirst({
  where: eq(users.email, "alice@example.com"),
  with: { posts: { where: eq(posts.published, true) } },
});

// Partial select
const emails = await db
  .select({ email: users.email, name: users.name })
  .from(users);

// Pagination
const page = await db
  .select()
  .from(posts)
  .where(eq(posts.published, true))
  .orderBy(desc(posts.createdAt))
  .limit(10)
  .offset(0);
```

### Insert

```ts
// Single insert
const [newUser] = await db
  .insert(users)
  .values({ email: "alice@example.com", name: "Alice" })
  .returning();

// Bulk insert
await db.insert(posts).values([
  { title: "Post 1", content: "Hello", authorId: newUser.id },
  { title: "Post 2", content: "World", authorId: newUser.id },
]);

// Upsert (on conflict)
await db
  .insert(users)
  .values({ email: "alice@example.com", name: "Alice Updated" })
  .onConflictDoUpdate({
    target: users.email,
    set: { name: "Alice Updated" },
  });
```

### Update

```ts
const [updated] = await db
  .update(users)
  .set({ name: "New Name", updatedAt: new Date() })
  .where(eq(users.id, userId))
  .returning();
```

### Delete

```ts
await db.delete(posts).where(eq(posts.authorId, userId));
```

### Joins

```ts
const result = await db
  .select({
    postTitle: posts.title,
    authorName: users.name,
  })
  .from(posts)
  .innerJoin(users, eq(posts.authorId, users.id))
  .where(eq(posts.published, true));
```

### Transactions

```ts
const result = await db.transaction(async (tx) => {
  const [user] = await tx
    .insert(users)
    .values({ email: "bob@example.com", name: "Bob" })
    .returning();

  await tx.insert(posts).values({
    title: "Bob's first post",
    content: "Hello!",
    authorId: user.id,
    published: true,
  });

  return user;
});
```

### Prepared Statements

```ts
const getUserByEmail = db
  .select()
  .from(users)
  .where(eq(users.email, sql.placeholder("email")))
  .prepare("get_user_by_email");

const user = await getUserByEmail.execute({ email: "alice@example.com" });
```

## Next.js Integration

### Server Actions

```ts
"use server";

import { db } from "@/db";
import { posts } from "@/db/schema";
import { revalidatePath } from "next/cache";

export async function createPost(formData: FormData) {
  await db.insert(posts).values({
    title: formData.get("title") as string,
    content: formData.get("content") as string,
    authorId: "current-user-id", // from auth
  });
  revalidatePath("/posts");
}
```

### Server Components

```ts
import { db } from "@/db";
import { posts } from "@/db/schema";
import { desc, eq } from "drizzle-orm";

export default async function PostsPage() {
  const allPosts = await db
    .select()
    .from(posts)
    .where(eq(posts.published, true))
    .orderBy(desc(posts.createdAt));

  return (
    <ul>
      {allPosts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

## NestJS Integration

### Module Setup

```ts
// db.module.ts
import { Module, Global } from "@nestjs/common";
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "./schema";

export const DB = Symbol("DB");

@Global()
@Module({
  providers: [
    {
      provide: DB,
      useFactory: () => {
        const client = postgres(process.env.DATABASE_URL!);
        return drizzle(client, { schema });
      },
    },
  ],
  exports: [DB],
})
export class DbModule {}
```

### Service Usage

```ts
import { Inject, Injectable } from "@nestjs/common";
import { eq } from "drizzle-orm";
import { DB } from "./db.module";
import { users } from "./schema";

@Injectable()
export class UsersService {
  constructor(@Inject(DB) private db: typeof import("./db")["db"]) {}

  async findByEmail(email: string) {
    return this.db.query.users.findFirst({
      where: eq(users.email, email),
    });
  }
}
```

## Best Practices

1. **Always use `returning()`** for insert/update/delete when you need the result
2. **Use the query API** (`db.query.*`) for relational data — it generates optimal JOINs
3. **Use `sql.placeholder()`** for prepared statements in hot paths
4. **Never use `drizzle-kit push` in production** — always generate and review migrations
5. **Keep schema in a single file** (or barrel-export from `schema/index.ts`) so drizzle-kit picks up all tables
6. **Add indexes** for frequently queried columns:

```ts
import { index } from "drizzle-orm/pg-core";

export const posts = pgTable(
  "posts",
  {
    // ... columns
  },
  (table) => [
    index("posts_author_id_idx").on(table.authorId),
    index("posts_created_at_idx").on(table.createdAt),
  ]
);
```

7. **Use `$inferSelect` and `$inferInsert`** for type inference:

```ts
type User = typeof users.$inferSelect;
type NewUser = typeof users.$inferInsert;
```

## Common Patterns

### Soft Deletes

```ts
export const users = pgTable("users", {
  // ...
  deletedAt: timestamp("deleted_at"),
});

// Query only active records
const activeUsers = await db
  .select()
  .from(users)
  .where(isNull(users.deletedAt));
```

### Full-Text Search (PostgreSQL)

```ts
import { sql } from "drizzle-orm";

const results = await db
  .select()
  .from(posts)
  .where(sql`to_tsvector('english', ${posts.content}) @@ plainto_tsquery('english', ${query})`);
```

### Count

```ts
import { count } from "drizzle-orm";

const [{ total }] = await db
  .select({ total: count() })
  .from(posts)
  .where(eq(posts.published, true));
```

## References

- [Drizzle ORM Docs](https://orm.drizzle.team/docs/overview)
- [Drizzle Kit Docs](https://orm.drizzle.team/kit-docs/overview)
- [Drizzle GitHub](https://github.com/drizzle-team/drizzle-orm)
