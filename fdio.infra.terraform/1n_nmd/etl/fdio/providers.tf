provider "nomad" {
  address = var.nomad_provider_address
  alias   = "yul1"
  #  ca_file   = var.nomad_provider_ca_file
  #  cert_file = var.nomad_provider_cert_file
  #  key_file  = var.nomad_provider_key_file
}

provider "vault" {
  address         = var.vault_provider_address
  skip_tls_verify = var.vault_provider_skip_tls_verify
  token           = var.vault_provider_token
}
