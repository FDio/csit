# Nomad
variable "datacenters" {
  description = "Specifies the list of DCs to be considered placing this task."
  type        = list(string)
  default     = ["yul1"]
}

variable "cpu" {
  description = "Specifies the CPU required to run this task in MHz."
  type        = number
  default     = 12000
}

variable "image" {
  description = "Specifies the Docker image to run."
  type        = string
  default     = "pmikus/docker-hfr-dispatcher-prod"
}

variable "job_name" {
  description = "Specifies a name for the job."
  type        = string
  default     = "hfr-dispatcher"
}

variable "memory" {
  description = "Specifies the memory required in MB."
  type        = number
  default     = 8000
}

variable "dispatchers" {
  type = list(object({
    id         = number
    namespace  = string
    version    = string
  }))
  default = [
    {
      id         = 1
      namespace  = "hfr"
      version    = "master"
    }
    #{
    #  id         = 2
    #  namespace  = "hfr"
    #  version    = "2606.0"
    #}
  ]
}