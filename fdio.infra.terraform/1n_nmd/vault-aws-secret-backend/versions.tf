terraform {
  backend "consul" {
    address = "consul.service.consul:8500"
    scheme  = "http"
    path    = "fdio/terraform/1n/nomad"
  }
  required_providers {
    vault = {
      version = ">=2.22.1"
    }
  }
  required_version = ">= 1.0.3"
}
