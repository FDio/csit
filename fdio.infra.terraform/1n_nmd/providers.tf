provider "nomad" {
  address = var.nomad_provider_address
  alias   = "yul1"
  #  ca_file   = var.nomad_provider_ca_file
  #  cert_file = var.nomad_provider_cert_file
  #  key_file  = var.nomad_provider_key_file
}

provider "vault" {
  address         = "http://10.30.51.28:8200"
  skip_tls_verify = true
  token           = var.token
}