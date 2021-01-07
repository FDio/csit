locals {
  datacenters = join(",", var.nomad_datacenters)
}

data "template_file" "nomad_job_prometheus" {
  template    = file("${path.module}/conf/nomad/prometheus.hcl")
  vars        = {
    datacenters               = local.datacenters
    job_name                  = var.prometheus_job_name
    use_canary                = var.prometheus_use_canary
    prometheus_group_count    = var.prometheus_group_count
    prometheus_version        = var.prometheus_version
    prometheus_service_name   = var.prometheus_service_name
    prometheus_cpu            = var.prometheus_cpu
    prometheus_mem            = var.prometheus_mem
    prometheus_port           = var.prometheus_port
    alertmanager_group_count  = var.alertmanager_group_count
    alertmanager_version      = var.alertmanager_version
    alertmanager_service_name = var.alertmanager_service_name
    alertmanager_cpu          = var.alertmanager_cpu
    alertmanager_mem          = var.alertmanager_mem
    alertmanager_port         = var.alertmanager_port
  }
}

resource "nomad_job" "nomad_job_prometheus" {
  jobspec     = data.template_file.nomad_job_prometheus.rendered
  detach      = false
}