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
variable "node_service_name" {
  description = "Node exporter service name"
  type        = string
  default     = "nodeexporter"
}

variable "node_version" {
  description = "Node exporter version"
  type        = string
  default     = "1.0.1"
}

variable "node_port" {
  description = "Node exporter TCP allocation"
  type        = number
  default     = 9100
}

# Blackbox Exporter
variable "blackbox_service_name" {
  description = "Blackbox exporter service name"
  type        = string
  default     = "blackboxexporter"
}

variable "blackbox_version" {
  description = "Blackbox exporter version"
  type        = string
  default     = "0.18.0"
}

variable "blackbox_port" {
  description = "Blackbox exporter TCP allocation"
  type        = number
  default     = 9115
}

# cAdvisor Exporter
variable "cadvisor_service_name" {
  description = "cAdvisor exporter service name"
  type        = string
  default     = "cadvisorexporter"
}

variable "cadvisor_image" {
  description = "cAdvisor exporter docker image"
  type        = string
  default     = "gcr.io/cadvisor/cadvisor:v0.38.7"
}

variable "cadvisor_port" {
  description = "cAdvisor exporter TCP allocation"
  type        = number
  default     = 8080
}