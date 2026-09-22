locals {
  datacenters = join(",", var.datacenters)
  flat_dispatchers = {
    for dispatcher in var.dispatchers : dispatcher.id => dispatcher
  }
}

resource "nomad_job" "hfr-dispatcher" {
  for_each = local.flat_dispatchers
  jobspec = file("${path.cwd}/nomad-${var.job_name}-${each.value.version}.hcl")
  hcl2 {
    allow_fs = true
    vars = {
      cpu         = var.cpu,
      datacenters = local.datacenters,
      image       = "${var.image}:${each.value.version}",
      job_name    = "${var.job_name}-${each.value.version}",
      memory      = var.memory,
      namespace   = each.value.namespace
    }
  }
  detach = false
}

output "nomad_job" {
  description = "ID of the EC2 instance"
  value       = values(nomad_job.hfr-dispatcher).*.id
}