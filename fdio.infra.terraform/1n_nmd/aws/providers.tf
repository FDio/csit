terraform {
  required_providers {
    vault           = {
      version       = ">=2.22.1"
    }
  }
  required_version = ">= 1.0.3"
}

provider "vault" {
  address         = "http://10.30.51.28:8200"
  skip_tls_verify = true
  token           = "s.4z5PsufFwV3sHbCzK9Y2Cojd"
}