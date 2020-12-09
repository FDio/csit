variable "nomad_provider_address" {
  description = "FD.io Nomad cluster address."
  type        = string
  default     = "http://nomad.service.consul:4646"
}

variable "nomad_acl" {
  description = "Nomad ACLs enabled/disabled"
  type        = bool
  default     = false
}