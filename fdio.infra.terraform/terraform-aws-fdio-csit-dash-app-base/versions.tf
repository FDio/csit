terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.31.0"
    }
    vault = {
      version = ">= 3.23.0"
    }
  }
  required_version = ">= 1.5.4"
}
