locals {
  artifact_source = join("",
    [
      "https://github.com",
      "/prometheus/prometheus/releases/download/",
      "v${var.pm_version}/prometheus-${var.pm_version}.linux-amd64.tar.gz"
    ]
  )
  datacenters = join(",", var.datacenters)
}

resource "nomad_job" "nomad_job_prometheus" {
  jobspec = templatefile(
    "${path.module}/conf/nomad/prometheus.hcl.tftpl",
    {
      artifact_source           = local.artifact_source,
      artifact_source_checksum  = var.artifact_source_checksum,
      auto_promote              = var.auto_promote,
      auto_revert               = var.auto_revert,
      canary                    = var.canary,
      cpu                       = var.cpu,
      constraint_value          = var.constraint_value,
      datacenters               = local.datacenters,
      group_count               = var.group_count,
      job_name                  = var.job_name,
      max_parallel              = var.max_parallel,
      memory                    = var.memory
      port                      = var.port,
      region                    = var.region,
      service_name              = var.service_name,
      use_canary                = var.use_canary,
      use_host_volume           = var.use_host_volume,
      use_vault_provider        = var.vault_secret.use_vault_provider,
      vault_kv_policy_name      = var.vault_secret.vault_kv_policy_name,
      vault_kv_path             = var.vault_secret.vault_kv_path,
      vault_kv_field_access_key = var.vault_secret.vault_kv_field_access_key,
      vault_kv_field_secret_key = var.vault_secret.vault_kv_field_secret_key,
      version                   = var.pm_version,
      volume_destination        = var.volume_destination,
      volume_source             = var.volume_source
  })
  detach = false
}
