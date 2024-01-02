output "role_arn" {
  depends_on = [
    aws_iam_role.role,
    aws_iam_policy.poilcy
  ]
  value       = aws_iam_role.role.arn
  description = "value of role arn"
}
