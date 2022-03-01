data "vault_generic_secret" "fdio_docs" {
  path = "kv/secret/data/etl/fdio_docs"
}

data "vault_aws_access_credentials" "creds" {
  backend = "${var.vault_name}-path"
  role    = "${var.vault_name}-role"
}

module "dash" {
  source = "../"

  elasticapp_description        = "FD.io CSIT Results Dashboard"
  elasticenv_environment        = {
    AWS_ACCESS_KEY_ID = data.vault_generic_secret.fdio_docs.data["access_key"]
    AWS_SECRET_ACCESS_KEY = data.vault_generic_secret.fdio_docs.data["secret_key"]
    AWS_DEFAULT_REGION = data.vault_generic_secret.fdio_docs.data["region"]
  }
  elasticapp_name               = "fdio-csit-dash"
  elasticenv_instance_type      = "t3.nano"
  elasticenv_minsize            = 1
  elasticenv_maxsize            = 2
  elasticenv_name               = "fdio-csit-dash-env"
  elasticenv_public_subnets     = ["subnet-XXXXXXXXXX", "subnet-XXXXXXXXX"] # Service Subnet
  elasticenv_elb_public_subnets = ["subnet-XXXXXXXXXX", "subnet-XXXXXXXXX"] # ELB Subnet
  elasticenv_tier               = "WebServer"

  vpc_tags_name        = "vpc-csit-dash"
  vpc_tags_environment = "vpc-csit-dash"
}
