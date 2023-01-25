locals {
  bucket       = var.application_bucket
  description  = var.application_description
  name         = var.application_name
  name_version = "${var.application_name}-base-${var.application_version}"
  source       = var.application_source
}

data "vault_aws_access_credentials" "creds" {
  backend = "${var.vault_name}-path"
  role    = "${var.vault_name}-role"
}

module "elastic_beanstalk_application_version" {
  source                   = "../terraform-aws-elastic-beanstalk-application-version"
  application_bucket       = local.bucket
  application_description  = local.description
  application_name         = local.name
  application_name_version = local.name_version
  application_source       = local.source
}
