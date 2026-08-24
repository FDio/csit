terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.27.0, < 7.0.0"
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
      version = ">= 4.6.0"
    }
  }
  required_version = ">= 1.4.2"
}
