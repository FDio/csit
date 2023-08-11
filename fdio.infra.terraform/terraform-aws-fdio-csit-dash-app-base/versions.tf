terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.7.0"
    }
    vault = {
      version = ">= 3.2.1"
    }
  }
  required_version = ">= 1.5.4"
}
