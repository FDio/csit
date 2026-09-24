terraform {
  backend "consul" {
    address = "10.30.51.24:8500"
    scheme  = "http"
    path    = "terraform/dash_m8g"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.27.0, < 7.0.0"
    }
    vault = {
      version = "5.12.0"
    }
  }
  required_version = ">= 1.14.6"
}
