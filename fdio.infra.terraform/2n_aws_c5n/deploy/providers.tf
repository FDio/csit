provider "aws" {
  region     = var.region
  access_key = data.vault_aws_access_credentials.creds.access_key
  secret_key = data.vault_aws_access_credentials.creds.secret_key
}

provider "vault" {
  address         = "http://10.30.51.28:8200"
  skip_tls_verify = true
  token           = "s.4z5PsufFwV3sHbCzK9Y2Cojd"
}