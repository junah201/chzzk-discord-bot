variable "AWS_AECCESS_KEY" {
  type        = string
  description = "AWS access key"
  sensitive   = true
}

variable "AWS_AECCESS_KEY_SECRET" {
  type        = string
  description = "AWS access key secret"
  sensitive   = true
}

variable "AWS_REGION" {
  type        = string
  description = "AWS region"
  default     = "ap-northeast-2"
}

variable "DISCORD_PUBLIC_KEY" {
  type = string
  description = "Discord public key"
}

variable "DISCORD_TOKEN" {
  type = string
  description = "Discord bot token"
}

variable "DISCORD_CLIENT_ID" {
  type = string
  description = "Discord client id"
  sensitive   = true
}

variable "DISCORD_CLIENT_SECRET" {
  type = string
  description = "Discord client secret"
  sensitive   = true
}

variable "lambda_build_bucket" {
  type        = string
  description = "S3 bucket for lambda build"
  default     = "chzzk-bot-lambda-build"
}
