terraform {
  backend "consul" {
    address = "10.30.51.24:8500"
    scheme  = "http"
    path    = "terraform/dash_m7g"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.31.0"
    }
    vault = {
      version = ">= 3.23.0"
    }
  }
  required_version = ">= 1.4.2"
}
