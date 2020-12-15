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

# Minio
variable "minio_job_name" {
  description = "Minio job name"
  type        = string
  default     = "minio"
}

variable "minio_service_name" {
  description = "Minio service name"
  type        = string
  default     = "minio"
}

variable "minio_group_count" {
  description = "Number of Minio group instances"
  type        = number
  default     = 1
}

variable "minio_host" {
  description = "Minio host"
  type        = string
  default     = "127.0.0.1"
}

variable "minio_port" {
  description = "Minio port"
  type        = number
  default     = 9000
}

variable "minio_cpu" {
  description = "CPU allocation for Minio"
  type        = number
  default     = 40000
}

variable "minio_memory" {
  description = "Memory allocation for Minio"
  type        = number
  default     = 40000
}

variable "minio_container_image" {
  description = "Minio docker image"
  type        = string
  default     = "minio/minio:latest"
}

variable "minio_envs" {
  description = "Minio environment variables"
  type        = list(string)
  default     = []
}

variable "minio_access_key" {
  description = "Minio access key"
  type        = string
  default     = "minio"
}

variable "minio_secret_key" {
  description = "Minio secret key"
  type        = string
  default     = "minio123"
}

variable "minio_data_dir" {
  description = "Minio server data dir"
  type        = string
  default     = "/data/"
}

variable "minio_use_host_volume" {
  description = "Use Nomad host volume feature"
  type        = bool
  default     = false
}

variable "minio_use_canary" {
  description = "Uses canary deployment for Minio"
  type        = bool
  default     = false
}

variable "minio_vault_secret" {
  description = "Set of properties to be able to fetch secret from vault"
  type        = object({
    use_vault_provider        = bool,
    vault_kv_policy_name      = string,
    vault_kv_path             = string,
    vault_kv_field_access_key = string,
    vault_kv_field_secret_key = string
  })
}

variable "minio_resource_proxy" {
  description = "Minio proxy resources"
  type        = object({
    cpu       = number,
    memory    = number
  })
  default     = {
    cpu       = 200,
    memory    = 128
  }
  validation {
    condition     = var.minio_resource_proxy.cpu >= 200 && var.minio_resource_proxy.memory >= 128
    error_message = "Proxy resource must be at least: cpu=200, memory=128."
  }
}

# MC
variable "mc_job_name" {
  description = "Minio client job name"
  type        = string
  default     = "mc"
}

variable "mc_service_name" {
  description = "Minio client service name"
  type        = string
  default     = "mc"
}

variable "mc_container_image" {
  description = "Minio client docker image"
  type        = string
  default     = "minio/mc:latest"
}

variable "mc_envs" {
  description = "Minio client environment variables"
  type        = list(string)
  default     = []
}

variable "minio_buckets" {
  description = "List of buckets to create on startup"
  type        = list(string)
  default     = []
}

variable "minio_upstreams" {
  description = "List of upstream services (list of object with service_name, port)"
  type        = list(object({
    service_name = string,
    port         = number,
  }))
  default     = []
}

variable "mc_extra_commands" {
  description = "Extra commands to run in MC container after creating buckets"
  type        = list(string)
  default     = [""]
}