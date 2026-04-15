resource "random_id" "suffix" {
  byte_length = 4
}

# ---------------------------
# COGNITO MODULE
# ---------------------------
module "cognito" {
  source       = "./modules/cognito"
  project_name = var.project_name
}

# ---------------------------
# DYNAMODB MODULE
# ---------------------------
module "dynamodb" {
  source       = "./modules/dynamodb"
  project_name = var.project_name
  table_name   = var.dynamodb_table_name
}

# ---------------------------
# S3 UPLOAD MODULE
# ---------------------------
module "s3_upload" {
  source       = "./modules/s3_upload"
  project_name = var.project_name
  bucket_name  = "${var.upload_bucket_prefix}-${random_id.suffix.hex}"
  frontend_domain = module.frontend_hosting.cloudfront_domain
}

# ---------------------------
# FRONTEND HOSTING MODULE
# ---------------------------
module "frontend_hosting" {
  source       = "./modules/frontend_hosting"
  project_name = var.project_name
  bucket_name  = "${var.frontend_bucket_prefix}-${random_id.suffix.hex}"
  backend_alb_dns = var.backend_alb_dns
}

## SSM
module "ssm" {
  source = "./modules/ssm"

  jira_base_url    = var.jira_base_url
  jira_email       = var.jira_email
  jira_token       = var.jira_token
  jira_project_key = var.jira_project_key
}




module "eks_core" {
  source       = "./modules/eks_core"
  project_name = var.project_name

  cluster_version     = "1.30"
  node_instance_type  = "t3.small"
  desired_size        = 2
  min_size            = 1
  max_size            = 3
}

module "eks_irsa" {
  source       = "./modules/eks_irsa"
  project_name = var.project_name

  oidc_provider_arn = module.eks_core.oidc_provider_arn
  oidc_provider_url = module.eks_core.oidc_provider_url

  namespace              = "incident-system"
  backend_service_account = "backend-incident-sa"

  dynamodb_table_arn = module.dynamodb.table_arn
  upload_bucket_arn  = module.s3_upload.s3_bucket_arn

  
}



