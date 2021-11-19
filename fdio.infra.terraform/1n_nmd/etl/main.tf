locals {
  datacenters = join(",", var.datacenters)
  envs        = join("\n", concat([], var.envs))
  upstreams   = jsonencode(var.upstreams)
}

data "template_file" "nomad_job_etl" {
  template = file("${path.module}/conf/nomad/etl.hcl")
  vars = {
    access_key                = var.access_key
    auto_promote              = var.auto_promote
    auto_revert               = var.auto_revert
    canary                    = var.canary
    cpu                       = var.cpu
    datacenters               = local.datacenters
    envs                      = local.envs
    group_count               = var.group_count
    host                      = var.host
    image                     = var.image
    job_name                  = var.job_name
    max_parallel              = var.max_parallel
    memory                    = var.memory
    region                    = var.region
    secret_key                = var.secret_key
    use_canary                = var.use_canary
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
