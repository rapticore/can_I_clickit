output "db_address" {
  value = aws_db_instance.postgres.address
}

output "db_endpoint" {
  value     = aws_db_instance.postgres.endpoint
  sensitive = true
}

output "redis_address" {
  value = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "data_bucket_arn" {
  value = aws_s3_bucket.data.arn
}

output "data_bucket_id" {
  value = aws_s3_bucket.data.id
}

output "alb_logs_bucket_id" {
  value = var.enable_alb_logs_bucket ? aws_s3_bucket.alb_logs[0].id : null
}
