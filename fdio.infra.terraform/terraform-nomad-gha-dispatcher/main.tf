locals {
  datacenters = join(",", var.datacenters)
  flat_dispatchers = {
    for dispatcher in var.dispatchers : dispatcher.namespace => dispatcher
  }
}

resource "nomad_job" "gha-dispatcher" {
  for_each = local.flat_dispatchers
  jobspec = templatefile(
    "${path.cwd}/nomad-${var.job_name}.hcl.tftpl",
    {
      cpu         = var.cpu,
      datacenters = local.datacenters,
      image       = "${var.image}-${each.value.namespace}:latest",
      job_name    = "${var.job_name}-${each.value.namespace}-${each.value.repository}",
      memory      = var.memory,
      namespace   = each.value.namespace,
      node_pool   = var.node_pool,
      region      = var.region,
      type        = var.type
  })
  detach = false
}