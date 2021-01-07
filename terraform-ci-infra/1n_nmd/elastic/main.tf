locals {
  datacenters = join(",", var.nomad_datacenters)
}

data "template_file" "nomad_job_beats" {
  template    = file("${path.module}/conf/nomad/beats.hcl")
  vars        = {
    job_name               = var.beats_job_name
    datacenters            = local.datacenters
    use_canary             = var.beats_use_canary
    data_dir               = var.beats_data_dir
    version                = var.beats_version
  }
}

data "template_file" "nomad_job_elastic" {
  template    = file("${path.module}/conf/nomad/elastic.hcl")
  vars        = {
    job_name               = var.elastic_job_name
    datacenters            = local.datacenters
    use_canary             = var.elastic_use_canary
    service_name           = var.elastic_service_name
    group_count            = var.elastic_group_count
    version                = var.elastic_version
    cluster_cpu            = var.elastic_cluster_cpu
    cluster_memory         = var.elastic_cluster_memory
    cluster_rest_port      = var.elastic_cluster_rest_port
    cluster_transport_port = var.elastic_cluster_transport_port
    kibana_cpu             = var.elastic_kibana_cpu
    kibana_memory          = var.elastic_kibana_memory
    kibana_port            = var.elastic_kibana_port
  }
}

resource "nomad_job" "nomad_job_beats" {
  jobspec     = data.template_file.nomad_job_beats.rendered
  detach      = false
}

resource "nomad_job" "nomad_job_elastic" {
  jobspec     = data.template_file.nomad_job_elastic.rendered
  detach      = false
}