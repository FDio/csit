terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.61.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.1.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 3.1.0"
    }
    vault = {
      version = ">=2.22.1"
    }
  }
  required_version = ">= 1.0.4"
}
