provider "vault" {
  address         = "http://10.30.51.28:8200"
  skip_tls_verify = true
  token           = var.token
}
