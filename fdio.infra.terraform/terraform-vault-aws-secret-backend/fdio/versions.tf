terraform {
  backend "consul" {
    address = "10.30.51.23:8500"
    scheme  = "http"
    path    = "terraform/aws-secret-backend"
  }
  required_providers {
    vault = {
      version = ">= 3.12.0"
    }
  }
  required_version = ">= 1.5.4"
}
