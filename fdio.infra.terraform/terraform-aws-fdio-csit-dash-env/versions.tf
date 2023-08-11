terraform {
  backend "consul" {
    address = "10.30.51.24:8500"
    scheme  = "http"
    path    = "terraform/dash"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.7.0"
    }
    vault = {
      version = ">= 3.12.0"
    }
  }
  required_version = ">= 1.5.4"
}
