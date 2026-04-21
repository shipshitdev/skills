# Env Setup - Environment Variable Management

Scaffold .env files, validate required variables, document secrets.

## Usage

```bash
/env-setup              # Interactive environment setup
/env-setup --validate   # Validate existing .env files
/env-setup --scaffold   # Generate .env template files
```

## Workflow

### Phase 1: Discover Required Variables

Scan codebase for `process.env.*` usage:

```bash
grep -r "process.env\." --include="*.ts" --include="*.tsx" --include="*.js" . | grep -v node_modules | sort -u
```

Check existing `.env*` files and config files for context.

### Phase 2: Generate .env Templates

Create `.env.example` from discovered variables. Group by service:

```env
# Application
NODE_ENV=development
PORT=3001

# Database (AWS RDS)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Authentication
AUTH_SECRET=...

# Monitoring
SENTRY_DSN=https://...

# AI / External APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# AWS
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
```

For monorepos, create per-app templates if apps need different vars.

### Phase 3: Validate

Check required variables are set and match expected formats:

```bash
# Quick check
if [ ! -f .env ]; then echo ".env not found"; exit 1; fi
```

For TypeScript projects, prefer zod-based env validation at app startup. Fail fast on missing vars.

### Phase 4: Secrets Management

**Never commit:** `.env`, `.env.local`, `.env.production`, `.env.staging`
**Always commit:** `.env.example` (template, no real values)

Ensure `.gitignore` covers all `.env*` files except `.env.example`.

For production: use AWS Secrets Manager, Vercel env vars, or platform-native secrets.

## Checklist

- [ ] Scan codebase for `process.env.*`
- [ ] Check existing `.env*` files
- [ ] Generate/update `.env.example`
- [ ] Validate required vars are set
- [ ] Confirm `.gitignore` excludes `.env*`
- [ ] Document vars that need explanation
