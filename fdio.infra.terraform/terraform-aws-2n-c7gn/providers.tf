provider "aws" {
  region     = var.region
  access_key = data.vault_aws_access_credentials.creds.access_key
  secret_key = data.vault_aws_access_credentials.creds.secret_key
}

provider "vault" {
  address         = "http://vault.service.consul:8200"
  skip_tls_verify = true
  token           = "hvs.bzHw4ZHsz9B0019P8I73yS6l"
}