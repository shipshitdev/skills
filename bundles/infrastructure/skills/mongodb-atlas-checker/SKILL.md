---
name: mongodb-atlas-checker
description: "Verifies MongoDB Atlas setup for Next.js and NestJS backends: connection strings, env vars, and pooling. Use before deployment or when troubleshooting database connections."
metadata:
  version: "2.2.2"
  tags: "mongodb, atlas, database, backend, nestjs, nextjs"
when_to_use: "MONGODB_URI, Atlas connection error"
---

# MongoDB Atlas Checker

## When to Use

- Verifying MongoDB Atlas backend setup
- Checking connection string configuration
- Validating environment variable setup
- Troubleshooting database connection issues
- Auditing database setup before deployment

## Quick Checklist

### 1. Environment Variables

- [ ] `MONGODB_URI` exists (not hardcoded)
- [ ] Uses `mongodb+srv://` protocol (required for Atlas)
- [ ] Includes database name
- [ ] Includes `retryWrites=true&w=majority`
- [ ] No credentials in `.env.example`

### 2. Connection String Format

```
mongodb+srv://USERNAME:PASSWORD@CLUSTER-HOST/DATABASE?retryWrites=true&w=majority
```

### 3. Driver Installation

- [ ] `mongoose` or `mongodb` package installed
- [ ] In dependencies (not devDependencies)

### 4. Connection Setup

- [ ] Singleton pattern (Next.js)
- [ ] `MongooseModule.forRoot()` (NestJS)
- [ ] Error handling implemented

### 5. Atlas Configuration

- [ ] IP whitelist configured
- [ ] Database user exists with permissions
- [ ] SSL/TLS enabled (default with `mongodb+srv://`)

## Common Issues

| Issue | Solution |
|-------|----------|
| Missing `MONGODB_URI` | Add to `.env.local` or `.env` |
| Wrong protocol | Use `mongodb+srv://` not `mongodb://` |
| Multiple connections (Next.js) | Use singleton pattern |
| Connection timeout | Check IP whitelist in Atlas |
| Auth failed | Verify credentials, URL-encode special chars |

## Recommended Connection Options

```typescript
{
  retryWrites: true,
  w: 'majority',
  maxPoolSize: 10,
  serverSelectionTimeoutMS: 5000,
  bufferCommands: false,
}
```

---

**For detailed setup patterns, verification scripts, and complete examples:** `references/full-guide.md`
