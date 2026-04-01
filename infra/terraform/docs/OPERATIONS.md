# Operations Runbook

## Monitoring

### CloudWatch Dashboards

Key metrics to monitor:

- **ECS**: CPUUtilization, MemoryUtilization, RunningTaskCount
- **ALB**: RequestCount, TargetResponseTime, HTTPCode_Target_5XX_Count, UnHealthyHostCount
- **RDS**: CPUUtilization, FreeableMemory, ReadIOPS, WriteIOPS, DatabaseConnections
- **ElastiCache**: CPUUtilization, CurrConnections, EngineCPUUtilization

### CloudWatch Alarms (Production)

The following alarms are auto-created in production:

| Alarm | Condition | Action |
|-------|-----------|--------|
| API CPU High | CPU > 85% for 10min | Investigate + scale |
| ALB 5xx Errors | > 10 5xx in 5min | Check API logs |
| Unhealthy Targets | Any unhealthy target | Check health endpoint |

### Log Groups

```
/ecs/clickit-{env}-api          # API application logs
/ecs/clickit-{env}-frontend     # Frontend application logs
/ecs/clickit-{env}-migration    # Migration task logs
```

View logs:
```bash
# Tail API logs
aws logs tail /ecs/clickit-dev-api --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /ecs/clickit-dev-api \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s000)
```

## Common Operations

### Scaling Manually

```bash
# Scale API to 3 tasks
aws ecs update-service \
  --cluster clickit-$ENV-cluster \
  --service clickit-$ENV-api \
  --desired-count 3

# Scale frontend to 2 tasks
aws ecs update-service \
  --cluster clickit-$ENV-cluster \
  --service clickit-$ENV-frontend \
  --desired-count 2
```

### Viewing Running Tasks

```bash
# List running tasks
aws ecs list-tasks --cluster clickit-$ENV-cluster --service-name clickit-$ENV-api

# Describe a task (get IP, status, etc.)
aws ecs describe-tasks --cluster clickit-$ENV-cluster --tasks TASK_ARN
```

### ECS Exec (Shell into Container)

```bash
aws ecs execute-command \
  --cluster clickit-$ENV-cluster \
  --task TASK_ID \
  --container api \
  --interactive \
  --command "/bin/sh"
```

### Database Operations

```bash
# Connect via SSM + port forwarding (requires bastion or SSM-enabled task)
# From within a Fargate task:
PGPASSWORD=$CLICKIT_DATABASE_URL psql -h DB_HOST -U clickit -d clickit
```

### Secret Rotation

```bash
# Update a secret
aws secretsmanager update-secret \
  --secret-id clickit/$ENV/jwt-secret-key \
  --secret-string "new-value"

# Force new deployment to pick up new secret
aws ecs update-service \
  --cluster clickit-$ENV-cluster \
  --service clickit-$ENV-api \
  --force-new-deployment
```

### Viewing ECR Images

```bash
aws ecr list-images --repository-name clickit/api
aws ecr list-images --repository-name clickit/frontend

# Get image scan results
aws ecr describe-image-scan-findings \
  --repository-name clickit/api \
  --image-id imageTag=latest
```

## Incident Response

### API Returning 5xx

1. Check API logs: `aws logs tail /ecs/clickit-$ENV-api --follow`
2. Check target group health: `aws elbv2 describe-target-health --target-group-arn $API_TG_ARN`
3. Check if DB is reachable: look for connection errors in logs
4. Check RDS metrics: CPU, connections, free memory
5. If recent deployment: roll back (see Deployment guide)

### Service Won't Start

1. Check stopped tasks: `aws ecs list-tasks --cluster CLUSTER --desired-status STOPPED`
2. Describe stopped task for exit code/reason: `aws ecs describe-tasks --tasks TASK_ARN`
3. Common causes:
   - Image pull failure: check ECR repo has the image
   - Secret not found: check Secrets Manager has all 6 secrets
   - Health check failure: check the health endpoint works locally
   - OOM: increase memory in Terraform and redeploy

### Database Connection Issues

1. Check RDS instance status: `aws rds describe-db-instances --db-instance-identifier clickit-$ENV-db`
2. Check security group allows port 5432 from app SG
3. Check DB connections metric (max 60 for t4g.micro)
4. Check if migration is running (locks tables)

### High Latency

1. Check ALB TargetResponseTime metric
2. Check RDS read/write IOPS — may need larger instance
3. Check Redis cache hit rate
4. Check ECS CPU utilization — may need to scale out
5. Check NAT gateway bandwidth (if making many external API calls)

## Disaster Recovery

### RDS Backup Restore

```bash
# List snapshots
aws rds describe-db-snapshots --db-instance-identifier clickit-$ENV-db

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier clickit-$ENV-db-restored \
  --db-snapshot-identifier SNAPSHOT_ID
```

### Full Environment Rebuild

```bash
cd infra/terraform/environments/$ENV
terraform destroy  # Careful!
terraform apply    # Rebuild from scratch
# Then: push images, run migration, deploy
```

## Cost Management

### Dev Environment (~$86/mo)

| Resource | Approx. Cost |
|----------|-------------|
| NAT Gateway (single) | $32 |
| RDS db.t4g.micro | $12 |
| ElastiCache cache.t4g.micro | $9 |
| Fargate Spot (API + Frontend) | $15 |
| ALB | $16 |
| Misc (logs, secrets, S3) | $2 |

### Prod Environment (~$260/mo)

| Resource | Approx. Cost |
|----------|-------------|
| NAT Gateway (x2, per-AZ) | $64 |
| RDS db.t4g.small Multi-AZ | $50 |
| ElastiCache cache.t4g.micro | $9 |
| Fargate Standard (2 API + 2 FE) | $85 |
| ALB | $16 |
| WAF | $10 |
| Misc (logs, secrets, S3, flow logs) | $26 |

### Cost Reduction Tips

- **Dev**: Stop services outside business hours
  ```bash
  # Scale to zero at night
  aws ecs update-service --cluster clickit-dev-cluster --service clickit-dev-api --desired-count 0
  aws ecs update-service --cluster clickit-dev-cluster --service clickit-dev-frontend --desired-count 0
  ```
- **Dev**: Consider stopping/starting RDS off-hours
- **Prod**: Monitor auto-scaling — ensure scale-in works properly
- Review CloudWatch log retention periodically
