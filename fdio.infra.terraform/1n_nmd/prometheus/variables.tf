# Nomad
variable "datacenters" {
  description = "Specifies the list of DCs to be considered placing this task"
  type        = list(string)
  default     = ["dc1"]
}

variable "region" {
  description = "Specifies the list of DCs to be considered placing this task"
  type        = string
  default     = "global"
}

variable "volume_source" {
  description = "The name of the volume to request"
  type        = string
  default     = "prod-volume-data1-1"
}

# Prometheus
variable "pm_version" {
  description = "Prometheus version"
  type        = string
  default     = "2.33.1"
}

variable "auto_promote" {
  description = "Specifies if the job should auto-promote to the canary version"
  type        = bool
  default     = true
}

variable "auto_revert" {
  description = "Specifies if the job should auto-revert to the last stable job"
  type        = bool
  default     = true
}

variable "canary" {
  description = "Equal to the count of the task group allows blue/green depl."
  type        = number
  default     = 1
}

variable "cpu" {
  description = "CPU allocation"
  type        = number
  default     = 2000
}

variable "data_dir" {
  description = "Prometheus DISK allocation"
  type        = string
  default     = "/data"
}

variable "group_count" {
  description = "Specifies the number of the task groups running under this one"
  type        = number
  default     = 4
}

variable "job_name" {
  description = "Specifies a name for the job"
  type        = string
  default     = "prometheus"
}

variable "max_parallel" {
  description = "Specifies the maximum number of updates to perform in parallel"
  type        = number
  default     = 1
}

variable "memory" {
  description = "Specifies the memory required in MB"
  type        = number
  default     = 4096
}

variable "port" {
  description = "Specifies the static TCP/UDP port to allocate"
  type        = number
  default     = 9090
}

variable "service_name" {
  description = "Specifies the name this service will be advertised in Consul"
  type        = string
  default     = "prometheus"
}

variable "use_canary" {
  description = "Uses canary deployment"
  type        = bool
  default     = true
}

variable "use_host_volume" {
  description = "Use Nomad host volume feature"
  type        = bool
  default     = true
}

variable "volume_destination" {
  description = "Specifies where the volume should be mounted inside the task"
  type        = string
  default     = "/data/"
}

variable "vault_secret" {
  type = object({
    use_vault_provider        = bool,
    vault_kv_policy_name      = string,
    vault_kv_path             = string,
    vault_kv_field_access_key = string,
    vault_kv_field_secret_key = string
  })
  description = "Set of properties to be able to fetch secret from vault."
  default = {
    use_vault_provider        = false
    vault_kv_policy_name      = "kv"
    vault_kv_path             = "secret/data/prometheus"
    vault_kv_field_access_key = "access_key"
    vault_kv_field_secret_key = "secret_key"
  }
}
