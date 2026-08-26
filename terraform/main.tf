terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

variable "region" { default = "eu-central-1" }
variable "environment" { default = "dev" }

provider "aws" { region = var.region }

resource "aws_ecr_repository" "platform" {
  name                 = "climate-ai-platform-${var.environment}"
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration { scan_on_push = true }
}

resource "aws_cloudwatch_log_group" "platform" {
  name              = "/climate-ai/${var.environment}"
  retention_in_days = 30
}

output "repository_url" { value = aws_ecr_repository.platform.repository_url }

