locals {
  datacenters = join(",", var.datacenters)
}

resource "nomad_job" "nomad_job_csit_shim" {
  jobspec = templatefile(
    "${path.module}/conf/nomad/vpp-device.hcl.tftpl",
    {
        datacenters   = local.datacenters
        job_name      = var.job_name
        group_count   = var.group_count
        cpu           = var.cpu
        mem           = var.memory
        image_aarch64 = var.image_aarch64
        image_x86_64  = var.image_x86_64
    }
  )
  detach  = false
}