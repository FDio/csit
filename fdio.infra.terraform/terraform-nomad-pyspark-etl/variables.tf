variable "nomad_acl" {
  description = "Nomad ACLs enabled/disabled."
  type        = bool
  default     = false
}
variable "nomad_provider_ca_file" {
  description = "A local file path to a PEM-encoded certificate authority."
  type        = string
  default     = "/etc/nomad.d/ssl/nomad-ca.pem"
}

variable "nomad_provider_cert_file" {
  description = "A local file path to a PEM-encoded certificate."
  type        = string
  default     = "/etc/nomad.d/ssl/nomad.pem"
}

variable "nomad_provider_key_file" {
  description = "A local file path to a PEM-encoded private key."
  type        = string
  default     = "/etc/nomad.d/ssl/nomad-key.pem"
}

variable "nomad_jobs" {
  description = "List of ETL jobs"
  type        = list(map(any))
  default = [
    {
      job_name = "etl-stats"
      script_name = "stats"
      memory = 50000
    },
    {
      job_name = "etl-iterative-hoststack"
      script_name = "iterative_hoststack"
      memory = 50000
    },
    {
      job_name = "etl-iterative-mrr"
      script_name = "iterative_mrr"
      memory = 50000
    },
    {
      job_name = "etl-iterative-ndrpdr"
      script_name = "iterative_ndrpdr"
      memory = 50000
    },
    {
      job_name = "etl-iterative-reconf"
      script_name = "iterative_reconf"
      memory = 50000
    },
    {
      job_name = "etl-iterative-soak"
      script_name = "iterative_soak"
      memory = 50000
    },
    {
      job_name = "etl-coverage-hoststack"
      script_name = "coverage_hoststack"
      memory = 50000
    },
    {
      job_name = "etl-coverage-mrr"
      script_name = "coverage_mrr"
      memory = 50000
    },
    {
      job_name = "etl-coverage-ndrpdr"
      script_name = "coverage_ndrpdr"
      memory = 50000
    },
    {
      job_name = "etl-coverage-reconf"
      script_name = "coverage_reconf"
      memory = 50000
    },
    {
      job_name = "etl-coverage-soak"
      script_name = "coverage_soak"
      memory = 50000
    },
    {
      job_name = "etl-trending-hoststack"
      script_name = "trending_hoststack"
      memory = 50000
    },
    {
      job_name = "etl-trending-mrr"
      script_name = "trending_mrr"
      memory = 60000
    },
    {
      job_name = "etl-trending-ndrpdr"
      script_name = "trending_ndrpdr"
      memory = 60000
    },
    {
      job_name = "etl-trending-soak"
      script_name = "trending_soak"
      memory = 60000
    }
  ]
}