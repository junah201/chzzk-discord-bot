module "lambda_default_role" {
  source = "./modules/role"
  name   = "LambdaDefault"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "kms:Decrypt"
      ],
      "Resource": "arn:aws:kms:*:*:*"
    },
    {
      "Action": [
        "dynamodb:*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_s3_bucket" "lambda_build_bucket" {
  bucket = var.lambda_build_bucket
}

// layers
module "pynacl_layer" {
  source = "terraform-aws-modules/lambda/aws"

  create_layer = true

  layer_name          = "pynacl_layer"
  description         = "PyNaCl"
  compatible_runtimes = ["python3.10"]

  source_path = "../layers/pynacl"

  store_on_s3 = true
  s3_bucket   = aws_s3_bucket.lambda_build_bucket.id
}

module "common_layer" {
  source = "terraform-aws-modules/lambda/aws"

  create_layer = true

  layer_name          = "common_layer"
  description         = "common (dataclasses, utils, etc)"
  compatible_runtimes = ["python3.10"]

  source_path = "../layers/common"

  store_on_s3 = true
  s3_bucket   = aws_s3_bucket.lambda_build_bucket.id
}

module "requests_layer" {
  source = "terraform-aws-modules/lambda/aws"

  create_layer = true

  layer_name          = "requests_layer"
  description         = "requests"
  compatible_runtimes = ["python3.10"]

  source_path = "../layers/requests"

  store_on_s3 = true
  s3_bucket   = aws_s3_bucket.lambda_build_bucket.id
}

// Lambdas
module "event_handler" {
  depends_on = [aws_s3_bucket.lambda_build_bucket, module.lambda_default_role]

  source = "terraform-aws-modules/lambda/aws"

  function_name = "event_handler"
  description   = "Receive event from Discord server"
  handler       = "main.lambda_handler"
  runtime       = "python3.10"
  timeout       = 120
  source_path   = "../lambdas/event_handler"

  store_on_s3 = true
  s3_bucket   = var.lambda_build_bucket

  create_role = false
  lambda_role = module.lambda_default_role.role_arn

  layers = [
    module.common_layer.lambda_layer_arn,
    module.requests_layer.lambda_layer_arn,
    module.pynacl_layer.lambda_layer_arn,
  ]

  environment_variables = {
    "DISCORD_PUBLIC_KEY" = var.DISCORD_PUBLIC_KEY
    "DISCORD_TOKEN" = var.DISCORD_TOKEN
  }

  tags = {
    version = "v1"
  }
}

module "live_check" {
  depends_on = [aws_s3_bucket.lambda_build_bucket, module.lambda_default_role]

  source = "terraform-aws-modules/lambda/aws"

  function_name = "live_check"
  description   = "live check"
  handler       = "main.lambda_handler"
  runtime       = "python3.10"
  timeout       = 120
  source_path   = "../lambdas/live_check"

  store_on_s3 = true
  s3_bucket   = var.lambda_build_bucket

  create_role = false
  lambda_role = module.lambda_default_role.role_arn

  layers = [
    module.common_layer.lambda_layer_arn,
    module.requests_layer.lambda_layer_arn,
  ]

  environment_variables = {
    "DISCORD_TOKEN" = var.DISCORD_TOKEN
  }

  tags = {
    version = "v1"
  }
}

module "discord_oauth2_redirect" {
  depends_on = [aws_s3_bucket.lambda_build_bucket, module.lambda_default_role]

  source = "terraform-aws-modules/lambda/aws"

  function_name = "discord_oauth2_redirect"
  description   = "discord_oauth2_redirect check"
  handler       = "main.lambda_handler"
  runtime       = "python3.10"
  timeout       = 120
  source_path   = "../lambdas/discord_oauth2_redirect"

  store_on_s3 = true
  s3_bucket   = var.lambda_build_bucket

  create_role = false
  lambda_role = module.lambda_default_role.role_arn

  layers = [
    module.common_layer.lambda_layer_arn,
    module.requests_layer.lambda_layer_arn,
  ]

  environment_variables = {
    "DISCORD_TOKEN" = var.DISCORD_TOKEN
    "DISCORD_CLIENT_ID" = var.DISCORD_CLIENT_ID
    "DISCORD_CLIENT_SECRET" = var.DISCORD_CLIENT_SECRET
  }

  tags = {
    version = "v1"
  }
}

module "discord_me" {
  depends_on = [aws_s3_bucket.lambda_build_bucket, module.lambda_default_role]

  source = "terraform-aws-modules/lambda/aws"

  function_name = "discord_me"
  description   = "로그인되어 있는 디스코드 계정 정보를 반환합니다."
  handler       = "main.lambda_handler"
  runtime       = "python3.10"
  timeout       = 120
  source_path   = "../lambdas/discord_me"

  store_on_s3 = true
  s3_bucket   = var.lambda_build_bucket

  create_role = false
  lambda_role = module.lambda_default_role.role_arn

  layers = [
    module.common_layer.lambda_layer_arn,
    module.requests_layer.lambda_layer_arn,
  ]

  tags = {
    version = "v1"
  }
}

module "discord_guilds" {
  depends_on = [aws_s3_bucket.lambda_build_bucket, module.lambda_default_role]

  source = "terraform-aws-modules/lambda/aws"

  function_name = "discord_guilds"
  description   = "로그인되어 있는 디스코드 계정의 서버 목록을 반환합니다."
  handler       = "main.lambda_handler"
  runtime       = "python3.10"
  timeout       = 120
  source_path   = "../lambdas/discord_guilds"

  store_on_s3 = true
  s3_bucket   = var.lambda_build_bucket

  create_role = false
  lambda_role = module.lambda_default_role.role_arn

  layers = [
    module.common_layer.lambda_layer_arn,
    module.requests_layer.lambda_layer_arn,
  ]

  tags = {
    version = "v1"
  }
}

// DynamoDB
resource "aws_dynamodb_table" "db_table" {
  name = "chzzk-bot-db"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "PK"
  range_key = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  global_secondary_index {
    name               = "GSI-SK"
    hash_key           = "SK"
    range_key          = "PK"
    projection_type    = "KEYS_ONLY"
  }
}
