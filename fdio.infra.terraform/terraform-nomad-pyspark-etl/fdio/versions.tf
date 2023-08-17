terraform {
  backend "consul" {
    address = "10.30.51.23:8500"
    scheme  = "http"
    path    = "terraform/etl"
  }
  required_providers {
    nomad = {
      source  = "hashicorp/nomad"
      version = ">= 1.4.20"
    }
    vault = {
      version = ">= 3.12.0"
    }
  }
  required_version = ">= 1.5.4"
}
