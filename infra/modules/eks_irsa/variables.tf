variable "project_name" {
  type = string
}

variable "oidc_provider_arn" {
  type = string
}

variable "oidc_provider_url" {
  type = string
}

variable "namespace" {
  type    = string
  default = "incident-system"
}

variable "backend_service_account" {
  type    = string
  default = "incident-backend-sa"
}

variable "alb_service_account" {
  type    = string
  default = "aws-load-balancer-controller"
}

variable "dynamodb_table_arn" {
  type = string
}

variable "upload_bucket_arn" {
  type = string
}

