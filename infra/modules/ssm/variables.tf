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