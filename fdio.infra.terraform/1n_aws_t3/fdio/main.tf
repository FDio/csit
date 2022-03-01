data "vault_generic_secret" "fdio_docs" {
  path = "kv/secret/data/etl/fdio_docs"
}

module "dash" {
  source = "../"

  aws_access_key_id         = data.vault_generic_secret.fdio_docs.data["access_key"]
  aws_secret_access_key     = data.vault_generic_secret.fdio_docs.data["secret_key"]
  aws_default_region        = data.vault_generic_secret.fdio_docs.data["region"]
}
