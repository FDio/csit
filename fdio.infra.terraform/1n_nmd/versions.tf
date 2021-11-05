terraform {
  backend "consul" {
    address = "consul.service.consul:8500"
    scheme  = "http"
    path    = "terraform/nomad"
  }
  required_providers {
    nomad = {
      source  = "hashicorp/nomad"
      version = "~> 1.4.9"
    }
    template = {
      source  = "hashicorp/template"
      version = "~> 2.2.0"
    }
    vault = {
      version = ">=2.14.0"
    }
  }
  required_version = ">= 1.0.3"
}