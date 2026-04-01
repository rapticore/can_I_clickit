variable "project" {
  type        = string
  description = "Project name"
  default     = "clickit"
}

variable "environment" {
  type        = string
  description = "Environment name"
  default     = "prod"
}

variable "aws_region" {
  type        = string
  description = "AWS region"
  default     = "us-east-1"
}

variable "api_keys_json" {
  type        = string
  description = "JSON array of API keys"
  sensitive   = true
}

variable "anthropic_api_key" {
  type        = string
  description = "Anthropic API key"
  default     = "PLACEHOLDER"
  sensitive   = true
}

variable "virustotal_api_key" {
  type        = string
  description = "VirusTotal API key"
  default     = "PLACEHOLDER"
  sensitive   = true
}

variable "domain_name" {
  type        = string
  description = "Domain name for HTTPS (leave empty for HTTP-only)"
  default     = ""
}
