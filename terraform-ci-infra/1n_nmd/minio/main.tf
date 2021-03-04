locals {
  datacenters              = join(",", var.nomad_datacenters)
  minio_env_vars           = join("\n",
    concat([
    ], var.minio_envs)
  )
  mc_env_vars              = join("\n",
    concat([
    ], var.mc_envs)
  )
  mc_formatted_bucket_list = formatlist("LOCALMINIO/%s", var.minio_buckets)
  mc_add_config_command    = concat(
    [
      "mc",
      "config",
      "host",
      "add",
      "LOCALMINIO",
      "http://${var.minio_service_name}.service.consul:${var.minio_port}",
      "$MINIO_ACCESS_KEY",
      "$MINIO_SECRET_KEY",
  ])
  mc_create_bucket_command = concat(["mc", "mb", "-p"], local.mc_formatted_bucket_list)
  command                  = join(" ", concat(local.mc_add_config_command, ["&&"], local.mc_create_bucket_command, [";"], concat(var.mc_extra_commands)))
}

data "template_file" "nomad_job_minio" {
  template    = file("${path.module}/conf/nomad/minio.hcl")
  vars        = {
    job_name           = var.minio_job_name
    datacenters        = local.datacenters
    use_canary         = var.minio_use_canary
    group_count        = var.minio_group_count
    use_host_volume    = var.minio_use_host_volume
    host_volume        = var.nomad_host_volume
    service_name       = var.minio_service_name
    host               = var.minio_host
    port               = var.minio_port
    upstreams          = jsonencode(var.minio_upstreams)
    cpu_proxy          = var.minio_resource_proxy.cpu
    memory_proxy       = var.minio_resource_proxy.memory
    use_vault_provider = var.minio_vault_secret.use_vault_provider
    image              = var.minio_container_image
    access_key         = var.minio_access_key
    secret_key         = var.minio_secret_key
    data_dir           = var.minio_data_dir
    envs               = local.minio_env_vars
    cpu                = var.minio_cpu
    memory             = var.minio_memory
  }
}

data "template_file" "nomad_job_mc" {
  template    = file("${path.module}/conf/nomad/mc.hcl")
  vars        = {
    job_name           = var.mc_job_name
    service_name       = var.mc_service_name
    datacenters        = local.datacenters
    minio_service_name = var.minio_service_name
    minio_port         = var.minio_port
    image              = var.mc_container_image
    access_key         = var.minio_access_key
    secret_key         = var.minio_secret_key
    use_vault_provider = var.minio_vault_secret.use_vault_provider
    envs               = local.mc_env_vars
    command            = local.command
  }
}

resource "nomad_job" "nomad_job_minio" {
  jobspec     = data.template_file.nomad_job_minio.rendered
  detach      = false
}

#resource "nomad_job" "nomad_job_mc" {
#  jobspec     = data.template_file.nomad_job_mc.rendered
#  detach      = false
#
#  depends_on  = [
#    nomad_job.nomad_job_minio
#  ]
#}