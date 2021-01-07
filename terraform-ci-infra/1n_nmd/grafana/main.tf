locals {
  datacenters = join(",", var.nomad_datacenters)
}

data "template_file" "nomad_job_grafana" {
  template    = file("${path.module}/conf/nomad/grafana.hcl")
  vars        = {
    datacenters  = local.datacenters
    job_name     = var.grafana_job_name
    use_canary   = var.grafana_use_canary
    group_count  = var.grafana_group_count
    version      = var.grafana_version
    service_name = var.grafana_service_name
    cpu          = var.grafana_cpu
    mem          = var.grafana_mem
    port         = var.grafana_port
  }
}

resource "nomad_job" "nomad_job_grafana" {
  jobspec     = data.template_file.nomad_job_grafana.rendered
  detach      = false
}