locals {
  tags = {
    "Name"        = "${var.application_name}"
    "Environment" = "${var.application_name}"
  }
}

resource "aws_elastic_beanstalk_application" "application" {
  name        = var.application_name
  description = var.application_description
  tags = local.tags

  dynamic "appversion_lifecycle" {
    for_each = var.appversion_lifecycle_service_role_arn != "" ? ["true"] : []
    content {
      service_role          = var.appversion_lifecycle_service_role_arn
      max_count             = var.appversion_lifecycle_max_count
      delete_source_from_s3 = var.appversion_lifecycle_delete_source_from_s3
    }
  }
}
