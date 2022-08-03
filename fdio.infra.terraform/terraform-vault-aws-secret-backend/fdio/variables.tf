variable "vault_provider_address" {
  description = "Vault cluster address."
  type        = string
  default     = "vault.service.consul:8200"
}

variable "vault_provider_skip_tls_verify" {
  description = "Verification of the Vault server's TLS certificate"
  type        = bool
  default     = false
}

variable "vault_provider_token" {
  description = "Vault root token"
  type        = string
  sensitive   = true
}
