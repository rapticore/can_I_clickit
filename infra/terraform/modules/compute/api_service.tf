# --- CloudWatch Log Group ---
resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/${var.project}-${var.environment}-api"
  retention_in_days = var.log_retention_days

  tags = var.tags
}

# --- Task Definition ---
resource "aws_ecs_task_definition" "api" {
  family                   = "${var.project}-${var.environment}-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.api_cpu
  memory                   = var.api_memory
  execution_role_arn       = var.ecs_execution_role_arn
  task_role_arn            = var.ecs_task_role_arn

  container_definitions = jsonencode([
    {
      name      = "api"
      image     = "${aws_ecr_repository.api.repository_url}:latest"
      essential = true

      portMappings = [{
        containerPort = 8000
        hostPort      = 8000
        protocol      = "tcp"
      }]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.api.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }

      environment = [
        { name = "CLICKIT_DEBUG", value = var.environment == "dev" ? "true" : "false" },
        { name = "CLICKIT_CORS_ORIGINS", value = jsonencode(split(",", var.cors_origins)) },
        { name = "PYTHONPATH", value = "/app" },
      ]

      secrets = [
        { name = "CLICKIT_DATABASE_URL", valueFrom = var.database_url_secret_arn },
        { name = "CLICKIT_REDIS_URL", valueFrom = var.redis_url_secret_arn },
        { name = "CLICKIT_JWT_SECRET_KEY", valueFrom = var.jwt_secret_key_secret_arn },
        { name = "CLICKIT_API_KEYS", valueFrom = var.api_keys_secret_arn },
        { name = "CLICKIT_ANTHROPIC_API_KEY", valueFrom = var.anthropic_api_key_secret_arn },
        { name = "CLICKIT_VIRUSTOTAL_API_KEY", valueFrom = var.virustotal_api_key_secret_arn },
      ]
    }
  ])

  tags = var.tags
}

# --- ECS Service ---
resource "aws_ecs_service" "api" {
  name            = "${var.project}-${var.environment}-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.api_desired_count

  capacity_provider_strategy {
    capacity_provider = var.use_fargate_spot ? "FARGATE_SPOT" : "FARGATE"
    weight            = 1
    base              = 0
  }

  network_configuration {
    subnets          = var.private_subnets
    security_groups  = [var.app_security_group_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.http]

  tags = var.tags
}
