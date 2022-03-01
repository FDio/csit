data "vault_generic_secret" "fdio_docs" {
  path = "kv/secret/data/etl/fdio_docs"
}

data "vault_aws_access_credentials" "creds" {
  backend = "${var.vault_name}-path"
  role    = "${var.vault_name}-role"
}

module "dash" {
  source = "../"

  aws_access_key_id     = data.vault_generic_secret.fdio_docs.data["access_key"]
  aws_secret_access_key = data.vault_generic_secret.fdio_docs.data["secret_key"]
  aws_default_region    = data.vault_generic_secret.fdio_docs.data["region"]

  elasticenv_vpc_id              = "vpc-csit-dash"
  elasticenv_instance_type       = "t3.nano"
  elasticenv_minsize             = 1
  elasticenv_maxsize             = 2
  elasticenv_public_subnets      = ["subnet-XXXXXXXXXX", "subnet-XXXXXXXXX"] # Service Subnet
  elasticenv_elb_public_subnets  = ["subnet-XXXXXXXXXX", "subnet-XXXXXXXXX"] # ELB Subnet
  elasticenv_tier                = "WebServer"
  elasticenv_solution_stack_name = "64bit Amazon Linux 2 v3.2.0 running Python 3.8"
}
