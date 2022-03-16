locals {
  bucket = "${var.application_name}-bucket"
  key    = "${var.application_name}.zip"
  source = "app.zip"
  tags = {
    "Name"        = "${var.application_name}"
    "Environment" = "${var.application_name}"
  }
}

# Create elastic beanstalk Application Version
resource "aws_s3_bucket" "bucket" {
  bucket = local.bucket
  tags   = local.tags
}

resource "aws_s3_object" "object" {
  bucket = aws_s3_bucket.bucket.id
  key    = local.key
  source = local.source
  tags   = local.tags
}

resource "aws_elastic_beanstalk_application_version" "application_version" {
  application = var.application_name
  description = var.application_description
  bucket      = aws_s3_bucket.bucket.id
  key         = aws_s3_object.object.id
  name        = var.application_version_name
  tags        = local.tags
}
