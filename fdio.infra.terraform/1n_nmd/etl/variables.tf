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

# ETL
variable "access_key" {
  description = "AWS access key"
  type        = string
  default     = "aws"
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
  description = "Specifies the CPU required to run this task in MHz"
  type        = number
  default     = 1000
}

variable "envs" {
  description = "ETL environment variables"
  type        = list(string)
  default     = []
}

variable "group_count" {
  description = "Specifies the number of the task groups running under this one"
  type        = number
  default     = 1
}

variable "image" {
  description = "The Docker image to run"
  type        = string
  default     = "pmikus/docker-centos-8-aws-glue:3.0.0"
}

variable "job_name" {
  description = "Specifies a name for the job"
  type        = string
  default     = "etl"
}

variable "kms_variables" {
  type = object({
    use_vault_kms        = string
    vault_address        = string,
    vault_kms_approle_kv = string,
    vault_kms_key_name   = string
  })
  description = "Set of properties to be able to transit secrets in vault"
  default = {
    use_vault_kms        = false
    vault_address        = "",
    vault_kms_approle_kv = "",
    vault_kms_key_name   = ""
  }
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

variable "secret_key" {
  description = "AWS secret key"
  type        = string
  default     = "aws"
}

variable "use_canary" {
  description = "Uses canary deployment for ETL"
  type        = bool
  default     = false
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
  description = "Set of properties to be able to fetch secret from vault"
  default = {
    use_vault_provider        = false
    vault_kv_policy_name      = "kv"
    vault_kv_path             = "secret/data/etl"
    vault_kv_field_access_key = "access_key"
    vault_kv_field_secret_key = "secret_key"
  }
}

variable "volume_destination" {
  description = "Specifies where the volume should be mounted inside the task"
  type        = string
  default     = "/data/"
}
