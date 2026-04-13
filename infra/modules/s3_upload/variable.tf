variable "bucket_name" {
  type = string
  default = "quanldl"
}

variable "project_name" {
  type = string
}
variable "frontend_domain" {
  type        = string
  description = "CloudFront domain name (without https://)"
}