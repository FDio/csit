data "vault_aws_access_credentials" "creds" {
  backend = "${var.vault-name}-path"
  role    = "${var.vault-name}-role"
}

module "etl" {
  source = "../"
  providers = {
    nomad = nomad.yul1
  }

  # nomad
  datacenters   = ["yul1"]

  # etl
  access_key         = data.vault_generic_secret.etl_creds.data["access_key"]
  cron               = "*/15 * * * * *"
  secret_key         = data.vault_generic_secret.etl_creds.data["secret_key"]
}
