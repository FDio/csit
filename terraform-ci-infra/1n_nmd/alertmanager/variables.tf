# Nomad
variable "nomad_datacenters" {
  description = "Nomad data centers"
  type        = list(string)
  default     = [ "dc1" ]
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
  default     = "0.21.0"
}

variable "alertmanager_use_canary" {
  description = "Uses canary deployment"
  type        = bool
  default     = false
}

variable "alertmanager_vault_secret" {
  description = "Set of properties to be able to fetch secret from vault"
  type        = object({
    use_vault_provider        = bool,
    vault_kv_policy_name      = string,
    vault_kv_path             = string,
    vault_kv_field_access_key = string,
    vault_kv_field_secret_key = string
  })
}

variable "alertmanager_cpu" {
  description = "Alertmanager CPU allocation"
  type        = number
  default     = 1000
}

variable "alertmanager_mem" {
  description = "Alertmanager RAM allocation"
  type        = number
  default     = 1024
}

variable "alertmanager_port" {
  description = "Alertmanager TCP allocation"
  type        = number
  default     = 9093
}