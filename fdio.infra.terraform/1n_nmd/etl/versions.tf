terraform {
  required_providers {
    nomad = {
      source  = "hashicorp/nomad"
      version = "~> 1.4.15"
    }
    template = {
      source  = "hashicorp/template"
      version = "~> 2.2.0"
    }
  }
  required_version = ">= 1.0.3"
}
