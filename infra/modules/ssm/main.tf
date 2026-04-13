resource "aws_ssm_parameter" "jira_base_url" {
  name  = "/incident-app/jira/base_url"
  type  = "String"
  value = var.jira_base_url
}

resource "aws_ssm_parameter" "jira_email" {
  name  = "/incident-app/jira/email"
  type  = "String"
  value = var.jira_email
}

resource "aws_ssm_parameter" "jira_token" {
  name  = "/incident-app/jira/token"
  type  = "SecureString"
  value = var.jira_token
}

resource "aws_ssm_parameter" "jira_project_key" {
  name  = "/incident-app/jira/project_key"
  type  = "String"
  value = var.jira_project_key
}