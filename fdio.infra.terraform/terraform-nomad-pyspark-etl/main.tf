data "vault_kv_secret_v2" "fdio_logs" {
  mount = "kv"
  name  = "etl/fdio_logs"
}

data "vault_kv_secret_v2" "fdio_docs" {
  mount = "kv"
  name  = "etl/fdio_docs"
}

data "vault_kv_secret_v2" "csit_docs" {
  mount = "kv"
  name  = "etl/csit_docs"
}

module "etl" {
  for_each = { for job in var.nomad_jobs : job.job_name => job }
  providers = {
    nomad = nomad.yul1
  }
  source = "../terraform-nomad-nomad-job"

  aws_access_key_id         = data.vault_kv_secret_v2.fdio_logs.data.access_key
  aws_secret_access_key     = data.vault_kv_secret_v2.fdio_logs.data.secret_key
  aws_default_region        = data.vault_kv_secret_v2.fdio_logs.data.region
  out_aws_access_key_id     = data.vault_kv_secret_v2.csit_docs.data.access_key
  out_aws_secret_access_key = data.vault_kv_secret_v2.csit_docs.data.secret_key
  out_aws_default_region    = data.vault_kv_secret_v2.csit_docs.data.region
  cron                      = "0 30 0 * * * *"
  datacenters               = ["yul1"]
  job_name                  = each.key
  memory                    = each.value.memory
}