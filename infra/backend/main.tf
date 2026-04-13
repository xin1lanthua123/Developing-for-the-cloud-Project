terraform {
  backend "s3" {
    bucket         = "cloud-incident-system-tf-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "cloud-incident-system-terraform-locks"
    encrypt        = true
  }
}




