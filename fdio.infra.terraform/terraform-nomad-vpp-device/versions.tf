terraform {
  required_providers {
    nomad = {
      source  = "hashicorp/nomad"
      version = ">= 1.4.19"
    }
  }
  required_version = ">= 1.3.7"
}
