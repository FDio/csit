terraform {
  backend "consul" {
    address = "10.30.51.23:8500"
    scheme  = "http"
    path    = "terraform/gha-dispatcher"
  }
  required_providers {
    nomad = {
      source  = "hashicorp/nomad"
      version = ">= 2.5.0"
    }
  }
  required_version = ">= 1.12.1"
}
