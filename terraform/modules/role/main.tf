resource "aws_iam_role" "role" {
  name               = "${var.name}Role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "${var.role_sid}",
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      }
    }
  ]
}
EOF
}


resource "aws_iam_policy" "poilcy" {
  name   = "${var.name}Policy"
  path   = "/"
  policy = var.policy
}

resource "aws_iam_role_policy_attachment" "role_attachment" {
  role       = aws_iam_role.role.name
  policy_arn = aws_iam_policy.poilcy.arn
}
