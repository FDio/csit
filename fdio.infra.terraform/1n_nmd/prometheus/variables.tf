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
  description = "Uses canary deployment"
  type        = bool
  default     = false
}

variable "prometheus_vault_secret" {
  description = "Set of properties to be able to fetch secret from vault"
  type        = object({
    use_vault_provider        = bool,
    vault_kv_policy_name      = string,
    vault_kv_path             = string,
    vault_kv_field_access_key = string,
    vault_kv_field_secret_key = string
  })
}

variable "prometheus_cpu" {
  description = "Prometheus CPU allocation"
  type        = number
  default     = 2000
}

variable "prometheus_mem" {
  description = "Prometheus RAM allocation"
  type        = number
  default     = 8192
}

variable "prometheus_port" {
  description = "Prometheus TCP allocation"
  type        = number
  default     = 9200
}

variable "prometheus_data_dir" {
  description = "Prometheus DISK allocation"
  type        = string
  default     = "/data"
}

variable "prometheus_use_host_volume" {
  description = "Use Nomad host volume feature"
  type        = bool
  default     = false
}