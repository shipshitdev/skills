# Deployment Workflow Reference

Detailed deployment patterns for various platforms and frameworks.

## Project Context Discovery

Before deploying, discover the project's setup:

1. **Identify Project Type**: Scan for `package.json`, `next.config.js`, `nest-cli.json`, `vite.config.js`
2. **Discover Deployment Platform**: Check for AWS configs, `vercel.json`, Dockerfiles, `.github/workflows/`
3. **Identify Build Commands**: Check `package.json` scripts for `build`, `build:prod`, `build:staging`
4. **Check Environment Configuration**: Review `.env.example` for required variables

## Framework-Specific Deployment

### Next.js (Vercel)

```bash
vercel --prod    # Production
vercel           # Preview
```

### NestJS (Docker/AWS)

```bash
docker build -t [project-name]:[tag] .
docker push [registry]/[project-name]:[tag]
```

### React (Static Hosting)

```bash
npm run build
aws s3 sync build/ s3://[bucket-name] --delete
aws cloudfront create-invalidation --distribution-id [id] --paths "/*"
```

## AWS Patterns

### ECS/Fargate

```bash
aws ecs update-service \
  --cluster [cluster-name] \
  --service [service-name] \
  --force-new-deployment
```

### Lambda

```bash
serverless deploy --stage [environment]
```

### S3/CloudFront Static

```bash
npm run build
aws s3 sync build/ s3://[bucket] --delete --cache-control "max-age=31536000"
aws cloudfront create-invalidation --distribution-id [id] --paths "/*"
```

## Database Considerations

Before deployment:

1. Run migrations: `npm run migrate:up` or equivalent
2. Verify connection strings for target environment
3. Check replica set configuration and network access
4. Verify indexes are created

## Rollback Procedures

### Docker/ECS

```bash
aws ecs update-service \
  --cluster [cluster] \
  --service [service] \
  --task-definition [previous-version]
```

### Vercel

```bash
vercel rollback
```

### Database

```bash
npm run migrate:down
```

## Deployment Patterns

- **Blue-Green**: Deploy new version alongside old, switch traffic when verified
- **Canary**: Deploy to small percentage, gradually increase if healthy
- **Rolling**: Update instances one at a time, maintain availability

## CI/CD Integration

```bash
# Check GitHub Actions
ls .github/workflows/

# Trigger deployment workflow
gh workflow run deploy.yml --ref main -f environment=production
```

## Safety Features

Always include for production:

- [ ] All tests passing
- [ ] Build successful
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] Rollback plan prepared
- [ ] Team notified
