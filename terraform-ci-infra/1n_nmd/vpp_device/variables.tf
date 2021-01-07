# Nomad
variable "nomad_datacenters" {
  description = "Nomad data centers"
  type        = list(string)
  default     = [ "dc1" ]
}

# CSIT SHIM
variable "csit_shim_job_name" {
  description = "CSIT SHIM job name"
  type        = string
  default     = "prod-csit-shim"
}

variable "csit_shim_group_count" {
  description = "Number of CSIT SHIM group instances"
  type        = number
  default     = 1
}

variable "csit_shim_cpu" {
  description = "CSIT SHIM task CPU"
  type        = number
  default     = 2000
}

variable "csit_shim_mem" {
  description = "CSIT SHIM task memory"
  type        = number
  default     = 10000
}