locals {
  datacenters              = join(",", var.nomad_datacenters)
}

data "template_file" "nomad_job_beats" {
  template    = file("${path.module}/conf/nomad/beats.hcl")
  vars        = {
    job_name           = var.beats_job_name
    datacenters        = local.datacenters
    use_canary         = var.beats_use_canary
    group_count        = var.beats_group_count
    data_dir           = var.beats_data_dir
    version            = var.beats_version
  }
}

resource "nomad_job" "nomad_job_beats" {
  jobspec     = data.template_file.nomad_job_beats.rendered
  detach      = false
}