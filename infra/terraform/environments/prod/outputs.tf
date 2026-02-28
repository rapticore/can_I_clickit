output "alb_dns_name" {
  value       = module.compute.alb_dns_name
  description = "ALB DNS name — use this to access the application"
}

output "ecs_cluster_name" {
  value = module.compute.ecs_cluster_name
}

output "api_service_name" {
  value = module.compute.api_service_name
}

output "frontend_service_name" {
  value = module.compute.frontend_service_name
}

output "ecr_api_repository_url" {
  value = module.compute.ecr_api_repository_url
}

output "ecr_frontend_repository_url" {
  value = module.compute.ecr_frontend_repository_url
}

output "migration_task_definition_arn" {
  value = module.compute.migration_task_definition_arn
}

output "db_endpoint" {
  value     = module.data.db_endpoint
  sensitive = true
}

output "redis_address" {
  value = module.data.redis_address
}

output "vpc_id" {
  value = module.networking.vpc_id
}

output "data_bucket" {
  value = module.data.data_bucket_id
}

output "waf_acl_arn" {
  value = module.security.waf_acl_arn
}
