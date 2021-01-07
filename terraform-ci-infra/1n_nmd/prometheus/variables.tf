# Nomad
variable "nomad_datacenters" {
  description = "Nomad data centers"
  type        = list(string)
  default     = [ "dc1" ]
}

# Prometheus
variable "prometheus_job_name" {
  description = "Prometheus job name"
  type        = string
  default     = "prometheus"
}

variable "prometheus_group_count" {
  description = "Number of prometheus group instances"
  type        = number
  default     = 1
}

variable "prometheus_service_name" {
  description = "Prometheus service name"
  type        = string
  default     = "prometheus"
}

variable "prometheus_version" {
  description = "Prometheus version"
  type        = string
  default     = "v2.24.0"
}

variable "prometheus_use_canary" {
  description = "Uses canary deployment for prometheus"
  type        = bool
  default     = false
}

variable "prometheus_cpu" {
  description = "Prometheus task CPU"
  type        = number
  default     = 40000
}

variable "prometheus_mem" {
  description = "Prometheus task memory"
  type        = number
  default     = 40000
}

variable "prometheus_port" {
  description = "Prometheus port"
  type        = number
  default     = 9200
}

# Alermanager
variable "alertmanager_job_name" {
  description = "Alertmanager job name"
  type        = string
  default     = "alertmanager"
}

variable "alertmanager_group_count" {
  description = "Number of alertmanager group instances"
  type        = number
  default     = 1
}

variable "alertmanager_service_name" {
  description = "Alertmanager service name"
  type        = string
  default     = "alertmanager"
}

variable "alertmanager_version" {
  description = "Alertmanager version"
  type        = string
  default     = "v0.21.0"
}

variable "alertmanager_use_canary" {
  description = "Uses canary deployment for alertmanager"
  type        = bool
  default     = false
}

variable "alertmanager_cpu" {
  description = "Alertmanager task CPU"
  type        = number
  default     = 1000
}

variable "alertmanager_mem" {
  description = "Alertmanager task memory"
  type        = number
  default     = 128
}

variable "alertmanager_port" {
  description = "Alertmanager port"
  type        = number
  default     = 9093
}