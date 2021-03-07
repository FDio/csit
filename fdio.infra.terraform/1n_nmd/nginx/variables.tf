# Nomad
variable "nomad_datacenters" {
  description = "Nomad data centers"
  type        = list(string)
  default     = [ "dc1" ]
}

variable "nomad_host_volume" {
  description = "Nomad Host Volume"
  type        = string
  default     = "persistence"
}

# Nginx
variable "nginx_job_name" {
  description = "Nginx job name"
  type        = string
  default     = "nginx"
}

variable "nginx_use_host_volume" {
  description = "Use Nomad host volume feature"
  type        = bool
  default     = false
}