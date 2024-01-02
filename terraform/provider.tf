terraform {
  required_version = ">= 1.5.3"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.63.0"
    }
  }
}

provider "aws" {
  access_key = var.AWS_AECCESS_KEY
  secret_key = var.AWS_AECCESS_KEY_SECRET
  region     = var.AWS_REGION
}
