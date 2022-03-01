provider "aws" {
  region     = var.region
  access_key = data.vault_aws_access_credentials.creds.access_key
  secret_key = data.vault_aws_access_credentials.creds.secret_key
}

provider "vault" {
  address         = var.vault_provider_address
  skip_tls_verify = var.vault_provider_skip_tls_verify
  token           = var.vault_provider_token
}
