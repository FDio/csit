data "vault_generic_secret" "fdio_logs" {
  path = "kv/secret/data/etl/fdio_logs"
}

data "vault_generic_secret" "fdio_docs" {
  path = "kv/secret/data/etl/fdio_docs"
}

module "etl" {
  providers = {
    nomad = nomad.yul1
  }
  source = "../"

  aws_access_key_id         = data.vault_generic_secret.fdio_logs.data["access_key"]
  aws_secret_access_key     = data.vault_generic_secret.fdio_logs.data["secret_key"]
  aws_default_region        = data.vault_generic_secret.fdio_logs.data["region"]
  out_aws_access_key_id     = data.vault_generic_secret.fdio_docs.data["access_key"]
  out_aws_secret_access_key = data.vault_generic_secret.fdio_docs.data["secret_key"]
  out_aws_default_region    = data.vault_generic_secret.fdio_docs.data["region"]
  cron                      = "@daily"
  datacenters               = ["yul1"]
}
