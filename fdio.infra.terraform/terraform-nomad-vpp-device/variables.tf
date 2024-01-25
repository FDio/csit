# Nomad
variable "datacenters" {
  description = "Specifies the list of DCs to be considered placing this task"
  type        = list(string)
  default     = ["dc1"]
}

# CSIT SHIM
variable "job_name" {
  description = "CSIT SHIM job name"
  type        = string
  default     = "prod-csit-shim"
}

variable "group_count" {
  description = "Number of CSIT SHIM group instances"
  type        = number
  default     = 1
}

variable "cpu" {
  description = "CSIT SHIM task CPU"
  type        = number
  default     = 2000
}

variable "memory" {
  description = "CSIT SHIM task memory"
  type        = number
  default     = 10000
}

variable "image_aarch64" {
  description = "CSIT SHIM AARCH64 docker image"
  type        = string
  default     = "fdiotools/csit_shim-ubuntu2004:prod-aarch64"
}

variable "image_x86_64" {
  description = "CSIT SHIM X86_64 docker image"
  type        = string
  default     = "fdiotools/csit_shim-ubuntu2004:prod-x86_64"
}