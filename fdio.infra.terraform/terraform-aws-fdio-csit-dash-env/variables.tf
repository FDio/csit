variable "region" {
  description = "AWS Region."
  type        = string
  default     = "eu-central-1"
}

variable "vault_provider_address" {
  description = "Vault cluster address."
  type        = string
  default     = "http://10.30.51.24:8200"
}

variable "vault_provider_skip_tls_verify" {
  description = "Verification of the Vault server's TLS certificate."
  type        = bool
  default     = false
}

variable "vault_provider_token" {
  description = "Vault root token."
  type        = string
  sensitive   = true
}

variable "vault_name" {
  type    = string
  default = "dynamic-aws-creds-vault-fdio-csit-jenkins"
}
