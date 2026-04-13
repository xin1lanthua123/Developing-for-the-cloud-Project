output "vpc_id" {
  value = module.eks_core.vpc_id
}
output "eks_cluster_name" {
  value = module.eks_core.cluster_name
}
output "cluster_endpoint" {
  value = module.eks_core.cluster_endpoint
}
output "backend_role_arn" {
  value = module.eks_irsa.backend_role_arn
}
output "alb_role_arn" {
  value = module.eks_irsa.alb_role_arn
}
output "dynamodb_table_name" {
  value = module.dynamodb.table_name
}

output "upload_bucket_name" {
  value = module.s3_upload.s3_bucket_id
}

output "upload_bucket_arn" {
  value = module.s3_upload.s3_bucket_arn
}

output "frontend_bucket" {
  value = module.frontend_hosting.bucket_name
}

output "frontend_url" {
  value = "https://${module.frontend_hosting.cloudfront_domain}"
}

output "cloudfront_distribution_id" {
  value = module.frontend_hosting.cloudfront_distribution_id
}

output "cognito_user_pool_id" {
  value = module.cognito.user_pool_id
}

output "cognito_client_id" {
  value = module.cognito.user_pool_client_id
}

output "cognito_issuer_url" {
  value = module.cognito.issuer_url
}

output "jira_ssm_params" {
  value = {
    base_url    = module.ssm.jira_base_url_param
    email       = module.ssm.jira_email_param
    token       = module.ssm.jira_token_param
    project_key = module.ssm.jira_project_key_param
  }
}