# Nomad
variable "nomad_datacenters" {
  description = "Nomad data centers"
  type        = list(string)
  default     = [ "dc1" ]
}

# Exporter
variable "exporter_job_name" {
  description = "Exporter job name"
  type        = string
  default     = "exporter"
}

variable "exporter_use_canary" {
  description = "Uses canary deployment"
  type        = bool
  default     = false
}

# Node Exporter
variable "node_exporter_service_name" {
  description = "Node exporter service name"
  type        = string
  default     = "nodeexporter"
}

variable "node_exporter_version" {
  description = "Node exporter version"
  type        = string
  default     = "1.0.1"
}

variable "node_exporter_port" {
  description = "Node exporter TCP allocation"
  type        = number
  default     = 9100
}