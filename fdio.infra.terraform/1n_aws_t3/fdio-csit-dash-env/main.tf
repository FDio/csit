data "vault_generic_secret" "fdio_docs" {
  path = "kv/secret/data/etl/fdio_docs"
}

data "vault_aws_access_credentials" "creds" {
  backend = "${var.vault_name}-path"
  role    = "${var.vault_name}-role"
}

module "dash" {
  source = "../"

  application_description                    = "FD.io CSIT Results Dashboard"
  application_name                           = "fdio-csit-dash-app"
  appversion_lifecycle_service_role_arn      = ""
  appversion_lifecycle_max_count             = 2
  appversion_lifecycle_delete_source_from_s3 = false

  environment_description            = "FD.io CSIT Results Dashboard"
  environment_name                   = "fdio-csit-dash-env"
  environment_solution_stack_name    = "64bit Amazon Linux 2 v3.3.11 running Python 3.8"
  environment_tier                   = "WebServer"
  environment_wait_for_ready_timeout = "20m"
  environment_version_label          = ""

  environment_variables = {
    "AWS_ACCESS_KEY_ID"     = data.vault_generic_secret.fdio_docs.data["access_key"]
    "AWS_SECRET_ACCESS_KEY" = data.vault_generic_secret.fdio_docs.data["secret_key"]
    "AWS_DEFAULT_REGION"    = data.vault_generic_secret.fdio_docs.data["region"]
  }
  instances_instance_types = "t3.large"
  subnet_availability_zone = "us-east-1a"
}
