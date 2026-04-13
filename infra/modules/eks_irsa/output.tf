output "backend_role_arn" {
  value = aws_iam_role.backend_irsa_role.arn
}

output "alb_role_arn" {
  value = aws_iam_role.alb_irsa_role.arn
}