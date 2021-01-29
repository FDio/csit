# Nomad
variable "nomad_datacenters" {
  description = "Nomad data centers"
  type        = list(string)
  default     = [ "dc1" ]
}

# Alermanager
variable "alertmanager_job_name" {
  description = "Job name"
  type        = string
  default     = "alertmanager"
}

variable "alertmanager_group_count" {
  description = "Number of group instances"
  type        = number
  default     = 1
}

variable "alertmanager_service_name" {
  description = "Service name"
  type        = string
  default     = "alertmanager"
}

variable "alertmanager_version" {
  description = "Version"
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
  description = "CPU allocation"
  type        = number
  default     = 1000
}

variable "alertmanager_mem" {
  description = "RAM allocation"
  type        = number
  default     = 1024
}

variable "alertmanager_port" {
  description = "TCP allocation"
  type        = number
  default     = 9093
}

variable "alertmanager_default_receiver" {
  description = "Alertmanager default receiver"
  type        = string
  default     = "default-receiver"
}

variable "alertmanager_slack_api_key" {
  description = "Alertmanager slack API key"
  type        = string
  default     = "XXXXXXXXX/XXXXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX"
}

variable "alertmanager_slack_channel" {
  description = "Alertmanager slack channel"
  type        = string
  default     = "slack-channel"
}