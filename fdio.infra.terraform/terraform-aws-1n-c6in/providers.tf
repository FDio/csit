provider "aws" {
  region     = var.region
  access_key = ephemeral.vault_kv_secret_v2.creds.data["access_key"]
  secret_key = ephemeral.vault_kv_secret_v2.creds.data["secret_key"]
}

provider "vault" {
}
