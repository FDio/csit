variable "vault_provider_address" {
  description = "Vault cluster address."
  type        = string
  default     = "http://10.30.51.26:8200"
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

variable "aws_access_key" {
  description = "AWS access key"
  type        = string
  sensitive   = true
}

variable "aws_secret_key" {
  description = "AWS secret key"
  type        = string
  sensitive   = true
}