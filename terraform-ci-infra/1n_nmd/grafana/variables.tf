# Nomad
variable "nomad_datacenters" {
  description = "Nomad data centers"
  type        = list(string)
  default     = [ "dc1" ]
}

# Grafana
variable "grafana_job_name" {
  description = "Grafana job name"
  type        = string
  default     = "grafana"
}

variable "grafana_group_count" {
  description = "Number of grafana group instances"
  type        = number
  default     = 1
}

variable "grafana_service_name" {
  description = "Grafana service name"
  type        = string
  default     = "grafana"
}

variable "grafana_version" {
  description = "Grafana version"
  type        = string
  default     = "7.3.7"
}

variable "grafana_use_canary" {
  description = "Uses canary deployment"
  type        = bool
  default     = false
}

variable "grafana_cpu" {
  description = "Grafana CPU allocation"
  type        = number
  default     = 2000
}

variable "grafana_mem" {
  description = "Grafana RAM allocation"
  type        = number
  default     = 8192
}

variable "grafana_port" {
  description = "Grafana TCP allocation"
  type        = number
  default     = 3000
}