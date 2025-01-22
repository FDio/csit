terraform {
  backend "consul" {
    address = "10.30.51.26:8500"
    scheme  = "http"
    path    = "terraform/aws-secret-backend"
  }
  required_providers {
    vault = {
      version = "4.3.0"
    }
  }
  required_version = ">= 1.5.4"
}
