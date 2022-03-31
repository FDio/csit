locals {
  datacenters = join(",", var.datacenters)
  envs        = join("\n", concat([], var.envs))
}

resource "nomad_job" "nomad_job_etl" {
  jobspec = templatefile(
    "${path.module}/conf/nomad/etl.hcl.tftpl",
    {
      aws_access_key_id         = var.aws_access_key_id,
      aws_secret_access_key     = var.aws_secret_access_key,
      aws_default_region        = var.aws_default_region
      cpu                       = var.cpu,
      cron                      = var.cron,
      datacenters               = local.datacenters,
      envs                      = local.envs,
      image                     = var.image,
      job_name                  = var.job_name,
      memory                    = var.memory,
      out_aws_access_key_id     = var.out_aws_access_key_id,
      out_aws_secret_access_key = var.out_aws_secret_access_key,
      out_aws_default_region    = var.out_aws_default_region
      prohibit_overlap          = var.prohibit_overlap,
      time_zone                 = var.time_zone,
      type                      = var.type,
      use_vault_provider        = var.vault_secret.use_vault_provider,
      vault_kv_policy_name      = var.vault_secret.vault_kv_policy_name,
      vault_kv_path             = var.vault_secret.vault_kv_path,
      vault_kv_field_access_key = var.vault_secret.vault_kv_field_access_key,
      vault_kv_field_secret_key = var.vault_secret.vault_kv_field_secret_key
  })
  detach = false
}
