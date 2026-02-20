output "vpc_id" {
  value = module.vpc.vpc_id
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "db_endpoint" {
  value     = aws_db_instance.postgres.endpoint
  sensitive = true
}

output "redis_endpoint" {
  value = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "api_gateway_url" {
  value = aws_apigatewayv2_stage.default.invoke_url
}

output "alb_dns_name" {
  value = aws_lb.api.dns_name
}

output "ecs_service_name" {
  value = aws_ecs_service.api.name
}

output "s3_bucket" {
  value = aws_s3_bucket.data.id
}
