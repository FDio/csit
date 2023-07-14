terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.7.0"
    }
    null = {
      source  = "hashicorp/null"
      version = ">= 3.2.1"
    }
    tls = {
      source  = "hashicorp/tls"
      version = ">= 4.0.4"
    }
    vault = {
      version = ">= 3.15.2"
    }
  }
  required_version = ">= 1.4.2"
}