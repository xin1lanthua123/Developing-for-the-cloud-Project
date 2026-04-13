resource "aws_dynamodb_table" "this" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "incident_id"

  attribute {
    name = "incident_id"
    type = "S"
  }
  attribute {
    name = "user_id"
    type = "S"
  }
  attribute {
    name = "created_at"
    type = "S"
  }
  global_secondary_index {
    name = "user_id-created_at-index"
    hash_key = "user_id"
    range_key = "created_at"
    projection_type = "ALL"
  }
  tags = {
    Project = var.project_name
  }
}

