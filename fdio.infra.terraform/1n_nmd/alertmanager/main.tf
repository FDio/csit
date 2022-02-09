locals {
  datacenters = join(",", var.datacenters)
  url         = join("",
    [
      "https://github.com",
      "/prometheus/alertmanager/releases/download/",
      "v${var.am_version}/",
      "alertmanager-${var.am_version}.linux-amd64.tar.gz"
    ]
  )
}

resource "nomad_job" "nomad_job_alertmanager" {
  jobspec = templatefile(
    "${path.module}/conf/nomad/alertmanager.hcl.tftpl",
    {
      auto_promote              = var.auto_promote,
      auto_revert               = var.auto_revert,
      canary                    = var.canary,
      cpu                       = var.cpu,
      datacenters               = local.datacenters,
      group_count               = var.group_count,
      job_name                  = var.job_name,
      max_parallel              = var.max_parallel,
      memory                    = var.memory
      port                      = var.port,
      region                    = var.region,
      service_name              = var.service_name,
      slack_jenkins_api_key     = var.slack_jenkins_api_key,
      slack_jenkins_channel     = var.slack_jenkins_channel,
      slack_jenkins_receiver    = var.slack_jenkins_receiver,
      slack_default_api_key     = var.slack_default_api_key,
      slack_default_channel     = var.slack_default_channel,
      slack_default_receiver    = var.slack_default_receiver,
      url                       = local.url,
      use_canary                = var.use_canary,
      use_host_volume           = var.use_host_volume,
      use_vault_provider        = var.vault_secret.use_vault_provider,
      vault_kv_policy_name      = var.vault_secret.vault_kv_policy_name,
      vault_kv_path             = var.vault_secret.vault_kv_path,
      vault_kv_field_access_key = var.vault_secret.vault_kv_field_access_key,
      vault_kv_field_secret_key = var.vault_secret.vault_kv_field_secret_key,
      version                   = var.am_version,
      volume_destination        = var.volume_destination,
      volume_source             = var.volume_source
  })
  detach = false
}
