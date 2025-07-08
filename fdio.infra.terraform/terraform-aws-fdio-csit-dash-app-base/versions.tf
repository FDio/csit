terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.99.1"
    }
    vault = {
      version = ">= 4.6.0"
    }
  }
  required_version = ">= 1.4.2"
}
