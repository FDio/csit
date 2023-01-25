locals {
  key = "${var.application_name_version}-${uuid()}.zip"
  tags = {
    "Name"        = "${var.application_name}"
    "Environment" = "${var.application_name}"
  }
}

# Create elastic beanstalk Application Version
# resource "aws_s3_bucket" "bucket" {
#   bucket = var.application_bucket
#   tags   = local.tags
# }
resource "aws_s3_object" "object" {
  bucket = var.application_bucket
  key    = local.key
  source = var.application_source
  tags   = local.tags
}

resource "aws_elastic_beanstalk_application_version" "application_version" {
  application = var.application_name
  description = var.application_description
  bucket      = var.application_bucket
  key         = aws_s3_object.object.id
  name        = var.application_name_version
  tags        = local.tags
}
