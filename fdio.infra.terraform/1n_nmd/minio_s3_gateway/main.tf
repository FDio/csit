locals {
  datacenters = join(",", var.datacenters)
  envs        = join("\n", concat([], var.envs))
  upstreams   = jsonencode(var.upstreams)
}

data "template_file" "nomad_job_minio" {
  template = file("${path.module}/conf/nomad/minio.hcl")
  vars = {
    access_key                = var.access_key
    auto_promote              = var.auto_promote
    auto_revert               = var.auto_revert
    canary                    = var.canary
    cpu                       = var.cpu
    cpu_proxy                 = var.resource_proxy.cpu
    datacenters               = local.datacenters
    envs                      = local.envs
    group_count               = var.group_count
    host                      = var.host
    image                     = var.image
    job_name                  = var.job_name
    max_parallel              = var.max_parallel
    memory                    = var.memory
    memory_proxy              = var.resource_proxy.memory
    mode                      = var.mode
    port_base                 = var.port_base
    port_console              = var.port_console
    region                    = var.region
    secret_key                = var.secret_key
    service_name              = var.service_name
    use_canary                = var.use_canary
    use_host_volume           = var.use_host_volume
    upstreams                 = local.upstreams
    use_vault_kms             = var.kms_variables.use_vault_kms
    use_vault_provider        = var.vault_secret.use_vault_provider
    vault_address             = var.kms_variables.vault_address
    vault_kms_approle_kv      = var.kms_variables.vault_kms_approle_kv
    vault_kms_key_name        = var.kms_variables.vault_kms_key_name
    vault_kv_policy_name      = var.vault_secret.vault_kv_policy_name
    vault_kv_path             = var.vault_secret.vault_kv_path
    vault_kv_field_access_key = var.vault_secret.vault_kv_field_access_key
    vault_kv_field_secret_key = var.vault_secret.vault_kv_field_secret_key
    volume_destination        = var.volume_destination
    volume_source             = var.volume_source
  }
}

resource "nomad_job" "nomad_job_minio" {
  jobspec = data.template_file.nomad_job_minio.rendered
  detach  = false
}
