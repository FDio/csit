terraform {
  backend "consul" {
    address = "10.30.51.23:8500"
    scheme  = "http"
    path    = "terraform/etl"
  }
  required_providers {
    nomad = {
      source  = "hashicorp/nomad"
      version = ">= 2.5.2"
    }
  }
  required_version = ">= 1.12.1"
}
