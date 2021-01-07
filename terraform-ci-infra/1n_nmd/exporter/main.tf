locals {
  datacenters             = join(",", var.nomad_datacenters)

  node_url_amd64 = join("",
    [
      "https://github.com",
      "/prometheus/node_exporter/releases/download/",
      "v${var.node_version}/",
      "node_exporter-${var.node_version}.linux-amd64.tar.gz"
    ]
  )
  node_url_arm64 = join("",
    [
      "https://github.com",
      "/prometheus/node_exporter/releases/download/",
      "v${var.node_version}/",
      "node_exporter-${var.node_version}.linux-arm64.tar.gz"
    ]
  )

  blackbox_url_amd64 = join("",
    [
      "https://github.com",
      "/prometheus/blackbox_exporter/releases/download/",
      "v${var.blackbox_version}/",
      "blackbox_exporter-${var.blackbox_version}.linux-amd64.tar.gz"
    ]
  )
  blackbox_url_arm64 = join("",
    [
      "https://github.com",
      "/prometheus/blackbox_exporter/releases/download/",
      "v${var.blackbox_version}/",
      "blackbox_exporter-${var.blackbox_version}.linux-arm64.tar.gz"
    ]
  )
}

data "template_file" "nomad_job_exporter" {
  template         = file("${path.module}/conf/nomad/exporter.hcl")
  vars             = {
    datacenters               = local.datacenters
    job_name                  = var.exporter_job_name
    use_canary                = var.exporter_use_canary
    node_url_amd64            = local.node_url_amd64
    node_url_arm64            = local.node_url_arm64
    node_version              = var.node_version
    node_service_name         = var.node_service_name
    node_port                 = var.node_port
    blackbox_url_amd64        = local.blackbox_url_amd64
    blackbox_url_arm64        = local.blackbox_url_arm64
    blackbox_version          = var.blackbox_version
    blackbox_service_name     = var.blackbox_service_name
    blackbox_port             = var.blackbox_port
    cadvisor_image            = var.cadvisor_image
    cadvisor_service_name     = var.cadvisor_service_name
    cadvisor_port             = var.cadvisor_port
  }
}

resource "nomad_job" "nomad_job_exporter" {
  jobspec          = data.template_file.nomad_job_exporter.rendered
  detach           = false
}