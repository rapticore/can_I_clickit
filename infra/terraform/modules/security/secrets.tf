# Secret shells — versions are created in the environment main.tf
# to avoid circular dependencies with data module outputs.

resource "aws_secretsmanager_secret" "database_url" {
  name                    = "${var.project}/${var.environment}/database-url"
  description             = "PostgreSQL connection URL"
  recovery_window_in_days = var.environment == "prod" ? 30 : 0

  tags = var.tags
}

resource "aws_secretsmanager_secret" "redis_url" {
  name                    = "${var.project}/${var.environment}/redis-url"
  description             = "Redis connection URL"
  recovery_window_in_days = var.environment == "prod" ? 30 : 0

  tags = var.tags
}

resource "aws_secretsmanager_secret" "jwt_secret_key" {
  name                    = "${var.project}/${var.environment}/jwt-secret-key"
  description             = "JWT signing secret"
  recovery_window_in_days = var.environment == "prod" ? 30 : 0

  tags = var.tags
}

resource "aws_secretsmanager_secret" "api_keys" {
  name                    = "${var.project}/${var.environment}/api-keys"
  description             = "API keys (JSON array)"
  recovery_window_in_days = var.environment == "prod" ? 30 : 0

  tags = var.tags
}

resource "aws_secretsmanager_secret" "anthropic_api_key" {
  name                    = "${var.project}/${var.environment}/anthropic-api-key"
  description             = "Anthropic API key (optional)"
  recovery_window_in_days = var.environment == "prod" ? 30 : 0

  tags = var.tags
}

resource "aws_secretsmanager_secret" "virustotal_api_key" {
  name                    = "${var.project}/${var.environment}/virustotal-api-key"
  description             = "VirusTotal API key (optional)"
  recovery_window_in_days = var.environment == "prod" ? 30 : 0

  tags = var.tags
}

# Auto-generate passwords
resource "random_password" "db_password" {
  length  = 32
  special = false
}

resource "random_password" "jwt_secret" {
  length  = 64
  special = false
}

# Seed JWT secret version (self-contained, no cross-module dependency)
resource "aws_secretsmanager_secret_version" "jwt_secret_key" {
  secret_id     = aws_secretsmanager_secret.jwt_secret_key.id
  secret_string = random_password.jwt_secret.result
}

# Seed API keys with user-provided value or default empty array
resource "aws_secretsmanager_secret_version" "api_keys" {
  secret_id     = aws_secretsmanager_secret.api_keys.id
  secret_string = var.api_keys_json
}

# Seed optional keys (placeholder if not provided)
resource "aws_secretsmanager_secret_version" "anthropic_api_key" {
  secret_id     = aws_secretsmanager_secret.anthropic_api_key.id
  secret_string = var.anthropic_api_key
}

resource "aws_secretsmanager_secret_version" "virustotal_api_key" {
  secret_id     = aws_secretsmanager_secret.virustotal_api_key.id
  secret_string = var.virustotal_api_key
}
