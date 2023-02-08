terraform {
  backend "consul" {
    address = "10.30.51.24:8500"
    scheme  = "http"
    path    = "terraform/dash"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.3.0"
    }
    vault = {
      version = ">= 3.12.0"
    }
  }
  required_version = ">= 1.3.7"
}
