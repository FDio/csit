locals {
  datacenters = join(",", var.nomad_datacenters)
}

data "template_file" "nomad_job_grafana" {
  template    = file("${path.module}/conf/nomad/grafana.hcl")
  vars        = {
    datacenters        = local.datacenters
    job_name           = var.grafana_job_name
    use_canary         = var.grafana_use_canary
    group_count        = var.grafana_group_count
    service_name       = var.grafana_service_name
    use_vault_provider = var.grafana_vault_secret.use_vault_provider
    image              = var.grafana_container_image
    cpu                = var.grafana_cpu
    mem                = var.grafana_mem
    port               = var.grafana_port
  }
}

resource "nomad_job" "nomad_job_grafana" {
  jobspec     = data.template_file.nomad_job_grafana.rendered
  detach      = false
}