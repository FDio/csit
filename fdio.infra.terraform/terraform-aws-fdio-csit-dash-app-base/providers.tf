provider "aws" {
  region     = data.vault_kv_secret_v2.creds.data["region"]
  access_key = data.vault_kv_secret_v2.creds.data["access_key"]
  secret_key = data.vault_kv_secret_v2.creds.data["secret_key"]
}

provider "vault" {
}
