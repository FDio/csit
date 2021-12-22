variable "nomad_acl" {
  description = "Nomad ACLs enabled/disabled."
  type        = bool
  default     = false
}

variable "nomad_provider_address" {
  description = "FD.io Nomad cluster address."
  type        = string
  default     = "http://10.32.8.14:4646"
}

variable "nomad_provider_ca_file" {
  description = "A local file path to a PEM-encoded certificate authority."
  type        = string
  default     = "/etc/nomad.d/ssl/nomad-ca.pem"
}

variable "nomad_provider_cert_file" {
  description = "A local file path to a PEM-encoded certificate."
  type        = string
  default     = "/etc/nomad.d/ssl/nomad-cli.pem"
}

variable "nomad_provider_key_file" {
  description = "A local file path to a PEM-encoded private key."
  type        = string
  default     = "/etc/nomad.d/ssl/nomad-cli-key.pem"
}

variable "vault_provider_address" {
  description = "Vault cluster address."
  type        = string
  default     = "http://10.30.51.28:8200"
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
