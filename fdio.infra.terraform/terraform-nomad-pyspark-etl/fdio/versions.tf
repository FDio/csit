terraform {
  backend "consul" {
    address = "vault.service.consul:8500"
    scheme  = "http"
    path    = "terraform/etl"
  }
  required_providers {
    nomad = {
      source  = "hashicorp/nomad"
      version = ">= 1.4.19"
    }
    vault = {
      version = ">= 3.12.0"
    }
  }
  required_version = ">= 1.3.7"
}
