data "vault_generic_secret" "creds" {
  path = "kv/secret/data/etl"
}

module "etl" {
  providers = {
    nomad = nomad.yul1
  }
  source = "../"

  access_key  = data.vault_generic_secret.creds.data["access_key"]
  cron        = "*/15 * * * * *"
  datacenters = ["yul1"]
  secret_key  = data.vault_generic_secret.creds.data["secret_key"]
}
