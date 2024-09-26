terraform {
  required_providers {
    nomad = {
      source  = "hashicorp/nomad"
      version = ">= 1.4.20"
    }
  }
  required_version = ">= 1.5.4"
}
