variable "project" {
  type        = string
  description = "Project name"
}

variable "environment" {
  type        = string
  description = "Environment name (dev, prod)"
}

variable "aws_region" {
  type        = string
  description = "AWS region"
}

# Networking
variable "vpc_id" {
  type        = string
  description = "VPC ID"
}

variable "public_subnets" {
  type        = list(string)
  description = "Public subnet IDs for ALB"
}

variable "private_subnets" {
  type        = list(string)
  description = "Private subnet IDs for ECS tasks"
}

variable "alb_security_group_id" {
  type        = string
  description = "Security group ID for ALB"
}

variable "app_security_group_id" {
  type        = string
  description = "Security group ID for app tasks"
}

# IAM
variable "ecs_execution_role_arn" {
  type        = string
  description = "ECS task execution role ARN"
}

variable "ecs_task_role_arn" {
  type        = string
  description = "ECS task role ARN"
}

# Secrets
variable "database_url_secret_arn" {
  type        = string
  description = "ARN of database URL secret"
}

variable "redis_url_secret_arn" {
  type        = string
  description = "ARN of Redis URL secret"
}

variable "jwt_secret_key_secret_arn" {
  type        = string
  description = "ARN of JWT secret key secret"
}

variable "api_keys_secret_arn" {
  type        = string
  description = "ARN of API keys secret"
}

variable "anthropic_api_key_secret_arn" {
  type        = string
  description = "ARN of Anthropic API key secret"
}

variable "virustotal_api_key_secret_arn" {
  type        = string
  description = "ARN of VirusTotal API key secret"
}

# API Service
variable "api_cpu" {
  type        = string
  description = "API task CPU units"
  default     = "512"
}

variable "api_memory" {
  type        = string
  description = "API task memory (MB)"
  default     = "1024"
}

variable "api_desired_count" {
  type        = number
  description = "Desired number of API tasks"
  default     = 1
}

variable "api_max_count" {
  type        = number
  description = "Maximum number of API tasks (auto-scaling)"
  default     = 10
}

# Frontend Service
variable "frontend_cpu" {
  type        = string
  description = "Frontend task CPU units"
  default     = "256"
}

variable "frontend_memory" {
  type        = string
  description = "Frontend task memory (MB)"
  default     = "512"
}

variable "frontend_desired_count" {
  type        = number
  description = "Desired number of frontend tasks"
  default     = 1
}

variable "frontend_max_count" {
  type        = number
  description = "Maximum number of frontend tasks (auto-scaling)"
  default     = 6
}

# Cluster Config
variable "use_fargate_spot" {
  type        = bool
  description = "Use Fargate Spot capacity provider"
  default     = true
}

variable "enable_autoscaling" {
  type        = bool
  description = "Enable ECS auto-scaling"
  default     = false
}

# ALB Config
variable "domain_name" {
  type        = string
  description = "Domain name for HTTPS (empty = HTTP only)"
  default     = ""
}

variable "cors_origins" {
  type        = string
  description = "Comma-separated allowed CORS origins"
  default     = "*"
}

variable "alb_logs_bucket_id" {
  type        = string
  description = "S3 bucket ID for ALB access logs (null to disable)"
  default     = null
}

variable "waf_acl_arn" {
  type        = string
  description = "WAF Web ACL ARN to associate with ALB (null to disable)"
  default     = null
}

# Logging
variable "log_retention_days" {
  type        = number
  description = "CloudWatch log retention in days"
  default     = 7
}

variable "tags" {
  type        = map(string)
  description = "Resource tags"
}
