locals {
  datacenters    = join(",", var.nomad_datacenters)

  prometheus_url = join("",
    [
      "https://github.com",
      "/prometheus/prometheus/releases/download/",
      "v${var.prometheus_version}/",
      "prometheus-${var.prometheus_version}.linux-amd64.tar.gz"
    ]
  )
}

data "template_file" "nomad_job_prometheus" {
  template       = file("${path.module}/conf/nomad/prometheus.hcl")
  vars           = {
    datacenters        = local.datacenters
    url                = local.prometheus_url
    job_name           = var.prometheus_job_name
    use_canary         = var.prometheus_use_canary
    group_count        = var.prometheus_group_count
    use_host_volume    = var.prometheus_use_host_volume
    host_volume        = var.nomad_host_volume
    data_dir           = var.prometheus_data_dir
    service_name       = var.prometheus_service_name
    use_vault_provider = var.prometheus_vault_secret.use_vault_provider
    version            = var.prometheus_version
    cpu                = var.prometheus_cpu
    mem                = var.prometheus_mem
    port               = var.prometheus_port
  }
}

resource "nomad_job" "nomad_job_prometheus" {
  jobspec        = data.template_file.nomad_job_prometheus.rendered
  detach         = false
}