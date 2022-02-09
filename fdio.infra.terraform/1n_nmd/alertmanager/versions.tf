terraform {
  required_providers {
    nomad = {
      source  = "hashicorp/nomad"
      version = ">= 1.4.16"
    }
  }
  required_version = ">= 1.1.4"
}