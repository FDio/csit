locals {
  datacenters = join(",", var.datacenters)
  envs        = join("\n", concat([], var.envs))
  upstreams   = jsonencode(var.upstreams)
}

data "template_file" "nomad_job_etl" {
  template = file("${path.module}/conf/nomad/etl.hcl")
  vars = {
    access_key                = var.access_key
    cpu                       = var.cpu
    cron                      = var.cron
    datacenters               = local.datacenters
    envs                      = local.envs
    image                     = var.image
    job_name                  = var.job_name
    max_parallel              = var.max_parallel
    memory                    = var.memory
    prohibit_overlap          = var.prohibit_overlap
    region                    = var.region
    secret_key                = var.secret_key
    stagger                   = var.stagger
    time_zone                 = var.time_zone
    use_host_volume           = var.use_host_volume
    use_vault_provider        = var.vault_secret.use_vault_provider
    vault_kv_policy_name      = var.vault_secret.vault_kv_policy_name
    vault_kv_path             = var.vault_secret.vault_kv_path
    vault_kv_field_access_key = var.vault_secret.vault_kv_field_access_key
    vault_kv_field_secret_key = var.vault_secret.vault_kv_field_secret_key
  }
}

resource "nomad_job" "nomad_job_etl" {
  jobspec = data.template_file.nomad_job_etl.rendered
  detach  = false
}