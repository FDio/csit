locals {
  bucket       = var.application_bucket
  description  = var.application_description
  name         = var.application_name
  name_version = "${var.application_name}-base-1.${var.application_version}"
  source       = var.application_source
}

ephemeral "vault_kv_secret_v2" "creds" {
  mount = "kv"
  name  = "elasticbeanstalk"
}

module "elastic_beanstalk_application_version" {
  source                   = "../terraform-aws-elastic-beanstalk-application-version"
  application_bucket       = local.bucket
  application_description  = local.description
  application_name         = local.name
  application_name_version = local.name_version
  application_source       = local.source
}
