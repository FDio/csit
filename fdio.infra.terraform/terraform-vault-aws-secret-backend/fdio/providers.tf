provider "vault" {
  address         = var.vault_provider_address
  skip_tls_verify = var.vault_provider_skip_tls_verify
  token           = var.vault_provider_token
}