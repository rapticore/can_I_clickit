# Secret ARNs (for ECS task definition secrets blocks)
output "database_url_secret_arn" {
  value = aws_secretsmanager_secret.database_url.arn
}

output "database_url_secret_id" {
  value = aws_secretsmanager_secret.database_url.id
}

output "redis_url_secret_arn" {
  value = aws_secretsmanager_secret.redis_url.arn
}

output "redis_url_secret_id" {
  value = aws_secretsmanager_secret.redis_url.id
}

output "jwt_secret_key_secret_arn" {
  value = aws_secretsmanager_secret.jwt_secret_key.arn
}

output "api_keys_secret_arn" {
  value = aws_secretsmanager_secret.api_keys.arn
}

output "anthropic_api_key_secret_arn" {
  value = aws_secretsmanager_secret.anthropic_api_key.arn
}

output "virustotal_api_key_secret_arn" {
  value = aws_secretsmanager_secret.virustotal_api_key.arn
}

# Passwords
output "db_password" {
  value     = random_password.db_password.result
  sensitive = true
}

# IAM Roles
output "ecs_execution_role_arn" {
  value = aws_iam_role.ecs_execution.arn
}

output "ecs_task_role_arn" {
  value = aws_iam_role.ecs_task.arn
}

# WAF
output "waf_acl_arn" {
  value = var.enable_waf ? aws_wafv2_web_acl.main[0].arn : null
}
