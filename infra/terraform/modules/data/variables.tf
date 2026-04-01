variable "project" {
  type        = string
  description = "Project name"
}

variable "environment" {
  type        = string
  description = "Environment name (dev, prod)"
}

variable "private_subnets" {
  type        = list(string)
  description = "Private subnet IDs"
}

variable "db_security_group_id" {
  type        = string
  description = "Security group ID for RDS"
}

variable "redis_security_group_id" {
  type        = string
  description = "Security group ID for ElastiCache"
}

variable "db_password" {
  type        = string
  description = "RDS master password"
  sensitive   = true
}

variable "db_instance_class" {
  type        = string
  description = "RDS instance class"
  default     = "db.t4g.micro"
}

variable "db_multi_az" {
  type        = bool
  description = "Enable Multi-AZ for RDS"
  default     = false
}

variable "db_backup_retention_days" {
  type        = number
  description = "RDS backup retention period in days"
  default     = 7
}

variable "enable_performance_insights" {
  type        = bool
  description = "Enable RDS Performance Insights"
  default     = false
}

variable "redis_node_type" {
  type        = string
  description = "ElastiCache node type"
  default     = "cache.t4g.micro"
}

variable "enable_alb_logs_bucket" {
  type        = bool
  description = "Create S3 bucket for ALB access logs (prod)"
  default     = false
}

variable "tags" {
  type        = map(string)
  description = "Resource tags"
}
