variable "project" {
  type        = string
  description = "Project name"
}

variable "environment" {
  type        = string
  description = "Environment name (dev, prod)"
}

variable "enable_waf" {
  type        = bool
  description = "Enable WAF v2 (recommended for prod)"
  default     = false
}

variable "api_keys_json" {
  type        = string
  description = "JSON array of API keys"
  default     = "[]"
  sensitive   = true
}

variable "anthropic_api_key" {
  type        = string
  description = "Anthropic API key (optional)"
  default     = "PLACEHOLDER"
  sensitive   = true
}

variable "virustotal_api_key" {
  type        = string
  description = "VirusTotal API key (optional)"
  default     = "PLACEHOLDER"
  sensitive   = true
}

variable "data_bucket_arn" {
  type        = string
  description = "ARN of the S3 data bucket for task role policy"
}

variable "tags" {
  type        = map(string)
  description = "Resource tags"
}
