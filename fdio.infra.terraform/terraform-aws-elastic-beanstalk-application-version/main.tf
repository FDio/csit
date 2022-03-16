locals {
  bucket = "${var.application_name}-bucket"
  tags = {
    "Name"        = "${var.application_name}"
    "Environment" = "${var.application_name}"
  }
}

# Create elastic beanstalk Application
resource "aws_s3_bucket" "bucket" {
  bucket = local.bucket
  tags   = local.tags
}

resource "aws_s3_object" "object" {
  bucket = aws_s3_bucket.bucket.id
  key    = "app.zip"
  source = "app.zip"
  tags   = local.tags
}

resource "aws_elastic_beanstalk_application_version" "application_version" {
  name        = "${var.application_name}-base"
  application = var.application_name
  description = var.application_description
  bucket      = aws_s3_bucket.bucket.id
  key         = aws_s3_object.object.id
  tags        = local.tags
}
