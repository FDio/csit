terraform {
  required_providers {
    nomad = {
      source  = "hashicorp/nomad"
      version = "~> 1.4.9"
    }
    template = {
      source  = "hashicorp/template"
      version = "~> 2.1.2"
    }
    vault = {
      version = ">=2.14.0"
    }
  }
  required_version = ">= 0.13"
}

provider "nomad" {
  address   = var.nomad_provider_address
  alias     = "yul1"
}