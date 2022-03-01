data "vault_generic_secret" "fdio_docs" {
  path = "kv/secret/data/etl/fdio_docs"
}

data "vault_aws_access_credentials" "creds" {
  backend = "${var.vault_name}-path"
  role    = "${var.vault_name}-role"
}

module "dash" {
  source = "../"

  application_description = "FD.io CSIT Results Dashboard"
  application_name        = "fdio-csit-dash"
  environment_name        = "fdio-csit-dash-env"
  environment_variables = {
    "AWS_ACCESS_KEY_ID"     = data.vault_generic_secret.fdio_docs.data["access_key"]
    "AWS_SECRET_ACCESS_KEY" = data.vault_generic_secret.fdio_docs.data["secret_key"]
    "AWS_DEFAULT_REGION"    = data.vault_generic_secret.fdio_docs.data["region"]
  }
  instances_instance_types = "t3.nano"

  vpc_tags_name        = "vpc-csit-dash"
  vpc_tags_environment = "vpc-csit-dash"
}
