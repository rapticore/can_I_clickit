# Deployment Guide

## Architecture Overview

```
                Internet
                   |
            +------v------+
            |   WAF (prod) |
            +------+------+
            +------v--------------------------+
            |     ALB (public subnets)         |
            |  /v1/* -> API TG (port 8000)     |
            |  /*    -> Frontend TG (3000)     |
            +------+--------------------------+
     --------------+---------------- Private App Tier
         +---------+---------+
    +----v----+        +-----v-----+
    | Fargate |        |  Fargate  |
    |  API    |        | Frontend  |
    +----+----+        +-----------+
    -----+--------------------------- Private Data Tier
    +----v----+   +-----------+
    |   RDS   |   | ElastiCache|
    | Postgres|   |   Redis    |
    +---------+   +-----------+
```

Single ALB with path-based routing: `/v1/*` goes to the API, everything else to the frontend.

## Prerequisites

- AWS CLI v2 configured with appropriate credentials
- Terraform >= 1.5.0
- Docker
- (Optional) A registered domain name for HTTPS

## One-Time Setup

### 1. Create Terraform State Infrastructure

```bash
# Create S3 bucket for state
aws s3api create-bucket \
  --bucket clickit-terraform-state \
  --region us-east-1

aws s3api put-bucket-versioning \
  --bucket clickit-terraform-state \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-encryption \
  --bucket clickit-terraform-state \
  --server-side-encryption-configuration '{
    "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "aws:kms"}}]
  }'

aws s3api put-public-access-block \
  --bucket clickit-terraform-state \
  --public-access-block-configuration '{
    "BlockPublicAcls": true,
    "IgnorePublicAcls": true,
    "BlockPublicPolicy": true,
    "RestrictPublicBuckets": true
  }'

# Create DynamoDB lock table
aws dynamodb create-table \
  --table-name clickit-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### 2. Deploy Dev Environment

```bash
cd infra/terraform/environments/dev

# Copy and edit variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

terraform init
terraform plan
terraform apply
```

### 3. Build and Push Docker Images

After `terraform apply` succeeds, note the ECR repository URLs from the outputs:

```bash
# Get ECR login
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $(terraform output -raw ecr_api_repository_url | cut -d/ -f1)

# Build and push API image
cd ../../../../backend
docker build -t $(terraform output -raw ecr_api_repository_url):latest .
docker push $(terraform output -raw ecr_api_repository_url):latest

# Build and push Frontend image
cd ../frontend
docker build -f Dockerfile.prod -t $(terraform output -raw ecr_frontend_repository_url):latest .
docker push $(terraform output -raw ecr_frontend_repository_url):latest
```

### 4. Run Database Migration

```bash
CLUSTER=$(terraform output -raw ecs_cluster_name)
TASK_DEF=$(terraform output -raw migration_task_definition_arn)
SUBNETS=$(aws ec2 describe-subnets --filters "Name=tag:Name,Values=*clickit*private*" --query 'Subnets[*].SubnetId' --output text | tr '\t' ',')
SG=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=*clickit*app*" --query 'SecurityGroups[0].GroupId' --output text)

aws ecs run-task \
  --cluster $CLUSTER \
  --task-definition $TASK_DEF \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SG],assignPublicIp=DISABLED}"

# Wait and check logs
aws logs tail /ecs/clickit-dev-migration --follow
```

### 5. Force New Deployment

```bash
CLUSTER=$(terraform output -raw ecs_cluster_name)

aws ecs update-service \
  --cluster $CLUSTER \
  --service $(terraform output -raw api_service_name) \
  --force-new-deployment

aws ecs update-service \
  --cluster $CLUSTER \
  --service $(terraform output -raw frontend_service_name) \
  --force-new-deployment

# Wait for services to stabilize
aws ecs wait services-stable \
  --cluster $CLUSTER \
  --services $(terraform output -raw api_service_name) $(terraform output -raw frontend_service_name)
```

### 6. Verify

```bash
ALB_DNS=$(terraform output -raw alb_dns_name)

# API health check
curl http://$ALB_DNS/v1/health

# Frontend
curl -s http://$ALB_DNS/ | head -20
```

## Per-Deployment Workflow

For subsequent deployments after initial setup:

```bash
# 1. Build + push images
docker build -t $ECR_API_URL:$GIT_SHA backend/
docker push $ECR_API_URL:$GIT_SHA

docker build -f frontend/Dockerfile.prod -t $ECR_FE_URL:$GIT_SHA frontend/
docker push $ECR_FE_URL:$GIT_SHA

# 2. Run migration (if schema changes)
aws ecs run-task --cluster $CLUSTER --task-definition $MIGRATION_TASK_DEF \
  --launch-type FARGATE --network-configuration "..."

# 3. Update services
aws ecs update-service --cluster $CLUSTER --service clickit-$ENV-api --force-new-deployment
aws ecs update-service --cluster $CLUSTER --service clickit-$ENV-frontend --force-new-deployment

# 4. Wait for stability
aws ecs wait services-stable --cluster $CLUSTER --services clickit-$ENV-api clickit-$ENV-frontend
```

## Rollback

To roll back to a previous deployment:

```bash
# Find previous task definition revision
aws ecs list-task-definitions --family-prefix clickit-$ENV-api --sort DESC --max-items 5

# Roll back
aws ecs update-service \
  --cluster $CLUSTER \
  --service clickit-$ENV-api \
  --task-definition clickit-$ENV-api:PREVIOUS_REVISION
```

## Deploying to Production

```bash
cd infra/terraform/environments/prod

cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars — production REQUIRES api_keys_json

terraform init
terraform plan
terraform apply
```

Production differences:
- Standard Fargate (no Spot)
- Multi-AZ RDS
- Auto-scaling enabled (API 2-10, Frontend 2-6)
- WAF enabled
- VPC Flow Logs enabled
- 30-day log retention

## HTTPS Setup (Optional)

1. Set `domain_name` in `terraform.tfvars`
2. `terraform apply` creates an ACM certificate
3. Add the DNS validation CNAME record to your DNS provider
4. Wait for certificate validation (~5 min)
5. `terraform apply` again to create the HTTPS listener
6. Point your domain's A record to the ALB DNS name (or create a CNAME)

## Environment Configuration

| Parameter | Dev | Prod |
|-----------|-----|------|
| Fargate | Spot | Standard |
| API | 0.5 vCPU / 1 GB, 1 task | 1 vCPU / 2 GB, 2 tasks |
| Frontend | 0.25 vCPU / 512 MB, 1 task | 0.5 vCPU / 1 GB, 2 tasks |
| Auto-scaling | Disabled | API 2-10, Frontend 2-6 |
| RDS | db.t4g.micro, single-AZ | db.t4g.small, Multi-AZ |
| NAT Gateway | Single | Per-AZ |
| WAF | Disabled | Enabled |
| Log retention | 7 days | 30 days |
| Est. monthly | ~$86 | ~$260 |
