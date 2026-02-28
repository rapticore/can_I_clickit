locals {
  tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# --- Networking ---
module "networking" {
  source = "../../modules/networking"

  project              = var.project
  environment          = var.environment
  aws_region           = var.aws_region
  single_nat_gateway   = true
  enable_vpc_flow_logs = false
  log_retention_days   = 7
  tags                 = local.tags
}

# --- Data ---
module "data" {
  source = "../../modules/data"

  project                     = var.project
  environment                 = var.environment
  private_subnets             = module.networking.private_subnets
  db_security_group_id        = module.networking.db_security_group_id
  redis_security_group_id     = module.networking.redis_security_group_id
  db_password                 = module.security.db_password
  db_instance_class           = "db.t4g.micro"
  db_multi_az                 = false
  db_backup_retention_days    = 7
  enable_performance_insights = false
  redis_node_type             = "cache.t4g.micro"
  enable_alb_logs_bucket      = false
  tags                        = local.tags
}

# --- Security ---
module "security" {
  source = "../../modules/security"

  project            = var.project
  environment        = var.environment
  enable_waf         = false
  api_keys_json      = var.api_keys_json
  anthropic_api_key  = var.anthropic_api_key
  virustotal_api_key = var.virustotal_api_key
  data_bucket_arn    = module.data.data_bucket_arn
  tags               = local.tags
}

# --- Secret Version Bridge ---
# Secret shells are in the security module; versions with actual connection
# strings are created here to avoid circular module dependencies.
resource "aws_secretsmanager_secret_version" "database_url" {
  secret_id     = module.security.database_url_secret_id
  secret_string = "postgresql+asyncpg://clickit:${module.security.db_password}@${module.data.db_address}:5432/clickit"
}

resource "aws_secretsmanager_secret_version" "redis_url" {
  secret_id     = module.security.redis_url_secret_id
  secret_string = "redis://${module.data.redis_address}:6379/0"
}

# --- Compute ---
module "compute" {
  source = "../../modules/compute"

  project     = var.project
  environment = var.environment
  aws_region  = var.aws_region

  # Networking
  vpc_id                = module.networking.vpc_id
  public_subnets        = module.networking.public_subnets
  private_subnets       = module.networking.private_subnets
  alb_security_group_id = module.networking.alb_security_group_id
  app_security_group_id = module.networking.app_security_group_id

  # IAM
  ecs_execution_role_arn = module.security.ecs_execution_role_arn
  ecs_task_role_arn      = module.security.ecs_task_role_arn

  # Secrets
  database_url_secret_arn       = module.security.database_url_secret_arn
  redis_url_secret_arn          = module.security.redis_url_secret_arn
  jwt_secret_key_secret_arn     = module.security.jwt_secret_key_secret_arn
  api_keys_secret_arn           = module.security.api_keys_secret_arn
  anthropic_api_key_secret_arn  = module.security.anthropic_api_key_secret_arn
  virustotal_api_key_secret_arn = module.security.virustotal_api_key_secret_arn

  # API sizing (dev: small + Spot)
  api_cpu           = "512"
  api_memory        = "1024"
  api_desired_count = 1
  api_max_count     = 2

  # Frontend sizing (dev: small + Spot)
  frontend_cpu           = "256"
  frontend_memory        = "512"
  frontend_desired_count = 1
  frontend_max_count     = 2

  # Cluster
  use_fargate_spot   = true
  enable_autoscaling = false

  # ALB
  domain_name        = var.domain_name
  cors_origins       = "*"
  alb_logs_bucket_id = null
  waf_acl_arn        = null

  # Logging
  log_retention_days = 7

  tags = local.tags

  depends_on = [
    aws_secretsmanager_secret_version.database_url,
    aws_secretsmanager_secret_version.redis_url,
  ]
}
