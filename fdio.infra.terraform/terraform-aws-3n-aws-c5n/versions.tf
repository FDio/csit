terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.3.0"
    }
    null = {
      source  = "hashicorp/null"
      version = ">= 3.1.1"
    }
    tls = {
      source  = "hashicorp/tls"
      version = ">= 4.0.3"
    }
    vault = {
      version = ">= 2.22.1"
    }
  }
  required_version = ">= 1.0.4"
}
