locals {
  datacenters = join(",", var.nomad_datacenters)
}

data "template_file" "nomad_job_csit_shim" {
  template    = file("${path.module}/conf/nomad/csit_shim.hcl")
  vars        = {
    datacenters   = local.datacenters
    job_name      = var.csit_shim_job_name
    group_count   = var.csit_shim_group_count
    cpu           = var.csit_shim_cpu
    mem           = var.csit_shim_mem
    image_aarch64 = var.csit_shim_image_aarch64
    image_x86_64  = var.csit_shim_image_x86_64
  }
}

resource "nomad_job" "nomad_job_csit_shim" {
  jobspec     = data.template_file.nomad_job_csit_shim.rendered
  detach      = false
}