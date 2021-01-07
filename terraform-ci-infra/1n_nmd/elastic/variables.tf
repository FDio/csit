# Nomad
variable "nomad_datacenters" {
  description = "Nomad data centers"
  type        = list(string)
  default     = [ "dc1" ]
}

# Beats
variable "beats_job_name" {
  description = "Beats job name"
  type        = string
  default     = "beats"
}

variable "beats_version" {
  description = "Beats job name"
  type        = string
  default     = "7.10.1"
}

variable "beats_data_dir" {
  description = "Beats data dir"
  type        = string
  default     = "local"
}

variable "beats_use_canary" {
  description = "Uses canary deployment for beats"
  type        = bool
  default     = false
}

# Elastic
variable "elastic_job_name" {
  description = "Elastic job name"
  type        = string
  default     = "elastic"
}

variable "elastic_group_count" {
  description = "Number of elastic group instances"
  type        = number
  default     = 1
}

variable "elastic_service_name" {
  description = "Elastic service name"
  type        = string
  default     = "elastic"
}

variable "elastic_version" {
  description = "Elastic job name"
  type        = string
  default     = "7.10.1"
}

variable "elastic_use_canary" {
  description = "Uses canary deployment for elastic"
  type        = bool
  default     = false
}

variable "elastic_master_cpu" {
  description = "Elastic Master group CPU"
  type        = number
  default     = 40000
}

variable "elastic_master_memory" {
  description = "Elastic Master group memory"
  type        = number
  default     = 40000
}

variable "elastic_master_rest_port" {
  description = "Elastic Kibana REST port"
  type        = number
  default     = 9200
}

variable "elastic_master_transport_port" {
  description = "Elastic Kibana Transport port"
  type        = number
  default     = 9300
}

variable "elastic_data_cpu" {
  description = "Elastic Data group CPU"
  type        = number
  default     = 40000
}

variable "elastic_data_memory" {
  description = "Elastic Data group memory"
  type        = number
  default     = 40000
}

variable "elastic_kibana_cpu" {
  description = "Elastic Kibana group CPU"
  type        = number
  default     = 1000
}

variable "elastic_kibana_memory" {
  description = "Elastic Kibana group memory"
  type        = number
  default     = 8192
}

variable "elastic_kibana_port" {
  description = "Elastic Kibana HTTP port"
  type        = number
  default     = 5601
}