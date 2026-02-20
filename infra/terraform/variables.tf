variable "project" {
  type    = string
  default = "clickit"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "api_image" {
  type    = string
  default = "ghcr.io/example/clickit-api:latest"
}

variable "api_cpu" {
  type    = string
  default = "512"
}

variable "api_memory" {
  type    = string
  default = "1024"
}

variable "api_desired_count" {
  type    = number
  default = 1
}
