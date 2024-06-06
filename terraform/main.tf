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
  timeout       = 570
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

module "get_guild_channels" {
  depends_on = [aws_s3_bucket.lambda_build_bucket, module.lambda_default_role]

  source = "terraform-aws-modules/lambda/aws"

  function_name = "get_guild_channels"
  description   = "특정 ID의 디스코드 서버의 채널 목록을 가져옵니다. 만약 해당 서버가 존재하지 않거나 접근할 수 없는 경우 404를 반환합니다."
  handler       = "main.lambda_handler"
  runtime       = "python3.10"
  timeout       = 120
  source_path   = "../lambdas/get_guild_channels"

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

module "post_notification" {
  depends_on = [aws_s3_bucket.lambda_build_bucket, module.lambda_default_role]

  source = "terraform-aws-modules/lambda/aws"

  function_name = "post_notification"
  description   = "치지직 알림을 추가합니다."
  handler       = "main.lambda_handler"
  runtime       = "python3.10"
  timeout       = 120
  source_path   = "../lambdas/post_notification"

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

module "get_notification_by_guild_id" {
  depends_on = [aws_s3_bucket.lambda_build_bucket, module.lambda_default_role]

  source = "terraform-aws-modules/lambda/aws"

  function_name = "get_notification_by_guild_id"
  description   = "특정 ID의 디스코드 서버의 알림 목록을 가져옵니다. 데이터가 없을 경우 빈 리스트를 반환합니다."
  handler       = "main.lambda_handler"
  runtime       = "python3.10"
  timeout       = 120
  source_path   = "../lambdas/get_notification_by_guild_id"

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

module "delete_notification" {
  depends_on = [aws_s3_bucket.lambda_build_bucket, module.lambda_default_role]

  source = "terraform-aws-modules/lambda/aws"

  function_name = "delete_notification"
  description   = "알림을 삭제합니다. 만약 해당 알림이 없으면 404를 반환합니다."
  handler       = "main.lambda_handler"
  runtime       = "python3.10"
  timeout       = 120
  source_path   = "../lambdas/delete_notification"

  store_on_s3 = true
  s3_bucket   = var.lambda_build_bucket

  create_role = false
  lambda_role = module.lambda_default_role.role_arn

  tags = {
    version = "v1"
  }
}

module "send_test_notification" {
  depends_on = [aws_s3_bucket.lambda_build_bucket, module.lambda_default_role]

  source = "terraform-aws-modules/lambda/aws"

  function_name = "send_test_notification"
  description   = "테스트 알림을 전송합니다."
  handler       = "main.lambda_handler"
  runtime       = "python3.10"
  timeout       = 120
  source_path   = "../lambdas/send_test_notification"

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

module "update_notification" {
  depends_on = [aws_s3_bucket.lambda_build_bucket, module.lambda_default_role]

  source = "terraform-aws-modules/lambda/aws"

  function_name = "update_notification"
  description   = "알림의 커스텀 메시지를 수정합니다."
  handler       = "main.lambda_handler"
  runtime       = "python3.10"
  timeout       = 120
  source_path   = "../lambdas/update_notification"

  store_on_s3 = true
  s3_bucket   = var.lambda_build_bucket

  create_role = false
  lambda_role = module.lambda_default_role.role_arn

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

  attribute {
    name = "guild_id"
    type = "S"
  }

  attribute {
    name = "type"
    type = "S"
  }

  attribute {
    name = "index"
    type = "N"
  }

  global_secondary_index {
    name               = "GSI-SK"
    hash_key           = "SK"
    range_key          = "PK"
    projection_type    = "KEYS_ONLY"
  }

  global_secondary_index {
    name               = "GSI-GuildID"
    hash_key           = "guild_id"
    range_key           = "PK"
    projection_type    = "INCLUDE"

    non_key_attributes = [
      "SK",
      "channel_id",
      "channel_name",
      "custom_message",
      "disable_button",
      "disable_embed",
    ]
  }

  global_secondary_index {
    name               = "GSI-type"
    hash_key           = "type"
    projection_type    = "INCLUDE"

    non_key_attributes = [
      "PK",
      "lastLiveId"
    ]
  }

  global_secondary_index {
    name               = "GSI-index"
    hash_key           = "index"
    range_key           = "PK"
    projection_type    = "ALL"
  }
}
