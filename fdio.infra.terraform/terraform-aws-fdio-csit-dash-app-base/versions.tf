terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.2.0"
    }
    vault = {
      version = ">= 4.6.0"
    }
  }
  required_version = ">= 1.4.2"
}
