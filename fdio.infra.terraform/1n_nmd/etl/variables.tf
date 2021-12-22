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

variable "cpu" {
  description = "Specifies the CPU required to run this task in MHz"
  type        = number
  default     = 10000
}

variable "cron" {
  description = "Specifies a cron expression configuring the interval to launch"
  type        = string
  default     = "@daily"
}

variable "envs" {
  description = "Specifies ETL environment variables"
  type        = list(string)
  default     = []
}

variable "image" {
  description = "Specifies the Docker image to run"
  type        = string
  default     = "pmikus/docker-ubuntu-focal-aws-glue:latest"
}

variable "job_name" {
  description = "Specifies a name for the job"
  type        = string
  default     = "etl"
}

variable "max_parallel" {
  description = "Specifies the maximum number of updates to perform in parallel"
  type        = number
  default     = 1
}

variable "memory" {
  description = "Specifies the memory required in MB"
  type        = number
  default     = 20000
}

variable "prohibit_overlap" {
  description = "Specifies if this job should wait until previous completed"
  type        = bool
  default     = true
}

variable "secret_key" {
  description = "AWS secret key"
  type        = string
  default     = "aws"
}

variable "stagger" {
  description = "Specifies the delay between each set of max_parallel updates"
  type        = string
  default     = "30m"
}

variable "time_zone" {
  description = "Specifies the time zone to evaluate the next launch interval"
  type        = string
  default     = "UTC"
}

variable "type" {
  description = "Specifies the Nomad scheduler to use"
  type        = string
  default     = "batch"
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
