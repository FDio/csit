variable "region" {
  description = "AWS Region."
  type        = string
  default     = "eu-central-1"
}

variable "vault_provider_address" {
  description = "Vault cluster address."
  type        = string
  default     = "http://vault.service.consul:8200"
}

variable "vault_provider_skip_tls_verify" {
  description = "Verification of the Vault server's TLS certificate."
  type        = bool
  default     = false
}

variable "vault_provider_token" {
  description = "Vault root token."
  type        = string
  default     = "s.4z5PsufFwV3sHbCzK9Y2Cojd"
}

variable "vault_name" {
  type    = string
  default = "dynamic-aws-creds-vault-fdio-csit-jenkins"
}

variable "application_bucket" {
  description = "The name of the bucket."
  type        = string
  default     = "elasticbeanstalk-eu-central-1-407116685360"
}

variable "application_description" {
  description = "Short description of the Application Version."
  type        = string
  default     = "FD.io CDASH"
}

variable "application_name" {
  description = "Name of the Beanstalk Application."
  type        = string
  default     = "fdio-csit-dash-app"
}

variable "application_source" {
  description = "The source file with application code."
  type        = string
  default     = "../../csit.infra.dash/app.zip"
}

variable "application_version" {
  description = "Application version string."
  type        = number
  default     = 41
}
