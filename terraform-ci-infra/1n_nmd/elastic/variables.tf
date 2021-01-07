# Nomad
variable "nomad_datacenters" {
  description = "Nomad data centers"
  type        = list(string)
  default     = [ "dc1" ]
}

# Beats
variable "beats_job_name" {
  description = "Beats job name"
  type        = string
  default     = "beats"
}

variable "beats_group_count" {
  description = "Number of beats group instances"
  type        = number
  default     = 1
}

variable "beats_version" {
  description = "Beats job name"
  type        = string
  default     = "6.2.3"
}

variable "beats_data_dir" {
  description = "Beats data dir"
  type        = string
  default     = "local"
}

variable "beats_use_canary" {
  description = "Uses canary deployment for beats"
  type        = bool
  default     = false
}