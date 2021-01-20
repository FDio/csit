locals {
  datacenters = join(",", var.nomad_datacenters)
}

data "template_file" "nomad_job_elastic" {
  template    = file("${path.module}/conf/nomad/elastic.hcl")
  vars        = {
    job_name               = var.elastic_job_name
    datacenters            = local.datacenters
    use_canary             = var.elastic_use_canary
    group_count            = var.elastic_group_count
    version                = var.elastic_version
    cluster_service_name   = var.elastic_cluster_service_name
    cluster_password       = var.elastic_cluster_password
    cluster_cpu            = var.elastic_cluster_cpu
    cluster_memory         = var.elastic_cluster_memory
    cluster_rest_port      = var.elastic_cluster_rest_port
    cluster_transport_port = var.elastic_cluster_transport_port
    kibana_service_name    = var.elastic_kibana_service_name
    kibana_cpu             = var.elastic_kibana_cpu
    kibana_memory          = var.elastic_kibana_memory
    kibana_port            = var.elastic_kibana_port
  }
}

resource "nomad_job" "nomad_job_elastic" {
  jobspec     = data.template_file.nomad_job_elastic.rendered
  detach      = false
}