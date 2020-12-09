# Nomad
variable "nomad_datacenters" {
  description = "Nomad data centers"
  type        = list(string)
  default     = [ "dc1" ]
}

# Nginx
variable "nginx_job_name" {
  description = "Nginx job name"
  type        = string
  default     = "nginx"
}