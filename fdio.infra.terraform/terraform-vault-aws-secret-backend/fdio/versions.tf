terraform {
  backend "consul" {
    address = "consul.service.consul:8500"
    scheme  = "http"
    path    = "terraform/aws-secret-backend"
  }
  required_providers {
    vault = {
      version = ">= 3.2.1"
    }
  }
  required_version = ">= 1.1.4"
}
