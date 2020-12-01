terraform {
  # This module is now only being tested with Terraform 0.13.x.
  required_version = ">= 0.13"
}

provider "nomad" {
  address = var.nomad_provider_address
  alias   = "yul1"
}