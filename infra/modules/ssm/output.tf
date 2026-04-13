output "jira_base_url_param" {
  value = aws_ssm_parameter.jira_base_url.name
}

output "jira_email_param" {
  value = aws_ssm_parameter.jira_email.name
  
}

output "jira_token_param" {
  value = aws_ssm_parameter.jira_token.name
}

output "jira_project_key_param" {
  value = aws_ssm_parameter.jira_project_key.name
}