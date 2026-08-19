variable "nomad_acl" {
  description = "Nomad ACLs enabled/disabled."
  type        = bool
  default     = false
}
variable "nomad_provider_ca_file" {
  description = "A local file path to a PEM-encoded certificate authority."
  type        = string
  default     = "/etc/nomad.d/ssl/nomad-ca.pem"
}

variable "nomad_provider_cert_file" {
  description = "A local file path to a PEM-encoded certificate."
  type        = string
  default     = "/etc/nomad.d/ssl/nomad.pem"
}

variable "nomad_provider_key_file" {
  description = "A local file path to a PEM-encoded private key."
  type        = string
  default     = "/etc/nomad.d/ssl/nomad-key.pem"
}