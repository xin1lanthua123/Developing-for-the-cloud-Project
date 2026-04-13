variable "project_name" {
  type = string
}

variable "lambda_zip_path" {
  type = string
}

variable "dynamodb_table_name" {
  type = string
}

variable "dynamodb_table_arn" {
  type = string
}

variable "upload_bucket_arn" {
  type = string
}

variable "upload_bucket_name" {
  type = string
}

variable "cognito_client_id" {
  type = string
}

variable "cognito_issuer_url" {
  type = string
}

variable "jira_base_url" {
  type = string
}

variable "jira_email" {
  type = string
}

variable "jira_token" {
  type = string
  sensitive = true
}

variable "jira_project_key" {
  type = string
}

variable "frontend_domain" {
  type = string
}