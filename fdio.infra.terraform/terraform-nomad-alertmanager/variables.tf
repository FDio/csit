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
  default     = "persistence"
}

# Alertmanager
variable "am_version" {
  description = "Alertmanager version"
  type        = string
  default     = "0.21.0"
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
  default     = 1000
}

variable "group_count" {
  description = "Specifies the number of the task groups running under this one"
  type        = number
  default     = 1
}

variable "job_name" {
  description = "Specifies a name for the job"
  type        = string
  default     = "alertmanager"
}

variable "max_parallel" {
  description = "Specifies the maximum number of updates to perform in parallel"
  type        = number
  default     = 1
}

variable "memory" {
  description = "Specifies the memory required in MB"
  type        = number
  default     = 1024
}

variable "port" {
  description = "Specifies the static TCP/UDP port to allocate"
  type        = number
  default     = 9093
}

variable "service_name" {
  description = "Specifies the name this service will be advertised in Consul"
  type        = string
  default     = "alertmanager"
}

variable "use_canary" {
  description = "Uses canary deployment"
  type        = bool
  default     = true
}

variable "use_host_volume" {
  description = "Use Nomad host volume feature"
  type        = bool
  default     = false
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
    vault_kv_path             = "secret/data/alertmanager"
    vault_kv_field_access_key = "access_key"
    vault_kv_field_secret_key = "secret_key"
  }
}

variable "volume_destination" {
  description = "Specifies where the volume should be mounted inside the task"
  type        = string
  default     = "/data/"
}

variable "slack_jenkins_api_key" {
  description = "Alertmanager jenkins slack API key"
  type        = string
  default     = "XXXXXXXXX/XXXXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX"
}

variable "slack_jenkins_receiver" {
  description = "Alertmanager jenkins slack receiver"
  type        = string
  default     = "jenkins-slack-receiver"
}

variable "slack_jenkins_channel" {
  description = "Alertmanager jenkins slack channel"
  type        = string
  default     = "jenkins-channel"
}

variable "slack_default_api_key" {
  description = "Alertmanager default slack API key"
  type        = string
  default     = "XXXXXXXXX/XXXXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX"
}

variable "slack_default_receiver" {
  description = "Alertmanager default slack receiver"
  type        = string
  default     = "default-slack-receiver"
}

variable "slack_default_channel" {
  description = "Alertmanager default slack channel"
  type        = string
  default     = "default-channel"
}