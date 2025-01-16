terraform {
  backend "consul" {
    address = "10.30.51.24:8500"
    scheme  = "http"
    path    = "terraform/dash_m8g"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.83.1"
    }
    vault = {
      version = ">= 4.6.0"
    }
  }
  required_version = ">= 1.10.4"
}
