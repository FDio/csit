locals {
  datacenters             = join(",", var.nomad_datacenters)

  node_exporter_url_amd64 = join("",
    [
      "https://github.com",
      "/prometheus/node_exporter/releases/download/",
      "v${var.node_exporter_version}/",
      "node_exporter-${var.node_exporter_version}.linux-amd64.tar.gz"
    ]
  )
  node_exporter_url_arm64 = join("",
    [
      "https://github.com",
      "/prometheus/node_exporter/releases/download/",
      "v${var.node_exporter_version}/",
      "node_exporter-${var.node_exporter_version}.linux-arm64.tar.gz"
    ]
  )
}

data "template_file" "nomad_job_exporter" {
  template         = file("${path.module}/conf/nomad/exporter.hcl")
  vars             = {
    datacenters                = local.datacenters
    job_name                   = var.exporter_job_name
    use_canary                 = var.exporter_use_canary
    node_exporter_url_amd64    = local.node_exporter_url_amd64
    node_exporter_url_arm64    = local.node_exporter_url_arm64
    node_exporter_version      = var.node_exporter_version
    node_exporter_service_name = var.node_exporter_service_name
    node_exporter_port         = var.node_exporter_port
  }
}

resource "nomad_job" "nomad_job_exporter" {
  jobspec          = data.template_file.nomad_job_exporter.rendered
  detach           = false
}