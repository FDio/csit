variable "nomad_acl" {
  description = "Nomad ACLs enabled/disabled."
  type        = bool
  default     = false
}

variable "nomad_provider_address" {
  description = "FD.io Nomad cluster address."
  type        = string
  default     = "http://10.30.51.23:4646"
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

variable "vault_provider_address" {
  description = "Vault cluster address."
  type        = string
  default     = "http://10.30.51.23:8200"
}

variable "vault_provider_skip_tls_verify" {
  description = "Verification of the Vault server's TLS certificate."
  type        = bool
  default     = false
}

variable "vault_provider_token" {
  description = "Vault root token."
  type        = string
  sensitive   = true
}

variable "nomad_jobs" {
  description = "List of ETL jobs"
  type        = list(map(any))
  default = [
    {
      job_name = "etl-stats"
      memory = 50000
    },
    #{
    #  job_name = "etl-iterative-hoststack"
    #  memory = 50000
    #},
    #{
    #  job_name = "etl-iterative-mrr"
    #  memory = 50000
    #},
    #{
    #  job_name = "etl-iterative-ndrpdr"
    #  memory = 50000
    #},
    #{
    #  job_name = "etl-iterative-reconf"
    #  memory = 50000
    #},
    #{
    #  job_name = "etl-iterative-soak"
    #  memory = 50000
    #},
    #{
    #  job_name = "etl-coverage-hoststack"
    #  memory = 50000
    #},
    #{
    #  job_name = "etl-coverage-mrr"
    #  memory = 50000
    #},
    #{
    #  job_name = "etl-coverage-ndrpdr"
    #  memory = 50000
    #},
    #{
    #  job_name = "etl-coverage-reconf"
    #  memory = 50000
    #},
    #{
    #  job_name = "etl-coverage-soak"
    #  memory = 50000
    #},
    {
      job_name = "etl-trending-hoststack"
      memory = 50000
    },
    {
      job_name = "etl-trending-mrr"
      memory = 60000
    },
    {
      job_name = "etl-trending-ndrpdr"
      memory = 60000
    },
    {
      job_name = "etl-trending-soak"
      memory = 60000
    }
  ]
}