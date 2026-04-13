variable "backend_alb_dns" {
  type = string
}
variable "project_name" {
  type        = string
  description = "Project name used for naming AWS resources"
  default     = "cloud-incident-system"
}

variable "aws_region" {
  type        = string
  description = "AWS region"
  default     = "us-east-1"
}

variable "lambda_zip_path" {
  type        = string
  description = "Path to the packaged Lambda zip file"
  default     = "../backend/zip-file/lambda.zip"
}

variable "dynamodb_table_name" {
  type        = string
  description = "DynamoDB table name"
  default     = "cloud-incident-table"
}

variable "upload_bucket_prefix" {
  type        = string
  description = "Prefix name for S3 upload bucket"
  default     = "cloud-incident-upload"
}

variable "frontend_bucket_prefix" {
  type        = string
  description = "Prefix name for frontend hosting bucket"
  default     = "cloud-incident-frontend"
}

variable "jira_base_url" {
  type        = string
  description = "Jira base URL"
}

variable "jira_email" {
  type        = string
  description = "Jira account email"
}

variable "jira_token" {
  type        = string
  description = "Jira API token"
  sensitive   = true
}

variable "jira_project_key" {
  type        = string
  description = "Jira project key"
}




