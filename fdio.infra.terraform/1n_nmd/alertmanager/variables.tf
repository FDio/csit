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

variable "alertmanager_slack_jenkins_api_key" {
  description = "Alertmanager jenkins slack API key"
  type        = string
  default     = "XXXXXXXXX/XXXXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX"
}

variable "alertmanager_slack_jenkins_receiver" {
  description = "Alertmanager jenkins slack receiver"
  type        = string
  default     = "jenkins-slack-receiver"
}

variable "alertmanager_slack_jenkins_channel" {
  description = "Alertmanager jenkins slack channel"
  type        = string
  default     = "jenkins-channel"
}

variable "alertmanager_slack_default_api_key" {
  description = "Alertmanager default slack API key"
  type        = string
  default     = "XXXXXXXXX/XXXXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX"
}

variable "alertmanager_slack_default_receiver" {
  description = "Alertmanager default slack receiver"
  type        = string
  default     = "default-slack-receiver"
}

variable "alertmanager_slack_default_channel" {
  description = "Alertmanager default slack channel"
  type        = string
  default     = "default-channel"
}