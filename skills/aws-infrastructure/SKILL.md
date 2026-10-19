---
name: aws-infrastructure
description: "Sets up AWS infrastructure: EC2, VPC, security groups, load balancers, Route53 DNS, and ACM certificates. Use when configuring or deploying AWS resources."
metadata:
  version: "2.2.4"
  tags: "aws, infrastructure, devops"
when_to_use: "auto-scaling, CloudWatch"
---

# AWS Infrastructure Expert

Use for EC2 instance setup, VPC and networking, security groups, Application Load Balancer setup, Route53 DNS, ACM certificate management, and CloudWatch monitoring. These are baseline recommendations; adapt sizes and ports to the project, and confirm before creating or changing real resources.

## EC2 setup

### Instance types

- **Development:** t3.medium (2 vCPU, 4GB RAM)
- **Production (small):** t3.large (2 vCPU, 8GB RAM)
- **Production (medium):** m5.large (2 vCPU, 8GB RAM)

### Storage

- Use gp3 SSD volumes
- Development: 20GB minimum
- Production: 100GB+ based on needs
- Enable EBS snapshots for backups

### Key pairs

- Generate or import SSH key pairs
- Store private keys securely
- Use IAM roles instead of access keys when possible

## VPC configuration

### Basic setup

- Create the VPC with a CIDR block (for example 10.0.0.0/16)
- Create public and private subnets
- Set up an Internet Gateway
- Configure route tables
- Set up a NAT Gateway for private subnets (if needed)

### Subnets

- Public subnets: load balancers, bastion hosts
- Private subnets: application servers, databases
- Multi-AZ for high availability

## Security groups

### Application security group

```
Inbound:
- HTTP (80) from ALB security group
- HTTPS (443) from ALB security group
- SSH (22) from bastion/your IP only

Outbound:
- All traffic (0.0.0.0/0)
```

### Database security group

```
Inbound:
- Postgres (5432) from application security group only
- Redis (6379) from application security group only
- SSH (22) from bastion/your IP only

Outbound:
- All traffic (0.0.0.0/0)
```

### Load balancer security group

```
Inbound:
- HTTP (80) from 0.0.0.0/0
- HTTPS (443) from 0.0.0.0/0

Outbound:
- HTTP (80) to application security group
- HTTPS (443) to application security group
```

## Application Load Balancer

### Setup

1. Create the ALB in public subnets.
2. Configure target groups (EC2 instances).
3. Set up health checks.
4. Configure listeners (HTTP to HTTPS redirect).
5. Attach an SSL certificate from ACM.

### Health checks

- Path: `/health` or `/api/health`
- Protocol: HTTP
- Port: 3001 (backend) or 3000 (frontend), or the app's actual port
- Healthy threshold: 2
- Unhealthy threshold: 2
- Timeout: 5 seconds
- Interval: 30 seconds

## Route53 DNS

### Domain setup

1. Create a hosted zone for the domain.
2. Create an A record (alias) pointing to the ALB.
3. Create a CNAME for the www subdomain.
4. Update nameservers at the domain registrar.

### SSL/TLS (ACM)

1. Request the certificate in ACM in the same region as the ALB. Only certificates used by CloudFront must be in us-east-1.
2. Validate via DNS (add the CNAME records).
3. Attach the certificate to the ALB listener.
4. ACM renews the certificate automatically while the DNS validation record stays in place.

## CloudWatch monitoring

### Metrics

- EC2: CPU, network (memory and disk metrics require the CloudWatch agent)
- ALB: request count, target response time, HTTP errors
- Custom metrics for application-specific data

### Alarms

- High CPU utilization
- Low disk space
- Application errors (via CloudWatch Logs)
- Unhealthy target instances

## Best practices

- Use IAM roles instead of access keys
- Enable CloudTrail for audit logging
- Use VPC endpoints for AWS service access
- Implement least-privilege security groups
- Use private subnets for databases
- Enable encryption at rest for EBS volumes
- Set up automated backups (EBS snapshots)
- Monitor costs with AWS Cost Explorer
