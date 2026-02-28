# --- CloudWatch Log Group ---
resource "aws_cloudwatch_log_group" "migration" {
  name              = "/ecs/${var.project}-${var.environment}-migration"
  retention_in_days = var.log_retention_days

  tags = var.tags
}

# --- Migration Task Definition ---
# Run via: aws ecs run-task --cluster CLUSTER --task-definition TASK_DEF --network-configuration ...
resource "aws_ecs_task_definition" "migration" {
  family                   = "${var.project}-${var.environment}-migration"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = var.ecs_execution_role_arn
  task_role_arn            = var.ecs_task_role_arn

  container_definitions = jsonencode([
    {
      name      = "migration"
      image     = "${aws_ecr_repository.api.repository_url}:latest"
      essential = true
      command   = ["alembic", "upgrade", "head"]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.migration.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }

      environment = [
        { name = "PYTHONPATH", value = "/app" },
      ]

      secrets = [
        { name = "CLICKIT_DATABASE_URL", valueFrom = var.database_url_secret_arn },
        { name = "CLICKIT_REDIS_URL", valueFrom = var.redis_url_secret_arn },
        { name = "CLICKIT_JWT_SECRET_KEY", valueFrom = var.jwt_secret_key_secret_arn },
      ]
    }
  ])

  tags = var.tags
}
